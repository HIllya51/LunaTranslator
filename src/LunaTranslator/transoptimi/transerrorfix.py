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
            "翻译结果修正",
            ["正则", "转义", "翻译", "替换"],
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):

        if "transerrorfix" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["transerrorfix"] = []
        noundictconfigdialog1(
            parent_window,
            savehook_new_data[gameuid]["transerrorfix"],
            "翻译结果修正_-_[[{}]]".format(savehook_new_data[gameuid]["title"]),
            ["正则", "转义", "翻译", "替换"],
        ).setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))

    def process_after(self, res, _):
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
            gameuid = gobject.base.gameuid
            return savehook_new_data[gameuid].get("transerrorfix", [])
        elif which == 3:
            gameuid = gobject.base.gameuid
            return (
                savehook_new_data[gameuid].get("transerrorfix", [])
                + transerrorfixdictconfig["dict_v2"]
            )
