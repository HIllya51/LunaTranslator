from textio.textsource.textsourcebase import basetext
from myutils.config import globalconfig
import NativeUtils, gobject


class copyboard(basetext):

    def end(self):
        NativeUtils.ClipBoardListenerStop()
        # 不需要disconnect。而且Qt6在结束时closeEvent里disconnect会谜之卡住最后的退出

    def __callback(self, ismy, string):
        if globalconfig["excule_from_self"] and ismy:
            return
        self.dispatchtext(string)

    def init(self) -> None:
        self.startsql(gobject.gettranslationrecorddir("0_copy.sqlite"))
        gobject.base.clipboardcallback.connect(self.__callback)
        NativeUtils.ClipBoardListenerStart()

    def gettextonce(self):
        return NativeUtils.ClipBoard.text
