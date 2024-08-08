from myutils.config import globalconfig, savehook_new_data, uid2gamepath
from myutils.utils import postusewhich, parsemayberegexreplace
from gui.inputdialog import noundictconfigdialog1
import gobject, json, functools
from myutils.hwnd import getExeIcon


class Process:

    @staticmethod
    def get_setting_window(parent_window):
        return (
            noundictconfigdialog1(
                parent_window,
                globalconfig["global_namemap2"],
                "专有名词翻译_直接替换_设置",
                ["正则",'转义', "原文", "翻译"],
            ),
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):

        noundictconfigdialog1(
            parent_window,
            savehook_new_data[gameuid]["namemap2"],
            "专有名词翻译_直接替换_-_" + savehook_new_data[gameuid]["title"],
            ["正则",'转义', "原文", "翻译"],
        ).setWindowIcon(getExeIcon(uid2gamepath[gameuid], cache=True))

    @property
    def using_X(self):
        return postusewhich("vndbnamemap") != 0

    def usewhich(self) -> dict:
        which = postusewhich("vndbnamemap")
        if which == 1:
            return globalconfig["global_namemap2"]
        elif which == 2:
            gameuid = gobject.baseobject.textsource.gameuid
            return savehook_new_data[gameuid]["namemap2"]
        elif which == 3:
            return savehook_new_data[gameuid]["namemap2"] + globalconfig["global_namemap2"]

    def process_before(self, s):

        namemap = self.usewhich()
        s=parsemayberegexreplace(namemap,s)
        bettermap = {}
        for k, v in namemap.items():
            for sp in ["・", " "]:
                spja = k.split(sp)
                spen = v.split(" ")
                if len(spja) == len(spen) and len(spen) > 1:
                    for i in range(len(spja)):
                        if len(spja[i]) >= 2:
                            bettermap[spja[i]] = spen[i]

        for k, v in namemap.items():
            s = s.replace(k, v)
        for k, v in bettermap.items():
            s = s.replace(k, v)
        return s, {}
