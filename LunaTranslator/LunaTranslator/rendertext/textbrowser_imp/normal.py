from qtsymbols import *
from rendertext.textbrowser_imp.base import base


class TextLine(base):
    def usingcolor(self):
        return self.basecolor

    def paintText(self, painter: QPainter):
        path = QPainterPath()

        text = self.text()
        font = self.font()
        font_m = QFontMetrics(font)
        path.addText(
            0,
            font_m.ascent(),
            font,
            text,
        )
        painter.fillPath(path, QBrush(self.usingcolor()))
