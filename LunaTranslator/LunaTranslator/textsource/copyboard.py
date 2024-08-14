from textsource.textsourcebase import basetext
from myutils.config import globalconfig
import winsharedutils, queue


class copyboard(basetext):

    def end(self):
        winsharedutils.clipboard_callback_stop(self.__hwnd)
        super().end()

    def __callback(self, string, ismy):
        if globalconfig["excule_from_self"] and ismy:
            return
        return self.__queue.put(string)

    def __init__(self) -> None:
        self.__ref = winsharedutils.clipboard_callback_type(self.__callback)
        self.__hwnd = winsharedutils.clipboard_callback(self.__ref)
        self.__queue = queue.Queue()
        super(copyboard, self).__init__("0", "copy")

    def gettextthread(self):
        return self.__queue.get()

    def gettextonce(self):
        return winsharedutils.clipboard_get()
