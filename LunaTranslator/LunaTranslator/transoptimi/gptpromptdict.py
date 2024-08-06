from myutils.config import globalconfig, savehook_new_data, uid2gamepath
from myutils.utils import postusewhich
from gui.inputdialog import postconfigdialog_
import gobject
from myutils.hwnd import getExeIcon


class Process:
    @staticmethod
    def get_setting_window(parent_window):
        return postconfigdialog_(
            parent_window,
            globalconfig["gptpromptdict"],
            "专有名词翻译_sakura_gpt_词典",
            ["原文", "翻译", "注释"],
            dictkeys=["src", "dst", "info"],
        )

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):
        postconfigdialog_(
            parent_window,
            savehook_new_data[gameuid]["gptpromptdict"],
            "专有名词翻译_sakura_gpt_词典",
            ["原文", "翻译", "注释"],
            dictkeys=["src", "dst", "info"],
        ).setWindowIcon(getExeIcon(uid2gamepath[gameuid], cache=True))

    def process_before(self, japanese):

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
        return japanese, {"gpt_dict": gpt_dict}

    @property
    def using_X(self):
        return postusewhich("gptpromptdict") != 0

    def usewhich(self) -> dict:
        which = postusewhich("gptpromptdict")
        if which == 1:
            return globalconfig["gptpromptdict"]
        elif which == 2:
            gameuid = gobject.baseobject.textsource.gameuid
            return savehook_new_data[gameuid]["gptpromptdict_use"]
        elif which == 3:
            gameuid = gobject.baseobject.textsource.gameuid
            return (
                savehook_new_data[gameuid]["gptpromptdict_use"]
                + globalconfig["gptpromptdict"]
            )
