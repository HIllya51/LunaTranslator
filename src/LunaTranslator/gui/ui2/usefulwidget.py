from qtsymbols import *
import functools
import windows
from myutils.wrapper import tryprint
from gui.ui2.dynalang import LElaWindow


class saveposwindow(LElaWindow):
    screengeochanged = pyqtSignal()

    def __init__(self, parent, poslist=None, flags=None) -> None:
        LElaWindow.__init__(self, parent)
        if flags:
            self.setWindowFlags(self.windowFlags() | flags)

        self.poslist = poslist
        if self.poslist:
            self.setGeometry(QRect(poslist[0], poslist[1], poslist[2], poslist[3]))
        self.adjust_window_to_screen_bounds(self.screen().geometry())
        self.___firstshow = True

    def showEvent(self, a0):
        if self.___firstshow:
            self.___firstshow = False
            self.windowHandle().screenChanged.connect(self.__screenChanged)
            self.__screenChanged(self.screen())
        return super().showEvent(a0)

    @tryprint
    def _changed(self, _id: str, geo: QRect):
        try:
            if _id != self.screen().serialNumber():
                return
        except:
            pass
        self.adjust_window_to_screen_bounds(geo)
        self.screengeochanged.emit()

    @tryprint
    def __screenChanged(self, screen: QScreen):
        screen.geometryChanged.connect(
            functools.partial(self._changed, screen.serialNumber())
        )

    @tryprint
    def adjust_window_to_screen_bounds(self, screen_rect: QRect):
        window_rect = self.geometry()
        new_x = window_rect.x()
        new_y = window_rect.y()
        new_width = window_rect.width()
        new_height = window_rect.height()

        if new_width > screen_rect.width():
            new_width = screen_rect.width()
        if new_height > screen_rect.height():
            new_height = screen_rect.height()
        if new_x + new_width > screen_rect.right() + 1:
            new_x = screen_rect.right() + 1 - new_width
        if new_y + new_height > screen_rect.bottom() + 1:
            new_y = screen_rect.bottom() + 1 - new_height
        if new_x < screen_rect.left():
            new_x = screen_rect.left()
        if new_y < screen_rect.top():
            new_y = screen_rect.top()

        new_window_rect = QRect(new_x, new_y, new_width, new_height)
        if new_window_rect != window_rect:
            self.setGeometry(new_window_rect)

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
