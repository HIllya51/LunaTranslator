import os, functools
from myutils.config import globalconfig, static_data, getlanguse, set_font_default
from myutils.utils import getlangsrc, getlangtgt
from gui.usefulwidget import (
    D_getsimplecombobox,
    getsimplecombobox,
    D_getIconButton,
    makescrollgrid,
)
from qtsymbols import *
import gobject


def changelang(parent, fonttype, _):
    if globalconfig[fonttype + "auto"]:
        font = set_font_default(
            getlangsrc() if fonttype == "fonttype" else getlangtgt(),
            fonttype)
        try:
            fonttypelayout = getattr(parent, fonttype)
            fonttypelayout.setCurrentFont(QFont(font))
        except AttributeError:
            pass


def changesettinglang(parent, _):
    if globalconfig["settingfonttypeauto"]:
        font = set_font_default(getlanguse(), "settingfonttype")
        try:
            settingfonttypelayout = getattr(parent, "settingfonttype")
            settingfonttypelayout.setCurrentFont(QFont(font))
        except AttributeError:
            pass
        gobject.baseobject.setcommonstylesheet()
    languageChangeEvent = QEvent(QEvent.Type.LanguageChange)
    QApplication.sendEvent(QApplication.instance(), languageChangeEvent)


def setTablanglz(self):
    return [
        [
            (
                dict(
                    title="翻译及OCR",
                    type="grid",
                    grid=(
                        [
                            "源语言",
                            D_getsimplecombobox(
                                static_data["language_list_translator"],
                                globalconfig,
                                "srclang3",
                                callback=functools.partial(changelang, self, "fonttype"),
                            ),
                        ],
                        [
                            "目标语言",
                            D_getsimplecombobox(
                                static_data["language_list_translator"],
                                globalconfig,
                                "tgtlang3",
                                callback=functools.partial(changelang, self, "fonttype2"),
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="软件显示语言",
                    type="grid",
                    grid=(
                        [
                            "软件显示语言",
                            D_getsimplecombobox(
                                (static_data["language_list_show"]),
                                globalconfig,
                                "languageuse",
                                callback=functools.partial(changesettinglang, self),
                                static=True,
                            ),
                            D_getIconButton(
                                callback=lambda: os.startfile(
                                    os.path.abspath(
                                        "./files/lang/{}.json".format(getlanguse())
                                    )
                                ),
                                icon="fa.gear",
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]


def setTablang(self, l):
    makescrollgrid(setTablanglz(self), l)
