from qtsymbols import *
import os, platform, functools, threading, uuid, json
from traceback import print_exc
import windows, qtawesome, winsharedutils, gobject
from webviewpy import (
    webview_native_handle_kind_t,
    Webview,
    declare_library_path,
)
from winsharedutils import HTMLBrowser
from myutils.config import _TR, globalconfig, _TRL
from myutils.wrapper import Singleton_close, tryprint
from myutils.utils import nowisdark, checkportavailable, checkisusingwine
from gui.dynalang import (
    LLabel,
    LMessageBox,
    LPushButton,
    LAction,
    LGroupBox,
    LFormLayout,
    LTabWidget,
    LStandardItemModel,
    LDialog,
    LMainWindow,
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


class LFocusCombo(FocusCombo):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__items = None

    def addItems(self, items):
        self.__items = items
        super().addItems(_TRL(items))

    def clear(self):
        self.__items = []
        super().clear()

    def updatelangtext(self):
        if self.__items:
            for i in range(self.count()):
                self.setItemText(i, _TR(self.__items[i]))


class FocusFontCombo(QFontComboBox, FocusCombo):
    pass


class FocusSpin(QSpinBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:

        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


class FocusDoubleSpin(QDoubleSpinBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:

        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


class TableViewW(QTableView):
    def __init__(self, *argc) -> None:
        super().__init__(*argc)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)

    def setIndexWidget(self, index: QModelIndex, w: QWidget):
        super().setIndexWidget(index, w)
        if w is None:
            return
        if self.rowHeight(index.row()) < w.height():
            self.setRowHeight(index.row(), w.height())

    def updatelangtext(self):
        m = self.model()
        if isinstance(m, LStandardItemModel):
            m.updatelangtext()

    def safetext(self, row, col=None):
        if col is None:
            index = row
        else:
            index = self.model().index(row, col)
        _1 = self.model().itemFromIndex(index)
        _1 = _1.text() if _1 else ""
        return _1

    def copytable(self) -> str:
        if len(self.selectedIndexes()) <= 1:
            return winsharedutils.clipboard_set(self.safetext(self.currentIndex()))
        _data = []
        minr = minc = 999999999
        maxr = maxc = 0
        for index in self.selectedIndexes():
            minr = min(minr, index.row())
            minc = min(minc, index.column())
            maxr = max(maxr, index.row())
            maxc = max(maxc, index.column())
            _data.append(self.safetext(index))
        data = {
            "data": _data,
            "row": maxr - minr + 1,
            "col": maxc - minc + 1,
        }
        winsharedutils.clipboard_set(json.dumps(data))

    def pastetable(self):
        string = winsharedutils.clipboard_get()
        try:
            js = json.loads(string)
            current = self.currentIndex()
            for _ in range(js["row"]):
                self.model().insertRow(current.row() + 1, [])

            for i, data in enumerate(js.get("data", [])):
                c = current.column() + i % js["col"]
                if c >= self.model().columnCount():
                    continue
                self.model().setItem(
                    current.row() + 1 + i // js["col"], c, QStandardItem(data)
                )

        except:
            self.model().itemFromIndex(self.currentIndex()).setText(string)


@Singleton_close
class dialog_showinfo(QDialog):

    def __init__(self, parent, title, info) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(title)
        l = QLabel(info)
        layout = QHBoxLayout()
        layout.addWidget(l)
        self.setLayout(layout)
        self.show()


def getQMessageBox(
    parent=None,
    title="",
    text="",
    useok=True,
    usecancel=False,
    okcallback=None,
    cancelcallback=None,
):
    msgBox = LMessageBox(parent)
    msgBox.setWindowTitle((title))
    msgBox.setText((text))
    btn = 0
    if useok:
        btn |= QMessageBox.Ok
    if usecancel:
        btn |= QMessageBox.Cancel

    msgBox.setStandardButtons(btn)
    msgBox.setDefaultButton(QMessageBox.Ok)
    ret = msgBox.exec()

    if ret == QMessageBox.Ok and okcallback:
        okcallback()
    elif ret == QMessageBox.Cancel and cancelcallback:
        cancelcallback()


def isinrect(pos, rect):
    x, y = pos.x(), pos.y()
    x1, x2, y1, y2 = rect
    return x >= x1 and x <= x2 and y <= y2 and y >= y1


def makerect(_):
    x, y, w, h = _
    return [x, x + w, y, y + h]


class saveposwindow(LMainWindow):
    def __init__(self, parent, poslist=None, flags=None) -> None:
        if flags:
            super().__init__(parent, flags=flags)
        else:
            super().__init__(parent)

        self.poslist = poslist
        if self.poslist:
            contains = False
            usescreen = QApplication.primaryScreen()
            for screen in QApplication.screens():
                if not screen.geometry().contains(QPoint(poslist[0], poslist[1])):
                    continue
                contains = True
                usescreen = screen
                break
            poslist[2] = max(0, min(poslist[2], usescreen.size().width()))
            poslist[3] = max(0, min(poslist[3], usescreen.size().height()))
            if not contains:
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

    def moveEvent(self, a0) -> None:
        self.__checked_savepos()

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


class commonsolveevent(QWidget):

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.Type.MouseButtonDblClick:
            return True
        elif a0.type() == QEvent.Type.EnabledChange:
            self.setEnabled(not self.isEnabled())
            return True
        return super().event(a0)


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


class MySwitch(commonsolveevent):
    clicked = pyqtSignal(bool)

    def click(self):
        self.setChecked(not self.checked)
        self.clicked.emit(self.checked)

    def sizeHint(self):
        return QSize(
            int(1.62 * globalconfig["buttonsize2"]), globalconfig["buttonsize2"]
        )

    def __init__(self, parent=None, sign=True, enable=True, icon=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.checked = sign
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.__currv = 0
        if sign:
            self.__currv = 20
        self.icon = icon

        self.animation = QVariantAnimation()
        self.animation.setDuration(80)
        self.animation.setStartValue(0)
        self.animation.setEndValue(20)
        self.animation.valueChanged.connect(self.update11)
        self.animation.finished.connect(self.onAnimationFinished)
        self.enable = enable

    def setEnabled(self, enable):
        self.enable = enable
        self.update()

    def isEnabled(self):
        return self.enable

    def isChecked(self):
        return self.checked

    def setChecked(self, check):
        if check == self.checked:
            return
        self.checked = check
        self.runanimeorshowicon()

    def update11(self):
        self.__currv = self.animation.currentValue()
        self.update()

    def runanimeorshowicon(self):
        if self.icon:
            self.update()
        else:
            self.runanime()

    def runanime(self):
        self.animation.setDirection(
            QVariantAnimation.Direction.Forward
            if self.checked
            else QVariantAnimation.Direction.Backward
        )
        self.animation.start()

    def getcurrentcolor(self):

        __ = QColor(
            [globalconfig["buttoncolor3"], globalconfig["buttoncolor2"]][self.checked]
        )
        if not self.enable:
            __ = disablecolor(__)
        return __

    def paintanime(self, painter: QPainter):

        painter.setBrush(self.getcurrentcolor())
        bigw = self.size().width() - self.sizeHint().width()
        bigh = self.size().height() - self.sizeHint().height()
        x = bigw // 2
        y = bigh // 2
        painter.drawRoundedRect(
            QRect(x, y, self.sizeHint().width(), self.sizeHint().height()),
            self.sizeHint().height() // 2,
            self.sizeHint().height() // 2,
        )

        offset = int(
            self.__currv * (self.sizeHint().width() - self.sizeHint().height()) / 20
        )
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(
            QPoint(
                x + self.sizeHint().height() // 2 + offset,
                y + self.sizeHint().height() // 2,
            ),
            int(self.sizeHint().height() * 0.35),
            int(self.sizeHint().height() * 0.35),
        )

    def painticon(self, painter: QPainter):

        icon: QIcon = qtawesome.icon(self.icon, color=self.getcurrentcolor())
        bigw = self.size().width() - self.sizeHint().width()
        bigh = self.size().height() - self.sizeHint().height()
        x = bigw // 2
        y = bigh // 2
        painter.drawPixmap(x, y, icon.pixmap(self.sizeHint()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        if self.icon:
            self.painticon(painter)
        else:
            self.paintanime(painter)

    def mouseReleaseEvent(self, event) -> None:
        if not self.enable:
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        try:
            self.checked = not self.checked
            self.clicked.emit(self.checked)
            self.runanimeorshowicon()
            # 父窗口deletelater
        except:
            pass

    def onAnimationFinished(self):
        pass


class IconButton(commonsolveevent):
    clicked = pyqtSignal()

    def sizeHint(self):
        return QSize(
            int(1.42 * globalconfig["buttonsize2"]),
            int(1.42 * globalconfig["buttonsize2"]),
        )

    def __init__(self, icon, enable=True, qicon=None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enable = enable
        self._icon = icon
        self._qicon = qicon

    def setEnabled(self, enable):
        self.enable = enable
        self.update()

    def isEnabled(self):
        return self.enable

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        if self._qicon:
            icon = self._qicon

        else:

            __ = QColor(globalconfig["buttoncolor2"])
            if not self.enable:
                __ = disablecolor(__)
            icon: QIcon = qtawesome.icon(self._icon, color=__)
        bigw = self.size().width() - self.sizeHint().width()
        bigh = self.size().height() - self.sizeHint().height()
        x = bigw // 2
        y = bigh // 2
        painter.drawPixmap(x, y, icon.pixmap(self.sizeHint()))

    def mouseReleaseEvent(self, event) -> None:
        if not self.enable:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class resizableframeless(saveposwindow):
    def __init__(self, parent, flags, poslist) -> None:
        super().__init__(parent, poslist, flags)
        self.setMouseTracking(True)

        self._padding = 5
        self.resetflags()

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

        if self._move_drag == False:
            self._right_rect = [
                self.width() - self._padding,
                self.width() + self._padding,
                self._padding,
                self.height() - self._padding,
            ]
            self._left_rect = [
                -self._padding,
                self._padding,
                self._padding,
                self.height() - self._padding,
            ]
            self._bottom_rect = [
                self._padding,
                self.width() - self._padding,
                self.height() - self._padding,
                self.height() + self._padding,
            ]
            self._top_rect = [
                self._padding,
                self.width() - self._padding,
                -self._padding,
                self._padding,
            ]
            self._corner_youxia = [
                self.width() - self._padding,
                self.width() + self._padding,
                self.height() - self._padding,
                self.height() + self._padding,
            ]
            self._corner_zuoxia = [
                -self._padding,
                self._padding,
                self.height() - self._padding,
                self.height() + self._padding,
            ]

            self._corner_youshang = [
                self.width() - self._padding,
                self.width() + self._padding,
                -self._padding,
                self._padding,
            ]

            self._corner_zuoshang = [
                -self._padding,
                self._padding,
                -self._padding,
                self._padding,
            ]
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
        if isinrect(event.pos(), self._corner_youxia):
            self._corner_drag_youxia = True
        elif isinrect(event.pos(), self._right_rect):
            self._right_drag = True
        elif isinrect(event.pos(), self._left_rect):
            self._left_drag = True
        elif isinrect(event.pos(), self._top_rect):
            self._top_drag = True
        elif isinrect(event.pos(), self._bottom_rect):
            self._bottom_drag = True
        elif isinrect(event.pos(), self._corner_zuoxia):
            self._corner_drag_zuoxia = True
        elif isinrect(event.pos(), self._corner_youshang):
            self._corner_drag_youshang = True
        elif isinrect(event.pos(), self._corner_zuoshang):
            self._corner_drag_zuoshang = True
        else:
            self._move_drag = True
            self.move_DragPosition = gpos - self.pos()

    def leaveEvent(self, a0) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(a0)

    def mouseMoveEvent(self, event):

        pos = event.pos()
        gpos = QCursor.pos()
        if isinrect(pos, self._corner_youxia):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif isinrect(pos, self._corner_zuoshang):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif isinrect(pos, self._corner_zuoxia):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif isinrect(pos, self._corner_youshang):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif isinrect(pos, self._bottom_rect):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif isinrect(pos, self._top_rect):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif isinrect(pos, self._right_rect):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif isinrect(pos, self._left_rect):
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
            self.setGeometry(
                (gpos - self.startxp).x(),
                (gpos - self.startxp).y(),
                self.startw - (gpos.x() - self.startx),
                self.starth - (gpos.y() - self.starty),
            )

        elif self._left_drag:
            self.setGeometry(
                (gpos - self.startxp).x(),
                self.y(),
                self.startw - (gpos.x() - self.startx),
                self.height(),
            )
        elif self._bottom_drag:
            self.resize(self.width(), event.pos().y())
        elif self._top_drag:
            self.setGeometry(
                self.x(),
                (gpos - self.startxp).y(),
                self.width(),
                self.starth - (gpos.y() - self.starty),
            )
        elif self._corner_drag_zuoxia:
            self.setGeometry(
                (gpos - self.startxp).x(),
                self.y(),
                self.startw - (gpos.x() - self.startx),
                event.pos().y(),
            )
        elif self._corner_drag_youxia:
            self.resize(pos.x(), pos.y())
        elif self._move_drag:
            self.move(gpos - self.move_DragPosition)

    def mouseReleaseEvent(self, QMouseEvent):
        self.resetflags()


class Prompt_dialog(LDialog):
    def __init__(self, parent, title, info, items) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowContextHelpButtonHint
            & ~Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowStaysOnTopHint
        )
        self.setWindowTitle(title)
        self.setWindowIcon(qtawesome.icon("fa-question"))

        _layout = QVBoxLayout()

        _layout.addWidget(LLabel(info))

        self.text = []
        for _ in items:

            le = QLineEdit()
            le.setText(_[1])
            self.text.append((le))
            hl = QHBoxLayout()
            hl.addWidget(LLabel(_[0]))
            hl.addWidget(le)
            _layout.addLayout(hl)
        button = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button.accepted.connect(self.accept)
        button.rejected.connect(self.reject)
        _layout.addWidget(button)
        self.setLayout(_layout)
        self.resize(400, 1)


def callbackwrap(d, k, call, _):
    d[k] = _

    if call:
        try:
            call(_)
        except:
            print_exc()


def comboboxcallbackwrap(internal, d, k, call, _):
    _ = internal[_]
    d[k] = _

    if call:
        try:
            call(_)
        except:
            print_exc()


def getsimplecombobox(
    lst, d, k, callback=None, fixedsize=False, internal=None, static=False, emit=False
):
    if static:
        s = FocusCombo()
    else:

        s = LFocusCombo()
    s.addItems(lst)

    if internal:
        if len(internal):
            if (k not in d) or (d[k] not in internal):
                d[k] = internal[0]

            s.setCurrentIndex(internal.index(d[k]))
        s.currentIndexChanged.connect(
            functools.partial(comboboxcallbackwrap, internal, d, k, callback)
        )
    else:
        if len(lst):
            if (k not in d) or (d[k] >= len(lst)):
                d[k] = 0

            s.setCurrentIndex(d[k])
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


def getspinbox(mini, maxi, d, key, double=False, step=1, callback=None, dec=1):
    if double:
        s = FocusDoubleSpin()
        s.setDecimals(dec)
    else:
        s = FocusSpin()
        d[key] = int(d[key])
    s.setMinimum(mini)
    s.setMaximum(maxi)
    s.setSingleStep(step)
    s.setValue(d[key])
    s.valueChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def D_getspinbox(mini, maxi, d, key, double=False, step=1, callback=None, dec=1):
    return lambda: getspinbox(mini, maxi, d, key, double, step, callback, dec)


def getIconButton(callback=None, icon="fa.paint-brush", enable=True, qicon=None):

    b = IconButton(icon, enable, qicon)

    if callback:
        b.clicked.connect(callback)

    return b


def D_getIconButton(callback=None, icon="fa.paint-brush", enable=True, qicon=None):
    return lambda: getIconButton(callback, icon, enable, qicon)


def getcolorbutton(
    d,
    key,
    callback,
    name=None,
    parent=None,
    icon="fa.paint-brush",
    constcolor=None,
    enable=True,
    transparent=True,
    qicon=None,
    sizefixed=False,
):
    if qicon is None:
        qicon = qtawesome.icon(icon, color=constcolor if constcolor else d[key])
    b = QPushButton()
    b.setIcon(qicon)
    b.setEnabled(enable)
    sz = int(1.42 * globalconfig["buttonsize2"])
    b.setIconSize(QSize(sz, sz))
    if sizefixed:
        b.setFixedSize(QSize(sz, sz))
    if transparent:
        b.setStyleSheet(
            """background-color: rgba(255, 255, 255, 0);
            color: black;
            border: 0px;
            font: 100 10pt;"""
        )
    if callback:
        b.clicked.connect(callback)
    b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
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
    transparent=True,
    qicon=None,
    sizefixed=False,
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
        transparent,
        qicon,
        sizefixed,
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
    d, key, enable=True, callback=None, name=None, pair=None, parent=None, default=None
):
    if default:
        if key not in d:
            d[key] = default

    b = MySwitch(sign=d[key], enable=enable)
    b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    b.clicked.connect(functools.partial(callbackwrap, d, key, callback))
    if pair:
        if pair not in dir(parent):
            setattr(parent, pair, {})
        getattr(parent, pair)[name] = b
    elif name:
        setattr(parent, name, b)
    return b


def D_getsimpleswitch(
    d, key, enable=True, callback=None, name=None, pair=None, parent=None, default=None
):
    return lambda: getsimpleswitch(
        d, key, enable, callback, name, pair, parent, default
    )


def selectcolor(
    parent, configdict, configkey, button, item=None, name=None, callback=None
):

    color = QColorDialog.getColor(QColor(configdict[configkey]), parent)
    if not color.isValid():
        return
    if button is None:
        button = getattr(item, name)
    button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
    configdict[configkey] = color.name()

    if callback:
        try:
            callback()
        except:
            print_exc()


def getboxlayout(
    widgets, lc=QHBoxLayout, margin0=False, makewidget=False, delay=False, both=False
):
    cp_layout = lc()

    def __do(cp_layout, widgets):
        for w in widgets:
            if callable(w):
                w = w()
            elif isinstance(w, str):
                w = LLabel(w)
            if isinstance(w, QWidget):
                cp_layout.addWidget(w)
            elif isinstance(w, QLayout):
                cp_layout.addLayout(w)

    _do = functools.partial(__do, cp_layout, widgets)
    if margin0:
        cp_layout.setContentsMargins(0, 0, 0, 0)
    if not delay:
        _do()
    if makewidget:
        w = QWidget()
        w.setLayout(cp_layout)
    if delay:
        return w, _do
    if both:
        return w, cp_layout
    if makewidget:
        return w
    return cp_layout


def getvboxwidget():
    return getboxlayout([], lc=QVBoxLayout, margin0=True, makewidget=True, both=True)


class abstractwebview(QWidget):
    on_load = pyqtSignal(str)
    on_ZoomFactorChanged = pyqtSignal(float)
    html_limit = 2 * 1024 * 1024

    # 必须的接口
    def _setHtml(self, html):
        pass

    def navigate(self, url):
        pass

    #
    def _parsehtml(self, html):
        return self._parsehtml_dark_auto(html)

    def set_zoom(self, zoom):
        pass

    def get_zoom(self):
        return 1

    def bind(self, fname, func):
        pass

    def eval(self, js, retsaver=None):
        pass

    def set_transparent_background(self):
        pass

    def clear(self):
        self.navigate("about:blank")

    def setHtml(self, html):
        html = self._parsehtml(html)
        if len(html) < self.html_limit:
            self._setHtml(html)
        else:
            lastcachehtml = gobject.gettempdir(str(uuid.uuid4()) + ".html")
            with open(lastcachehtml, "w", encoding="utf8") as ff:
                ff.write(html)
            self.navigate(lastcachehtml)

    def _parsehtml_dark(self, html):
        if nowisdark():
            html = (
                html
                + """
    <style>
        body 
        { 
            background-color: rgb(44,44,44);
            color: white; 
        }
    </style>"""
            )
        return html

    def _parsehtml_dark_auto(self, html):
        return (
            html
            + """
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
        )


class WebivewWidget(abstractwebview):

    def __del__(self):
        winsharedutils.remove_ZoomFactorChanged(self.get_controller(), self.__token)

    def bind(self, fname, func):
        self.webview.bind(fname, func)

    def eval(self, js):
        self.webview.eval(js)

    def get_controller(self):
        return self.webview.get_native_handle(
            webview_native_handle_kind_t.WEBVIEW_NATIVE_HANDLE_KIND_BROWSER_CONTROLLER
        )

    def get_hwnd(self):
        return self.webview.get_native_handle(
            webview_native_handle_kind_t.WEBVIEW_NATIVE_HANDLE_KIND_UI_WIDGET
        )

    def __init__(self, parent=None, debug=True, usedarklight=True) -> None:
        super().__init__(parent)
        declare_library_path(
            os.path.abspath(
                os.path.join(
                    "files/plugins/",
                    ("DLL32", "DLL64")[platform.architecture()[0] == "64bit"],
                    "webview",
                )
            )
        )
        self.webview = None
        self.webview = Webview(debug=debug, window=int(self.winId()))
        zoomfunc = winsharedutils.add_ZoomFactorChanged_CALLBACK(
            self.on_ZoomFactorChanged.emit
        )
        self.__token = winsharedutils.add_ZoomFactorChanged(
            self.get_controller(), zoomfunc
        )
        self.keepref = [zoomfunc]
        self.webview.bind("__on_load", self._on_load)
        self.webview.init("""window.__on_load(window.location.href)""")
        if usedarklight:
            self.__darkstate = None
            t = QTimer(self)
            t.setInterval(100)
            t.timeout.connect(self.__darkstatechecker)
            t.timeout.emit()
            t.start()

    def __darkstatechecker(self):
        dl = globalconfig["darklight2"]
        if dl == self.__darkstate:
            return
        self.__darkstate = dl
        winsharedutils.put_PreferredColorScheme(self.get_controller(), dl)

    def set_zoom(self, zoom):
        winsharedutils.put_ZoomFactor(self.get_controller(), zoom)

    def get_zoom(self):
        return winsharedutils.get_ZoomFactor(self.get_controller())

    def _on_load(self, href):
        self.on_load.emit(href)

    def navigate(self, url):
        self.webview.navigate(url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self.webview:
            hwnd = self.get_hwnd()
            size = a0.size() * self.devicePixelRatioF()
            windows.MoveWindow(hwnd, 0, 0, size.width(), size.height(), True)

    def _setHtml(self, html):
        self.webview.set_html(html)

    def set_transparent_background(self):
        winsharedutils.set_transparent_background(self.get_controller())


class QWebWrap(abstractwebview):

    def __init__(self, p=None) -> None:
        super().__init__(p)
        if isqt5:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
        else:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
        if "QTWEBENGINE_REMOTE_DEBUGGING" not in os.environ:
            DEBUG_PORT = 5588
            for i in range(100):
                if checkportavailable(DEBUG_PORT):
                    break
                DEBUG_PORT += 1
            os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = str(DEBUG_PORT)
        self.DEBUG_URL = (
            "http://127.0.0.1:%s" % os.environ["QTWEBENGINE_REMOTE_DEBUGGING"]
        )
        self.internal = QWebEngineView(self)
        self.internal.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.internal.customContextMenuRequested.connect(self._qwmenu)
        self.internal.loadFinished.connect(self._loadFinish)
        self.internal_zoom = 1
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.__getzoomfactor)
        t.timeout.emit()
        t.start()

    def _qwmenu(self, pos):

        if isqt5:
            from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

            web_menu = self.internal.page().createStandardContextMenu()
        else:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtWebEngineCore import QWebEnginePage

            web_menu = self.internal.createStandardContextMenu()
        loadinspector = QAction("Inspect")
        if (
            self.internal.page().action(QWebEnginePage.WebAction.InspectElement)
            not in web_menu.actions()
        ):
            web_menu.addAction(loadinspector)
        action = web_menu.exec(self.internal.mapToGlobal(pos))

        if action == loadinspector:

            class QMW(saveposwindow):
                def closeEvent(_self, e):
                    self.internal.page().setDevToolsPage(None)
                    super(QMW, _self).closeEvent(e)

                def __init__(_self) -> None:
                    super().__init__(
                        gobject.baseobject.commonstylebase,
                        poslist=globalconfig["qwebinspectgeo"],
                    )
                    _self.setWindowTitle("Inspect")
                    _self.internal = QWebEngineView(_self)
                    _self.setCentralWidget(_self.internal)
                    _self.internal.load(QUrl(self.DEBUG_URL))
                    self.internal.page().setDevToolsPage(_self.internal.page())
                    self.internal.page().triggerAction(
                        QWebEnginePage.WebAction.InspectElement
                    )

                    _self.show()

            QMW()

    def _loadFinish(self):
        self.on_load.emit(self.internal.url().url())

    def eval(self, js, retsaver=None):
        if not retsaver:
            retsaver = lambda _: 1
        self.internal.page().runJavaScript(js, retsaver)

    def set_transparent_background(self):
        self.internal.page().setBackgroundColor(Qt.GlobalColor.transparent)

    def set_zoom(self, zoom):
        self.internal_zoom = zoom
        self.internal.setZoomFactor(zoom)

    def get_zoom(self):
        return self.internal.zoomFactor()

    def __getzoomfactor(self):
        z = self.internal.zoomFactor()
        if z != self.internal_zoom:
            self.internal_zoom = z
            self.on_ZoomFactorChanged.emit(z)

    def navigate(self, url: str):

        if not url.lower().startswith("http"):
            url = url.replace("\\", "/")
        self.internal.load(QUrl(url))

    def _setHtml(self, html):
        self.internal.setHtml(html)

    @tryprint
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.internal.resize(a0.size())

    def _parsehtml(self, html):
        return self._parsehtml_dark(html)


class mshtmlWidget(abstractwebview):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        iswine = checkisusingwine()
        if iswine or (HTMLBrowser.version() < 10001):  # ie10之前，sethtml会乱码
            self.html_limit = 0
        self.browser = HTMLBrowser(int(self.winId()))
        self.curr_url = None
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.__getcurrenturl)
        t.timeout.emit()
        t.start()

    def __getcurrenturl(self):
        _u = self.browser.get_current_url()
        if self.curr_url != _u:
            self.curr_url = _u
            self.on_load.emit(_u)

    def navigate(self, url):
        self.browser.navigate(url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = a0.size() * self.devicePixelRatioF()
        self.browser.resize(0, 0, size.width(), size.height())

    def _setHtml(self, html):
        self.browser.set_html(html)

    def _parsehtml(self, html):
        html = self._parsehtml_dark(html)
        html = """<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8" /></head><body style=" font-family:'{}'">{}</body></html>""".format(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family(),
            html,
        )
        return html


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


class auto_select_webview(QWidget):
    on_load = pyqtSignal(str)
    on_ZoomFactorChanged = pyqtSignal(float)

    def clear(self):
        self.internal.clear()

    def navigate(self, url):
        self._maybecreate()
        self.internal.set_zoom(self.internalsavedzoom)
        self.internal.navigate(url)

    def setHtml(self, html):
        self._maybecreate()
        self.internal.set_zoom(self.internalsavedzoom)
        self.internal.setHtml(html)

    def set_zoom(self, zoom):
        self.internalsavedzoom = zoom
        self.internal.set_zoom(zoom)

    def sizeHint(self):
        return QSize(256, 192)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.is_fallback = -2
        self.contex = -1
        self.internal = (
            abstractwebview()
        )  # 加个占位的widget，否则等待加载的时候有一瞬间的灰色背景。
        self.lock = threading.Lock()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.internal)
        self.setLayout(layout)
        self.internalsavedzoom = 1

    def internalzoomchanged(self, zoom):
        self.internalsavedzoom = zoom
        self.on_ZoomFactorChanged.emit(zoom)

    def _maybecreate(self):
        with self.lock:
            self._maybecreate_internal()

    def _maybecreate_internal(self):
        if globalconfig["usewebview"] == self.contex:
            return
        if self.is_fallback == globalconfig["usewebview"]:
            return
        if self.internal:
            self.layout().removeWidget(self.internal)
        self.internal = self._createwebview()
        self.internal.set_zoom(self.internalsavedzoom)
        self.internal.on_load.connect(self.on_load)
        self.internal.on_ZoomFactorChanged.connect(self.internalzoomchanged)
        self.layout().addWidget(self.internal)

    def _createwebview(self):
        self.contex = globalconfig["usewebview"]
        try:
            if self.contex == 0:
                browser = mshtmlWidget()
            elif self.contex == 1:
                browser = WebivewWidget()
            elif self.contex == 2:
                browser = QWebWrap()
        except:
            print_exc()
            self.is_fallback = self.contex
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
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
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
    v = QVBoxLayout()
    q.setLayout(v)
    v.setContentsMargins(0, 0, 0, 0)
    q.lazyfunction = functools.partial(getrealwidgetfunction, v)
    tab.addTab(q, title)


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
                    w = w()
                if w.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed:
                    needstretch = True
                hb.addWidget(w)
            if needstretch:
                hb.insertStretch(0)
                hb.addStretch()
            wid = hb
        else:
            if callable(wid):
                wid = wid()
            elif isinstance(wid, str):
                wid = QLabel(wid)
                wid.setOpenExternalLinks(True)
            if wid.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed:
                hb = QHBoxLayout()
                hb.setContentsMargins(0, 0, 0, 0)
                hb.addStretch()
                hb.addWidget(wid)
                hb.addStretch()
                wid = hb
        if name:
            lay.addRow(name, wid)

        else:
            lay.addRow(wid)


def makegroupingrid(args):
    lis = args.get("grid")
    title = args.get("title", None)
    _type = args.get("type", "form")
    parent = args.get("parent", None)
    groupname = args.get("name", None)
    enable = args.get("enable", True)
    internallayoutname = args.get("internallayoutname", None)
    group = LGroupBox()

    if not enable:
        group.setEnabled(False)
    if groupname and parent:
        setattr(parent, groupname, group)
    if title:
        group.setTitle(title)
    else:
        group.setStyleSheet(
            "QGroupBox{ margin-top:0px;} QGroupBox:title {margin-top: 0px;}"
        )

    if _type == "grid":
        grid = QGridLayout()
        group.setLayout(grid)
        automakegrid(grid, lis)
        if internallayoutname:
            setattr(parent, internallayoutname, grid)
    elif _type == "form":
        lay = LFormLayout()
        group.setLayout(lay)
        makeforms(lay, lis)
        if internallayoutname:
            setattr(parent, internallayoutname, lay)
    return group


def automakegrid(grid: QGridLayout, lis, save=False, savelist=None):

    maxl = 0
    linecolss = []
    for nowr, line in enumerate(lis):
        nowc = 0
        linecolssx = []
        for item in line:
            if type(item) == str:
                cols = 1
            elif type(item) != tuple:
                wid, cols = item, 1
            elif len(item) == 2:

                wid, cols = item
            elif len(item) == 3:
                wid, cols, arg = item
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
                wid = LLabel(item)
            elif type(item) != tuple:
                wid, cols = item, 1
            elif len(item) == 2:

                wid, cols = item
                if type(wid) == str:
                    wid = LLabel(wid)
            elif len(item) == 3:
                wid, cols, arg = item
                if type(wid) == str:
                    wid = LLabel(wid)
                    if arg == "link":
                        wid.setOpenExternalLinks(True)
                elif arg == "group":
                    wid = makegroupingrid(wid)
            if cols > 0:
                cols = cols
            elif cols == 0:
                cols = maxl - sum(linecolss[nowr])
            else:
                cols = -maxl // cols
            do = None
            if callable(wid):
                wid = wid()
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


def makegrid(grid=None, save=False, savelist=None, savelay=None, delay=False):

    class gridwidget(QWidget):
        pass

    gridlayoutwidget = gridwidget()
    gridlay = QGridLayout()
    gridlay.setAlignment(Qt.AlignmentFlag.AlignTop)
    gridlayoutwidget.setLayout(gridlay)
    gridlayoutwidget.setStyleSheet("gridwidget{background-color:transparent;}")

    def do(gridlay, grid, save, savelist, savelay):
        automakegrid(gridlay, grid, save, savelist)
        if save:
            savelay.append(gridlay)

    __do = functools.partial(do, gridlay, grid, save, savelist, savelay)
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


def makescrollgrid(grid, lay, save=False, savelist=None, savelay=None):
    wid, do = makegrid(grid, save, savelist, savelay, delay=True)
    swid = makescroll()
    lay.addWidget(swid)
    swid.setWidget(wid)
    do()
    return wid


def makesubtab_lazy(
    titles=None, functions=None, klass=None, callback=None, delay=False
):
    if klass:
        tab = klass()
    else:
        tab = LTabWidget()

    def __(t, i):
        try:
            w = t.currentWidget()
            if "lazyfunction" in dir(w):
                w.lazyfunction()
                delattr(w, "lazyfunction")
        except:
            print_exc()
        if callback:
            callback(i)

    tab.currentChanged.connect(functools.partial(__, tab))

    def __do(tab, titles, functions):
        if titles and functions:
            for i, func in enumerate(functions):
                tabadd_lazy(tab, titles[i], func)

    ___do = functools.partial(__do, tab, titles, functions)
    if not delay:
        ___do()
        return tab
    else:
        return tab, ___do


@Singleton_close
class listediter(LDialog):
    def showmenu(self, p: QPoint):
        curr = self.hctable.currentIndex()
        r = curr.row()
        if r < 0:
            return
        menu = QMenu(self.hctable)
        remove = LAction("删除")
        copy = LAction("复制")
        up = LAction("上移")
        down = LAction("下移")
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
        curr = self.hctable.currentIndex()
        target = (curr.row() + dy) % self.hcmodel.rowCount()
        text = self.internalrealname[curr.row()]
        self.internalrealname.pop(curr.row())
        self.hcmodel.removeRow(curr.row())
        self.internalrealname.insert(target, text)
        if self.namemapfunction:
            text = self.namemapfunction(text)
        self.hcmodel.insertRow(target, [QStandardItem(text)])
        self.hctable.setCurrentIndex(self.hcmodel.index(target, 0))

    def __init__(
        self,
        parent,
        title,
        header,
        lst,
        closecallback=None,
        ispathsedit=None,
        isrankeditor=False,
        namemapfunction=None,
        candidates=None,
    ) -> None:
        super().__init__(parent)
        self.lst = lst
        self.candidates = candidates
        self.closecallback = closecallback
        self.ispathsedit = ispathsedit
        self.isrankeditor = isrankeditor
        try:
            self.setWindowTitle(title)
            model = LStandardItemModel()
            model.setHorizontalHeaderLabels([header])
            self.hcmodel = model
            self.namemapfunction = namemapfunction
            table = TableViewW()
            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
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
            formLayout = QVBoxLayout()
            self.setLayout(formLayout)
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
                    combo = LFocusCombo()
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
                self.buttons = threebuttons(texts=["添加行", "删除行", "上移", "下移"])
                self.buttons.btn1clicked.connect(self.click1)
                self.buttons.btn2clicked.connect(self.clicked2)
                self.buttons.btn3clicked.connect(functools.partial(self.moverank, -1))
                self.buttons.btn4clicked.connect(functools.partial(self.moverank, 1))

            formLayout.addWidget(self.buttons)
            self.resize(600, self.sizeHint().height())
            self.show()
        except:
            print_exc()

    def clicked2(self):
        skip = []
        for index in self.hctable.selectedIndexes():
            if index.row() in skip:
                continue
            skip.append(index.row())
        skip = reversed(sorted(skip))

        for row in skip:
            self.hcmodel.removeRow(row)
            self.internalrealname.pop(row)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.buttons.setFocus()

        rows = self.hcmodel.rowCount()
        rowoffset = 0
        dedump = set()
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
            self.closecallback()

    def __cb(self, paths):
        for path in paths:
            self.internalrealname.insert(0, path)
            self.hcmodel.insertRow(0, [QStandardItem(path)])

    def __changed(self, item: QStandardItem, idx):
        self.internalrealname[item.row()] = self.candidates[idx]

    def click1(self):
        if self.candidates:
            self.internalrealname.insert(0, self.candidates[0])
            item = QStandardItem("")
            self.hcmodel.insertRow(0, [item])
            combo = LFocusCombo()
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


class listediterline(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, name, header, reflist, ispathsedit=None):
        super().__init__()
        self.setReadOnly(True)
        self.reflist = reflist
        self.setText("|".join(reflist))

        self.clicked.connect(
            functools.partial(
                listediter,
                self,
                name,
                header,
                reflist,
                closecallback=self.callback,
                ispathsedit=ispathsedit,
            )
        )

    def callback(self):
        self.setText("|".join(self.reflist))

    def mousePressEvent(self, e):
        self.clicked.emit()
        super().mousePressEvent(e)


def openfiledirectory(directory, multi, edit, isdir, filter1="*.*", callback=None):
    if isdir:
        f = QFileDialog.getExistingDirectory(directory=directory)
        res = f
    else:
        if multi:
            f = QFileDialog.getOpenFileNames(directory=directory, filter=filter1)
        else:
            f = QFileDialog.getOpenFileName(directory=directory, filter=filter1)
        res = f[0]

    if len(res) == 0:
        return
    if edit:
        edit.setText("|".join(res) if multi else res)
    if callback:
        callback(res)


def getsimplepatheditor(
    text=None,
    multi=False,
    isdir=False,
    filter1="*.*",
    callback=None,
    useiconbutton=False,
    reflist=None,
    name=None,
    header=None,
):
    lay = QHBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)

    if multi:
        e = listediterline(
            name, header, reflist, dict(isdir=isdir, multi=False, filter1=filter1)
        )
        lay.addWidget(e)
    else:
        e = QLineEdit(text)
        e.setReadOnly(True)
        if useiconbutton:
            bu = getIconButton(icon="fa.gear")
            clear = getIconButton(icon="fa.remove")
        else:
            bu = LPushButton("选择" + ("文件夹" if isdir else "文件"))
            clear = LPushButton("清除")
        bu.clicked.connect(
            functools.partial(
                openfiledirectory,
                text,
                multi,
                e,
                isdir,
                "" if isdir else filter1,
                callback,
            )
        )

        def __(_cb, _e):
            _cb("")
            _e.setText("")

        clear.clicked.connect(functools.partial(__, callback, e))
        lay.addWidget(e)
        lay.addWidget(bu)
        lay.addWidget(clear)
    return lay


class pixmapviewer(QWidget):
    tolastnext = pyqtSignal(int)

    def __init__(self, p=None) -> None:
        super().__init__(p)
        self.pix = None
        self._pix = None

    def showpixmap(self, pix: QPixmap):
        pix.setDevicePixelRatio(self.devicePixelRatioF())
        self.pix = pix
        self._pix = None
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
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self._pix)
        return super().paintEvent(e)


class statusbutton(QPushButton):
    statuschanged = pyqtSignal(int)

    def __init__(self, icons, colors):
        super().__init__()
        self.idx = 0
        self.icons = icons
        self.colors = colors
        self.clicked.connect(self.setChecked)
        self.seticon()

    def seticon(self):
        color = QColor(self.colors[self.idx])
        if not self.isEnabled():
            color = disablecolor(color)
        icon = qtawesome.icon(self.icons[self.idx], color=color)
        self.setIcon(icon)

    def setChecked(self, a0):
        super().setChecked(a0)
        self.idx += 1
        self.idx %= 2
        self.statuschanged.emit(self.idx)
        self.seticon()

    def setEnabled(self, _):
        super().setEnabled(_)
        self.seticon()


class LIconLabel(LLabel):
    def __init__(self, *argc):
        super().__init__(*argc)
        self._icon = QIcon()
        self._size = QSize()

    def setIcon(self, icon: QIcon):
        self._icon = icon
        self.update()

    def setIconSize(self, size: QSize):
        self._size = size
        self.update()

    def paintEvent(self, a0: QPaintEvent) -> None:

        painter = QPainter(self)
        if self._size.isEmpty():
            size = self.size()
        else:
            size = self._size
        rect = QRect(
            (self.width() - size.width()) // 2,
            (self.height() - size.height()) // 2,
            size.width(),
            size.height(),
        )
        self._icon.paint(
            painter,
            rect,
            Qt.AlignmentFlag.AlignCenter,
            QIcon.Mode.Normal,
            QIcon.State.On,
        )


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
        ll.removeItem(item)
        w = item.widget()
        if w:
            w.deleteLater()
            continue
        l = item.layout()
        if l:
            clearlayout(l)
            l.deleteLater()
            continue
