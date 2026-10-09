from qtsymbols import *
import windows, NativeUtils, gobject, threading
from myutils.config import globalconfig
from myutils.hwnd import safepixmap
from gui.dynalang import LAction, LDialog, LFormLayout
from gui.usefulwidget import getspinbox, ColorButton
from gui.ocrtranslationoverlay import (
    OCRTranslationOverlay,
    OCRCaptureSnapshot,
    suspend_ocr_capture,
)
from traceback import print_exc
from myutils.wrapper import Singleton_activate


class SideGrip(QWidget):
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == Qt.Edge.LeftEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.Edge.TopEdge:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.Edge.RightEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, _):
        self.mousePos = None


class Mainw(QMainWindow):
    _gripSize = 8

    def __init__(self, x):
        QMainWindow.__init__(self, x)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | self.windowFlags())
        self.sideGrips = [
            SideGrip(self, Qt.Edge.LeftEdge),
            SideGrip(self, Qt.Edge.TopEdge),
            SideGrip(self, Qt.Edge.RightEdge),
            SideGrip(self, Qt.Edge.BottomEdge),
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QSizeGrip(self) for i in range(4)]
        for s in self.cornerGrips:
            s.setStyleSheet("background-color: transparent;")

    @property
    def gripSize(self):
        return self._gripSize

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(
            self.gripSize, self.gripSize, -self.gripSize, -self.gripSize
        )

        # top left
        self.cornerGrips[0].setGeometry(QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QRect(outRect.topRight(), inRect.topRight()).normalized()
        )
        # bottom right
        self.cornerGrips[2].setGeometry(
            QRect(inRect.bottomRight(), outRect.bottomRight())
        )
        # bottom left
        self.cornerGrips[3].setGeometry(
            QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized()
        )

        # left edge
        self.sideGrips[0].setGeometry(0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(), inRect.top(), self.gripSize, inRect.height()
        )
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(), inRect.width(), self.gripSize
        )

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.updateGrips()


