from qtsymbols import *
from myutils.config import globalconfig


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
        return (c.red(), c.green(), c.blue(), globalconfig["showcixing_touming"] / 100)

    def _randomcolor(self, word):
        color = self._randomcolor_1(word)
        if not color:
            return None
        r, g, b, a = color
        return f"rgba({r}, {g}, {b}, {a})"

    def _getfontinfo(self, origin):
        if origin:
            fm = globalconfig["fonttype"]
        else:
            fm = globalconfig["fonttype2"]
        return fm, globalconfig["fontsize"], globalconfig["showbold"]

    def _getfontinfo_kana(self):
        fm, fs, bold = self._getfontinfo(True)
        return fm, fs * globalconfig["kanarate"], bold

    def _getkanacolor(self):
        return globalconfig["jiamingcolor"]
