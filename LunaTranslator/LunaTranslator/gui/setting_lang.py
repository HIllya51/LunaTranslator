import os, functools
from myutils.config import globalconfig, static_data, getlanguse
from gui.usefulwidget import (
    D_getsimplecombobox,
    getsimplecombobox,
    D_getIconButton,
    makescrollgrid,
)
from qtsymbols import *


def createlangs(self):
    self.srclangswitcher = getsimplecombobox(
        static_data["language_list_translator"], globalconfig, "srclang3"
    )
    return self.srclangswitcher


def changelang(_):
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
                            functools.partial(createlangs, self),
                        ],
                        [
                            "目标语言",
                            D_getsimplecombobox(
                                static_data["language_list_translator"],
                                globalconfig,
                                "tgtlang3",
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
                                callback=changelang,
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
