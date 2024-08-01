from myutils.config import savehook_new_data, globalconfig
import gobject, json, functools
from traceback import print_exc
from gui.inputdialog import postconfigdialog_
from myutils.utils import postusewhich


class Process:

    @staticmethod
    def get_setting_window(parent_window):
        return (
            postconfigdialog_(
                parent_window,
                globalconfig["global_namemap"],
                "专有名词翻译_直接替换_设置",
                ["原文", "翻译"],
            ),
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):

        def checkchange(gameuid, __):
            __2 = json.dumps(savehook_new_data[gameuid]["namemap"])
            if __ != __2:
                savehook_new_data[gameuid]["vndbnamemap_modified"] = True

        __ = json.dumps(savehook_new_data[gameuid]["namemap"])
        postconfigdialog_(
            parent_window,
            savehook_new_data[gameuid]["namemap"],
            "专有名词翻译_直接替换_设置",
            ["原文", "翻译"],
            closecallback=functools.partial(checkchange, gameuid, __),
        )

    @property
    def using_X(self):
        return postusewhich("vndbnamemap") != 0

    def usewhich(self) -> dict:
        which = postusewhich("vndbnamemap")
        if which == 1:
            return globalconfig["global_namemap"]
        elif which == 2:
            gameuid = gobject.baseobject.textsource.gameuid
            return savehook_new_data[gameuid]["namemap"]
        elif which == 3:
            _ = {}
            _.update(globalconfig["global_namemap"])
            gameuid = gobject.baseobject.textsource.gameuid
            _.update(savehook_new_data[gameuid]["namemap"])
            return _

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
