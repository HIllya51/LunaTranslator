from qtsymbols import *
from gui.rendertext.textbrowser_imp.base import base


class TextLine(base):
    @property
    def stylestates(self):
        return (
            self._basecolor.get(),
            self.config["fillcolor"],
            self.config["reverse"],
            self.config["trace"],
            self.config["width"],
            self.config["width_rate"],
        )

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
        _ = QColor(self.config["fillcolor"]), self.basecolor
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

        pix = QPixmap(self.size())
        font_m = QFontMetricsF(font)
        pen = QPen(
            self.m_outLineColor,
            fontOutLineWidth,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        path = QPainterPath()
        path.addText(
            fontOutLineWidth,
            fontOutLineWidth + font_m.ascent(),
            font,
            text,
        )
        pix.fill(Qt.GlobalColor.transparent)
        pixpainter = QPainter(pix)
        pixpainter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pixpainter.strokePath(path, pen)
        pixpainter.end()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        for i in range(1 + int(10 * self.config["trace"])):

            painter.drawPixmap(
                QRectF(
                    i / 10,
                    i / 10,
                    pix.width(),
                    pix.height(),
                ),
                pix,
                QRectF(0, 0, pix.width(), pix.height()),
            )
        path = QPainterPath()
        path.addText(
            fontOutLineWidth,
            fontOutLineWidth + font_m.ascent(),
            font,
            text,
        )

        painter.fillPath(path, QBrush(self.m_contentColor))
