from qtsymbols import *
import os, re, functools, hashlib, json, math, csv, io, pickle
from traceback import print_exc
import windows, qtawesome, winsharedutils, gobject, platform, threading
from myutils.config import _TR, globalconfig, mayberelpath
from myutils.wrapper import Singleton, threader
from myutils.utils import nowisdark, checkisusingwine
from ctypes import POINTER, cast, c_char
from gui.dynalang import (
    LLabel,
    LPushButton,
    LAction,
    LGroupBox,
    LFormLayout,
    LTabWidget,
    LStandardItemModel,
    LDialog,
    LMainWindow,
    LToolButton,
)


class FocusCombo(QComboBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:

        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


class SuperCombo(FocusCombo):
    Visoriginrole = Qt.ItemDataRole.UserRole + 1
    Internalrole = Visoriginrole + 1

    def __init__(self, parent=None, static=False) -> None:
        super().__init__(parent)
        self.mo = QStandardItemModel()
        self.static = static
        self.setModel(self.mo)
        self.vu = QListView()
        self.setView(self.vu)

    def addItem(self, item, internal=None, icon=None):
        text = _TR(item) if not self.static else item
        if icon:
            item1 = QStandardItem(icon, text)
        else:
            item1 = QStandardItem(text)
        item1.setData(item, self.Visoriginrole)
        item1.setData(internal, self.Internalrole)
        self.mo.appendRow(item1)

    def clear(self):
        self.mo.clear()

    def addItems(self, items, internals=None, icons=None):
        for i, item in enumerate(items):
            iternal = None
            if internals and i < len(internals):
                iternal = internals[i]
            icon = icons[i] if icons else None
            self.addItem(item, iternal, icon=icon)

    def updatelangtext(self):
        if self.static:
            return
        for _ in range(self.mo.rowCount()):
            item = self.mo.item(_, 0)
            item.setData(
                _TR(item.data(self.Visoriginrole)), Qt.ItemDataRole.DisplayRole
            )

    def getIndexData(self, index):
        item = self.mo.item(index, 0)
        return item.data(self.Internalrole)

    def setRowVisible(self, row, vis):
        self.vu.setRowHidden(row, not vis)
        item = self.mo.item(row, 0)
        if vis:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
        else:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)


class FocusFontCombo(QFontComboBox, FocusCombo):
    pass


class FocusSpinBase(QAbstractSpinBox):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:
        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


class FocusSpin(QSpinBox, FocusSpinBase):
    pass


class FocusDoubleSpin(QDoubleSpinBox, FocusSpinBase):
    pass


