import json
import sys, os

sys.path.append(os.path.dirname(__file__))
import qdarktheme
from qdarktheme._resources.colors import ACCENT_COLORS


def tryloadconfig():
    try:
        with open("userconfig/PyQtDarkTheme.json", "r", encoding="utf8") as ff:
            return json.loads(ff.read())
    except:
        return {}


def stylesheet_1(theme):
    config = tryloadconfig()
    corner_shape = config.get("corner_shape_1", "sharp")
    color = config.get("color_1", "pink")
    return qdarktheme.load_stylesheet(
        theme=theme,
        corner_shape=corner_shape,
        custom_colors={"primary": ACCENT_COLORS[theme][color]},
    )
