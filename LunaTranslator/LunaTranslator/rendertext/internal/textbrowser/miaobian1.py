from qtsymbols import *
from rendertext.internal.textbrowser.base import base


class TextLine(base):

    def colorpair(self):
        return QColor(self.config["fillcolor"]), QColor(self.basecolor)

    def paintText(self, painter: QPainter):
        self.m_outLineColor, self.m_contentColor = self.colorpair()
        self.m_fontOutLineWidth = self.config["width"]

        text = self.text()
        font = self.font()
        font_m = QFontMetrics(font)
        path = QPainterPath()
        path.addText(
            self.m_fontOutLineWidth,
            self.m_fontOutLineWidth + font_m.ascent(),
            font,
            text,
        )

        pen = QPen(
            self.m_outLineColor,
            self.m_fontOutLineWidth,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )

        painter.strokePath(path, pen)
        painter.fillPath(path, QBrush(self.m_contentColor))
