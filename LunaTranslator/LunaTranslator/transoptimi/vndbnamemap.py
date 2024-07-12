from myutils.config import savehook_new_data, globalconfig
import gobject
from traceback import print_exc
from gui.inputdialog import postconfigdialog_
from myutils.utils import checkpostusing


class Process:

    @staticmethod
    def get_setting_window(parent_window):
        return (
            postconfigdialog_(
                parent_window,
                globalconfig["global_namemap"],
                "指定人名翻译",
                ["人名", "翻译"],
            ),
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):
        return (
            postconfigdialog_(
                parent_window,
                savehook_new_data[gameuid]["namemap"],
                "指定人名翻译",
                ["人名", "翻译"],
            ),
        )

    @property
    def using_X(self):
        for _ in (0,):
            try:
                if not gobject.baseobject.textsource:
                    break
                gameuid = gobject.baseobject.textsource.gameuid
                if savehook_new_data[gameuid]["transoptimi_followdefault"]:
                    break
                return savehook_new_data[gameuid]["vndbnamemap_use"]

            except:
                print_exc()
                break
        return checkpostusing("vndbnamemap")

    def usewhich(self) -> dict:
        for _ in (0,):
            try:
                if not gobject.baseobject.textsource:
                    break
                gameuid = gobject.baseobject.textsource.gameuid
                if savehook_new_data[gameuid]["transoptimi_followdefault"]:
                    break
                return savehook_new_data[gameuid]["namemap"]

            except:
                print_exc()
                break
        return globalconfig["global_namemap"]

    def process_before(self, s):

        namemap = self.usewhich()
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
