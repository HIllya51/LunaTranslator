from qtsymbols import *
from rendertext.textbrowser_imp.base import base


class TextLine(base):
    def moveoffset(self):
        font = self.font()
        fontOutLineWidth = (
            self.config["width"] + font.pointSizeF() * self.config["width_rate"]
        )
        return fontOutLineWidth, fontOutLineWidth

    def extraWH(self):
        font = self.font()
        fontOutLineWidth = (
            self.config["width"] + font.pointSizeF() * self.config["width_rate"]
        )
        fontOutLineWidth *= 2
        fontOutLineWidth += self.config["trace"]
        return (fontOutLineWidth, fontOutLineWidth)

    def colorpair(self):
        _ = QColor(self.config["fillcolor"]), QColor(self.basecolor)
        if self.config["reverse"]:
            _ = reversed(_)
        return _

    def paintText(self, painter: QPainter):
        self.m_outLineColor, self.m_contentColor = self.colorpair()
        text = self.text()
        font = self.font()
        fontOutLineWidth = (
            self.config["width"] + font.pointSizeF() * self.config["width_rate"]
        )

        font_m = QFontMetrics(font)
        path = QPainterPath()
        for i in range(self.config["trace"]):
            path.addText(
                fontOutLineWidth + i,
                fontOutLineWidth + i + font_m.ascent(),
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

        painter.strokePath(path, pen)
        path = QPainterPath()
        path.addText(
            fontOutLineWidth,
            fontOutLineWidth + font_m.ascent(),
            font,
            text,
        )

        painter.fillPath(path, QBrush(self.m_contentColor))
