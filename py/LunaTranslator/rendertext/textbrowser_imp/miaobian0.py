from qtsymbols import *
from rendertext.textbrowser_imp.base import base


class TextLine(base):

    def colorpair(self):
        return QColor(self.basecolor), QColor(self.config["fillcolor"])

    def paintText(self, painter: QPainter):
        self.m_outLineColor, self.m_contentColor = self.colorpair()
        fontOutLineWidth = self.config["width"]

        text = self.text()
        font = self.font()
        font_m = QFontMetricsF(font)
        path = QPainterPath()
        path.addText(
            fontOutLineWidth,
            fontOutLineWidth + font_m.ascent(),
            font,
            text,
        )

        pen = QPen(
            self.m_outLineColor,
            fontOutLineWidth,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )

        painter.fillPath(path, QBrush(self.m_contentColor))
        painter.strokePath(path, pen)
