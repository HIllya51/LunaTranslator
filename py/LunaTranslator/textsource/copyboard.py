from textsource.textsourcebase import basetext
from myutils.config import globalconfig
import winsharedutils, gobject


class copyboard(basetext):

    def end(self):
        winsharedutils.clipboard_callback_stop(self.__hwnd)

    def __callback(self, string, ismy):
        if globalconfig["excule_from_self"] and ismy:
            return
        self.dispatchtext(string)

    def init(self) -> None:
        self.startsql(gobject.gettranslationrecorddir("0_copy.sqlite"))
        self.__ref = winsharedutils.clipboard_callback_type(self.__callback)
        self.__hwnd = winsharedutils.clipboard_callback(self.__ref)

    def gettextonce(self):
        return winsharedutils.clipboard_get()
