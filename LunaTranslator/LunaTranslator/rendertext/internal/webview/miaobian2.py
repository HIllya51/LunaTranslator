from qtsymbols import *
from rendertext.internal.webview.miaobian1 import TextLine as TL1


class TextLine(TL1):

    def colorpair(self, color):
        return color, self.config["fillcolor"]
