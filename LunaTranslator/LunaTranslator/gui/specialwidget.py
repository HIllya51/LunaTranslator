from qtsymbols import *
from traceback import print_exc
from myutils.wrapper import trypass
import threading


class chartwidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        font = QFont("Arial", 10)
        fmetrics = QFontMetrics(font)

        fhall = fmetrics.height()
        self.font = font

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


class ScrollFlow(QWidget):
    bgclicked = pyqtSignal()

    def resizeEvent(self, a0) -> None:
        self.qscrollarea.resize(self.size())
        return super().resizeEvent(a0)

    def __init__(self):
        super(ScrollFlow, self).__init__()

        class qw(QWidget):
            def mousePressEvent(_, _2) -> None:
                self.bgclicked.emit()

        self.listWidget = qw(self)
        # self.listWidget.setFixedWidth(600)
        self.lazyitems = []
        self.lazydoneidx = []
        self.l = FlowLayout()

        self.listWidget.setLayout(self.l)

        self.qscrollarea = QScrollArea(self)
        self.qscrollarea.setWidgetResizable(True)
        self.qscrollarea.setWidget(self.listWidget)

    @trypass
    def addwidget(self, wid):
        self.l.addWidget(wid)

    @trypass
    def insertwidget(self, idx, wid):
        self.l.insertWidget(idx, wid)

    @trypass
    def removeidx(self, index):
        _ = self.l.takeAt(index)
        _.widget().hide()

    @trypass
    def setfocus(self, idx):
        self.widget(idx).setFocus()

    @trypass
    def widget(self, idx):
        idx = min(idx, len(self.l._item_list) - 1)
        idx = max(idx, 0)
        return self.l._item_list[idx].widget()


class FlowLayout(QLayout):
    heightChanged = pyqtSignal(int)

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self._item_list = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def insertWidget(self, idx, widget):
        item = QWidgetItem(widget)
        widget.setParent(self.parentWidget())
        widget.adjustSize()
        widget.setVisible(True)
        self._item_list.insert(idx, item)

        self._do_layout(self.geometry(), False)

    def addItem(self, item):  # pylint: disable=invalid-name
        self._item_list.append(item)

    def addSpacing(self, size):  # pylint: disable=invalid-name
        self.addItem(
            QSpacerItem(size, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        )

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def setGeometry(self, rect):  # pylint: disable=invalid-name
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):  # pylint: disable=invalid-name
        return self.minimumSize()

    def minimumSize(self):  # pylint: disable=invalid-name
        size = QSize()

        for item in self._item_list:
            minsize = item.minimumSize()
            extent = item.geometry().bottomRight()
            size = size.expandedTo(QSize(minsize.width(), extent.y()))

        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _do_layout(self, rect, test_only=False):
        m = self.contentsMargins()
        effective_rect = rect.adjusted(+m.left(), +m.top(), -m.right(), -m.bottom())
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0
        for item in self._item_list:
            wid = item.widget()

            space_x = self.spacing()
            space_y = self.spacing()
            if wid is not None:
                space_x += wid.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Horizontal,
                )
                space_y += wid.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical,
                )

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                sz = item.sizeHint()
                item.setGeometry(QRect(QPoint(x, y), sz))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        new_height = y + line_height - rect.y()
        self.heightChanged.emit(new_height)
        return new_height


class lazyscrollflow(QWidget):
    bgclicked = pyqtSignal()

    def mousePressEvent(self, _2) -> None:
        self.bgclicked.emit()

    def __init__(self):
        super().__init__()
        self.widgets = []
        self.fakegeos = []
        self._spacing = 6
        self._margin = self._spacing  # 9
        self.lock = threading.Lock()
        self.internalwid = QWidget(self)
        self.qscrollarea = ScrollArea(self)
        self.qscrollarea.setWidgetResizable(True)
        self.qscrollarea.setWidget(self.internalwid)
        self.qscrollarea.scrolled.connect(lambda _: self.doshowlazywidget(True, _))

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.qscrollarea.resize(self.size())
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

                widfunc, _ = self.widgets[i]
                if not widfunc:
                    continue
                self.widgets[i] = (None, _)
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
                pass

    @trypass
    def resizeandshow(self, procevent=True):
        self.fakeresize()
        self.doshowlazywidget(procevent, self.internalwid.visibleRegion())

    def addwidget(self, widfunc):
        self.insertwidget(-1, widfunc)

    @trypass
    def switchidx(self, idx1, idx2):
        with self.lock:
            self.widgets[idx1], self.widgets[idx2] = (
                self.widgets[idx2],
                self.widgets[idx1],
            )
            self.fakegeos[idx1], self.fakegeos[idx2] = (
                self.fakegeos[idx2],
                self.fakegeos[idx1],
            )
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

            if isinstance(widfunc, QWidget):
                widfunc.setParent(self.internalwid)
                widfunc.adjustSize()
                widfunc.setVisible(True)
        if refresh:
            self.resizeandshow()

    @trypass
    def removeidx(self, idx):
        with self.lock:
            if idx >= 0 and idx < len(self.widgets):
                w = self.widgets[idx]
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

    def spacing(self):
        return self._spacing

    def fakeresize(self):
        if self.qscrollarea.verticalScrollBar().isVisible():
            scrollw = self.qscrollarea.verticalScrollBar().width()
        else:
            scrollw = 0
        with self.lock:
            # m = self.contentsMargins()
            rect = QRect()
            rect.setSize(self.size())
            effective_rect = rect.adjusted(
                self._margin, self._margin, -self._margin, -self._margin
            )  # (+m.left(), +m.top(), -m.right(), -m.bottom())
            x = effective_rect.x()
            y = effective_rect.y()
            line_height = 0
            for i, wid in enumerate(self.widgets):

                space_x = self.spacing()
                space_y = self.spacing()

                if isinstance(wid, QWidget):
                    sz = wid.size()
                    resize = True
                else:
                    _, sz = wid
                    resize = False
                next_x = x + sz.width() + space_x
                if next_x > effective_rect.right() - scrollw and line_height > 0:
                    x = effective_rect.x()
                    y = y + line_height + space_y
                    next_x = x + sz.width() + space_x
                    line_height = 0
                if resize:
                    wid.setGeometry(QRect(QPoint(x, y), sz))
                self.fakegeos[i] = QRect(QPoint(x, y), sz)
                x = next_x
                line_height = max(line_height, sz.height())

            new_height = y + line_height - rect.y() + self._margin
            self.internalwid.setFixedHeight(new_height)
            return new_height
