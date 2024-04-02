import functools

from PyQt5.QtWidgets import QComboBox
from gui.inputdialog import getsomepath1, noundictconfigdialog1
from myutils.config import globalconfig, _TRL
import os, functools
import gobject
from gui.usefulwidget import (
    getsimplecombobox,
    getspinbox,
    getcolorbutton,
    yuitsu_switch,
    getsimpleswitch,
)


def setTab5_direct(self):
    self.voicecombo = QComboBox()
    self.voicelistsignal.connect(functools.partial(showvoicelist, self))
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self, x))


def setTab5(self):
    self.tabadd_lazy(self.tab_widget, ("语音合成"), lambda: setTab5lz(self))


def getttsgrid(self):

    grids = []
    i = 0
    self.ocrswitchs = {}
    line = []
    for name in globalconfig["reader"]:

        _f = "./LunaTranslator/tts/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue

        line += [
            ((globalconfig["reader"][name]["name"]), 6),
            getsimpleswitch(
                globalconfig["reader"][name],
                "use",
                name=name,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["reader"],
                    "readerswitchs",
                    name,
                    gobject.baseobject.startreader,
                ),
                pair="readerswitchs",
            ),
        ]
        if "path" in globalconfig["reader"][name]:
            line += [
                getcolorbutton(
                    globalconfig,
                    "",
                    callback=functools.partial(
                        getsomepath1,
                        self,
                        globalconfig["reader"][name]["name"],
                        globalconfig["reader"][name],
                        "path",
                        globalconfig["reader"][name]["name"],
                        gobject.baseobject.startreader,
                        True,
                    ),
                    icon="fa.gear",
                    constcolor="#FF69B4",
                )
            ]
        else:
            line += [""]
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
    gridlayoutwidget = self.makegrid(grids)
    gridlayoutwidget = self.makescroll(gridlayoutwidget)
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
