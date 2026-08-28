from qtsymbols import *
from myutils.config import globalconfig
import gobject
from sometypes import WordSegResult


class FontInfo:
    def __init__(self, fm, size, bold, italic):
        self.fm = fm
        self.size = size
        self.bold = bold
        self.italic = italic

    @property
    def qfont(self):

        font = QFont()
        font.setFamily(self.fm)
        font.setPointSizeF(self.size)
        font.setBold(self.bold)
        font.setItalic(self.italic)
        return font

    @property
    def dict(self):
        return dict(
            fontFamily=self.fm, fontSize=self.size, bold=self.bold, italic=self.italic
        )


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
    COLOR_DEFAULT = 3
    KANA_COLOR = 4
    FENCI_COLOR = 5

    def __init__(self, T, klass=None):
        self.type = T
        self.klass = klass

    def get(self):
        if self.type == self.RAW_TEXT_COLOR:
            return globalconfig.get("rawtextcolor", "#000000")
        if self.type == self.KANA_COLOR:
            return globalconfig.get("jiamingcolor", "black")
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
    def __init__(self, word: WordSegResult):
        self.isdeli = word.isdeli
        self.cixing = word.wordclass
        self.donthighlight = word.donthighlight
        self.specialinfo = bool(word.specialinfo)
        super().__init__(
            ColorControl.FENCI_COLOR,
            (self.isdeli, self.cixing, self.specialinfo, self.donthighlight),
        )

    def _randomcolor_1(self):
        if self.specialinfo:
            return (255, 170, 255, 1)
        if self.donthighlight:
            return None
        if self.isdeli:
            return None
        if not globalconfig.get("show_fenci", True):
            return None
        c = QColor(Qt.GlobalColor.white)
        if self.cixing:
            try:
                if globalconfig["cixingcolorshow"][self.cixing] == False:
                    return None
                c = QColor(globalconfig["cixingcolor"][self.cixing])
            except:
                pass
        return (
            c.red(),
            c.green(),
            c.blue(),
            globalconfig.get("showcixing_touming", 30) / 100,
        )

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
    @property
    def _clickable(self):
        return (globalconfig.get("usesearchword", True)) or (
            globalconfig.get("usesearchword_S", False)
            and (globalconfig.get("searchword_S_mousetrigger", "left") != "hover")
        )

    @property
    def _clickhovershow(self):
        return (
            globalconfig.get("usesearchword", True)
            or globalconfig.get("usesearchword_S", False)
            or globalconfig.get("word_hover_show_word_info", False)
        )

    def _getfontinfo(self, texttype: TextType):
        if texttype == TextType.Origin:
            fm = globalconfig.get("fonttype", gobject.tempconfig.get("fonttype", ""))
            fs = globalconfig.get("fontsizeori", 16)
            bold = globalconfig.get("showbold", False)
            italic = globalconfig.get("showitalic", False)
        else:
            fm = globalconfig.get("fonttype2", gobject.tempconfig.get("fonttype2", ""))
            fs = globalconfig.get("fontsize", 16)
            bold = globalconfig.get("showbold_trans", False)
            italic = globalconfig.get("showitalic_trans", False)
        return FontInfo(fm, fs, bold, italic)

    def _getfontinfo_kana(self):
        info = self._getfontinfo(TextType.Origin)
        info.size *= globalconfig.get("kanarate", 0.5)
        if not globalconfig.get("kanafontfollowdefault", True):
            info.fm = globalconfig.get("kanafont", info.fm)
            info.bold = globalconfig.get("kanabold", info.bold)
            info.italic = globalconfig.get("kanaitalic", info.italic)
        return info

    def _createqfont(self, texttype: TextType, klass=None):
        info = self._getfontinfo(texttype)
        if klass:
            data: dict = globalconfig["fanyi"].get(klass, {}).get("privatefont", {})
            if (not data.get("fontfamily_df", True)) and ("fontfamily" in data):
                info.fm = data["fontfamily"]
            if (not data.get("fontsize_df", True)) and ("fontsize" in data):
                info.size = data["fontsize"]
            if (not data.get("showbold_df", True)) and ("showbold" in data):
                info.bold = data["showbold"]
            if (not data.get("showitalic_df", True)) and ("showitalic" in data):
                info.italic = data["showitalic"]

        return info.qfont
