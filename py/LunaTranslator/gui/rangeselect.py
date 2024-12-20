from qtsymbols import *
import windows, winsharedutils, gobject
from myutils.config import globalconfig
from gui.resizeablemainwindow import Mainw
from gui.dynalang import LAction
from traceback import print_exc


class rangeadjust(Mainw):
    closesignal = pyqtSignal()
    traceoffsetsignal = pyqtSignal(QPoint)

    def starttrace(self, pos):
        self.tracepos = self.geometry().topLeft()
        self.traceposstart = pos

    def traceoffset(self, curr):
        hwnd = gobject.baseobject.hwnd
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
        self.setGeometry(
            target.x(),
            target.y(),
            _geo.width(),
            _geo.height(),
        )

    def rect(self):
        geo = self.geometry()
        return QRectF(
            0,
            0,
            geo.width() / self.devicePixelRatioF(),
            geo.height() / self.devicePixelRatioF(),
        ).toRect()

    def __init__(self, parent):
        super(rangeadjust, self).__init__(parent)
        self.traceoffsetsignal.connect(self.traceoffset)
        self.label = QLabel(self)
        self.setstyle()
        self.closesignal.connect(self.close)
        self.tracepos = QPoint()
        self.drag_label = QLabel(self)
        self.drag_label.setGeometry(0, 0, 4000, 2000)
        self._isTracking = False
        self._rect = None
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

    def showmenu(self, p):
        menu = QMenu(self)
        close = LAction(("关闭"))
        menu.addAction(close)
        action = menu.exec(QCursor.pos())
        if action == close:
            self._rect = None
            self.close()

    def setstyle(self):
        self.label.setStyleSheet(
            " border:%spx solid %s; background-color: rgba(0,0,0, %s); border-radius:0;"
            % (globalconfig["ocrrangewidth"], globalconfig["ocrrangecolor"], 1 / 255)
        )

    def mouseMoveEvent(self, e):
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            _geo = self.geometry()
            _geo.translate(self._endPos)
            self.setGeometry(*_geo.getRect())

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def rectoffset(self, rect):
        r = self.devicePixelRatioF()
        _ = [
            (
                rect.left() + int(globalconfig["ocrrangewidth"] * r),
                rect.top() + int(globalconfig["ocrrangewidth"] * r),
            ),
            (
                rect.right() - int(globalconfig["ocrrangewidth"] * r),
                rect.bottom() - int(globalconfig["ocrrangewidth"] * r),
            ),
        ]
        return _

    def setGeometry(self, x, y, w, h):
        windows.MoveWindow(int(self.winId()), x, y, w, h, True)

    def geometry(self):
        rect = windows.GetWindowRect(int(self.winId()))
        return QRect(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])

    def moveEvent(self, e):
        if self._rect:
            self._rect = self.rectoffset(self.geometry())

    def enterEvent(self, QEvent):
        self.drag_label.setStyleSheet("background-color:rgba(0,0,0, 0.1)")

    def leaveEvent(self, QEvent):
        self.drag_label.setStyleSheet("background-color:none")

    def resizeEvent(self, a0):

        self.label.setGeometry(0, 0, self.width(), self.height())
        if self._rect:
            self._rect = self.rectoffset(self.geometry())
        super(rangeadjust, self).resizeEvent(a0)

    def getrect(self):
        return self._rect

    def setrect(self, rect):
        self.tracepos = QPoint()
        if rect:
            (x1, y1), (x2, y2) = rect
            self.show()
            r = self.devicePixelRatioF()
            self.setGeometry(
                x1 - int(globalconfig["ocrrangewidth"] * r),
                y1 - int(globalconfig["ocrrangewidth"] * r),
                x2 - x1 + int(2 * globalconfig["ocrrangewidth"] * r),
                y2 - y1 + int(2 * globalconfig["ocrrangewidth"] * r),
            )
        self._rect = rect
        # 由于使用movewindow而非qt函数，导致内部执行绪有问题。


class rangeselect(QMainWindow):
    def __init__(self, parent=None):

        super(rangeselect, self).__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.backlabel = QLabel(self)
        self.rectlabel = QLabel(self)
        self.backlabel.move(0, 0)
        # self.setWindowOpacity(0.5)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.reset()

    def reset(self):
        if len(QApplication.screens()) == 1:
            self.setGeometry(QRect(QPoint(0, 0), QApplication.screens()[0].size()))
        else:
            winsharedutils.maximum_window(int(self.winId()))
        self.once = True
        self.is_drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.__start = None
        self.__end = None
        self.startauto = False
        self.rectlabel.resize(0, 0)
        self.rectlabel.setStyleSheet(
            " border:%spx solid %s; background-color: rgba(0,0,0, 0)"
            % (globalconfig["ocrrangewidth"], globalconfig["ocrrangecolor"])
        )
        self.backlabel.setStyleSheet(
            "background-color: rgba(255,255,255, %s)" % globalconfig["ocrselectalpha"]
        )

    def resizeEvent(self, e: QResizeEvent):
        if len(QApplication.screens()) == 1:
            pass
        else:
            winsharedutils.maximum_window(int(self.backlabel.winId()))
        self.backlabel.resize(e.size())

    def paintEvent(self, event):

        if self.is_drawing:

            pp = QPainter(self)
            pen = QPen(QColor(globalconfig["ocrrangecolor"]))
            pen.setWidth(globalconfig["ocrrangewidth"])
            pp.setPen(pen)
            _x1 = self.start_point.x()
            _y1 = self.start_point.y()
            _x2 = self.end_point.x()
            _y2 = self.end_point.y()
            _sp = QPoint(
                min(_x1, _x2) - globalconfig["ocrrangewidth"],
                min(_y1, _y2) - globalconfig["ocrrangewidth"],
            )
            _ep = QPoint(
                max(_x1, _x2) + globalconfig["ocrrangewidth"],
                max(_y1, _y2) + globalconfig["ocrrangewidth"],
            )
            self.rectlabel.setGeometry(QRect(_sp, _ep))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.once = False
            self.close()
        elif event.button() == Qt.MouseButton.LeftButton:
            if self.startauto:
                self.callbackfunction(event)
            else:
                self.end_point = self.start_point = event.pos()
                self.is_drawing = True
                self.__start = self.__end = windows.GetCursorPos()

    def mouseMoveEvent(self, event):

        if self.startauto and self.is_drawing == False:
            self.is_drawing = True
            self.end_point = self.start_point = event.pos()
            self.__start = self.__end = windows.GetCursorPos()
        if self.is_drawing:
            self.end_point = event.pos()
            self.__end = windows.GetCursorPos()
            self.update()

    def getRange(self):
        if self.__start is None:
            self.__start = self.__end
        x1, y1, x2, y2 = (
            self.__start.x,
            self.__start.y,
            self.__end.x,
            self.__end.y,
        )

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        return ((x1, y1), (x2, y2))

    def callbackfunction(self, event):
        if not self.once:
            return
        self.once = False
        self.end_point = event.pos()
        self.__end = windows.GetCursorPos()
        self.close()
        try:
            self.callback(self.getRange())
        except:
            print_exc()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callbackfunction(event)


screen_shot_ui = None


def rangeselct_function(callback, startauto):
    global screen_shot_ui
    if screen_shot_ui is not None:
        # 完全销毁旧的实例
        screen_shot_ui.deleteLater()
        screen_shot_ui = None

    screen_shot_ui = rangeselect()
    screen_shot_ui.show()
    screen_shot_ui.reset()
    screen_shot_ui.callback = callback
    windows.SetFocus(int(screen_shot_ui.winId()))
    screen_shot_ui.startauto = startauto
