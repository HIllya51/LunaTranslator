import json
import os
from qtsymbols import *
import functools

isdark = False


def disablecolor(__: QColor):
    if __.rgb() == 0xFF000000:
        return Qt.GlobalColor.gray
    __ = QColor(
        max(0, (__.red() - 64)),
        max(
            0,
            (__.green() - 64),
        ),
        max(0, (__.blue() - 64)),
    )
    return __


def _defaultcolor():
    return QColor(("#000000", "#ffffff")[isdark])


def _colorgen(color, disabled):
    color = QColor(color) if color else _defaultcolor()
    if disabled:
        color = disablecolor(color)
    return color


class CharIconEngine(QIconEngine):

    def __init__(self, iconic: "IconicFont", char, color):
        super().__init__()
        self.iconic = iconic
        self.char = char
        self.color = functools.partial(_colorgen, color)

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state):
        painter.save()
        painter.setPen(self.color(mode == QIcon.Mode.Disabled))
        draw_size = round(0.875 * rect.height())
        painter.setFont(self.iconic.font(draw_size))
        painter.drawText(
            rect,
            int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter),
            self.char,
        )
        painter.restore()

    def pixmap(self, size, mode, state):
        pm = QPixmap(size)
        pm.fill(Qt.GlobalColor.transparent)
        self.paint(QPainter(pm), QRect(QPoint(0, 0), size), mode, state)
        return pm


class IconicFont(QObject):
    def __init__(self, ttf_filename, charmap_filename):

        super().__init__()
        self.charmap = {}
        self.icon_cache: "dict[str, QIcon]" = {}
        self.load_font(ttf_filename, charmap_filename)

    def load_font(self, ttf_filename, charmap_filename):
        directory = "files/static/fonts"

        with open(os.path.join(directory, ttf_filename), "rb") as font_data:
            id_ = QFontDatabase.addApplicationFontFromData(QByteArray(font_data.read()))

        loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

        self.fontname = loadedFontFamilies[0]

        with open(os.path.join(directory, charmap_filename), "r") as codes:
            self.charmap = json.load(codes)

    def icon(self, name, color):
        if isinstance(color, QColor):
            cache_key = "{}{}".format(name, color.name())
        else:
            cache_key = "{}{}".format(name, color)

        if cache_key not in self.icon_cache:

            char = chr(int((self.charmap[name[3:]]), 16))
            self.icon_cache[cache_key] = self._icon_by_painter(char, color)

        return self.icon_cache[cache_key]

    def font(self, size):
        font = QFont()
        font.setFamily(self.fontname)
        font.setPixelSize(round(size))
        font.setBold(False)
        return font

    def _icon_by_painter(self, char, color):
        engine = CharIconEngine(self, char, color)
        return QIcon(engine)


_resource = {"iconic": None}


def _instance():

    if _resource["iconic"] is None:
        _resource["iconic"] = IconicFont(
            "fontawesome4.7-webfont.ttf", "fontawesome4.7-webfont-charmap.json"
        )
    return _resource["iconic"]


def icon(name, color=None):
    return _instance().icon(name, color)
