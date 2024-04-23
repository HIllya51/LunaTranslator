from scalemethod.base import scalebase
import windows


class Method(scalebase):
    def changestatus(self, hwnd, full):
        windows.SetForegroundWindow(hwnd)
        windows.keybd_event(18, 0, 0, 0)  # alt
        windows.keybd_event(13, 0, 0, 0)  # enter

        windows.keybd_event(13, 0, windows.KEYEVENTF_KEYUP, 0)
        windows.keybd_event(18, 0, windows.KEYEVENTF_KEYUP, 0)
