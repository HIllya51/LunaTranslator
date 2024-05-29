import json
import os
from qtsymbols import *


class CharIconPainter:

    def paint(self, iconic, painter, rect, char, color):
        painter.save()
        qcolor = QColor(color)
        painter.setPen(qcolor)
        draw_size = round(0.875 * rect.height())
        painter.setFont(iconic.font(draw_size))
        painter.drawText(
            rect,
            int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter),
            char,
        )
        painter.restore()


class CharIconEngine(QIconEngine):

    def __init__(self, iconic, painter, char, color):
        super().__init__()
        self.iconic = iconic
        self.painter = painter
        self.char = char
        self.color = color

    def paint(self, painter, rect):
        self.painter.paint(self.iconic, painter, rect, self.char, self.color)

    def pixmap(self, size, mode, state):
        pm = QPixmap(size)
        pm.fill(Qt.GlobalColor.transparent)
        self.paint(QPainter(pm), QRect(QPoint(0, 0), size))
        return pm


class IconicFont(QObject):
    def __init__(self, ttf_filename, charmap_filename):

        super().__init__()
        self.painter = CharIconPainter()
        self.charmap = {}
        self.icon_cache = {}
        self.load_font(ttf_filename, charmap_filename)

    def load_font(self, ttf_filename, charmap_filename):
        directory = "./files/fonts"

        with open(os.path.join(directory, ttf_filename), "rb") as font_data:
            id_ = QFontDatabase.addApplicationFontFromData(QByteArray(font_data.read()))

        loadedFontFamilies = QFontDatabase.applicationFontFamilies(id_)

        self.fontname = loadedFontFamilies[0]

        with open(os.path.join(directory, charmap_filename), "r") as codes:
            self.charmap = json.load(codes)

    def icon(self, name, color):

        cache_key = "{}{}".format(name, color)

        if cache_key not in self.icon_cache:

            char = chr(int((self.charmap[name[3:]]), 16))
            self.icon_cache[cache_key] = self._icon_by_painter(
                self.painter, char, color
            )

        return self.icon_cache[cache_key]

    def font(self, size):
        font = QFont()
        font.setFamily(self.fontname)
        font.setPixelSize(round(size))
        return font

    def _icon_by_painter(self, painter, char, color):
        engine = CharIconEngine(self, painter, char, color)
        return QIcon(engine)


_resource = {"iconic": None}


def _instance():

    if _resource["iconic"] is None:
        _resource["iconic"] = IconicFont(
            "fontawesome4.7-webfont.ttf", "fontawesome4.7-webfont-charmap.json"
        )
    return _resource["iconic"]


def icon(name, color="#000000"):
    return _instance().icon(name, color)
