from qtsymbols import *
from rendertext.textbrowser_imp.normal import TextLine as TextLabel_0


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

    def draw(self, painter):
        r = self.parent().devicePixelRatioF()
        if self.shadow_pixmap.isNull():
            size = QSize(painter.device().width(), painter.device().height()) * r
            self.shadow_pixmap = QPixmap(size)
            self.shadow_pixmap.setDevicePixelRatio(r)
            self.shadow_pixmap.fill(Qt.GlobalColor.transparent)
            shadow_painter = QPainter(self.shadow_pixmap)
            shadow_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for _ in range(self.x):
                super().draw(shadow_painter)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(
            -int(self.parent().x()),
            -int(self.parent().y()) - self.parent().parent().parent().parent().y(),
            self.shadow_pixmap,
        )


class TextLine(TextLabel_0):

    def usingcolor(self):
        return QColor(self.config["fillcolor"])

    def setShadow_internal(self, colorshadow, width=1, deepth=1):

        shadow2 = CachedQGraphicsDropShadowEffect_multi(self, deepth)

        shadow2.setBlurRadius(width)
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
