import os
import sys
import json

sys.path.append(os.path.dirname(__file__))
from common import *
from gui.inputdialog import autoinitdialog


def get_setting_window(parent, callback, isdark):

    config = tryloadconfig()
    darklight = ["light", "dark"][isdark]

    def callback1():
        with open("userconfig/PyQtDarkTheme.json", "w", encoding="utf8") as ff:
            ff.write(json.dumps(config))
        callback()

    autoinitdialog(
        parent,
        config,
        "PyQtDarkTheme",
        600,
        [
            {
                "type": "combo",
                "name": "corner shape",
                "k": "corner_shape_1",
                "list": ["sharp", "rounded"],
                "internal": ["sharp", "rounded"],
            },
            {
                "type": "combo",
                "name": "color",
                "k": "color_1",
                "list": list(ACCENT_COLORS[darklight].keys()),
                "internal": list(ACCENT_COLORS[darklight].keys()),
            },
            {"type": "okcancel", "callback": callback1},
        ],
    )
