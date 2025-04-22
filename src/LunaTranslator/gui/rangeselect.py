from qtsymbols import *
import windows, NativeUtils, gobject
from myutils.config import globalconfig
from gui.dynalang import LAction
from traceback import print_exc


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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None


class Mainw(QMainWindow):
    _gripSize = 8

    def __init__(self, x):
        QMainWindow.__init__(self, x)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

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
            s.setStyleSheet(""" background-color: transparent;  """)

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
        close = LAction("关闭", menu)
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
        r = int(globalconfig["ocrrangewidth"] * r)
        _ = [(rect.left() + r, rect.top() + r), (rect.right() - r, rect.bottom() - r)]
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

    def closeEvent(self, a0):
        self.deleteLater()
        windows.SetForegroundWindow(self.originhwnd)
        return super().closeEvent(a0)

    def __init__(self, parent=None):

        super(rangeselect, self).__init__(parent)
        self.is_drawing = False
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
            NativeUtils.MaximumWindow(int(self.winId()))
        self.once = True
        self.is_drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.__start = None
        self.__end = None
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
            NativeUtils.MaximumWindow(int(self.backlabel.winId()))
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
            self.end_point = self.start_point = event.pos()
            self.is_drawing = True
            self.__start = self.__end = windows.GetCursorPos()

    def mouseMoveEvent(self, event):

        if not self.is_drawing:
            self.is_drawing = True
            self.end_point = self.start_point = event.pos()
            self.__start = self.__end = windows.GetCursorPos()
        else:
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


class rangeselect_1(QMainWindow):
    def __init__(self, p, xx):

        self.is_drawing = False
        super(rangeselect_1, self).__init__(p)
        self.xx = xx
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.backlabel = QLabel(self)
        self.backlabel.move(0, 0)
        self.backlabel2 = QLabel(self)
        self.backlabel2.move(0, 0)
        self.rectlabel = QLabel(self)
        # self.setWindowOpacity(0.5)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def reset(self):
        screen = QApplication.primaryScreen()
        self.setGeometry(QRect(QPoint(0, 0), screen.size()))

        screen_geometry = screen.geometry()
        if self.xx:
            screenshot = screen.grabWindow(
                0,
                screen_geometry.x(),
                screen_geometry.y(),
                screen_geometry.width(),
                screen_geometry.height(),
            )
            self.screenshot = screenshot
            self.backlabel.setPixmap(screenshot)
        self.once = True
        self.is_drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.rectlabel.resize(0, 0)
        self.rectlabel.setStyleSheet(
            " border:%spx solid %s; background-color: rgba(0,0,0, 0)"
            % (globalconfig["ocrrangewidth"], globalconfig["ocrrangecolor"])
        )
        self.backlabel2.setStyleSheet(
            "background-color: rgba(255,255,255, %s)" % globalconfig["ocrselectalpha"]
        )

    def resizeEvent(self, e: QResizeEvent):
        self.backlabel.resize(e.size())
        self.backlabel2.resize(e.size())

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
            self.end_point = self.start_point = event.pos()
            self.is_drawing = True

    def mouseMoveEvent(self, event):

        if not self.is_drawing:
            self.is_drawing = True
            self.end_point = self.start_point = event.pos()
        else:
            self.end_point = event.pos()
            self.update()

    def getRange(self):
        x1, y1, x2, y2 = (
            self.start_point.x() * self.devicePixelRatioF(),
            self.start_point.y() * self.devicePixelRatioF(),
            self.end_point.x() * self.devicePixelRatioF(),
            self.end_point.y() * self.devicePixelRatioF(),
        )
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        return ((int(x1), int(y1)), (int(x2), int(y2)))

    def callbackfunction(self, event):
        if not self.once:
            return
        self.once = False
        self.end_point = event.pos()
        self.close()
        try:
            (x1, y1), (x2, y2) = self.getRange()
            img = None
            if self.xx and (x1 != x2 and y1 != y2):
                img = self.screenshot.copy(
                    QRect(QPoint(x1, y1), QPoint(x2, y2))
                ).toImage()
            self.callback(self.getRange(), img)
        except:
            print_exc()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callbackfunction(event)

    def closeEvent(self, a0):
        self.deleteLater()
        windows.SetForegroundWindow(self.originhwnd)
        return super().closeEvent(a0)


def rangeselct_function(callback, x=True):
    if len(QApplication.screens()) == 1:
        screen_shot_ui = rangeselect_1(gobject.baseobject.translation_ui, x)
    else:
        screen_shot_ui = rangeselect(gobject.baseobject.translation_ui)
    screen_shot_ui.originhwnd = windows.GetForegroundWindow()
    screen_shot_ui.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
    screen_shot_ui.show()
    screen_shot_ui.reset()
    screen_shot_ui.callback = callback
    windows.SetFocus(int(screen_shot_ui.winId()))
