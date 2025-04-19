from myutils.config import savehook_new_data, globalconfig
import gobject
from qtsymbols import *
from myutils.utils import postusewhich, case_insensitive_replace
from myutils.config import get_launchpath
from myutils.hwnd import getExeIcon
from gui.inputdialog import postconfigdialog_


class Process:
    @staticmethod
    def get_setting_window(parent_window):
        return postconfigdialog_(
            parent_window,
            globalconfig["noundictconfig_ex"],
            "专有名词翻译",
            ["原文", "翻译", "注释"],
            dictkeys=["src", "dst", "info"],
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):
        if "noundictconfig_ex" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["noundictconfig_ex"] = []
        postconfigdialog_(
            parent_window,
            savehook_new_data[gameuid]["noundictconfig_ex"],
            "专有名词翻译_-_[[{}]]".format(savehook_new_data[gameuid]["title"]),
            ["原文", "翻译", "注释"],
            dictkeys=["src", "dst", "info"],
        ).setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))

    @property
    def using_X(self):
        return postusewhich("noundict") != 0

    def usewhich(self) -> dict:
        which = postusewhich("noundict")
        if which == 1:
            return globalconfig["noundictconfig_ex"]
        elif which == 2:
            gameuid = gobject.baseobject.gameuid
            return savehook_new_data[gameuid].get("noundictconfig_ex", [])
        elif which == 3:
            gameuid = gobject.baseobject.gameuid
            return (
                savehook_new_data[gameuid].get("noundictconfig_ex", [])
                + globalconfig["noundictconfig_ex"]
            )

    def __createfake(self):
        ___idx = 1
        if ___idx == 1:
            xx = "ZX{}Z".format(chr(ord("B") + self.zhanweifu))
        elif ___idx == 2:
            xx = "{{{}}}".format(self.zhanweifu)
        self.zhanweifu += 1
        return xx

    def process_before(self, japanese):
        used = []
        gpt_dict = []
        srcs = set()
        for gpt in self.usewhich():
            src = gpt["src"]
            if src in srcs:
                continue
            srcs.add(src)
            if src not in japanese:
                continue
            gpt_dict.append(gpt)
            used.append((src, gpt["dst"]))

        self.zhanweifu = 0
        japanese1, mp1 = self.process_before1(japanese, used)

        return japanese1, {
            "gpt_dict": gpt_dict,
            "gpt_dict_origin": japanese,
            "zhanweifu": mp1,
        }

    def process_before1(self, content: str, dic: list):
        mp1 = {}
        for k, v in dic:
            if not k:
                continue
            xx = self.__createfake()
            content = content.replace(k, xx)
            mp1[xx] = v
        return content, mp1

    def process_after(self, res: str, context):
        mp1 = context["zhanweifu"]
        for key in mp1:
            res = case_insensitive_replace(res, key, mp1[key])
        return res
