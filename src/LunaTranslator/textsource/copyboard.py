from textsource.textsourcebase import basetext
from myutils.config import globalconfig
import winsharedutils, gobject


class copyboard(basetext):

    def end(self):
        winsharedutils.stopclipboardlisten()
        gobject.baseobject.translation_ui.clipboardcallback.disconnect()

    def __callback(self, ismy, string):
        if globalconfig["excule_from_self"] and ismy:
            return
        if gobject.baseobject.freezeclipboard:
            gobject.baseobject.freezeclipboard = False
            return
        self.dispatchtext(string)

    def init(self) -> None:
        gobject.baseobject.freezeclipboard = False
        self.startsql(gobject.gettranslationrecorddir("0_copy.sqlite"))
        gobject.baseobject.translation_ui.clipboardcallback.connect(self.__callback)
        winsharedutils.startclipboardlisten()

    def gettextonce(self):
        return winsharedutils.clipboard_get()
