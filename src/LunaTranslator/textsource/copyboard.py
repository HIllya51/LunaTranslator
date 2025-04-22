from textsource.textsourcebase import basetext
from myutils.config import globalconfig
import NativeUtils, gobject


class copyboard(basetext):

    def end(self):
        NativeUtils.ClipBoardListenerStop()
        gobject.baseobject.translation_ui.clipboardcallback.disconnect()

    def __callback(self, ismy, string):
        if globalconfig["excule_from_self"] and ismy:
            return
        self.dispatchtext(string)

    def init(self) -> None:
        self.startsql(gobject.gettranslationrecorddir("0_copy.sqlite"))
        gobject.baseobject.translation_ui.clipboardcallback.connect(self.__callback)
        NativeUtils.ClipBoardListenerStart()

    def gettextonce(self):
        return NativeUtils.ClipBoard.text
