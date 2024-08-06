from qtsymbols import *
import os, functools
import gobject
from myutils.config import globalconfig, static_data
from gui.inputdialog import (
    autoinitdialog_items,
    noundictconfigdialog1,
    autoinitdialog,
    yuyinzhidingsetting,
)
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    makescrollgrid,
    D_getIconButton,
    yuitsu_switch,
    FocusCombo,
    D_getsimpleswitch,
)


def showvoicelist(self, obj):

    if obj is None:
        try:
            self.voicecombo.clear()
        except:
            pass
        return
    vl = obj.voiceshowlist
    idx = obj.voicelist.index(obj.voice)
    try:

        self.voicecombo.clear()
        self.voicecombo.addItems(vl)
        self.voicecombo.setCurrentIndex(idx)
    except:
        self.voicecombo_cache = vl, idx


def changevoice(self, text):
    if gobject.baseobject.reader is None:
        return
    gobject.baseobject.reader.voice = gobject.baseobject.reader.voicelist[
        self.voicecombo.currentIndex()
    ]


def createvoicecombo(self):

    self.voicecombo = FocusCombo()
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self, x))
    try:
        vl, idx = self.voicecombo_cache
        self.voicecombo.addItems(vl)
        if idx >= 0:
            self.voicecombo.setCurrentIndex(idx)
    except:
        pass
    return self.voicecombo


def setTab5(self, l):
    makescrollgrid(setTab5lz(self), l)


def getttsgrid(self):

    grids = []
    i = 0
    self.ttswitchs = {}
    line = []
    for name in globalconfig["reader"]:

        _f = "./LunaTranslator/tts/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue
        if "args" in globalconfig["reader"][name]:
            items = autoinitdialog_items(globalconfig["reader"][name])
            items[-1]["callback"] = functools.partial(
                gobject.baseobject.startreader, name, True, True
            )
            _3 = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["reader"][name]["name"],
                    800,
                    items,
                ),
                icon="fa.gear",
            )

        else:
            _3 = ""

        line += [
            globalconfig["reader"][name]["name"],
            D_getsimpleswitch(
                globalconfig["reader"][name],
                "use",
                name=name,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["reader"],
                    "ttswitchs",
                    name,
                    gobject.baseobject.startreader,
                ),
                pair="ttswitchs",
            ),
            _3,
        ]
        if i % 3 == 2:
            grids.append(line)
            line = []
        else:
            line += [""]
        i += 1
    if len(line):
        grids.append(line)
    return grids


def setTab5lz(self):
    grids = []
    grids += [
        [
            (
                dict(title="引擎", type="grid", grid=getttsgrid(self)),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="声音",
                    grid=[
                        [
                            "选择声音",
                            functools.partial(createvoicecombo, self),
                        ],
                        [
                            "语速_(-10~10)",
                            D_getspinbox(-10, 10, globalconfig["ttscommon"], "rate"),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="音频播放",
                    grid=[
                        [
                            "引擎",
                            D_getsimplecombobox(
                                static_data["audioengine_vis"],
                                globalconfig,
                                "audioengine",
                                internal=static_data["audioengine"],
                                static=True,
                            ),
                        ],
                        [
                            "音量_(0~100)",
                            D_getspinbox(0, 100, globalconfig["ttscommon"], "volume"),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="行为",
                    type="grid",
                    grid=[
                        [
                            "自动朗读",
                            D_getsimpleswitch(
                                globalconfig, "autoread", name="autoread", parent=self
                            ),
                        ],
                        [
                            "不被打断",
                            D_getsimpleswitch(globalconfig, "ttsnointerrupt"),
                        ],
                        [
                            "朗读原文",
                            D_getsimpleswitch(globalconfig, "read_raw"),
                        ],
                        [
                            "朗读翻译",
                            D_getsimpleswitch(globalconfig, "read_trans"),
                        ],
                        [
                            "朗读的翻译",
                            (
                                D_getsimplecombobox(
                                    [
                                        globalconfig["fanyi"][x]["name"]
                                        for x in globalconfig["fanyi"]
                                    ],
                                    globalconfig,
                                    "read_translator",
                                ),
                                0,
                            ),
                        ],
                        [
                            "语音指定",
                            D_getsimpleswitch(globalconfig["ttscommon"], "tts_skip"),
                            D_getIconButton(
                                callback=lambda: yuyinzhidingsetting(
                                    self, globalconfig["ttscommon"]["tts_skip_regex"]
                                ),
                                icon="fa.gear",
                            ),
                        ],
                        [
                            "语音修正",
                            D_getsimpleswitch(globalconfig["ttscommon"], "tts_repair"),
                            D_getIconButton(
                                callback=lambda: noundictconfigdialog1(
                                    self,
                                    globalconfig["ttscommon"]["tts_repair_regex"],
                                    "语音修正",
                                    ["正则",'转义', "原文", "替换"],
                                ),
                                icon="fa.gear",
                            ),
                            "",
                            D_getsimpleswitch(
                                globalconfig["ttscommon"], "tts_repair_use_at_translate"
                            ),
                            "作用于翻译",
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    return grids
