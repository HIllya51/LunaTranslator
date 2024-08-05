from myutils.config import savehook_new_data, globalconfig
import gobject, json, functools
from traceback import print_exc
from gui.inputdialog import noundictconfigdialog1
from myutils.utils import postusewhich, parsemayberegexreplace


class Process:

    @staticmethod
    def get_setting_window(parent_window):
        return noundictconfigdialog1(
            parent_window,
            globalconfig["global_regexrepair"],
            "正则表达式替换",
            ["正则", "原文", "替换"],
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):

        noundictconfigdialog1(
            parent_window,
            savehook_new_data[gameuid]["regexrepair"],
            "正则表达式替换",
            ["正则", "原文", "替换"],
        )

    @property
    def using_X(self):
        return postusewhich("regexrepair") != 0

    def usewhich(self) -> dict:
        which = postusewhich("regexrepair")
        if which == 1:
            return globalconfig["global_regexrepair"]
        elif which == 2:
            gameuid = gobject.baseobject.textsource.gameuid
            return savehook_new_data[gameuid]["regexrepair"]
        elif which == 3:

            gameuid = gobject.baseobject.textsource.gameuid
            return (
                savehook_new_data[gameuid]["regexrepair"]
                + globalconfig["global_regexrepair"]
            )

    def process_before(self, s):

        return parsemayberegexreplace(self.usewhich(), s), {}
