import functools
from qtsymbols import *
from gui.inputdialog import autoinitdialog_items, noundictconfigdialog1, autoinitdialog
from myutils.config import globalconfig, _TRL
import os, functools
import gobject
from gui.usefulwidget import (
    getsimplecombobox,
    getspinbox,
    makegrid,
    makescroll,
    getcolorbutton,
    tabadd_lazy,
    yuitsu_switch,
    getsimpleswitch,
)


def setTab5_direct(self):
    self.voicecombo = QComboBox()
    self.voicelistsignal.connect(functools.partial(showvoicelist, self))
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self, x))


def setTab5(self):
    tabadd_lazy(self.tab_widget, ("语音合成"), lambda: setTab5lz(self))


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
            items[-1]["callback"] = gobject.baseobject.startreader
            _3 = getcolorbutton(
                globalconfig,
                "",
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["reader"][name]["name"],
                    800,
                    items,
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            )

        else:
            _3 = ""

        line += [
            ((globalconfig["reader"][name]["name"]), 6),
            (
                getsimpleswitch(
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
                1,
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

    grids = getttsgrid(self)
    grids += [
        [],
        [("选择声音", 6), (self.voicecombo, 15)],
        [
            ("语速:(-10~10)", 6),
            (getspinbox(-10, 10, globalconfig["ttscommon"], "rate"), 3),
        ],
        [
            ("音量:(0~100)", 6),
            (getspinbox(0, 100, globalconfig["ttscommon"], "volume"), 3),
        ],
        [("自动朗读", 6), (getsimpleswitch(globalconfig, "autoread"), 1)],
        [("不被打断", 6), (getsimpleswitch(globalconfig, "ttsnointerrupt"), 1)],
        [
            ("朗读原文", 6),
            (getsimpleswitch(globalconfig, "read_raw"), 1),
            "",
            "",
            ("朗读翻译", 6),
            (getsimpleswitch(globalconfig, "read_trans"), 1),
        ],
        [
            ("朗读的翻译", 6),
            (
                getsimplecombobox(
                    _TRL(
                        [
                            globalconfig["fanyi"][x]["name"]
                            for x in globalconfig["fanyi"]
                        ]
                    ),
                    globalconfig,
                    "read_translator",
                ),
                15,
            ),
        ],
        [],
        [
            ("语音修正", 6),
            getsimpleswitch(globalconfig["ttscommon"], "tts_repair"),
            getcolorbutton(
                globalconfig,
                "",
                callback=lambda x: noundictconfigdialog1(
                    self,
                    globalconfig["ttscommon"],
                    "tts_repair_regex",
                    "语音修正",
                    ["正则", "原文", "替换"],
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        ],
    ]
    gridlayoutwidget = makegrid(grids)
    gridlayoutwidget = makescroll(gridlayoutwidget)
    return gridlayoutwidget


def changevoice(self, text):

    globalconfig["reader"][gobject.baseobject.reader_usevoice]["voice"] = (
        gobject.baseobject.reader.voicelist[self.voicecombo.currentIndex()]
    )


def showvoicelist(self, vl, idx):
    self.voicecombo.blockSignals(True)
    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
    if idx >= 0:
        self.voicecombo.setCurrentIndex(idx)
    self.voicecombo.blockSignals(False)