class TableViewW(QTableView):
    def __init__(self, *argc, updown=False, copypaste=False) -> None:
        super().__init__(*argc)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.copypaste = copypaste
        self.updown = updown
        if updown or copypaste:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.showmenu)

    def showmenu(self, pos):
        if not self.currentIndex().isValid():
            return
        menu = QMenu(self)
        up = LAction("上移", menu)
        down = LAction("下移", menu)
        copy = LAction("复制", menu)
        paste = LAction("粘贴", menu)
        if self.updown:
            menu.addAction(up)
            menu.addAction(down)
        if self.copypaste:
            menu.addAction(copy)
            menu.addAction(paste)
        action = menu.exec(self.cursor().pos())
        if action == up:
            self.moverank(-1)
        elif action == down:
            self.moverank(1)
        elif action == copy:
            self.copytable()
        elif action == paste:
            self.pastetable()

    def keyPressEvent(self, e):
        if self.copypaste:
            if e.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if e.key() == Qt.Key.Key_C:
                    self.copytable()
                elif e.key() == Qt.Key.Key_V:
                    self.pastetable()
                else:
                    super().keyPressEvent(e)
            else:
                super().keyPressEvent(e)
        else:
            super().keyPressEvent(e)

    def insertplainrow(self, row=0):
        self.model().insertRow(
            row, [QStandardItem() for _ in range(self.model().columnCount())]
        )

    def dedumpmodel(self, col):

        rows = self.model().rowCount()
        dedump = set()
        needremoves = []
        for row in range(rows):
            if isinstance(col, int):
                k = self.getdata(row, col)
            elif callable(col):
                k = col(row)
            if k == "" or k in dedump:
                needremoves.append(row)
                continue
            dedump.add(k)

        for row in reversed(needremoves):
            self.model().removeRow(row)

    def removeselectedrows(self):
        curr = self.currentIndex()
        if not curr.isValid():
            return []
        row = curr.row()
        col = curr.column()
        skip = []
        for index in self.selectedIndexes():
            if index.row() in skip:
                continue
            skip.append(index.row())
        skip = list(reversed(sorted(skip)))

        for row in skip:
            self.model().removeRow(row)
        row = min(row, self.model().rowCount() - 1)
        self.setCurrentIndex(self.model().index(row, col))
        return skip

    def moverank(self, dy):
        curr = self.currentIndex()
        if not curr.isValid():
            return
        row, col = curr.row(), curr.column()

        model = self.model()
        realws = []
        for _ in range(self.model().columnCount()):
            w = self.indexWidget(self.model().index(row, _))
            if w is None:
                realws.append(None)
                continue
            l: QHBoxLayout = w.layout()
            w = l.takeAt(0).widget()
            realws.append(w)
        target = (row + dy) % model.rowCount()
        model.insertRow(target, model.takeRow(row))
        self.setCurrentIndex(model.index(target, col))
        for _ in range(self.model().columnCount()):
            self.setIndexWidget(self.model().index(target, _), realws[_])
        return row, target

    def indexWidgetX(self, row_or_index, col=None):
        if col is None:
            index: QModelIndex = row_or_index
        else:
            index = self.model().index(row_or_index, col)
        w = self.indexWidget(index)
        if w is None:
            return w
        l: QHBoxLayout = w.layout()
        return l.itemAt(0).widget()

    def inputMethodEvent(self, event: QInputMethodEvent):
        # setindexwidget之后，会导致谜之循环触发，异常；
        # 没有setindexwidget的，会跳转到第一个输入的字母的行，正常，但我不想要。
        pres = event.commitString()
        if not pres:
            super().inputMethodEvent(event)
        else:
            event.accept()

    def setIndexWidget(self, index: QModelIndex, w: QWidget):
        if w is None:
            return
        __w = QWidget()
        __l = QHBoxLayout(__w)
        __l.setContentsMargins(0, 0, 0, 0)
        __l.addWidget(w)
        super().setIndexWidget(index, __w)
        if self.rowHeight(index.row()) < w.height():
            self.setRowHeight(index.row(), w.height())

    def updatelangtext(self):
        m = self.model()
        if isinstance(m, LStandardItemModel):
            m.updatelangtext()

    def getindexdata(self, index):
        return self.model().itemFromIndex(index).text()

    def setindexdata(self, index, data):
        self.model().setItem(index.row(), index.column(), QStandardItem(data))

    def compatiblebool(self, data):
        if isinstance(data, str):
            data = data.lower() == "true"
        elif isinstance(data, bool):
            data = data
        else:
            raise Exception()
        return data

    def compatiblejson(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        elif isinstance(data, (list, dict, tuple)):
            data = data
        else:
            raise Exception()
        return data

    def getdata(self, row_or_index, col=None):
        if col is None:
            index: QModelIndex = row_or_index
        else:
            index = self.model().index(row_or_index, col)
        _1 = self.model().itemFromIndex(index)
        if not _1:
            return ""
        return self.getindexdata(index)

    def copytable(self) -> str:
        _data = []
        lastrow = -1
        for index in self.selectedIndexes():
            if index.row() != lastrow:
                _data.append([])
                lastrow = index.row()
            data = self.getdata(index)
            if not isinstance(data, str):
                data = json.dumps(data, ensure_ascii=False)
            _data[-1].append(data)
        output = io.StringIO()

        csv_writer = csv.writer(output, delimiter="\t")
        for row in _data:
            csv_writer.writerow(row)
        csv_str = output.getvalue()
        output.close()
        winsharedutils.clipboard_set(csv_str)

    def pastetable(self):
        current = self.currentIndex()
        if not current.isValid():
            return
        string = winsharedutils.clipboard_get()
        try:
            csv_file = io.StringIO(string)
            csv_reader = csv.reader(csv_file, delimiter="\t")
            my_list = list(csv_reader)
            csv_file.close()
            if len(my_list) == 1 and len(my_list[0]) == 1:
                self.setindexdata(current, my_list[0][0])
                return
            for j, line in enumerate(my_list):
                self.insertplainrow(current.row() + 1)
            for j, line in enumerate(my_list):
                for i in range(len(line)):
                    data = line[i]
                    c = current.column() + i
                    if c >= self.model().columnCount():
                        continue
                    self.setindexdata(
                        self.model().index(current.row() + 1 + j, c), data
                    )
        except:
            print_exc()
            self.setindexdata(current, string)


def findnearestscreen(rect: QRect):
    # QScreen ,distance
    # -1时，是有交集
    # -2时，是被包围
    # >=0时，是不在任何屏幕内
    mindis = 9999999999
    usescreen = QApplication.primaryScreen()
    for screen in QApplication.screens():
        rect1, rect2 = screen.geometry(), rect
        if rect1.contains(rect2):
            return screen, -2
        if rect1.intersects(rect2):
            r = rect1.intersected(rect2)
            area = r.width() * r.width()
            dis = -area
        else:
            distances = []
            distances.append(abs(rect1.right() - rect2.left()))
            distances.append(abs(rect1.left() - rect2.right()))
            distances.append(abs(rect1.bottom() - rect2.top()))
            distances.append(abs(rect1.top() - rect2.bottom()))
            dis = min(distances)
        if dis < mindis:
            mindis = dis
            usescreen = screen
    if mindis < 0:
        mindis = -1
    return usescreen, mindis


class saveposwindow(LMainWindow):
    def __init__(self, parent, poslist=None, flags=None) -> None:
        if flags:
            super().__init__(parent, flags=flags)
        else:
            super().__init__(parent)

        self.poslist = poslist
        if self.poslist:
            usescreen, mindis = findnearestscreen(QRect(poslist[0], poslist[1], 1, 1))
            poslist[2] = max(0, min(poslist[2], usescreen.size().width()))
            poslist[3] = max(0, min(poslist[3], usescreen.size().height()))
            if mindis != -2:
                poslist[0] = min(
                    max(poslist[0], 0), usescreen.size().width() - poslist[2]
                )
                poslist[1] = min(
                    max(poslist[1], 0), usescreen.size().height() - poslist[3]
                )
            self.setGeometry(*poslist)

    def __checked_savepos(self):
        if not self.poslist:
            return
        if windows.IsZoomed(int(self.winId())) != 0:
            return
        # self.isMaximized()会在event结束后才被设置，不符合预期。
        for i, _ in enumerate(self.geometry().getRect()):
            self.poslist[i] = _

    def resizeEvent(self, a0) -> None:
        self.__checked_savepos()
        super().resizeEvent(a0)

    def moveEvent(self, a0) -> None:
        self.__checked_savepos()
        super().moveEvent(a0)

    def closeEvent(self, event: QCloseEvent):
        self.__checked_savepos()


class closeashidewindow(saveposwindow):
    showsignal = pyqtSignal()
    realshowhide = pyqtSignal(bool)

    def __init__(self, parent, poslist=None) -> None:
        super().__init__(parent, poslist)
        self.showsignal.connect(self.showfunction)
        self.realshowhide.connect(self.realshowhidefunction)

    def realshowhidefunction(self, show):
        if show:
            self.showNormal()
        else:
            self.hide()

    def showfunction(self):
        if self.isMinimized():
            self.showNormal()
        elif self.isVisible():
            self.hide()
        else:
            self.show()

    def closeEvent(self, event: QCloseEvent):
        self.hide()
        event.ignore()
        super().closeEvent(event)


def disablecolor(__: QColor):
    if __.rgb() == 0xFF000000:
        return Qt.GlobalColor.gray
    __ = QColor(
        max(0, (__.red() - 64)),
        max(
            0,
            (__.green() - 64),
        ),
        max(0, (__.blue() - 64)),
    )
    return __


class MySwitch(QAbstractButton):
    clicksignal = pyqtSignal()

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.Type.MouseButtonDblClick:
            return True
        elif a0.type() == QEvent.Type.FontChange:
            self.__loadsize()
        return super().event(a0)

    def __loadsize(self):
        h = QFontMetricsF(self.font()).height()
        sz = QSizeF(1.62 * h * gobject.Consts.btnscale, h * gobject.Consts.btnscale)
        self.setFixedSize(sz.toSize())

    def __init__(self, parent=None, sign=True, enable=True):
        super().__init__(parent)
        self.setCheckable(True)
        super().setChecked(sign)
        super().setEnabled(enable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicksignal.connect(self.click)
        self.__currv = 0
        if sign:
            self.__currv = 20

        self.animation = QVariantAnimation()
        self.animation.setDuration(80)
        self.animation.setStartValue(0)
        self.animation.setEndValue(20)
        self.animation.valueChanged.connect(self.update11)
        self.animation.finished.connect(self.onAnimationFinished)
        self.__loadsize()

    def click(self):
        super().click()
        self.runanime()

    def setChecked(self, check):
        if check == self.isChecked():
            return
        super().setChecked(check)
        self.runanime()

    def update11(self):
        self.__currv = self.animation.currentValue()
        self.update()

    def runanime(self):
        self.animation.setDirection(
            QVariantAnimation.Direction.Forward
            if self.isChecked()
            else QVariantAnimation.Direction.Backward
        )
        self.animation.start()

    def getcurrentcolor(self):

        __ = QColor(
            [gobject.Consts.buttoncolor_disable, gobject.Consts.buttoncolor][
                self.isChecked()
            ]
        )
        if not self.isEnabled():
            __ = disablecolor(__)
        return __

    def paintanime(self, painter: QPainter):

        painter.setBrush(self.getcurrentcolor())
        wb = self.width() * 0.1
        hb = self.height() * 0.125
        painter.drawRoundedRect(
            QRectF(
                wb,
                hb,
                self.width() - 2 * wb,
                self.height() - 2 * hb,
            ),
            self.height() / 2 - hb,
            self.height() / 2 - hb,
        )
        r = self.height() * 0.275
        rb = self.height() / 2 - hb - r
        offset = self.__currv * (self.width() - 2 * wb - 2 * r - 2 * rb) / 20
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(
            QPointF(
                (wb + r + rb) + offset,
                (self.height() / 2),
            ),
            r,
            r,
        )

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        self.paintanime(painter)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        try:
            super().setChecked(not self.isChecked())
            self.clicked.emit(self.isChecked())
            self.runanime()
            # 父窗口deletelater
        except:
            pass

    def onAnimationFinished(self):
        pass


class resizableframeless(saveposwindow):
    cursorSet = pyqtSignal(Qt.CursorShape)
    isDragging = pyqtSignal(bool)

    def __init__(self, parent, flags, poslist) -> None:
        super().__init__(parent, poslist, flags)
        self.setMouseTracking(True)
        # WS_THICKFRAME可以让无边框窗口可resize，但不兼容透明窗口
        self._padding = 5
        self.usesysmove = False
        self.resetflags()

    def setCursor(self, a0):
        super().setCursor(a0)
        self.cursorSet.emit(a0)

    def isdoingsomething(self):
        return (
            self._move_drag
            or self._corner_drag_youxia
            or self._bottom_drag
            or self._top_drag
            or self._corner_drag_zuoxia
            or self._right_drag
            or self._left_drag
            or self._corner_drag_zuoshang
            or self._corner_drag_youshang
        )

    def resetflags(self):
        self._move_drag = False
        self._corner_drag_youxia = False
        self._bottom_drag = False
        self._top_drag = False
        self._corner_drag_zuoxia = False
        self._right_drag = False
        self._left_drag = False
        self._corner_drag_zuoshang = False
        self._corner_drag_youshang = False

    def resizeEvent(self, e):
        pad = self._padding
        w = self.width()
        h = self.height()
        if self._move_drag == False:
            self._right_rect = QRect(w - pad, pad, 2 * pad, h - 2 * pad)
            self._left_rect = QRect(-pad, pad, 2 * pad, h - 2 * pad)
            self._bottom_rect = QRect(pad, h - pad, w - 2 * pad, 2 * pad)
            self._top_rect = QRect(pad, -pad, w - 2 * pad, 2 * pad)
            self._corner_youxia = QRect(w - pad, h - pad, 2 * pad, 2 * pad)
            self._corner_zuoxia = QRect(-pad, h - pad, 2 * pad, 2 * pad)
            self._corner_youshang = QRect(w - pad, -pad, 2 * pad, 2 * pad)
            self._corner_zuoshang = QRect(-pad, -pad, 2 * pad, 2 * pad)
        super().resizeEvent(e)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        gpos = QCursor.pos()
        self.startxp = gpos - self.pos()
        self.starty = gpos.y()
        self.startx = gpos.x()
        self.starth = self.height()
        self.startw = self.width()
        pos = event.pos()
        if self._corner_youxia.contains(pos):
            self._corner_drag_youxia = True
            self.isDragging.emit(True)
        elif self._right_rect.contains(pos):
            self._right_drag = True
            self.isDragging.emit(True)
        elif self._left_rect.contains(pos):
            self._left_drag = True
            self.isDragging.emit(True)
        elif self._top_rect.contains(pos):
            self._top_drag = True
            self.isDragging.emit(True)
        elif self._bottom_rect.contains(pos):
            self._bottom_drag = True
            self.isDragging.emit(True)
        elif self._corner_zuoxia.contains(pos):
            self._corner_drag_zuoxia = True
            self.isDragging.emit(True)
        elif self._corner_youshang.contains(pos):
            self._corner_drag_youshang = True
            self.isDragging.emit(True)
        elif self._corner_zuoshang.contains(pos):
            self._corner_drag_zuoshang = True
            self.isDragging.emit(True)
        else:
            # 用系统拖放有时会有问题。有时会和游戏竞争鼠标，导致窗口位置抖动。
            # 那么尽量不使用系统拖放，以避免触发这个问题，暂时没办法解决。
            # 检查DPI，仅当多屏幕且DPI不一致时才使用系统移动。
            self.usesysmove = winsharedutils.NeedUseSysMove()
            if self.usesysmove:
                winsharedutils.MouseMoveWindow(int(self.winId()))
            self._move_drag = True
            self.move_DragPosition = gpos - self.pos()

    def leaveEvent(self, a0) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(a0)

    def mouseMoveEvent(self, event: QMouseEvent):

        pos = event.pos()
        gpos = QCursor.pos()
        if self._corner_youxia.contains(pos):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif self._corner_zuoshang.contains(pos):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif self._corner_zuoxia.contains(pos):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif self._corner_youshang.contains(pos):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif self._bottom_rect.contains(pos):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif self._top_rect.contains(pos):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif self._right_rect.contains(pos):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif self._left_rect.contains(pos):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        if self._right_drag:
            self.resize(pos.x(), self.height())
        elif self._corner_drag_youshang:
            self.setGeometry(
                self.x(),
                (gpos - self.startxp).y(),
                pos.x(),
                self.starth - (gpos.y() - self.starty),
            )
        elif self._corner_drag_zuoshang:
            self.setgeokeepminsize(
                (gpos - self.startxp).x(),
                (gpos - self.startxp).y(),
                self.startw - (gpos.x() - self.startx),
                self.starth - (gpos.y() - self.starty),
            )

        elif self._left_drag:
            self.setgeokeepminsize(
                (gpos - self.startxp).x(),
                self.y(),
                self.startw - (gpos.x() - self.startx),
                self.height(),
            )
        elif self._bottom_drag:
            self.resize(self.width(), pos.y())
        elif self._top_drag:
            self.setgeokeepminsize(
                self.x(),
                (gpos - self.startxp).y(),
                self.width(),
                self.starth - (gpos.y() - self.starty),
            )
        elif self._corner_drag_zuoxia:
            x, y, w, h = self.calculatexywh(
                (gpos - self.startxp).x(),
                self.y(),
                self.startw - (gpos.x() - self.startx),
                pos.y(),
            )
            self.setGeometry(x, self.y(), w, h)
        elif self._corner_drag_youxia:
            self.resize(pos.x(), pos.y())
        elif self._move_drag:
            self.isDragging.emit(True)
            if not self.usesysmove:
                self.move(gpos - self.move_DragPosition)

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.resetflags()
        self.isDragging.emit(False)

    def setgeokeepminsize(self, *argc):
        self.setGeometry(*self.calculatexywh(*argc))

    def calculatexywh(self, x, y, w, h):
        width = max(w, self.minimumWidth())
        height = max(h, self.minimumHeight())
        x -= width - w
        y -= height - h
        return x, y, width, height


def callbackwrap(d, k, call, _):
    d[k] = _

    if call:
        try:
            call(_)
        except:
            print_exc()


def comboboxcallbackwrap(s: SuperCombo, d, k, call, _):
    _ = s.getIndexData(_)
    d[k] = _

    if call:
        try:
            call(_)
        except:
            print_exc()


def getsimplecombobox(
    lst,
    d=None,
    k=None,
    callback=None,
    fixedsize=False,
    internal=None,
    static=False,
    default=None,
):
    if d is None:
        d = {}
    initvar = d.get(k, default)
    s = SuperCombo(static=static)
    s.addItems(lst, internal)

    if internal:
        if len(internal):
            if (k not in d) or (initvar not in internal):
                initvar = internal[0]

            s.setCurrentIndex(internal.index(initvar))
        s.currentIndexChanged.connect(
            functools.partial(comboboxcallbackwrap, s, d, k, callback)
        )
    else:
        if len(lst):
            if (k not in d) or (initvar >= len(lst)):
                initvar = 0

            s.setCurrentIndex(initvar)
        s.currentIndexChanged.connect(functools.partial(callbackwrap, d, k, callback))
    if fixedsize:
        s.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return s


def D_getsimplecombobox(
    lst, d, k, callback=None, fixedsize=False, internal=None, static=False
):
    return lambda: getsimplecombobox(lst, d, k, callback, fixedsize, internal, static)


def getlineedit(d, key, callback=None, readonly=False):
    s = QLineEdit()
    s.setText(d[key])
    s.setReadOnly(readonly)
    s.textChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def getspinbox(
    mini, maxi, d: dict, key: str, double=False, step=1, callback=None, default=None
):
    initvar = d.get(key, default)
    if double:
        s = FocusDoubleSpin()
        s.setDecimals(math.ceil(-math.log10(step)))
    else:
        s = FocusSpin()
        initvar = int(initvar)
    s.setMinimum(mini)
    s.setMaximum(maxi)
    s.setSingleStep(step)
    s.setValue(initvar)
    s.valueChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def D_getspinbox(mini, maxi, d, key, double=False, step=1, callback=None, default=None):
    return lambda: getspinbox(mini, maxi, d, key, double, step, callback, default)


def getIconButton(
    callback=None, icon="fa.gear", enable=True, qicon=None, callback2=None, fix=True
):

    b = IconButton(icon, enable, qicon, fix=fix)

    if callback:
        b.clicked_1.connect(callback)
    if callback2:
        b.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        b.customContextMenuRequested.connect(callback2)
    return b


def D_getIconButton(
    callback=None, icon="fa.gear", enable=True, qicon=None, callback2=None, fix=True
):
    return lambda: getIconButton(
        callback, icon, enable, qicon, callback2=callback2, fix=fix
    )


def check_grid_append(grids):
    if len(grids) < 2:
        return
    len0 = len(grids[0])
    notx = True
    for line in grids:
        if len(line) != len0:
            continue
        if line[-1] != "":
            notx = False
    if notx:
        for line in grids:
            if len(line) != len0:
                continue
            line.pop(-1)
    return notx


def getcolorbutton(
    d,
    key,
    callback=None,
    name=None,
    parent=None,
    icon="fa.paint-brush",
    constcolor=None,
    enable=True,
    qicon=None,
):
    if qicon is None:
        qicon = qtawesome.icon(icon, color=constcolor if constcolor else d[key])
    b = IconButton(None, enable=enable, parent=parent, qicon=qicon)
    if callback:
        b.clicked.connect(callback)
    if name:
        setattr(parent, name, b)
    return b


def D_getcolorbutton(
    d,
    key,
    callback,
    name=None,
    parent=None,
    icon="fa.paint-brush",
    constcolor=None,
    enable=True,
    qicon=None,
):
    return lambda: getcolorbutton(
        d,
        key,
        callback,
        name,
        parent,
        icon,
        constcolor,
        enable,
        qicon,
    )


def yuitsu_switch(parent, configdict, dictobjectn, key, callback, checked):
    dictobject = getattr(parent, dictobjectn)
    if checked:
        for k in dictobject:
            configdict[k]["use"] = k == key
            dictobject[k].setChecked(k == key)
    if callback:
        callback(key, checked)


def getsimpleswitch(
    d: dict,
    key: str,
    enable=True,
    callback=None,
    name=None,
    pair=None,
    parent=None,
    default=None,
):
    initvar = d.get(key, default)
    b = MySwitch(sign=initvar, enable=enable)
    b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    b.clicked.connect(functools.partial(callbackwrap, d, key, callback))
    if pair:
        if pair not in dir(parent):
            setattr(parent, pair, {})
        getattr(parent, pair)[name] = b
    elif name:
        setattr(parent, name, b)
    return b


def __getsmalllabel(text):
    __ = LLabel(text)
    __.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
    __.setOpenExternalLinks(True)
    return __


def getsmalllabel(text=""):
    return lambda: __getsmalllabel(text)


def D_getsimpleswitch(
    d, key, enable=True, callback=None, name=None, pair=None, parent=None, default=None
):
    return lambda: getsimpleswitch(
        d, key, enable, callback, name, pair, parent, default
    )


def getColor(color, parent, alpha=False):

    color_dialog = QColorDialog(color, parent)
    if alpha:
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
    if alpha:
        layout = color_dialog.layout()
        clearlayout(layout.itemAt(0).layout().takeAt(0))
        layout = (
            layout.itemAt(0).layout().itemAt(0).layout().itemAt(2).widget().layout()
        )
        layout.takeAt(1).widget().hide()
        layout.takeAt(1).widget().hide()
        layout.takeAt(1).widget().hide()
        layout.takeAt(1).widget().hide()
        layout.takeAt(1).widget().hide()
        layout.takeAt(1).widget().hide()

        layout.takeAt(layout.count() - 1).widget().hide()
        layout.takeAt(layout.count() - 1).widget().hide()
        if not alpha:
            layout.takeAt(layout.count() - 1).widget().hide()
            layout.takeAt(layout.count() - 1).widget().hide()
    if color_dialog.exec_() != QColorDialog.DialogCode.Accepted:
        return QColor()
    return color_dialog.selectedColor()


def selectcolor(
    parent,
    configdict,
    configkey,
    button,
    item=None,
    name=None,
    callback=None,
    alpha=False,
):

    color = getColor(QColor(configdict[configkey]), parent, alpha)
    if not color.isValid():
        return
    if button is None:
        button = getattr(item, name)
    button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
    configdict[configkey] = (
        color.name(QColor.NameFormat.HexArgb) if alpha else color.name()
    )
    if callback:
        try:
            callback()
        except:
            print_exc()


def getboxlayout(
    widgets, lc=QHBoxLayout, margin0=False, makewidget=False, delay=False, both=False
):
    w = QWidget() if makewidget else None
    cp_layout = lc(w)

    def __do(cp_layout: QBoxLayout, widgets):
        for w in widgets:
            if callable(w):
                w = w()
            elif isinstance(w, str):
                w = makelabel(w)
            if isinstance(w, QWidget):
                cp_layout.addWidget(w)
            elif isinstance(w, QLayout):
                cp_layout.addLayout(w)

    _do = functools.partial(__do, cp_layout, widgets)
    if margin0:
        cp_layout.setContentsMargins(0, 0, 0, 0)
    if not delay:
        _do()
    if delay:
        return w, _do
    if both:
        return w, cp_layout
    if makewidget:
        return w
    return cp_layout


class abstractwebview(QWidget):
    on_load = pyqtSignal(str)
    on_ZoomFactorChanged = pyqtSignal(float)
    html_limit = 2 * 1024 * 1024

    # 必须的接口
    def getHtml(self, elementid):
        return

    def setHtml(self, html):
        pass

    def navigate(self, url):
        pass

    def wrapgetlabel(self, getlabel):
        if not getlabel:
            return

        def __(f):
            _ = f()
            return winsharedutils.str_alloc(_)

        return functools.partial(__, getlabel)

    def add_menu(self, index=0, getlabel=None, callback=None):
        return index + 1

    def add_menu_noselect(
        self,
        index=0,
        getlabel=None,
        callback=None,
        checkable=False,
        getchecked=None,
        getuse=None,
    ):
        return index + 1

    #
    def parsehtml(self, html):
        pass

    def set_zoom(self, zoom):
        pass

    def get_zoom(self):
        return 1

    def bind(self, fname, func):
        pass

    def eval(self, js, retsaver=None):
        pass

    def _parsehtml_codec(self, html):

        html = """<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8" /></head>{}</html>""".format(
            html
        )
        return html

    def _parsehtml_font(self, html):
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
        html = """<body style=" font-family:'{}'">{}</body>""".format(font, html)
        return html

    def _parsehtml_dark(self, html):
        if nowisdark():
            html = (
                """
    <style>
        body 
        { 
            background-color: rgb(44,44,44);
            color: white; 
        }
    </style>"""
                + html
            )
        return html

    def _parsehtml_dark_auto(self, html):
        return (
            """
<style>
@media (prefers-color-scheme: dark) 
{
    :root {
        color-scheme: dark;
    }
    body 
    { 
        background-color: rgb(44,44,44);
        color: white; 
    }
}
</style>
"""
            + html
        )


SingleExtensionSetting = None


class MiddleClickTab(QTabWidget):
    midclicked = pyqtSignal(int)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if a0.button() == Qt.MouseButton.MiddleButton:
            i = self.tabBar().tabAt(a0.pos())
            if i != -1:
                self.midclicked.emit(i)
        return super().mouseReleaseEvent(a0)


class SingleExtensionSetting_(saveposwindow):
    def __init__(self, parent):
        super().__init__(parent, globalconfig["extensionsetting"])
        self.tabw = MiddleClickTab(self)
        self.tabw.setTabsClosable(True)
        self.tabw.tabCloseRequested.connect(self.close_tab)
        self.tabw.currentChanged.connect(self.changetab)
        self.tabw.midclicked.connect(self.close_tab)
        self.setCentralWidget(self.tabw)
        self.destroyed.connect(SingleExtensionSetting_.ondestroyed)

    @staticmethod
    def ondestroyed():
        global SingleExtensionSetting
        SingleExtensionSetting = None

    def closeEvent(self, event):
        self.deleteLater()
        return super().closeEvent(event)

    def gamename(self, w, url):
        return "{}  [{}]".format(w.name, url) if w.name else url

    def changetab(self, i):
        self.setWindowIcon(self.tabw.tabIcon(i))
        self.settitle(i)

    def settitle(self, i):
        self.setWindowTitle(
            "{}  [{}]".format(self.tabw.tabText(i), self.tabw.widget(i).url)
        )

    def close_tab(self, i):
        w = self.tabw.widget(i)
        self.tabw.removeTab(i)
        w.deleteLater()
        self.tabw.tabBar().setVisible(self.tabw.count() > 1)
        if self.tabw.count() == 0:
            self.close()

    def titlechange(self, w: QWidget, t: str):
        i = self.tabw.indexOf(w)
        self.tabw.setTabText(i, t)
        if i == self.tabw.currentIndex():
            self.settitle(i)

    def urlchange(self, w: QWidget, url: str):
        i = self.tabw.indexOf(w)
        if i == self.tabw.currentIndex():
            self.settitle(i)

    def iconchange(self, w: QWidget, icon: QIcon):
        i = self.tabw.indexOf(w)
        self.tabw.setTabIcon(i, icon)
        if i == self.tabw.currentIndex():
            self.setWindowIcon(icon)

    def createpage(self, name, settingurl, icon):
        w = WebviewWidget(self, loadext=True)
        w.name = name
        w.titlechanged.connect(functools.partial(self.titlechange, w))
        w.IconChanged.connect(functools.partial(self.iconchange, w))
        w.on_load.connect(functools.partial(self.urlchange, w))
        w.navigate(settingurl)
        idx = self.tabw.currentIndex() + 1
        self.tabw.insertTab(idx, w, self.gamename(w, settingurl))
        self.tabw.tabBar().setVisible(self.tabw.count() > 1)

        self.tabw.setTabIcon(idx, QIcon(icon) if icon else qtawesome.icon("fa.gear"))
        self.tabw.setCurrentIndex(idx)
        self.changetab(self.tabw.currentIndex())
        self.show()


def ExtensionSetting(name, settingurl, icon):
    global SingleExtensionSetting
    if not SingleExtensionSetting:
        SingleExtensionSetting = SingleExtensionSetting_(
            gobject.baseobject.commonstylebase
        )
    SingleExtensionSetting.createpage(name, settingurl, icon)


@Singleton
class Exteditor(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("浏览器插件")
        self.resize(QSize(600, 400))

        model = LStandardItemModel()
        model.setHorizontalHeaderLabels(["移除", "", "名称", "禁用", "设置"])

        table = TableViewW()

        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.__menu)
        vbox = QVBoxLayout(self)
        vbox.addWidget(table)
        btn = LPushButton("添加")
        btn.clicked.connect(functools.partial(self.tryMessage, self.Addext))
        vbox.addWidget(btn)
        self.show()
        self.model = model
        self.table = table
        self.tryMessage(self.listexts)

    def Addext(self, *_):
        chromes = os.path.join(
            os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Default\Extensions"
        )
        edges = os.path.join(
            os.environ["LOCALAPPDATA"], r"Microsoft\Edge\User Data\Default\Extensions"
        )
        if os.path.isdir(edges):
            edgeslen = len(os.listdir(edges))
        else:
            edgeslen = 0
        if os.path.isdir(chromes):
            chromelen = len(os.listdir(chromes))
        else:
            chromelen = 0
        if chromelen > edgeslen:
            path = chromes
        elif edgeslen > 0:
            path = edges
        else:
            path = ""
        res = QFileDialog.getExistingDirectory(
            self, None, path, options=QFileDialog.Option.DontResolveSymlinks
        )
        if not res:
            return

        WebviewWidget.Extensions_Add(res)
        self.listexts()

    def __menu(self, _):
        curr = self.table.currentIndex()
        if not curr.isValid():
            return
        if curr.column() != 2:
            return
        menu = QMenu(self.table)
        copyid = LAction("复制_ID", menu)

        menu.addAction(copyid)
        action = menu.exec(self.table.cursor().pos())

        if action == copyid:
            winsharedutils.clipboard_set(
                self.table.model().data(curr, Qt.ItemDataRole.UserRole + 10)
            )

    def listexts(self):
        self.model.removeRows(0, self.model.rowCount())
        for _i, (_id, name, able) in enumerate(WebviewWidget.Extensions_List()):

            _i = self.model.rowCount()
            item = QStandardItem(name)
            item.setData(_id, Qt.ItemDataRole.UserRole + 10)
            self.model.appendRow(
                [
                    QStandardItem(""),
                    QStandardItem(""),
                    item,
                    QStandardItem(""),
                    QStandardItem(""),
                ]
            )
            d = {"1": able}
            self.table.setIndexWidget(
                self.model.index(_i, 3),
                getsimpleswitch(
                    d,
                    "1",
                    callback=functools.partial(
                        self.tryMessage, self.enablex, _id, not able
                    ),
                ),
            )
            self.table.setIndexWidget(
                self.model.index(_i, 0),
                getIconButton(
                    callback=functools.partial(self.tryMessage, self.removex, _id),
                    icon="fa.times",
                ),
            )
            t = QTimer(self)
            t.setInterval(1000)
            t.timeout.connect(
                functools.partial(
                    self.checkinfo,
                    _id,
                    self.model.index(_i, 1),
                    self.model.index(_i, 3),
                    self.model.index(_i, 4),
                    name,
                    t,
                )
            )
            t.start(0)

    def checkinfo(
        self, _id, i1: QModelIndex, i3: QModelIndex, i4: QModelIndex, name, t: QTimer
    ):
        if not (i1.isValid() and i4.isValid()):
            return t.stop()
        info = WebviewWidget.Extensions_Manifest_Info(_id)
        if info is None:
            return
        setting = info.get("url")
        if setting:
            self.table.setIndexWidget(
                i4,
                getIconButton(
                    callback=functools.partial(
                        ExtensionSetting, name, setting, info.get("icon")
                    ),
                    enable=self.table.indexWidgetX(i3).isChecked(),
                ),
            )
        icon = info.get("icon")
        if icon:
            self.table.setIndexWidget(
                i1,
                getIconButton(
                    qicon=QIcon(icon),
                    callback=functools.partial(os.startfile, info["path"]),
                    enable=self.table.indexWidgetX(i3).isChecked(),
                ),
            )
        t.stop()

    def enablex(self, _id, able, _):
        WebviewWidget.Extensions_Enable(_id, able)
        self.listexts()

    def removex(self, _id):
        WebviewWidget.Extensions_Remove(_id)
        self.listexts()

    def tryMessage(self, func, *args):
        try:
            func(*args)
        except Exception as e:
            QMessageBox.critical(self, _TR("错误"), str(e))


class WebviewWidget(abstractwebview):
    html_limit = 1572834
    # https://github.com/MicrosoftEdge/WebView2Feedback/issues/1355#issuecomment-1384161283
    dropfilecallback = pyqtSignal(str)
    loadextensionwindow = pyqtSignal(str)
    titlechanged = pyqtSignal(str)
    IconChanged = pyqtSignal(QIcon)

    def getHtml(self, elementid):
        # 不可以在bind函数里调用，否则会阻塞
        _ = []
        if elementid:
            js = "document.getElementById('{}').innerHTML".format(elementid)
        else:
            js = "document.documentElement.outerHTML"
        self.eval(js, _.append)
        if not _:
            return ""
        return json.loads(_[0])

    def bind(self, fname, func):
        self.binds[fname] = func
        winsharedutils.webview2_bind(self.webview, fname)

    def eval(self, js, callback=None):
        cb = winsharedutils.webview2_evaljs_CALLBACK(callback) if callback else None
        winsharedutils.webview2_evaljs(self.webview, js, cb)

    def add_menu(self, index=0, getlabel=None, callback=None):
        __ = winsharedutils.webview2_add_menu_CALLBACK(callback) if callback else None
        self.callbacks.append(__)
        getlabel = self.wrapgetlabel(getlabel)
        __3 = (
            winsharedutils.webview2_contextmenu_gettext(getlabel) if getlabel else None
        )
        self.callbacks.append(__3)
        winsharedutils.webview2_add_menu(self.webview, index, __3, __)
        return index + 1

    def add_menu_noselect(
        self,
        index=0,
        getlabel=None,
        callback=None,
        checkable=False,
        getchecked=None,
        getuse=None,
    ):
        __ = (
            winsharedutils.webview2_add_menu_noselect_CALLBACK(callback)
            if callback
            else None
        )
        self.callbacks.append(__)
        __1 = (
            winsharedutils.webview2_add_menu_noselect_getchecked(getchecked)
            if getchecked
            else None
        )
        self.callbacks.append(__1)
        __2 = (
            winsharedutils.webview2_add_menu_noselect_getuse(getuse) if getuse else None
        )
        self.callbacks.append(__2)
        getlabel = self.wrapgetlabel(getlabel)
        __3 = (
            winsharedutils.webview2_contextmenu_gettext(getlabel) if getlabel else None
        )
        self.callbacks.append(__3)
        winsharedutils.webview2_add_menu_noselect(
            self.webview, index, __3, __, checkable, __1, __2
        )
        return index + 1

    @staticmethod
    def showError(e: Exception):
        QMessageBox.critical(
            gobject.baseobject.settin_ui,
            _TR("错误"),
            str(e)
            + "\n\n"
            + _TR(
                "找不到Webview2Runtime！\n请安装Webview2Runtime，或者下载固定版本后解压到软件目录中。"
            ),
        )
        if int(platform.version().split(".")[0]) <= 6:
            os.startfile(
                "https://archive.org/download/microsoft-edge-web-view-2-runtime-installer-v109.0.1518.78"
            )
        else:
            os.startfile("https://developer.microsoft.com/microsoft-edge/webview2")

    @staticmethod
    def __getuserdir():
        _ = []
        __ = winsharedutils.webview2_get_userdir_callback(_.append)
        winsharedutils.webview2_get_userdir(__)
        if _:
            return _[0]

    @staticmethod
    def __ExtensionDir(extid: str):
        path = WebviewWidget.__getuserdir()
        if not path:
            return
        path = os.path.join(path, "EBWebView/Default/Secure Preferences")
        try:
            with open(path, "r", encoding="utf8") as ff:
                js = json.load(ff)
            path = js["extensions"]["settings"][extid]["path"]
            return path
        except:
            pass

    @staticmethod
    def Extensions_Manifest_Info(extid: str):
        path = WebviewWidget.__ExtensionDir(extid)
        if not path:
            return
        path1 = os.path.join(path, "manifest.json")
        try:
            with open(path1, "r", encoding="utf8") as ff:
                manifest = json.load(ff)
            data = {}
            data["path"] = path
            try:
                icons = manifest["icons"]
                icon = icons[str(max((int(_) for _ in icons)))]
                data["icon"] = os.path.join(path, icon)
            except:
                pass
            try:
                path = manifest["options_ui"]["page"]
                url = "chrome-extension://{}/{}".format(extid, path)
                data["url"] = url
            except:
                pass
            return data
        except:
            return

    @staticmethod
    def Extensions_List():
        collect = []

        def __(_, _1, _2):
            collect.append((_, _1, _2))

        _ = winsharedutils.webview2_list_ext_CALLBACK_T(__)
        windows.CHECK_FAILURE(winsharedutils.webview2_ext_list(_))
        return collect

    @staticmethod
    def Extensions_Enable(_id, enable):
        windows.CHECK_FAILURE(winsharedutils.webview2_ext_enable(_id, enable))

    @staticmethod
    def Extensions_Remove(_id):
        windows.CHECK_FAILURE(winsharedutils.webview2_ext_rm(_id))

    @staticmethod
    def Extensions_Add(path):
        windows.CHECK_FAILURE(winsharedutils.webview2_ext_add(path))

    @staticmethod
    def findFixedRuntime():
        hasset = os.environ.get("WEBVIEW2_BROWSER_EXECUTABLE_FOLDER")
        if hasset:
            # 已设置的环境变量会影响检测。直接返回就行了
            return hasset
        maxversion = (0, 0, 0, 0)
        maxvf = None

        for f in os.listdir("."):
            f = os.path.abspath(f)
            version = winsharedutils.detect_webview2_version(f)
            # 这个API似乎可以检测runtime是否是有效的，比自己查询版本更好
            if not version:
                continue
            if (version[0] > 109) and (int(platform.version().split(".")[0]) <= 6):
                continue
            if version > maxversion:
                maxversion = version
                maxvf = f
                print(maxversion, f)
        return maxvf

    @staticmethod
    def onDestroy(ptr):
        winsharedutils.webview2_destroy(ptr)

    def event(self, a0: QEvent):
        if a0.type() == QEvent.Type.User + 1:
            winsharedutils.webview2_put_PreferredColorScheme(
                self.webview, globalconfig["darklight2"]
            )
        return super().event(a0)

    def __init__(self, parent=None, transp=False, loadext=False) -> None:
        super().__init__(parent)
        self.webview = None
        self.binds = {}
        self.callbacks = []
        self.url = ""
        FixedRuntime = WebviewWidget.findFixedRuntime()
        if FixedRuntime:
            os.environ["WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"] = FixedRuntime
            # 在共享路径上无法运行
            os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = "--no-sandbox"
        self.webview = winsharedutils.WebView2PTR()
        windows.CHECK_FAILURE(
            winsharedutils.webview2_create(
                windows.pointer(self.webview), int(self.winId()), transp, loadext
            )
        )
        winsharedutils.webview2_put_PreferredColorScheme(
            self.webview, globalconfig["darklight2"]
        )
        self.loadextensionwindow.connect(self.__loadextensionwindow)
        self.destroyed.connect(functools.partial(WebviewWidget.onDestroy, self.webview))
        self.monitorptrs = []
        self.monitorptrs.append(
            winsharedutils.webview2_zoomchange_callback_t(self.zoomchange)
        )
        self.monitorptrs.append(
            winsharedutils.webview2_navigating_callback_t(self.__on_load)
        )
        self.monitorptrs.append(
            winsharedutils.webview2_webmessage_callback_t(self.webmessage_callback_f)
        )
        self.monitorptrs.append(
            winsharedutils.webview2_FilesDropped_callback_t(self.dropfilecallback.emit)
        )
        self.monitorptrs.append(
            winsharedutils.webview2_titlechange_callback_t(self.titlechanged.emit)
        )
        self.monitorptrs.append(
            winsharedutils.webview2_IconChanged_callback_t(self.IconChangedF)
        )
        winsharedutils.webview2_set_observe_ptrs(self.webview, *self.monitorptrs)

        self.add_menu()
        self.add_menu_noselect()
        self.cachezoom = 1

    def IconChangedF(self, ptr, size):
        pixmap = QPixmap()
        pixmap.loadFromData(cast(ptr, POINTER(c_char))[:size])
        if not pixmap.isNull():
            self.IconChanged.emit(QIcon(pixmap))

    def __on_load(self, url: str, loadinnew: bool):
        if loadinnew:
            threading.Thread(target=self.loadextensionwindow.emit, args=(url,)).start()
        else:
            self.on_load.emit(url)
            self.url = url

    def __loadextensionwindow(self, url: str):
        ExtensionSetting(None, url, None)

    def webmessage_callback_f(self, js: str):
        # 其实不应该在这里处理回调，否则例如如果在这里用getHTML，会卡死。
        # 应该用PostMessageW(m_message_window, WM_APP, 0, (LPARAM) func)传出去再处理才对。
        # 但是暂时没问题，就先这样吧。
        try:
            js = json.loads(js)
            method = js.get("method")
            args = js.get("args")
            self.binds[method](*args)
        except:
            print_exc()

    def zoomchange(self, zoom):
        self.cachezoom = zoom
        self.on_ZoomFactorChanged.emit(zoom)
        self.set_zoom(zoom)  # 置为默认值，档navi/sethtml时才能保持

    def set_zoom(self, zoom):
        winsharedutils.webview2_put_ZoomFactor(self.webview, zoom)
        self.cachezoom = winsharedutils.webview2_get_ZoomFactor(self.webview)

    def get_zoom(self):
        # winsharedutils.get_ZoomFactor(self.get_controller()) 性能略差
        return self.cachezoom

    def navigate(self, url):
        winsharedutils.webview2_navigate(self.webview, url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        r = self.devicePixelRatioF()
        winsharedutils.webview2_resize(
            self.webview, int(r * a0.size().width()), int(r * a0.size().height())
        )

    def setHtml(self, html):
        winsharedutils.webview2_sethtml(self.webview, html)

    def parsehtml(self, html):
        return self._parsehtml_codec(self._parsehtml_dark_auto(html))


class WebviewWidget_for_auto(WebviewWidget):
    pluginsedit = pyqtSignal()
    reloadx = pyqtSignal()

    def appendext(self):
        globalconfig["webviewLoadExt_cishu"] = not globalconfig["webviewLoadExt_cishu"]
        auto_select_webview.switchtype()

    def __init__(self, parent=None) -> None:
        super().__init__(parent, loadext=globalconfig["webviewLoadExt_cishu"])
        self.pluginsedit.connect(functools.partial(Exteditor, self))
        self.reloadx.connect(self.appendext)

        nexti = self.add_menu_noselect()
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("附加浏览器插件"),
            threader(self.reloadx.emit),
            True,
            getchecked=lambda: globalconfig["webviewLoadExt_cishu"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("浏览器插件"),
            threader(self.pluginsedit.emit),
            False,
            getuse=lambda: globalconfig["webviewLoadExt_cishu"],
        )
        nexti = self.add_menu_noselect(nexti)
        self.cachezoom = 1


class mshtmlWidget(abstractwebview):
    def getHtml(self, elementid):
        _ = []
        cb = winsharedutils.html_get_select_text_cb(_.append)
        winsharedutils.html_get_html(self.browser, cb, elementid)
        if not _:
            return ""
        return _[0]

    def eval(self, js):
        winsharedutils.html_eval(self.browser, js)

    def __bindhelper(self, func, ppwc, argc):
        argv = []
        for i in range(argc):
            argv.append(ppwc[argc - 1 - i])
        func(*argv)

    def bind(self, fname, func):
        __f = winsharedutils.html_bind_function_FT(
            functools.partial(self.__bindhelper, func)
        )
        self.bindfs.append(__f)
        winsharedutils.html_bind_function(self.browser, fname, __f)

    @staticmethod
    def onDestroy(ptr):
        winsharedutils.html_release(ptr)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.callbacks = []
        self.bindfs = []
        iswine = checkisusingwine()
        if iswine or (winsharedutils.html_version() < 10001):  # ie10之前，sethtml会乱码
            self.html_limit = 0
        self.browser = winsharedutils.html_new(int(self.winId()))
        self.destroyed.connect(functools.partial(mshtmlWidget.onDestroy, self.browser))
        self.curr_url = None
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.__getcurrent)
        t.timeout.emit()
        t.start()
        self.add_menu(0, lambda: _TR("复制"), winsharedutils.clipboard_set)
        self.add_menu(0)

    def __getcurrent(self):
        def __(_u):
            if self.curr_url != _u:
                self.curr_url = _u
                self.on_load.emit(_u)

        cb = winsharedutils.html_get_select_text_cb(__)
        winsharedutils.html_get_current_url(self.browser, cb)

        if winsharedutils.html_check_ctrlc(self.browser):
            cb = winsharedutils.html_get_select_text_cb(winsharedutils.clipboard_set)
            winsharedutils.html_get_select_text(self.browser, cb)

    def navigate(self, url):
        winsharedutils.html_navigate(self.browser, url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = a0.size() * self.devicePixelRatioF()
        winsharedutils.html_resize(self.browser, 0, 0, size.width(), size.height())

    def setHtml(self, html):
        winsharedutils.html_set_html(self.browser, html)

    def parsehtml(self, html):
        return self._parsehtml_codec(self._parsehtml_font(self._parsehtml_dark(html)))

    def add_menu(self, index=0, getlabel=None, callback=None):
        cb = winsharedutils.html_add_menu_cb(callback) if callback else None
        self.callbacks.append(cb)
        getlabel = self.wrapgetlabel(getlabel)
        cb2 = winsharedutils.html_add_menu_gettext(getlabel) if getlabel else None
        self.callbacks.append(cb2)
        winsharedutils.html_add_menu(self.browser, index, cb2, cb)
        return index + 1

    def add_menu_noselect(
        self,
        index=0,
        getlabel=None,
        callback=None,
        checkable=False,
        getchecked=None,
        getuse=None,
    ):
        cb = winsharedutils.html_add_menu_cb2(callback) if callback else None
        self.callbacks.append(cb)
        getlabel = self.wrapgetlabel(getlabel)
        cb2 = winsharedutils.html_add_menu_gettext(getlabel) if getlabel else None
        self.callbacks.append(cb2)
        winsharedutils.html_add_menu_noselect(self.browser, index, cb2, cb)
        return index + 1


class CustomKeySequenceEdit(QKeySequenceEdit):
    changeedvent = pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        if len(value.toString()):
            self.clearFocus()
        self.changeedvent.emit(value.toString().replace("Meta", "Win"))
        self.setKeySequence(QKeySequence(value))


def getsimplekeyseq(dic, key, callback=None):
    key1 = CustomKeySequenceEdit(QKeySequence(dic[key]))

    def __(_d, _k, cb, s):
        _d[_k] = s
        if cb:
            cb()

    key1.changeedvent.connect(functools.partial(__, dic, key, callback))
    return key1


def D_getsimplekeyseq(dic, key, callback=None):
    return lambda: getsimplekeyseq(dic, key, callback)


switchtypes = []


class auto_select_webview(QWidget):
    on_load = pyqtSignal(str)
    on_ZoomFactorChanged = pyqtSignal(float)

    def getHtml(self, elementid):
        return self.internal.getHtml(elementid)

    def eval(self, js):
        self.internal.eval(js)

    def bind(self, funcname, function):
        self.bindinfo.append((funcname, function))
        self.internal.bind(funcname, function)

    def add_menu(self, index=0, getlabel=None, callback=None):
        self.addmenuinfo.append((index, getlabel, callback))
        return self.internal.add_menu(index, getlabel, callback)

    def add_menu_noselect(
        self,
        index=0,
        getlabel=None,
        callback=None,
        checkable=False,
        getchecked=None,
        getuse=None,
    ):
        self.addmenuinfo_noselect.append(
            (index, getlabel, callback, checkable, getchecked, getuse)
        )
        return self.internal.add_menu_noselect(
            index, getlabel, callback, checkable, getchecked, getuse
        )

    def clear(self):
        self.internal.setHtml(self.internal.parsehtml(""))  # 夜间

    def navigate(self, url):
        self.internal.navigate(url)

    def setHtml(self, html):
        html = self.internal.parsehtml(html)
        if len(html) < self.internal.html_limit:
            self.internal.setHtml(html)
        else:
            md5 = hashlib.md5(html.encode("utf8", errors="ignore")).hexdigest()
            lastcachehtml = gobject.gettempdir(md5 + ".html")
            with open(lastcachehtml, "w", encoding="utf8") as ff:
                ff.write(html)
            self.internal.navigate(lastcachehtml)

    def set_zoom(self, zoom):
        self.internal.set_zoom(zoom)

    def sizeHint(self):
        return QSize(256, 192)

    def __init__(self, parent, dyna=False, loadex=True) -> None:
        super().__init__(parent)
        self.loadex = loadex
        self.addmenuinfo = []
        self.addmenuinfo_noselect = []
        self.bindinfo = []
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.internal = None
        self.saveurl = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._maybecreate_internal()
        if dyna:
            switchtypes.append(self)
        self.setHtml("")

    @staticmethod
    def switchtype():
        for i, _ in enumerate(switchtypes):
            _._maybecreate_internal(shoudong=True if i == 0 else False)

    def _on_load(self, url: str):
        self.saveurl = url
        self.on_load.emit(url)

    def _createinternal(self, shoudong=False):
        if self.internal:
            self.layout().removeWidget(self.internal)
            self.internal.deleteLater()
        self.internal = self._createwebview(shoudong=shoudong)
        self.internal.on_load.connect(self._on_load)
        self.internal.on_ZoomFactorChanged.connect(self.on_ZoomFactorChanged)
        self.layout().addWidget(self.internal)
        for _ in self.addmenuinfo:
            self.internal.add_menu(*_)
        for _ in self.addmenuinfo_noselect:
            self.internal.add_menu_noselect(*_)
        for _ in self.bindinfo:
            self.internal.bind(*_)

    def _maybecreate_internal(self, shoudong=False):
        if not self.internal:
            return self._createinternal(shoudong=shoudong)
        if (
            self.saveurl
            and (self.saveurl != "about:blank")
            and (not self.saveurl.startswith("file:///"))
        ):
            self._createinternal(shoudong=shoudong)
            self.internal.navigate(self.saveurl)
        else:
            html = self.internal.getHtml(None)
            self._createinternal(shoudong=shoudong)
            self.internal.setHtml(html)

    def _createwebview(self, shoudong=False):
        try:
            browser = (WebviewWidget, WebviewWidget_for_auto)[self.loadex]()
        except Exception as e:
            print_exc()
            if shoudong:
                WebviewWidget.showError(e)
            browser = mshtmlWidget()
        return browser


class threebuttons(QWidget):
    btn1clicked = pyqtSignal()
    btn2clicked = pyqtSignal()
    btn3clicked = pyqtSignal()
    btn4clicked = pyqtSignal()
    btn5clicked = pyqtSignal()

    def __init__(self, texts=None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if len(texts) >= 1:
            button = LPushButton(self)
            button.setText(texts[0])
            button.clicked.connect(self.btn1clicked)
            layout.addWidget(button)
        if len(texts) >= 2:
            button2 = LPushButton(self)
            button2.setText(texts[1])
            button2.clicked.connect(self.btn2clicked)

            layout.addWidget(button2)
        if len(texts) >= 3:
            button3 = LPushButton(self)
            button3.setText(texts[2])
            button3.clicked.connect(self.btn3clicked)
            layout.addWidget(button3)
        if len(texts) >= 4:
            button4 = LPushButton(self)
            button4.setText(texts[3])
            button4.clicked.connect(self.btn4clicked)
            layout.addWidget(button4)
        if len(texts) >= 5:
            button5 = LPushButton(self)
            button5.setText(texts[4])
            button5.clicked.connect(self.btn5clicked)
            layout.addWidget(button5)


def tabadd_lazy(tab, title, getrealwidgetfunction):
    q = QWidget()
    v = QVBoxLayout(q)
    v.setContentsMargins(0, 0, 0, 0)
    q.lazyfunction = functools.partial(getrealwidgetfunction, v)
    tab.addTab(q, title)


def makelabel(s: str):
    islink = ("<a" in s) and ("</a>" in s)
    wid = LLabel(s)
    if islink:
        wid.setOpenExternalLinks(True)
    return wid


def makeforms(lay: LFormLayout, lis):
    for line in lis:
        if len(line) == 0:
            lay.addRow(QLabel())
            continue
        elif len(line) == 1:
            name, wid = None, line[0]
        else:
            name, wid = line
        if isinstance(wid, (tuple, list)):
            hb = QHBoxLayout()
            hb.setContentsMargins(0, 0, 0, 0)

            needstretch = False
            for w in wid:
                if callable(w):
                    w: QWidget = w()
                if w.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed:
                    needstretch = True
                hb.addWidget(w)
            if needstretch:
                hb.insertStretch(0)
                hb.addStretch()
            wid = hb
        elif isinstance(wid, dict):
            # group
            wid = makegroupingrid(wid)
        else:
            if callable(wid):
                try:
                    wid = wid()
                except:
                    print_exc()
                    wid = QWidget()
            elif isinstance(wid, str):
                wid = makelabel(wid)
            if isinstance(wid, QWidget) and (
                wid.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
            ):
                hb = QHBoxLayout()
                hb.setContentsMargins(0, 0, 0, 0)
                hb.addStretch()
                hb.addWidget(wid)
                hb.addStretch()
                wid = hb
        if name is not None:
            lay.addRow(name, wid)
        else:
            lay.addRow(wid)


class NQGroupBox(QGroupBox):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.setObjectName("notitle")


def makegroupingrid(args):
    lis = args.get("grid")
    title = args.get("title", None)
    _type = args.get("type", "form")
    parent = args.get("parent", None)
    groupname = args.get("name", None)
    enable = args.get("enable", True)
    internallayoutname = args.get("internallayoutname", None)

    if title:
        group = LGroupBox()
        group.setTitle(title)
    else:
        group = NQGroupBox()
    if not enable:
        group.setEnabled(False)
    if groupname and parent:
        setattr(parent, groupname, group)

    if _type == "grid":
        grid = QGridLayout(group)
        automakegrid(grid, lis)
        if internallayoutname:
            setattr(parent, internallayoutname, grid)
    elif _type == "form":
        lay = LFormLayout(group)
        makeforms(lay, lis)
        if internallayoutname:
            setattr(parent, internallayoutname, lay)
    return group


def automakegrid(grid: QGridLayout, lis, savelist=None):
    save = isinstance(savelist, list)
    maxl = 1
    linecolss = []
    for nowr, line in enumerate(lis):
        nowc = 0
        linecolssx = []
        for item in line:
            if type(item) == str:
                cols = 1
            elif isinstance(item, dict):
                cols = 0
            elif type(item) != tuple:
                wid, cols = item, 1
            elif len(item) == 2:

                wid, cols = item
            nowc += cols
            linecolssx.append(cols)
        maxl = max(maxl, nowc)
        linecolss.append(linecolssx)

    for nowr, line in enumerate(lis):
        nowc = 0
        if save:
            ll = []
        for item in line:
            if type(item) == str:
                cols = 1
                wid = makelabel(item)
            elif isinstance(item, dict):
                # group
                wid = makegroupingrid(item)
                cols = 0
            elif type(item) != tuple:
                wid, cols = item, 1
            elif len(item) == 2:

                wid, cols = item
                if type(wid) == str:
                    wid = makelabel(wid)
            if cols > 0:
                cols = cols
            elif cols == 0:
                cols = maxl - sum(linecolss[nowr])
            else:
                cols = -maxl // cols
            do = None
            if callable(wid):
                try:
                    wid = wid()
                except:
                    print_exc()
                    wid = QWidget()
                if isinstance(wid, tuple):
                    wid, do = wid
            grid.addWidget(wid, nowr, nowc, 1, cols)
            if do:
                do()
            if save:
                ll.append(wid)
            nowc += cols
        if save:
            savelist.append(ll)
        grid.setRowMinimumHeight(nowr, 25)


def makegrid(grid=None, savelist=None, savelay=None, delay=False):

    class gridwidget(QWidget):
        pass

    gridlayoutwidget = gridwidget()
    gridlay = QGridLayout(gridlayoutwidget)
    gridlay.setAlignment(Qt.AlignmentFlag.AlignTop)
    gridlayoutwidget.setStyleSheet("gridwidget{background-color:transparent;}")

    def do(gridlay, grid, savelist, savelay):
        automakegrid(gridlay, grid, savelist)
        if isinstance(savelay, list):
            savelay.append(gridlay)

    __do = functools.partial(do, gridlay, grid, savelist, savelay)

    if not delay:
        __do()
        return gridlayoutwidget
    return gridlayoutwidget, __do


def makescroll():
    scroll = QScrollArea()
    # scroll.setHorizontalScrollBarPolicy(1)
    scroll.setStyleSheet("""QScrollArea{background-color:transparent;border:0px}""")
    scroll.setWidgetResizable(True)
    return scroll


def makescrollgrid(grid, lay, savelist=None, savelay=None):
    wid, do = makegrid(grid, savelist, savelay, delay=True)
    swid = makescroll()
    lay.addWidget(swid)
    swid.setWidget(wid)
    do()
    return wid


def makesubtab_lazy(
    titles=None, functions=None, klass=None, callback=None, delay=False, initial=None
):
    if klass:
        tab: LTabWidget = klass()
    else:
        tab = LTabWidget()

    def __(t: LTabWidget, initial, i):
        if initial:
            object, key = initial
            object[key] = i
        try:
            w = t.currentWidget()
            if "lazyfunction" in dir(w):
                w.lazyfunction()
                delattr(w, "lazyfunction")
        except:
            print_exc()
        if callback:
            callback(i)

    can = initial and (initial[1] in initial[0])
    if not can:
        tab.currentChanged.connect(functools.partial(__, tab, initial))

    def __do(tab: LTabWidget, titles, functions, initial):
        if titles and functions:
            for i, func in enumerate(functions):
                tabadd_lazy(tab, titles[i], func)
        if can:
            tab.setCurrentIndex(initial[0][initial[1]])
            tab.currentChanged.connect(functools.partial(__, tab, initial))
            tab.currentChanged.emit(initial[0][initial[1]])

    ___do = functools.partial(__do, tab, titles, functions, initial)
    if not delay:
        ___do()
        return tab
    else:
        return tab, ___do


@Singleton
class listediter(LDialog):
    def showmenu(self, p: QPoint):
        curr = self.hctable.currentIndex()
        if not curr.isValid():
            return
        menu = QMenu(self.hctable)
        remove = LAction("删除", menu)
        copy = LAction("复制", menu)
        up = LAction("上移", menu)
        down = LAction("下移", menu)
        if not (self.isrankeditor):
            menu.addAction(remove)
            menu.addAction(copy)
        if not (self.candidates):
            menu.addAction(up)
            menu.addAction(down)
        action = menu.exec(self.hctable.cursor().pos())

        if action == remove:
            self.hcmodel.removeRow(curr.row())
            self.internalrealname.pop(curr.row())
        elif action == copy:
            winsharedutils.clipboard_set(self.hcmodel.itemFromIndex(curr).text())

        elif action == up:

            self.moverank(-1)

        elif action == down:
            self.moverank(1)

    def moverank(self, dy):
        _pair = self.hctable.moverank(dy)
        if not _pair:
            return
        src, tgt = _pair
        self.internalrealname.insert(tgt, self.internalrealname.pop(src))

    def __init__(
        self,
        parent,
        title,
        lst,
        closecallback=None,
        ispathsedit=None,
        isrankeditor=False,
        namemapfunction=None,
        candidates=None,
        exec=False,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self.lst = lst
        self.candidates = candidates
        self.closecallback = closecallback
        self.ispathsedit = ispathsedit
        self.isrankeditor = isrankeditor
        try:
            self.setWindowTitle(title)
            model = LStandardItemModel()
            self.hcmodel = model
            self.namemapfunction = namemapfunction
            table = TableViewW()
            table.horizontalHeader().setVisible(False)
            table.horizontalHeader().setStretchLastSection(True)
            if isrankeditor or (not (ispathsedit is None)) or self.candidates:
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
            table.setWordWrap(False)
            table.setModel(model)

            table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            table.customContextMenuRequested.connect(self.showmenu)
            self.hctable = table
            self.internalrealname = []
            formLayout = QVBoxLayout(self)
            formLayout.addWidget(self.hctable)
            for row, k in enumerate(lst):  # 2
                try:
                    if namemapfunction:
                        namemapfunction(k)
                except:
                    continue
                self.internalrealname.append(k)
                if namemapfunction:
                    k = namemapfunction(k)
                item = QStandardItem(k)
                self.hcmodel.insertRow(row, [item])

                if candidates:
                    combo = SuperCombo()
                    _vis = self.candidates
                    if self.namemapfunction:
                        _vis = [self.namemapfunction(_) for _ in _vis]
                    combo.addItems(_vis)
                    combo.setCurrentIndex(self.candidates.index(lst[row]))
                    combo.currentIndexChanged.connect(
                        functools.partial(self.__changed, item)
                    )
                    self.hctable.setIndexWidget(self.hcmodel.index(row, 0), combo)
            if isrankeditor:
                self.buttons = threebuttons(texts=["上移", "下移"])
                self.buttons.btn1clicked.connect(functools.partial(self.moverank, -1))
                self.buttons.btn2clicked.connect(functools.partial(self.moverank, 1))
            elif self.candidates:
                self.buttons = threebuttons(texts=["添加行", "删除行"])
                self.buttons.btn1clicked.connect(self.click1)
                self.buttons.btn2clicked.connect(self.clicked2)
            else:
                if self.ispathsedit and self.ispathsedit.get("dirorfile", False):
                    self.buttons = threebuttons(
                        texts=["添加文件", "添加文件夹", "删除行", "上移", "下移"]
                    )
                    self.buttons.btn1clicked.connect(
                        functools.partial(self._addfile, False)
                    )
                    self.buttons.btn2clicked.connect(
                        functools.partial(self._addfile, True)
                    )
                    self.buttons.btn3clicked.connect(self.clicked2)
                    self.buttons.btn4clicked.connect(
                        functools.partial(self.moverank, -1)
                    )
                    self.buttons.btn5clicked.connect(
                        functools.partial(self.moverank, 1)
                    )
                else:
                    xx = "添加行"
                    if self.ispathsedit:
                        if self.ispathsedit.get("isdir", False):
                            xx = "添加文件夹"
                        else:
                            xx = "添加文件"
                    self.buttons = threebuttons(texts=[xx, "删除行", "上移", "下移"])
                    self.buttons.btn1clicked.connect(self.click1)
                    self.buttons.btn2clicked.connect(self.clicked2)
                    self.buttons.btn3clicked.connect(
                        functools.partial(self.moverank, -1)
                    )
                    self.buttons.btn4clicked.connect(
                        functools.partial(self.moverank, 1)
                    )

            formLayout.addWidget(self.buttons)
            self.resize(600, self.sizeHint().height())
            if exec:
                self.exec()
            else:
                self.show()
        except:
            print_exc()

    def clicked2(self):
        skip = self.hctable.removeselectedrows()
        for row in skip:
            self.internalrealname.pop(row)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.buttons.setFocus()

        rows = self.hcmodel.rowCount()
        rowoffset = 0
        dedump = set()
        if self.closecallback:
            before = pickle.dumps(self.lst)
        self.lst.clear()
        for row in range(rows):
            if self.namemapfunction:
                k = self.internalrealname[row]
            else:
                k = self.hcmodel.item(row, 0).text()
            if k == "" or k in dedump:
                rowoffset += 1
                continue
            self.lst.append(k)
            dedump.add(k)
        if self.closecallback:
            after = pickle.dumps(self.lst)
            self.closecallback(before != after)

    def __cb(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        for path in paths:
            self.internalrealname.insert(0, path)
            self.hcmodel.insertRow(0, [QStandardItem(path)])

    def __changed(self, item: QStandardItem, idx):
        self.internalrealname[item.row()] = self.candidates[idx]

    def _addfile(self, isdir):
        openfiledirectory(
            "",
            multi=True,
            edit=None,
            isdir=isdir,
            filter1=self.ispathsedit.get("filter1", "*.*"),
            callback=self.__cb,
        )

    def click1(self):
        if self.candidates:
            self.internalrealname.insert(0, self.candidates[0])
            item = QStandardItem("")
            self.hcmodel.insertRow(0, [item])
            combo = SuperCombo()
            _vis = self.candidates
            if self.namemapfunction:
                _vis = [self.namemapfunction(_) for _ in _vis]
            combo.addItems(_vis)
            combo.currentIndexChanged.connect(functools.partial(self.__changed, item))
            self.hctable.setIndexWidget(self.hcmodel.index(0, 0), combo)
        elif self.ispathsedit is None:
            self.internalrealname.insert(0, "")
            self.hcmodel.insertRow(0, [QStandardItem("")])
        else:
            openfiledirectory(
                "",
                multi=True,
                edit=None,
                isdir=self.ispathsedit.get("isdir", False),
                filter1=self.ispathsedit.get("filter1", "*.*"),
                callback=self.__cb,
            )


class ClickableLine(QLineEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, e):
        self.clicked.emit()
        super().mousePressEvent(e)


class listediterline(QWidget):

    def text(self):
        return self.edit.text()

    def setText(self, t):
        return self.edit.setText(t)

    def __init__(
        self,
        name,
        reflist,
        ispathsedit=None,
        directedit=False,
        specialklass=None,
        exec=False,
    ):
        super().__init__()
        self.edit = ClickableLine()
        self.reflist = reflist
        self.setText("|".join((str(_) for _ in reflist)))
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.edit)
        if not specialklass:
            specialklass = listediter
        callback = functools.partial(
            specialklass,
            self,
            name,
            reflist,
            closecallback=self.callback,
            ispathsedit=ispathsedit,
            exec=exec,
        )
        self.directedit = directedit
        if directedit:

            def __(t):
                self.reflist.clear()
                self.reflist.extend(t.split("|"))

            self.edit.textChanged.connect(__)

            def __2():
                self.edit.setReadOnly(True)
                callback()

            hbox.addWidget(getIconButton(callback=__2))
        else:
            self.edit.setReadOnly(True)
            self.edit.clicked.connect(callback)

    def callback(self, changed):
        if changed:
            self.setText("|".join((str(_) for _ in self.reflist)))
        if self.directedit:
            self.edit.setReadOnly(False)


def openfiledirectory(directory, multi, edit, isdir, filter1="*.*", callback=None):
    if isdir:
        res = QFileDialog.getExistingDirectory(directory=directory)
    else:
        res = (QFileDialog.getOpenFileName, QFileDialog.getOpenFileNames)[multi](
            directory=directory, filter=filter1
        )[0]

    if not res:
        return
    if isinstance(res, list):
        res = [mayberelpath(_) for _ in res]
    else:
        res = mayberelpath(res)
    if edit:
        edit.setText("|".join(res) if isinstance(res, list) else res)
    if callback:
        callback(res)


def getsimplepatheditor(
    text=None,
    multi=False,
    isdir=False,
    filter1="*.*",
    callback=None,
    icons=None,
    reflist=None,
    name=None,
    header=None,
    dirorfile=False,
    clearable=True,
    clearset=None,
    isfontselector=False,
    w=False,
):
    lay = QHBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)
    if multi:
        e = listediterline(
            name,
            reflist,
            dict(isdir=isdir, multi=False, filter1=filter1, dirorfile=dirorfile),
        )
        lay.addWidget(e)
    else:
        e = QLineEdit(text)
        e.setReadOnly(True)
        if icons:
            bu = getIconButton(icon=icons[0])
            if clearable:
                clear = getIconButton(icon=icons[1])
        else:
            bu = LPushButton("选择" + ("文件夹" if isdir else "文件"))
            if clearable:
                clear = LPushButton("清除")
        if clearable:
            lay.clear = clear

        if isfontselector:

            def __selectfont(callback, e):
                f = QFont()
                text = e.text()
                if text:
                    f.fromString(text)
                font, ok = QFontDialog.getFont(f, e)
                if ok:
                    _s = font.toString()
                    callback(_s)
                    e.setText(_s)

            _cb = functools.partial(__selectfont, callback, e)
        else:
            _cb = functools.partial(
                openfiledirectory,
                text,
                multi,
                e,
                isdir,
                "" if isdir else filter1,
                callback,
            )
        bu.clicked.connect(_cb)
        lay.addWidget(e)
        lay.addWidget(bu)
        if clearable:

            def __(_cb, _e, t):
                _cb("")
                if not t:
                    _e.setText("")
                elif callable(t):
                    _e.setText(t())

            clear.clicked.connect(functools.partial(__, callback, e, clearset))
            lay.addWidget(clear)
    if w and isinstance(lay, QLayout):
        w = QWidget()
        w.setLayout(lay)
        lay = w
    return lay


class threeswitch(QWidget):
    btnclicked = pyqtSignal(int)
    sizeChanged = pyqtSignal(QSize)

    def selectlayout(self, i):
        try:
            for _ in range(len(self.btns)):
                self.btns[(i + _) % len(self.btns)].setEnabled(False)
            for _ in range(len(self.btns)):
                self.btns[(i + _) % len(self.btns)].setChecked(_ == 0)
            self.btnclicked.emit(i)
            for _ in range(1, len(self.btns)):
                self.btns[(i + _) % len(self.btns)].setEnabled(True)
        except:
            pass

    def __init__(self, p, icons):
        super().__init__(p)
        self.btns = []
        hv = QHBoxLayout(self)
        hv.setContentsMargins(0, 0, 0, 0)
        hv.setSpacing(0)
        for i, icon in enumerate(icons):
            btn = IconButton(parent=self, icon=icon, checkable=True)
            btn.clicked.connect(functools.partial(self.selectlayout, i))
            btn.sizeChanged.connect(self.sizechange)
            self.btns.append(btn)
            hv.addWidget(btn)

    def sizechange(self, size: QSize):
        self.setFixedSize(QSize(size.width() * len(self.btns), size.height()))
        self.sizeChanged.emit(self.size())


class pixmapviewer(QWidget):
    tolastnext = pyqtSignal(int)

    def wheelEvent(self, e: QWheelEvent) -> None:
        self.tolastnext.emit([-1, 1][e.angleDelta().y() < 0])
        return super().wheelEvent(e)

    def __init__(self, p=None) -> None:
        super().__init__(p)
        self.pix = None
        self._pix = None
        self.boxtext = [], []

    def showpixmap(self, pix: QPixmap):
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        self.pix = pix
        self._pix = None
        self.boxtext = [], []
        self.update()

    def showboxtext(self, box, text):
        self._pix = None
        self.boxtext = box, text
        self.update()

    def paintEvent(self, e):
        if self.pix:
            if self._pix:
                if self._pix.size() != self.size() * self.devicePixelRatioF():
                    self._pix = None
            if not self._pix:

                rate = self.devicePixelRatioF()
                self._pix = QPixmap(self.size() * rate)
                self._pix.setDevicePixelRatio(rate)
                self._pix.fill(Qt.GlobalColor.transparent)

                if not self.pix.isNull():
                    painter = QPainter(self._pix)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                    pix = self.pix.scaled(
                        self.size() * self.devicePixelRatioF(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    x = self.width() / 2 - pix.width() / 2 / self.devicePixelRatioF()
                    y = self.height() / 2 - pix.height() / 2 / self.devicePixelRatioF()
                    painter.drawPixmap(int(x), int(y), pix)
                    boxs, texts = self.boxtext
                    try:
                        scale = pix.height() / self.pix.height() / rate
                        parsex = lambda xx: (xx) * scale + x
                        parsey = lambda yy: (yy) * scale + y
                        font = QFont()
                        font.setFamily(globalconfig["fonttype"])
                        font.setPointSizeF(globalconfig["fontsizeori"])
                        pen = QPen()
                        pen.setColor(QColor(globalconfig["rawtextcolor"]))
                        painter.setFont(font)
                        painter.setPen(pen)
                        for i in range(len(boxs)):
                            painter.drawText(
                                QPointF(parsex(boxs[i][0]), parsey(boxs[i][1])),
                                texts[i],
                            )
                            for j in range(len(boxs[i]) // 2):
                                painter.drawLine(
                                    QPointF(
                                        parsex(boxs[i][j * 2]),
                                        parsey(boxs[i][j * 2 + 1]),
                                    ),
                                    QPointF(
                                        parsex(boxs[i][(j * 2 + 2) % len(boxs[i])]),
                                        parsey(boxs[i][(j * 2 + 3) % len(boxs[i])]),
                                    ),
                                )
                    except:
                        print_exc()
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self._pix)
        return super().paintEvent(e)


class IconButton(QPushButton):
    clicked_1 = pyqtSignal()
    sizeChanged = pyqtSignal(QSize)

    def event(self, e):
        if e.type() == QEvent.Type.FontChange:
            self.resizedirect()
        elif e.type() == QEvent.Type.EnabledChange:
            self.__seticon()
        return super().event(e)

    def resizedirect(self):
        h = QFontMetricsF(self.font()).height()
        sz = (QSizeF(h, h) * gobject.Consts.btnscale).toSize()
        if self.fix:
            self.setFixedSize(sz)
        else:
            self.setFixedHeight(sz.height())
        self.setIconSize(sz)
        self.sizeChanged.emit(sz)

    def __init__(
        self, icon, enable=True, qicon=None, parent=None, checkable=False, fix=True
    ):
        super().__init__(parent)
        self._icon = icon
        self.clicked.connect(self.clicked_1)
        self.clicked.connect(self.__seticon)
        self._qicon = qicon
        self.fix = fix
        if fix:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border:transparent;padding: 0px;")
        self.setCheckable(checkable)
        self.setEnabled(enable and (bool(icon) or bool(qicon)))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resizedirect()

    def setIconStr(self, icon: str):
        self._icon = icon
        self.__seticon()

    def __seticon(self):
        if self._qicon:
            icon = self._qicon
        else:
            if self._icon is None:
                # 用于虚拟占位度量
                return
            if self.isCheckable():
                if isinstance(self._icon, str):
                    icons = [self._icon, self._icon]
                else:
                    icons = self._icon
                icon = icons[self.isChecked()]
                colors = ["", gobject.Consts.buttoncolor]
                color = QColor(colors[self.isChecked()])
            else:
                color = QColor(gobject.Consts.buttoncolor)
                icon = self._icon
            if not self.isEnabled():
                color = disablecolor(color)
            icon = qtawesome.icon(icon, color=color)
        self.setIcon(icon)

    def setChecked(self, a0):
        super().setChecked(a0)
        self.__seticon()

    def setEnabled(self, _):
        super().setEnabled(_)
        self.__seticon()


class SplitLine(QFrame):
    def __init__(self, *argc):
        super().__init__(*argc)
        self.setStyleSheet("background-color: gray;")
        self.setFixedHeight(2)


def clearlayout(ll: QLayout):
    while ll.count():
        item = ll.takeAt(0)
        if not item:
            continue
        w = item.widget()
        if w:
            w.hide()
            w.deleteLater()
            continue
        l = item.layout()
        if l:
            clearlayout(l)
            l.deleteLater()
            continue


def showhidelayout(ll: QLayout, vis):
    for _ in range(ll.count()):
        item = ll.itemAt(_)
        if not item:
            continue
        w = item.widget()
        if w:
            if vis:
                if not w.isVisible():
                    w.setVisible(True)
            else:
                w.setVisible(False)
            continue
        l = item.layout()
        if l:
            showhidelayout(l, vis)
            continue


class FQPlainTextEdit(QPlainTextEdit):
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        # 点击浏览器后，无法重新获取焦点。
        windows.SetFocus(int(self.winId()))
        return super().mousePressEvent(a0)


class FQLineEdit(QLineEdit):
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        # 点击浏览器后，无法重新获取焦点。
        windows.SetFocus(int(self.winId()))
        return super().mousePressEvent(a0)


class VisLFormLayout(LFormLayout):
    # 简易实现
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._row_widgets = {}
        self._reverse = {}
        self._row_vis = {}
        if "takeRow" not in dir(self):
            # qt5.5兼容
            self.takeRow = self.__takeRow

    def __takeRow(self, row):
        label_item = self.itemAt(row, QFormLayout.ItemRole.LabelRole)
        field_item = self.itemAt(row, QFormLayout.ItemRole.FieldRole)
        if label_item:
            self.removeItem(label_item)
        if field_item:
            self.removeItem(field_item)

        class __res:
            def __init__(self_, fieldItem, labelItem):
                self_.labelItem, self_.fieldItem = labelItem, fieldItem

        return __res(field_item, label_item)

    def addRow(self, label_or_field, field=None):
        row_index = self.rowCount()
        if field is None:
            super().addRow(label_or_field)
            field = label_or_field
            label_or_field = None
        else:
            super().addRow(label_or_field, field)
        self._row_widgets[row_index] = (label_or_field, field)
        self._row_vis[row_index] = True
        self._reverse[field] = row_index
        return row_index

    def setRowVisible(self, row_index, visible):
        if isinstance(row_index, int):
            pass
        elif isinstance(row_index, (QWidget, QLayout)):
            row_index = self._reverse[row_index]
        if self._row_vis[row_index] == visible:
            return
        insert_position = sum(1 for i in range(row_index) if self._row_vis[i])
        if visible:
            label, field = self._row_widgets[row_index]
            if label is not None:
                super().insertRow(insert_position, label, field)
            else:
                super().insertRow(insert_position, field)
            if isinstance(field, QWidget):
                if not field.isVisible():
                    field.setVisible(True)
            else:
                showhidelayout(field, True)
        else:
            tres = self.takeRow(insert_position)
            label = tres.labelItem
            if label:
                self.removeItem(label)
                label.widget().deleteLater()
            if tres.fieldItem:
                if tres.fieldItem.widget():
                    tres.fieldItem.widget().hide()
                else:
                    showhidelayout(tres.fieldItem.layout(), False)
        self._row_vis[row_index] = visible


class CollapsibleBox(NQGroupBox):
    def __init__(self, delayloadfunction=None, parent=None, margin0=True):
        super(CollapsibleBox, self).__init__(parent)
        lay = QVBoxLayout(self)
        if margin0:
            lay.setContentsMargins(0, 0, 0, 0)
        self.func = delayloadfunction
        self.toggle(False)

    def toggle(self, checked):
        if checked and self.func:
            self.func(self.layout())
            self.func = None
        self.setVisible(checked)


class CollapsibleBoxWithButton(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, delayloadfunction=None, title="", parent=None, toggled=False):
        super(CollapsibleBoxWithButton, self).__init__(parent)
        self.toggle_button = LToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.toggled.connect(self.__toggled)
        self.toggle_button.toggled.connect(self.toggled)
        self.content_area = CollapsibleBox(delayloadfunction, self)
        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)
        self.__toggled(toggled)

    def __toggled(self, checked):
        self.toggle_button.setChecked(checked)
        self.content_area.toggle(checked)
        self.toggle_button.setIcon(
            qtawesome.icon("fa.chevron-down" if checked else "fa.chevron-right")
        )


def createfoldgrid(
    grid,
    title,
    d: dict = None,
    k=None,
    internallayoutname=None,
    parent=None,
):

    def __(grid, internallayoutname, parent, lay: QLayout):
        w, do = makegrid(grid, delay=True)
        lay.addWidget(w)
        if internallayoutname:
            setattr(parent, internallayoutname, w.layout())
        do()

    toggled = d[k] if d else False
    box = CollapsibleBoxWithButton(
        functools.partial(__, grid, internallayoutname, parent),
        title,
        toggled=toggled,
    )
    if d:
        box.toggled.connect(functools.partial(d.__setitem__, k))
    return box


class editswitchTextBrowser(QWidget):
    textChanged = pyqtSignal(str)

    def heightForWidth(self, w):
        return self.browser.heightForWidth(w)

    def resizeEvent(self, a0):
        self.switch.move(self.width() - self.switch.width(), 0)
        return super().resizeEvent(a0)

    def __init__(self, parent=None):
        super().__init__(parent)
        stack = QStackedWidget()
        self.edit = QPlainTextEdit()
        self.browser = QLabel()
        self.browser.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.browser.setWordWrap(True)
        self.browser.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.edit.textChanged.connect(
            lambda: (
                self.browser.setText(
                    "<html>"
                    + re.sub(
                        r'href="([^"]+)"',
                        "",
                        re.sub(r'src="([^"]+)"', "", self.edit.toPlainText()),
                    )
                    + "</html>"
                ),
                self.textChanged.emit(self.edit.toPlainText()),
            )
        )
        stack.addWidget(self.browser)
        stack.addWidget(self.edit)
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(stack)
        self.switch = IconButton(parent=self, icon="fa.edit", checkable=True)
        self.switch.raise_()
        self.switch.clicked.connect(stack.setCurrentIndex)

    def settext(self, text):
        self.edit.setPlainText(text)

    def text(self):
        return self.edit.toPlainText()


class FlowWidget(QWidget):
    def __init__(self, parent=None, groups=3):
        super().__init__(parent)
        self.margin = QMargins(5, 5, 5, 5)
        self.spacing = 5
        self._item_list = [[] for _ in range(groups)]

    def insertWidget(self, group, index, w: QWidget):
        w.setParent(self)
        w.show()
        self._item_list[group].insert(index, w)
        self.doresize()

    def addWidget(self, group, w: QWidget):
        self.insertWidget(group, len(self._item_list[group]), w)

    def removeWidget(self, w: QWidget):
        for _ in self._item_list:
            if w in _:
                _.remove(w)
                w.deleteLater()
                self.doresize()
                break

    def doresize(self):
        line_height = 0
        spacing = self.spacing
        y = self.margin.left()
        for listi in self._item_list:
            x = self.margin.top()
            for i, item in enumerate(listi):

                next_x = x + item.sizeHint().width() + spacing
                if (
                    next_x - spacing + self.margin.right() > self.width()
                    and line_height > 0
                ):
                    x = self.margin.top()
                    y = y + line_height + spacing
                    next_x = x + item.sizeHint().width() + spacing

                size = item.sizeHint()
                if (i == len(listi) - 1) and isinstance(item, editswitchTextBrowser):
                    w = self.width() - self.margin.right() - x
                    size = QSize(w, max(size.height(), item.heightForWidth(w)))

                item.setGeometry(QRect(QPoint(x, y), size))
                line_height = max(line_height, size.height())
                x = next_x
            y = y + line_height + spacing
        self.setFixedHeight(y + self.margin.bottom() - spacing)

    def resizeEvent(self, a0):
        self.doresize()


class ClickableLabel(LLabel):
    def __init__(self, *argc, **kw):
        super().__init__(*argc, **kw)
        self.setClickable(True)
        self.setStyleSheet(
            r"""ClickableLabel{
                background:transparent
            }
            ClickableLabel:hover{
                background-color: rgba(128,128,128,0.3)
            }"""
            ""
        )

    def setClickable(self, clickable: bool):
        self._clickable = clickable

    def mouseReleaseEvent(self, event: QMouseEvent):
        if (
            self._clickable
            and event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.pos())
        ):
            self.clicked.emit()

    clicked = pyqtSignal()


class PopupWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Popup)
        self.dragging = False
        self.offset = None

    def display(self, pos=None):
        self.move(pos if pos else QCursor.pos())
        self.show()

    def mousePressEvent(self, event: QMouseEvent):
        if not self.rect().contains(event.pos()):
            return super().mousePressEvent(event)

        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = QCursor.pos() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.rect().contains(event.pos()):
            return super().mouseMoveEvent(event)
        if self.dragging:
            self.move(QCursor.pos() - self.offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.rect().contains(event.pos()):
            return super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.offset = None

    def closeEvent(self, a0):
        self.deleteLater()
        return super().closeEvent(a0)
