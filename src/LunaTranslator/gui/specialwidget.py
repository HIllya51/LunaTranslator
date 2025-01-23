from qtsymbols import *
import threading
from traceback import print_exc
from myutils.wrapper import trypass


class chartwidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        font = QFont("Arial", 10)
        fmetrics = QFontMetricsF(font)

        fhall = fmetrics.height()
        self.font = font
        self.data = None
        self.ymargin = int(fhall) + 10  # 20
        self.valuewidth = 10
        self.xtext = lambda x: str(x)
        self.ytext = lambda y: str(y)
        self.fmetrics = fmetrics
        self.scalelinelen = 5

    def setdata(self, data):
        data = sorted(data, key=lambda _: _[0])
        self.data = data

    def paintEvent(self, event):
        if self.data is None or len(self.data) == 0:
            return
        try:
            if len(self.data) == 1:
                self.data.insert(0, (0, 0))
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            pen = QPen(Qt.GlobalColor.blue)
            pen.setWidth(2)
            painter.setPen(pen)

            painter.setFont(self.font)

            ymargin = self.ymargin

            xmargin = 0

            max_y = int(max(y for _, y in self.data))
            y_labels = [self.ytext(i * max_y / 5) for i in range(6)]

            x_labels = [self.xtext(x) for x, _ in self.data]
            for l in y_labels:
                xmargin = max(xmargin, self.fmetrics.size(0, l).width())

            xmargin = xmargin + self.scalelinelen

            width = (
                self.width()
                - xmargin
                - max(
                    self.fmetrics.size(0, x_labels[-1]).width() // 2,
                    self.fmetrics.size(0, self.ytext(self.data[-1][1])).width() // 2,
                )
            )

            height = self.height() - 2 * ymargin

            # 纵坐标
            for i, label in enumerate(y_labels):
                y = int(ymargin + height - i * (height / 5))
                painter.drawLine(xmargin - self.scalelinelen, y, xmargin, y)
                painter.drawText(
                    xmargin - self.scalelinelen - self.fmetrics.size(0, label).width(),
                    y + 5,
                    label,
                )

            painter.drawLine(xmargin, ymargin, xmargin, ymargin + height)  # Y轴
            painter.drawLine(
                xmargin, ymargin + height, xmargin + width, ymargin + height
            )  # X轴

            # 计算数据点在绘图区域中的坐标
            x_scale = width / (len(self.data) - 1)
            y_scale = height / max(max(y for _, y in self.data), 1)

            points = []
            for i, (x, y) in enumerate(self.data):
                x_coord = xmargin + i * x_scale
                y_coord = ymargin + height - y * y_scale
                points.append((int(x_coord), int(y_coord)))

            # 绘制折线
            rects = []
            texth = self.fmetrics.height()
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                painter.drawLine(x1, y1, x2, y2)

                if self.data[i + 1][1]:  #!=0
                    text = self.ytext(self.data[i + 1][1])
                    W = self.fmetrics.size(0, text).width()
                    newrect = QRect(x2 - W // 2, y2 - 10, W, texth)
                    if any(_.intersected(newrect) for _ in rects):
                        continue
                    else:
                        rects.append(newrect)
                        painter.drawText(x2 - W // 2, y2 - 10, text)  # value
            lastx2 = -999
            for i, (x, y) in enumerate(points):
                painter.drawLine(x, ymargin + height, x, ymargin + height + 5)  # 刻度线

                thisw = self.fmetrics.size(0, x_labels[i]).width()
                thisx = x - thisw // 2

                if thisx > lastx2:

                    painter.drawText(
                        thisx,
                        ymargin + height + 20,
                        x_labels[i],
                    )  # 标签
                    lastx2 = thisx + thisw

        except:
            print_exc()


class ScrollArea(QScrollArea):
    scrolled = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalScrollBar().valueChanged.connect(self.handleScroll)

    def handleScroll(self, value):

        viewport_rect = self.viewport().rect()
        horizontal_scrollbar = self.horizontalScrollBar()
        vertical_scrollbar = self.verticalScrollBar()

        x = horizontal_scrollbar.value()
        y = vertical_scrollbar.value()
        width = viewport_rect.width()
        height = viewport_rect.height()

        visible_rect = QRect(x, y, width, height)
        self.scrolled.emit(visible_rect)

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Left or e.key() == Qt.Key.Key_Right:
            return e.ignore()
        super().keyPressEvent(e)


class lazyscrollflow(ScrollArea):
    bgclicked = pyqtSignal()

    def mousePressEvent(self, _2) -> None:
        self.bgclicked.emit()

    def directshow(self):
        QApplication.processEvents()
        self.doshowlazywidget(True, self.internalwid.visibleRegion().boundingRect())

    def __init__(self):
        super().__init__()
        self.setStyleSheet("lazyscrollflow{background: transparent;}")
        self.widgets = []
        self.fakegeos = []
        self._spacing = 6
        self._margin = self._spacing  # 9
        self.lock = threading.Lock()
        self.internalwid = QWidget(self)
        self.setWidgetResizable(True)
        self.setWidget(self.internalwid)
        self.scrolled.connect(lambda _: self.doshowlazywidget(True, _))

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resizeandshow(False)
        return super().resizeEvent(a0)

    @trypass
    def doshowlazywidget(self, procevent, region: QRect):
        needdos = []
        with self.lock:
            for i, geo in enumerate(self.fakegeos):
                if isinstance(self.widgets[i], QWidget):
                    continue

                if not region.intersects(geo):
                    continue

                widfunc = self.widgets[i]
                if not widfunc:
                    continue
                self.widgets[i] = None
                needdos.append((i, widfunc))
        for i, widfunc in needdos:
            try:
                with self.lock:
                    widfunc = widfunc()
                    widfunc.setParent(self.internalwid)
                    widfunc.adjustSize()
                    widfunc.setVisible(True)
                    widfunc.setGeometry(self.fakegeos[i])
                    self.widgets[i] = widfunc
                if procevent:
                    QApplication.processEvents()  # 会在最大化时死锁

            except:
                break

    @trypass
    def resizeandshow(self, procevent=True):
        self.fakeresize()
        self.doshowlazywidget(procevent, self.internalwid.visibleRegion())

    def addwidget(self, widfunc):
        self.insertwidget(-1, widfunc)

    @trypass
    def switchidx(self, idx1, idx2):
        with self.lock:
            self.widgets.insert(idx2, self.widgets.pop(idx1))
            self.fakegeos.insert(idx2, self.fakegeos.pop(idx1))
        self.resizeandshow()

    @trypass
    def insertwidget(self, idx, widfunc):
        refresh = True
        with self.lock:
            if idx == -1:
                refresh = False
                idx = len(self.widgets)
            self.widgets.insert(idx, widfunc)
            self.fakegeos.insert(idx, QRect())
        if refresh:
            self.resizeandshow()

    @trypass
    def totop1(self, idx):
        if idx == 0:
            return
        with self.lock:
            self.widgets.insert(0, self.widgets.pop(idx))
            self.fakegeos.insert(0, self.fakegeos.pop(idx))
        self.resizeandshow()

    @trypass
    def removeidx(self, idx):
        with self.lock:
            if idx >= 0 and idx < len(self.widgets):
                w = self.widgets[idx]
                if isinstance(w, QWidget):
                    w.setParent(None)
                    w.deleteLater()
                self.widgets.pop(idx)
                self.fakegeos.pop(idx)
        self.resizeandshow()

    @trypass
    def setfocus(self, idx):
        self.widget(idx).setFocus()

    @trypass
    def widget(self, idx):
        with self.lock:
            if idx > 0 or idx < len(self.widgets):
                return self.widgets[idx]
            else:
                return None

    def setsize(self, size: QSize):
        self._size = size

    def setSpacing(self, s):
        self._spacing = s

    def spacing(self):
        return self._spacing

    def anylyze(self, effective_rect: QRect, space_x, N):
        x = effective_rect.x()
        for _ in range(N):
            next_x = x + self._size.width() + space_x
            if next_x > effective_rect.right():
                return x
            x = next_x
        return x

    def fakeresize(self):
        with self.lock:
            scrollw = (
                self.verticalScrollBar().width()
                if self.verticalScrollBar().isVisible()
                else 0
            )
            effective_rect = QRect(
                self._margin,
                self._margin,
                self.width() - 2 * self._margin - scrollw,
                self.height() - 2 * self._margin,
            )
            x = effective_rect.x()
            y = effective_rect.y()
            space_x = self.spacing()
            space_y = self.spacing()
            dx = (
                effective_rect.right()
                - self.anylyze(effective_rect, space_x, len(self.widgets))
            ) // 2
            for i, wid in enumerate(self.widgets):
                if isinstance(wid, QWidget):
                    resize = True
                else:
                    resize = False
                next_x = x + self._size.width() + space_x
                if next_x > effective_rect.right() and i:
                    x = effective_rect.x()
                    y = y + self._size.height() + space_y
                    next_x = x + self._size.width() + space_x
                if resize:
                    wid.setGeometry(QRect(QPoint(x + dx, y), self._size))
                self.fakegeos[i] = QRect(QPoint(x + dx, y), self._size)
                x = next_x

            new_height = y + self._size.height() + self._margin
        self.internalwid.setFixedHeight(new_height)


def has_intersection(interval1, interval2):
    start = max(interval1[0], interval2[0])
    end = min(interval1[1], interval2[1])

    if start <= end:
        return True
    else:
        return None


class delayloadvbox(QWidget):

    def setheight(self, h):
        self._h = h
        self.setFixedHeight(len(self.internal_widgets) * self._h)
        for _ in self.internal_widgets:
            if isinstance(_, QWidget):
                _.resize(_.width(), h)

    def __init__(self, h=1):
        super().__init__()
        self._h = h
        self.internal_widgets = []
        self.lock = threading.Lock()
        self.nowvisregion = QRect()

    def resizeEvent(self, e: QResizeEvent):

        if e.oldSize().width() != e.size().width():
            with self.lock:
                for w in self.internal_widgets:
                    if isinstance(w, QWidget):
                        w.resize(self.width(), w.height())
        return super().resizeEvent(e)

    def _dovisinternal(self, procevent, region: QRect):
        if region.isEmpty():
            return
        visrange = (region.y(), region.y() + region.height())
        ylastend = self.y()
        ydiff = self.y()
        needdos = []
        with self.lock:
            for i in range(len(self.internal_widgets)):
                ystart = ylastend
                yend = ystart + self._h
                ylastend = yend
                if isinstance(self.internal_widgets[i], QWidget):
                    self.internal_widgets[i].move(0, ystart - ydiff)
                    continue
                if not has_intersection((ystart, yend), visrange):
                    continue

                widfunc = self.internal_widgets[i]
                if not widfunc:
                    continue
                self.internal_widgets[i] = None
                needdos.append((i, widfunc, ystart - ydiff, self._h))

        for i, widfunc, ystart, h in needdos:
            try:
                with self.lock:
                    widfunc = widfunc()
                    widfunc.setParent(self)
                    widfunc.setVisible(True)
                    widfunc.move(0, ystart)
                    widfunc.resize(self.width(), h)
                    self.internal_widgets[i] = widfunc
                if procevent:
                    QApplication.processEvents()
            except:
                break

        self.nowvisregion = region

    @trypass
    def switchidx(self, idx1, idx2):
        with self.lock:
            self.internal_widgets.insert(idx2, self.internal_widgets.pop(idx1))
        self._dovisinternal(False, self.nowvisregion)

    def popw(self, i):
        with self.lock:
            if i >= 0 and i < self.len():
                w = self.internal_widgets[i]
                if isinstance(w, QWidget):
                    w.setParent(None)
                    w.deleteLater()
                self.internal_widgets.pop(i)
            self.setFixedHeight(len(self.internal_widgets) * self._h)
            # setFixedHeight会导致上面的闪烁
        self._dovisinternal(False, self.nowvisregion)

    def torank1(self, i):
        if i == 0:
            return
        with self.lock:
            self.internal_widgets.insert(0, self.internal_widgets.pop(i))
        self._dovisinternal(False, self.nowvisregion)

    def insertw(self, i, wf):
        refresh = True
        with self.lock:
            if i == -1:
                refresh = False
                i = self.len()
            self.internal_widgets.insert(i, wf)
            self.setFixedHeight(len(self.internal_widgets) * self._h)
        if refresh:
            self._dovisinternal(False, self.nowvisregion)

    def w(self, i):
        _ = self.internal_widgets[i]
        if isinstance(_, QWidget):
            return _
        return None

    def len(self):
        return len(self.internal_widgets)


class shownumQPushButton(QPushButton):
    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self.num = 0
        self.setCheckable(True)
        self.clicked.connect(self.setChecked)

    def setnum(self, num):
        self.num = num
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.num:
            return
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.gray)
        rect = self.rect()

        textRect = self.fontMetrics().boundingRect(self.text())
        numberRect = rect.adjusted(textRect.width() + 10, 0, -10, 0)

        painter.drawText(
            numberRect,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            str(self.num),
        )

        numberRect = rect.adjusted(10, 0, textRect.width() + -10, 0)
        painter.drawText(
            numberRect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            ("+", "-")[self.isChecked()],
        )


class shrinkableitem(QWidget):
    def __init__(self, p, shrinker: shownumQPushButton, opened):
        super().__init__(p)
        self.lay = QVBoxLayout(self)
        # self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        self.btn = shrinker
        self.items = delayloadvbox()
        self.btn.clicked.connect(self.Revert)
        self.lay.addWidget(self.btn)
        self.lay.addWidget(self.items)
        self.items.setVisible(opened)
        shrinker.setChecked(opened)
        self._ref_p_stackedlist = p
        self._h = 1

    def visheight(self):
        hh = self.btn.height()
        if self.items.isVisible():
            hh += self.items.height()
        return hh

    def _dovisinternal(self, procevent, region: QRect):
        if not self.items.isVisible():
            return

        region.setY(region.y() - self.btn.height())
        # region.setHeight(region.height() - self.btn.height())
        # 按理说应该减的，但不知道其他哪里写错了，下面少几十个像素的高度，就这样吧。
        self.items._dovisinternal(procevent, QRect(region))

    def Revert(self):
        self.items.setVisible(not self.items.isVisible())
        self._ref_p_stackedlist.doshowlazywidget(True)

    def settitle(self, text):
        self.btn.setText(text)

    @trypass
    def switchidx(self, idx1, idx2):
        self.items.switchidx(idx1, idx2)

    def insertw(self, i, wf):
        self.items.insertw(i, wf)

    def torank1(self, i):
        self.items.torank1(i)

    def popw(self, i):
        return self.items.popw(i)

    def w(self, i):
        return self.items.w(i)

    def len(self):
        return self.items.len()

    def button(self):
        return self.btn

    def setheight(self, h):
        self.items.setheight(h)


class stackedlist(ScrollArea):
    bgclicked = pyqtSignal()

    def setheight(self, h):
        for i in range(self.len()):
            self.w(i).setheight(h)
        self._h = h

    def mousePressEvent(self, _2) -> None:
        self.bgclicked.emit()

    def directshow_1(self):
        self.doshowlazywidget(True, self.internal.visibleRegion().boundingRect())

    def directshow(self):
        QApplication.processEvents()
        self.doshowlazywidget(True, self.internal.visibleRegion().boundingRect())

    def resizeEvent(self, e: QResizeEvent):
        try:
            self.doshowlazywidget(False, self.internal.visibleRegion().boundingRect())
        except:
            pass
        return super().resizeEvent(e)

    def __init__(self):
        super().__init__()
        self._h = 1
        self.setStyleSheet(
            """QWidget#shit{background-color:transparent;}QScrollArea{background-color:transparent;border:0px}"""
        )
        self.setWidgetResizable(True)
        internal = QWidget()
        internal.setObjectName("shit")
        self.setWidget(internal)
        self.setWidgetResizable(True)
        self.lay = QVBoxLayout(internal)
        self.lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.widgets = []
        self.fakegeos = []
        self._spacing = 6
        self._margin = self._spacing  # 9
        self.lock = threading.Lock()
        self.internal = internal
        self.scrolled.connect(lambda _: self.doshowlazywidget(True, _))
        self.saveregion = QRect()

    @trypass
    def doshowlazywidget(self, procevent, region: QRect = None):
        if region:
            self.saveregion = QRect(region)
        else:
            region = QRect(self.saveregion)
        for i in range(self.len()):
            self.w(i)._dovisinternal(procevent, QRect(region))
            region.setY(region.y() - self.w(i).visheight())
            region.setHeight(region.height() - self.w(i).visheight())

    def insertw(self, i, w: shrinkableitem):
        w.setheight(self._h)
        self.lay.insertWidget(i, w)

    def popw(self, i) -> shrinkableitem:
        self.lay.takeAt(i).widget().deleteLater()

    def w(self, i) -> shrinkableitem:
        return self.lay.itemAt(i).widget()

    def len(self):
        return self.lay.count()

    def switchidx(self, i1, i2):
        self.lay.insertItem(i2, self.lay.takeAt(i1))
