import os, functools
from myutils.config import globalconfig, _TRL, static_data, getlanguse
from gui.usefulwidget import (
    D_getsimplecombobox,
    getsimplecombobox,
    D_getcolorbutton,
    makescrollgrid,
)


def createlangs(self):
    self.srclangswitcher = getsimplecombobox(
        _TRL(static_data["language_list_translator"]), globalconfig, "srclang3"
    )
    return self.srclangswitcher


def setTablanglz(self):
    return [
        [("翻译及OCR语言", 15)],
        [
            ("源语言", 5),
            (functools.partial(createlangs, self), 5),
        ],
        [
            ("目标语言", 5),
            (
                D_getsimplecombobox(
                    _TRL(static_data["language_list_translator"]),
                    globalconfig,
                    "tgtlang3",
                ),
                5,
            ),
        ],
        [],
        [
            ("本软件显示语言(重启生效)", 5),
            (
                D_getsimplecombobox(
                    (static_data["language_list_show"]), globalconfig, "languageuse"
                ),
                5,
            ),
            (
                D_getcolorbutton(
                    globalconfig,
                    "",
                    callback=lambda: os.startfile(
                        os.path.abspath("./files/lang/{}.json".format(getlanguse()))
                    ),
                    icon="fa.gear",
                    constcolor="#FF69B4",
                ),
                1,
            ),
        ],
        [],
    ]


def setTablang(self, l):
    makescrollgrid(setTablanglz(self), l)
