from myutils.config import globalconfig, savehook_new_data, get_launchpath
from myutils.utils import postusewhich, parsemayberegexreplace
from gui.inputdialog import noundictconfigdialog1
import gobject
from myutils.hwnd import getExeIcon


class Process:

    @staticmethod
    def get_setting_window(parent_window):
        return (
            noundictconfigdialog1(
                parent_window,
                globalconfig["global_namemap2"],
                "专有名词翻译_直接替换",
                ["正则", "转义", "原文", "翻译"],
            ),
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):

        if "namemap2" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["namemap2"] = []
        noundictconfigdialog1(
            parent_window,
            savehook_new_data[gameuid]["namemap2"],
            "专有名词翻译_直接替换_-_[[{}]]".format(savehook_new_data[gameuid]["title"]),
            ["正则", "转义", "原文", "翻译"],
        ).setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))

    @property
    def using_X(self):
        return postusewhich("vndbnamemap") != 0

    def usewhich(self) -> dict:
        which = postusewhich("vndbnamemap")
        if which == 1:
            return globalconfig["global_namemap2"]
        elif which == 2:
            gameuid = gobject.baseobject.gameuid
            return savehook_new_data[gameuid].get("namemap2", [])
        elif which == 3:
            gameuid = gobject.baseobject.gameuid
            return (
                savehook_new_data[gameuid].get("namemap2", [])
                + globalconfig["global_namemap2"]
            )

    def process_before(self, s):

        namemap = self.usewhich()
        s = parsemayberegexreplace(namemap, s)
        return s, {}
