from myutils.config import transerrorfixdictconfig
from myutils.utils import parsemayberegexreplace
from gui.inputdialog import noundictconfigdialog1


class Process:
    @staticmethod
    def get_setting_window(parent_window):
        return noundictconfigdialog1(
            parent_window,
            transerrorfixdictconfig["dict_v2"],
            "翻译结果替换设置",
            ["正则", "翻译", "替换"],
        )

    def process_after(self, res, mp1):
        res = parsemayberegexreplace(transerrorfixdictconfig["dict_v2"], res)
        return res
