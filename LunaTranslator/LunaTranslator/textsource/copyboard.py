import time
from textsource.textsourcebase import basetext
from myutils.config import globalconfig
import winsharedutils, os
import windows


class copyboard(basetext):
    def __init__(self) -> None:
        self.last_paste_str = ""

        super(copyboard, self).__init__("0", "copy")

    def gettextthread(self):

        time.sleep(0.1)
        paste_str = winsharedutils.clipboard_get()

        if self.last_paste_str != paste_str:
            self.last_paste_str = paste_str
            if (
                globalconfig["excule_from_self"]
                and windows.GetWindowThreadProcessId(windows.GetClipboardOwner())
                == os.getpid()
            ):
                return
            return paste_str

    def gettextonce(self):
        return winsharedutils.clipboard_get()
