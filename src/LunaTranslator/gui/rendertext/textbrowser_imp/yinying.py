from qtsymbols import *
from gui.rendertext.textbrowser_imp.normal import TextLine as TextLabel_0


class QGraphicsDropShadowEffect_multi(QGraphicsDropShadowEffect):
    def __init__(self, x) -> None:
        self.x = x
        super().__init__()

    def draw(self, painter) -> None:
        for i in range(self.x):
            super().draw(painter)


class CachedQGraphicsDropShadowEffect_multi(QGraphicsDropShadowEffect):
    def __init__(self, parent=None, x=1):
        super().__init__(parent)
        self.shadow_pixmap = QPixmap()
        self.x = x
        self.savey = None  # iterappend中被移动而不需重绘
        self.lastppppy = None

    def draw(self, painter):
        if self.shadow_pixmap.isNull():
            r = self.parent().devicePixelRatioF()
            size = self.boundingRect().toRect().united(painter.viewport()).size() * r
            self.shadow_pixmap = QPixmap(size)
            self.shadow_pixmap.setDevicePixelRatio(r)
            self.shadow_pixmap.fill(Qt.GlobalColor.transparent)
            shadow_painter = QPainter(self.shadow_pixmap)
            shadow_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for _ in range(self.x):
                super().draw(shadow_painter)
            self.savey = self.parent().y()
            self.lastppppy = self.parent().parent().parent().parent().y()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(
            -int(self.parent().x()) - self.parent().movedx,  # 阿拉伯语绘制偏移
            -self.lastppppy - self.savey,
            self.shadow_pixmap,
        )


class TextLine(TextLabel_0):

    @property
    def stylestates(self):
        return (
            self._basecolor.get(),
            self.config["fillcolor"],
            self.config["shadowR"],
            self.config["shadowR_ex"],
            self.config["shadowforce"],
        )

    def usingcolor(self):
        return QColor(self.config["fillcolor"])

    def setShadow_internal(self, colorshadow, width=1, deepth=1):

        shadow2 = CachedQGraphicsDropShadowEffect_multi(self, deepth)

        shadow2.setBlurRadius(max(1, width))
        shadow2.setOffset(0)
        shadow2.setColor(QColor(colorshadow))
        self.setGraphicsEffect(shadow2)

    def setShadow(self):
        font = self.font()
        self.setShadow_internal(
            self.basecolor,
            font.pointSizeF() * self.config["shadowR"] + self.config["shadowR_ex"],
            self.config["shadowforce"],
        )
