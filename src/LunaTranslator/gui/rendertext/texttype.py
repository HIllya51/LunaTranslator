from qtsymbols import *
from myutils.config import globalconfig


class TextType:
    Origin = 0
    Translate = 1
    Info = 2
    Error_origin = 3
    Error_translator = 4


class ColorControl:
    RAW_TEXT_COLOR = 0
    TS_COLOR = 1
    ERROR_COLOR = 2
    COLOR_DEFAULT = 2
    KANA_COLOR = 3
    FENCI_COLOR = 4

    def __init__(self, T, klass=None):
        self.type = T
        self.klass = klass

    def get(self):
        if self.type == self.RAW_TEXT_COLOR:
            return globalconfig["rawtextcolor"]
        if self.type == self.KANA_COLOR:
            return globalconfig["jiamingcolor"]
        if self.type == self.ERROR_COLOR:
            return "red"
        if self.type == self.COLOR_DEFAULT:
            return "black"
        if self.type == self.TS_COLOR:
            return globalconfig["fanyi"].get(self.klass, {}).get("color", "black")

    def asklass(self):
        if self.type == self.RAW_TEXT_COLOR:
            return "ColorControl_RAW_TEXT_COLOR"
        if self.type == self.KANA_COLOR:
            return "ColorControl_KANA_COLOR"
        if self.type == self.ERROR_COLOR:
            return "ColorControl_ERROR_COLOR"
        if self.type == self.COLOR_DEFAULT:
            return "ColorControl_COLOR_DEFAULT"

    def _tuple_(self):
        if self.klass:
            return (self.type, self.klass)
        return self.type

    def __repr__(self):
        return str(self._tuple_())

    def __hash__(self):
        return self._tuple_().__hash__()

    def __eq__(self, value: "ColorControl"):
        return self._tuple_() == value._tuple_()


class TranslateColor(ColorControl):
    def __init__(self, klass):
        super().__init__(ColorControl.TS_COLOR, klass)

    def get(self):
        return globalconfig["fanyi"].get(self.klass, {}).get("color", "black")

    def asklass(self):
        return "ColorControl_TS_COLOR_{}".format(self.klass)


class FenciColor(ColorControl):
    def __init__(self, word):
        self.isdeli = word.get("isdeli", False)
        self.cixing = word.get("cixing", None)
        super().__init__(ColorControl.FENCI_COLOR, (self.isdeli, self.cixing))

    def _randomcolor_1(self):
        if self.isdeli:
            return None
        if not globalconfig["show_fenci"]:
            return None
        c = QColor("white")
        if self.cixing:
            try:
                if globalconfig["cixingcolorshow"][self.cixing] == False:
                    return None
                c = QColor(globalconfig["cixingcolor"][self.cixing])
            except:
                pass
        return (c.red(), c.green(), c.blue(), globalconfig["showcixing_touming"] / 100)

    def get(self):
        color = self._randomcolor_1()
        if not color:
            color = (0, 0, 0, 0)
        r, g, b, a = color
        return "rgba({}, {}, {}, {})".format(r, g, b, a)

    def asklass(self):
        return "ColorControl_FENCI_COLOR_{}".format(
            "".join(format(x, "02x") for x in str(self.klass).encode("utf8"))
        )


class SpecialColor:
    RawTextColor = ColorControl(ColorControl.RAW_TEXT_COLOR)
    ErrorColor = ColorControl(ColorControl.ERROR_COLOR)
    DefaultColor = ColorControl(ColorControl.COLOR_DEFAULT)
    KanaColor = ColorControl(ColorControl.KANA_COLOR)


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
