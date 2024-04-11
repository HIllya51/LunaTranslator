from PyQt5.QtWidgets import QMenu, QApplication, QMainWindow, QLabel, QAction, QDialog
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent
from myutils.config import _TR
import gobject
from myutils.config import globalconfig
from gui.resizeablemainwindow import Mainw
import windows


class rangeadjust(Mainw):

    def __init__(self, parent):

        super(rangeadjust, self).__init__(parent)
        self.label = QLabel(self)
        self.setstyle()
        self.drag_label = QLabel(self)
        self.drag_label.setGeometry(0, 0, 4000, 2000)
        self._isTracking = False
        self._rect = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        for s in self.cornerGrips:
            s.raise_()

    def showmenu(self, p):
        menu = QMenu(self)
        close = QAction(_TR("关闭"))
        menu.addAction(close)
        action = menu.exec(self.mapToGlobal(p))
        if action == close:
            self._rect = None
            self.close()

    def setstyle(self):
        self.label.setStyleSheet(
            " border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"
            % (globalconfig["ocrrangewidth"], globalconfig["ocrrangecolor"])
        )

    def mouseMoveEvent(self, e):
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def rectoffset(self, rect):
        return [
            (
                rect.left() + globalconfig["ocrrangewidth"],
                rect.top() + globalconfig["ocrrangewidth"],
            ),
            (
                rect.right() - globalconfig["ocrrangewidth"],
                rect.bottom() - globalconfig["ocrrangewidth"],
            ),
        ]

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
        self._rect = rect
        if rect:
            (x1, y1), (x2, y2) = rect
            self.setGeometry(
                x1 - globalconfig["ocrrangewidth"],
                y1 - globalconfig["ocrrangewidth"],
                x2 - x1 + 2 * globalconfig["ocrrangewidth"],
                y2 - y1 + 2 * globalconfig["ocrrangewidth"],
            )
            self.show()


class rangeselct(QMainWindow):
    def __init__(self, parent):

        super(rangeselct, self).__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Tool
        )  # |Qt.WindowStaysOnTopHint  )
        self.rectlabel = QLabel(self)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def reset(self):
        # screens = QDesktopWidget().screenCount()
        # desktop = QDesktopWidget().screenGeometry(0)
        # for i in range(1, screens):
        #     desktop = desktop.united(QDesktopWidget().screenGeometry(i))
        desktop = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(desktop)
        self.rectlabel.resize(desktop.size())
        self.setCursor(Qt.CrossCursor)
        self.is_drawing = False
        self.setMouseTracking(True)
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.startauto = False
        self.clickrelease = False
        self.rectlabel.setStyleSheet(
            " border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"
            % (globalconfig["ocrrangewidth"], globalconfig["ocrrangecolor"])
        )

    def immediateend(self):
        try:

            self.close()

            self.callback(self.getRange())
        except:
            pass

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
        if event.button() == Qt.LeftButton:
            if self.clickrelease:
                self.clickrelease = False
                self.mouseReleaseEvent(event)
            else:
                self.start_point = event.pos()
                self.end_point = self.start_point
                self.is_drawing = True

    def mouseMoveEvent(self, event):

        if self.startauto and self.is_drawing == False:
            self.is_drawing = True
            self.end_point = self.start_point = event.pos()
            self.startauto = False
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()

    def getRange(self):
        start_point = self.mapToGlobal(self.start_point)
        end_point = self.mapToGlobal(self.end_point)
        x1, y1, x2, y2 = (
            start_point.x(),
            start_point.y(),
            end_point.x(),
            end_point.y(),
        )

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        return ((x1, y1), (x2, y2))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()

            self.close()
            self.callback(self.getRange())


screen_shot_ui = None


def rangeselct_function(parent, callback, clickrelease, startauto):
    global screen_shot_ui
    if screen_shot_ui is None:
        screen_shot_ui = rangeselct(parent)
    screen_shot_ui.reset()
    screen_shot_ui.show()
    screen_shot_ui.callback = callback
    windows.SetFocus(int(screen_shot_ui.winId()))

    screen_shot_ui.startauto = startauto
    screen_shot_ui.clickrelease = clickrelease


from myutils.wrapper import Singleton_close


@Singleton_close
class moveresizegame(QDialog):

    def __init__(self, parent, hwnd):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setWindowTitle("调整窗口  " + windows.GetWindowText(hwnd))
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint  )
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.5)

        self.setMouseTracking(True)

        self._isTracking = False

        self.hwnd = hwnd
        self.maxed = False
        if self.hwnd == 0:
            self.close()
        try:
            rect = windows.GetWindowRect(self.hwnd)
            if rect:
                self.setGeometry(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            self.show()
        except:
            self.close()

    def moveEvent(self, a0) -> None:
        rect = self.geometry()
        if self.isMaximized() == False:
            try:
                windows.MoveWindow(
                    self.hwnd,
                    rect.left(),
                    rect.top(),
                    rect.right() - rect.left(),
                    rect.bottom() - rect.top(),
                    False,
                )
            except:
                pass
        return super().moveEvent(a0)

    def closeEvent(self, a0) -> None:
        gobject.baseobject.moveresizegame = None
        return super().closeEvent(a0)

    def mouseMoveEvent(self, e):
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)
            rect = self.geometry()
            if self.isMaximized() == False:
                try:
                    windows.MoveWindow(
                        self.hwnd,
                        rect.left(),
                        rect.top(),
                        rect.right() - rect.left(),
                        rect.bottom() - rect.top(),
                        False,
                    )
                except:
                    pass

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def changeEvent(self, a0) -> None:
        if a0.type() == QEvent.WindowStateChange:
            try:
                if self.isMaximized():
                    windows.ShowWindow(self.hwnd, windows.SW_MAXIMIZE)
                else:
                    windows.ShowWindow(self.hwnd, windows.SW_SHOWNORMAL)
            except:
                pass

    def resizeEvent(self, a0):
        if self.isMaximized() == False:
            rect = self.geometry()
            try:
                windows.MoveWindow(
                    self.hwnd,
                    rect.left(),
                    rect.top(),
                    rect.right() - rect.left(),
                    rect.bottom() - rect.top(),
                    False,
                )
            except:
                pass
