from qtsymbols import *
from myutils.config import globalconfig
from gui.textbrowser import TextType


class dataget:
    def _getfontinfo(self, texttype: TextType):
        if texttype == TextType.Origin:
            fm = globalconfig["fonttype"]
            fs = globalconfig["fontsizeori"]
            bold = globalconfig["showbold"]
        else:
            fm = globalconfig["fonttype2"]
            fs = globalconfig["fontsize"]
            bold = globalconfig["showbold_trans"]
        return fm, fs, bold

    def _getfontinfo_kana(self):
        fm, fs, bold = self._getfontinfo(TextType.Origin)
        return fm, fs * globalconfig["kanarate"], bold