@Singleton_activate
class yangshisetting(LDialog):
    def __init__(self, p):
        super().__init__(p, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("样式")
        form = LFormLayout(self)
        spin = getspinbox(
            0,
            1,
            globalconfig,
            "ocrrangealpha",
            default=0.1,
            double=True,
            callback=gobject.base.textsource.setstyle,
        )
        form.addRow("不透明度", spin)
        spin = getspinbox(
            1,
            20,
            globalconfig,
            "ocrrangewidth",
            default=1,
            callback=gobject.base.textsource.setstyle,
        )
        form.addRow("宽度", spin)
        colorbtn = ColorButton(
            self,
            globalconfig,
            "ocrrangecolor",
            callback=gobject.base.textsource.setstyle,
            default="#000000",
        )
        form.addRow("颜色", colorbtn)
        self.show()


class rangeadjust(Mainw):
    closesignal = pyqtSignal()
    traceoffsetsignal = pyqtSignal(QPoint)
    overlaytranslationsignal = pyqtSignal(object)

    @property
    def isfocus(self):
        return self.__isfocus

    @isfocus.setter
    def isfocus(self, f):
        def cleanother():
            for r in self.ranges:
                range_ui: "rangeadjust" = r.range_ui
                if range_ui != self:
                    if range_ui.__isfocus:
                        range_ui.__isfocus = False
                        range_ui.setstyle()

        if sum(r.range_ui._rect.isValid() for r in self.ranges) > 1:
            if f:
                cleanother()
                self.__isfocus = True
            else:
                self.__isfocus = False
        else:
            cleanother()
            self.__isfocus = False
        self.setstyle()

    def mouseDoubleClickEvent(self, a0):
        self.isfocus = not self.isfocus
        gobject.base.translation_ui.startTranslater()
        return super().mouseDoubleClickEvent(a0)

    def starttrace(self, pos):
        self.tracepos = self.geometry().topLeft()
        self.traceposstart = pos

    def traceoffset(self, curr: QPoint):
        hwnd = gobject.base.hwnd
        if not hwnd:
            self.tracepos = QPoint()
            return
        if windows.MonitorFromWindow(hwnd) != windows.MonitorFromWindow(
            int(self.winId())
        ):
            self.tracepos = QPoint()
            return
        keystate = windows.GetKeyState(windows.VK_LBUTTON)
        if keystate < 0 and windows.GetForegroundWindow() == int(self.winId()):
            self.tracepos = QPoint()
            return
        if self._isTracking:
            self.tracepos = QPoint()
            return
        _geo = self.geometry()
        if self.tracepos.isNull():
            self.tracepos = _geo.topLeft()
            self.traceposstart = curr
        target = self.tracepos + (curr - self.traceposstart) * self.devicePixelRatioF()
        self.setGeometry(QRect(target.x(), target.y(), _geo.width(), _geo.height()))

    def rect(self):
        geo = self.geometry()
        return QRectF(
            0,
            0,
            geo.width() / self.devicePixelRatioF(),
            geo.height() / self.devicePixelRatioF(),
        ).toRect()

    def __init__(self, parent, ranges):
        super().__init__(parent)
        self._ready = False
        self.ocr_source_lock = threading.RLock()
        self._ocr_overlay_revision = 0
        self._ocr_overlay_original = None
        self.translation_overlay = None
        self._mousetransp = False
        self.__isfocus = False
        self.ranges: list = ranges
        self.traceoffsetsignal.connect(self.traceoffset)
        self.label = QLabel(self)
        self.setstyle()
        self.closesignal.connect(self.close)
        self.tracepos = QPoint()
        self.drag_label = QLabel(self)
        self.drag_label.setGeometry(0, 0, 4000, 2000)
        self._isTracking = False
        self._rect = QRect()
        self._styledlg = None
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        for s in self.cornerGrips:
            s.raise_()
        windows.WindowFocus.giveup(self.winId())
        self.translation_overlay = OCRTranslationOverlay(self)
        self.overlaytranslationsignal.connect(self.translation_overlay.receive)
        self._ready = True
        self._updateWindowRgn()

    def showmenu(self, _):
        menu = QMenu(self)
        menu.setWindowFlags(
            menu.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        multiregion = LAction("多重区域模式", menu)
        multiregion.setCheckable(True)
        multiregion.setChecked(globalconfig.get("multiregion", False))
        menu.addAction(multiregion)
        focus = None
        if globalconfig.get("multiregion", False):
            focus = LAction("聚焦", menu)
            focus.setCheckable(True)
            focus.setChecked(self.isfocus)
            menu.addAction(focus)
        menu.addSeparator()
        style = LAction("样式", menu)
        menu.addAction(style)
        overlay = LAction("原地显示翻译", menu)
        overlay.setCheckable(True)
        overlay.setChecked(globalconfig.get("ocr_translation_overlay", False))
        menu.addAction(overlay)
        close = LAction("关闭", menu)
        mousetransp = LAction("鼠标穿透窗口", menu)
        mousetransp.setCheckable(True)
        mousetransp.setChecked(self._mousetransp)
        menu.addAction(mousetransp)
        menu.addAction(close)
        with suspend_ocr_capture():
            action = menu.exec(QCursor.pos())
        if action == multiregion:
            checked = multiregion.isChecked()
            globalconfig["multiregion"] = checked
            if not checked:
                gobject.base.textsource.leaveone()
        elif action == overlay:
            globalconfig["ocr_translation_overlay"] = overlay.isChecked()
            # 同步 OCR 设置页里的开关
            gobject.base.ocr_inplace_switch.emit(overlay.isChecked())
            gobject.base.textsource.setstyle()
        elif action == style:
            yangshisetting(self)
        elif focus is not None and action == focus:
            self.isfocus = focus.isChecked()
            gobject.base.translation_ui.startTranslater()
        elif action == mousetransp:
            self.setmousetransp(mousetransp.isChecked())
        elif action == close:
            self._set_ocr_rect(QRect())
            self.isfocus = False
            self.close()

    def _updateWindowRgn(self):
        hwnd = int(self.winId())
        if not hwnd:
            return
        # 鼠标穿透或透明度为 0 时，仅保留四条边框可响应鼠标，内部鼠标穿透。
        if self._mousetransp or globalconfig.get("ocrrangealpha", 0.1) == 0:
            geo = self.geometry()
            if geo.width() > 0 and geo.height() > 0:
                border = round(
                    max(
                        globalconfig.get("ocrrangewidth", 1),
                        self.gripSize,
                    )
                    * self.devicePixelRatioF()
                )
                windows.WindowRgn.set_frame(
                    hwnd, geo.width(), geo.height(), border
                )
        else:
            windows.WindowRgn.clear(hwnd)

    def setmousetransp(self, b):
        self._mousetransp = b
        if b:
            # 穿透模式下不显示悬停半透明高亮，避免边框内侧出现额外半透明带
            self.drag_label.setStyleSheet("background-color:none")
        if getattr(self, "_ready", False):
            self._updateWindowRgn()

    def setstyle(self):
        if self.translation_overlay is not None:
            self.translation_overlay.sync()
        self.label.setStyleSheet(
            " border:%spx solid %s; background-color: rgba(0,0,0, %s); border-radius:0;"
            % (
                globalconfig.get("ocrrangewidth", 1),
                "red" if self.isfocus else globalconfig.get("ocrrangecolor", "#000000"),
                1 / 255,
            )
        )
        if getattr(self, "_ready", False):
            self._updateWindowRgn()

    def capture_snapshot(self):
        # Called by workers; no native/Qt widget access under this lock.
        with self.ocr_source_lock:
            return OCRCaptureSnapshot(self._ocr_overlay_revision, self._rect.getRect())

    def remember_overlay_source(self, text, snapshot=None):
        # Validation and revision assignment must be atomic with selection edits.
        with self.ocr_source_lock:
            if snapshot is not None and snapshot != self.capture_snapshot():
                return None
            if text != self._ocr_overlay_original:
                self._ocr_overlay_original = text
                self._ocr_overlay_revision += 1
                self.overlaytranslationsignal.emit((self._ocr_overlay_revision, None, ""))
            return self._ocr_overlay_revision

    def invalidate_overlay(self):
        with self.ocr_source_lock:
            self._ocr_overlay_original = None
            self._ocr_overlay_revision += 1
            self.overlaytranslationsignal.emit((self._ocr_overlay_revision, None, ""))

    def _set_ocr_rect(self, rect):
        with self.ocr_source_lock:
            if rect != self._rect:
                self._rect = QRect(rect)
                self.invalidate_overlay()

    def showEvent(self, event):
        super().showEvent(event)
        if self.translation_overlay is not None:
            self.translation_overlay.sync()

    def hideEvent(self, event):
        if self.translation_overlay is not None:
            self.translation_overlay.hide()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.invalidate_overlay()
        if self.translation_overlay is not None:
            self.translation_overlay.hide()
        super().closeEvent(event)

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            _geo = self.geometry()
            _geo.translate(self._endPos)
            self.setGeometry(_geo)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.pos().x(), e.pos().y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def rectoffset(self, rect: QRect):
        r = round(globalconfig.get("ocrrangewidth", 1) * self.devicePixelRatioF())
        return rect.adjusted(r, r, -r, -r)

    def setGeometry(self, r: QRect):
        if r == self.geometry():
            return
        windows.MoveWindow(
            int(self.winId()), r.left(), r.top(), r.width(), r.height(), True
        )

    def geometry(self):
        rect = windows.GetWindowRect(int(self.winId()))
        return QRect(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])

    def moveEvent(self, _):
        if self._rect.isValid():
            self._set_ocr_rect(self.rectoffset(self.geometry()))
        if self.translation_overlay is not None:
            self.translation_overlay.sync()

    def enterEvent(self, _):
        if self._mousetransp:
            return
        self.drag_label.setStyleSheet(
            "background-color:rgba(0,0,0, {})".format(
                globalconfig.get("ocrrangealpha", 0.1)
            )
        )

    def leaveEvent(self, _):
        if self._mousetransp:
            return
        self.drag_label.setStyleSheet("background-color:none")

    def resizeEvent(self, a0):
        self.label.setGeometry(self.rect())
        if self._rect.isValid():
            self._set_ocr_rect(self.rectoffset(self.geometry()))
        if getattr(self, "_ready", False):
            self._updateWindowRgn()
        if self.translation_overlay is not None:
            self.translation_overlay.sync()
        super().resizeEvent(a0)

    def getrect(self):
        with self.ocr_source_lock:
            return QRect(self._rect)

    def setrect(self, rect: QRect, show=True):
        if rect != self._rect:
            self.invalidate_overlay()
        self.tracepos = QPoint()
        if rect.isValid():
            if show:
                self.show()
            r = round(globalconfig.get("ocrrangewidth", 1) * self.devicePixelRatioF())
            self.setGeometry(rect.adjusted(-r, -r, r, r))
        self._set_ocr_rect(rect)
        if self.translation_overlay is not None:
            self.translation_overlay.sync()
        # 由于使用movewindow而非qt函数，导致内部执行绪有问题。


def rangeselct_function(callback, parent: QWidget = None, hideshow=False):
    p = gobject.base.translation_ui
    if hideshow:
        currpos = p.pos()
        _save = {}
        # hide会有隐藏动画残影
        if parent:
            currpos2 = parent.pos()
            parent.move(-9999, -9999)
        p.move(-9999, -9999)
        try:
            gobject.base.textsource.pause_recognition()
            for _ in gobject.base.textsource.ranges:
                _save[_] = _.range_ui.getrect()
                _.range_ui.setrect(QRect(-9999, -9999, 1, 1), show=False)
        except:
            print_exc()

    def reset():
        if not hideshow:
            return
        gobject.base.translation_ui.move(currpos)
        if parent:
            parent.move(currpos2)
        try:
            for _ in gobject.base.textsource.ranges:
                _.range_ui.setrect(_save[_], show=False)
            gobject.base.textsource.resume_recognition()
        except:
            print_exc()

    p = p.winid if p.isVisible() else None
    color = QColor(globalconfig.get("ocrrangecolor", "#000000"))

    called = []

    def __cb(x1, y1, x2, y2, xoff, yoff, ptr, size):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        pix = safepixmap(ptr[:size]).copy(x1, y1, x2 - x1, y2 - y1).toImage()
        reset()
        rect = QRect(x1 + xoff, y1 + yoff, x2 - x1, y2 - y1)
        callback(rect, pix)
        called.append(0)

    cb = NativeUtils.CreateSelectRangeWindow_CB(__cb)
    NativeUtils.CreateSelectRangeWindow(
        p,
        globalconfig.get("ocrselectalpha", 0.3),
        color.red(),
        color.green(),
        color.blue(),
        globalconfig.get("ocrrangewidth", 1),
        cb,
    )
    if not called:
        reset()
        callback(QRect(), None)
