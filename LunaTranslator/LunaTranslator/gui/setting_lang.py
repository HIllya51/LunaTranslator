import os
from myutils.config import globalconfig, static_data, getlanguse, loadlangviss
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getIconButton,
    makescrollgrid,
)
from qtsymbols import *


def changelang(_):
    languageChangeEvent = QEvent(QEvent.Type.LanguageChange)
    QApplication.sendEvent(QApplication.instance(), languageChangeEvent)


def setTablanglz(self):
    inner, vis = loadlangviss()
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
                                "srclang4",
                                internal=static_data[
                                    "language_list_translator_inner"
                                ],
                            ),
                        ],
                        [
                            "目标语言",
                            D_getsimplecombobox(
                                static_data["language_list_translator"],
                                globalconfig,
                                "tgtlang4",
                                internal=static_data[
                                    "language_list_translator_inner"
                                ],
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
                                vis,
                                globalconfig,
                                "languageuse2",
                                callback=changelang,
                                static=True,
                                internal=inner,
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
