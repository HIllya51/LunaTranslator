from myutils.config import transerrorfixdictconfig, savehook_new_data
from myutils.utils import parsemayberegexreplace, postusewhich
from gui.inputdialog import noundictconfigdialog1
import gobject
from myutils.config import get_launchpath
from myutils.hwnd import getExeIcon


class Process:
    @staticmethod
    def get_setting_window(parent_window):
        return noundictconfigdialog1(
            parent_window,
            transerrorfixdictconfig["dict_v2"],
            "翻译结果修正_设置",
            ["正则",'转义', "翻译", "替换"],
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):

        noundictconfigdialog1(
            parent_window,
            savehook_new_data[gameuid]["transerrorfix"],
            "翻译结果修正_-_" + savehook_new_data[gameuid]["title"],
            ["正则",'转义', "翻译", "替换"],
        ).setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))

    def process_after(self, res, mp1):
        res = parsemayberegexreplace(self.usewhich(), res)
        return res

    @property
    def using_X(self):
        return postusewhich("transerrorfix") != 0

    def usewhich(self) -> dict:
        which = postusewhich("transerrorfix")
        if which == 1:
            return transerrorfixdictconfig["dict_v2"]
        elif which == 2:
            gameuid = gobject.baseobject.gameuid
            return savehook_new_data[gameuid]["transerrorfix"]
        elif which == 3:
            gameuid = gobject.baseobject.gameuid
            return (
                savehook_new_data[gameuid]["transerrorfix"]
                + transerrorfixdictconfig["dict_v2"]
            )
