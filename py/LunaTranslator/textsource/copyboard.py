from textsource.textsourcebase import basetext
from myutils.config import globalconfig
import gobject
from qtsymbols import *


class copyboard(basetext):

    def end(self):
        QApplication.clipboard().disconnect()

    def __callback(self):
        clipboard = QApplication.clipboard()
        if globalconfig["excule_from_self"] and clipboard.ownsClipboard():
            return
        self.dispatchtext(clipboard.text("plain")[0])

    def init(self) -> None:
        self.startsql(gobject.gettranslationrecorddir("0_copy.sqlite"))
        QApplication.clipboard().dataChanged.connect(self.__callback)

    def gettextonce(self):
        return QApplication.clipboard().text("plain")[0]
