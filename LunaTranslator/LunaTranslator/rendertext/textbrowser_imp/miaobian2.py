from qtsymbols import *
from rendertext.textbrowser_imp.miaobian1 import TextLine as TB1


class TextLine(TB1):
    def colorpair(self):
        return QColor(self.basecolor), QColor(self.config["fillcolor"])
