from qtsymbols import *
from myutils.config import globalconfig
from gui.textbrowser import TextType
import random


class dataget:

    def _randomcolor_1(self, word):
        if word.get("isdeli", False):
            return None
        c = QColor("white")
        if "cixing" in word:
            try:
                if globalconfig["cixingcolorshow"][word["cixing"]] == False:
                    return None
                c = QColor(globalconfig["cixingcolor"][word["cixing"]])
            except:
                pass
        return (c.red(), c.green(), c.blue())

    def _randomcolor(self, word):
        color = self._randomcolor_1(word)
        if not color:
            color = (random.randint(0, 255) for _ in range(3))
        r, g, b = color
        return "rgba({}, {}, {}, {})".format(r, g, b, globalconfig["showcixing_touming"] / 100)

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
