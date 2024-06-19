from qtsymbols import *
from rendertext.internal.textbrowser.normal import TextLine as TextLabel_0


class TextLine(TextLabel_0):
    def usingcolor(self):
        return QColor(self.config["fillcolor"])

    def setShadow(self):
        font = self.font()
        self.setShadow_internal(
            self.basecolor,
            font.pointSizeF() * self.config["shadowR"],
            self.config["shadowforce"],
        )
