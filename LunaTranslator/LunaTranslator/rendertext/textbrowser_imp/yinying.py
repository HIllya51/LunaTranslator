from qtsymbols import *
from rendertext.textbrowser_imp.normal import TextLine as TextLabel_0


class QGraphicsDropShadowEffect_multi(QGraphicsDropShadowEffect):
    def __init__(self, x) -> None:
        self.x = x
        super().__init__()

    def draw(self, painter) -> None:
        for i in range(self.x):
            super().draw(painter)


class TextLine(TextLabel_0):
    def usingcolor(self):
        return QColor(self.config["fillcolor"])

    def setShadow_internal(self, colorshadow, width=1, deepth=1):

        shadow2 = QGraphicsDropShadowEffect_multi(deepth)

        shadow2.setBlurRadius(width)
        shadow2.setOffset(0)
        shadow2.setColor(QColor(colorshadow))
        self.setGraphicsEffect(shadow2)

    def setShadow(self):
        font = self.font()
        self.setShadow_internal(
            self.basecolor,
            font.pointSizeF() * self.config["shadowR"],
            self.config["shadowforce"],
        )
