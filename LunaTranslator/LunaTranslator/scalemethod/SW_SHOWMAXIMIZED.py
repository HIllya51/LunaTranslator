from scalemethod.base import scalebase
from winsharedutils import letfullscreen, recoverwindow


class Method(scalebase):
    def changestatus(self, hwnd, full):
        if full:
            self.savewindowstatus = letfullscreen(hwnd)
        else:
            recoverwindow(hwnd, self.savewindowstatus)
        return True