from qtsymbols import *
from gui.rendertext.texttype import (
    dataget,
    TextType,
    ColorControl,
    SpecialColor,
    FenciColor,
    FontInfo,
)
import gobject, json, os
import hashlib
from urllib.parse import quote
from myutils.config import globalconfig, static_data, ui_settings
import copy
from sometypes import WordSegResult


class wordwithcolor:
    def __init__(self, word: WordSegResult, color: str):
        self.word = word
        self.color = color

    def as_dict(self):
        d = self.word.as_dict()
        d.update(color=self.color)
        return d


class webview_common(dataget):
    def __init__(self):
        self.colorset: "set[ColorControl]" = set()
        self.ts_klass: "dict[str, dict]" = {}

    def debugeval(self, js: str): ...
    def refreshcontent(self): ...
    def calllunaloadready(self):
        self.colorset.clear()
        self.ts_klass.clear()
        self.setselectable(globalconfig.get("selectable", True))
        self.showhideerror(globalconfig.get("showtranexception", True))
        self.showhideorigin(globalconfig.get("isshowrawtext", True))
        self.showhidetranslate(globalconfig.get("showfanyi", True))
        self.showhidename(globalconfig.get("showfanyisource", False))
        self.showatcenter(globalconfig.get("showatcenter", True))
        self.showtextareabackground(ui_settings.get("text_area_background", False))
        self.setTextAreaBackStyle()
        self.showhideclick()
        self.showhidert(globalconfig.get("isshowhira", True))
        self.setfontstyle()
        self.setdisplayrank(globalconfig.get("displayrank", 0))
        self.sethovercolor(globalconfig.get("hovercolor", "#80000000"))
        self.settooltipsstyle(
            ui_settings.get("word_hover_bg_color", "#333"),
            ui_settings.get("word_hover_text_color", "white"),
            ui_settings.get("word_hover_border", 8),
            ui_settings.get("word_hover_border_R", 4),
        )
        self.verticalhorizontal(globalconfig.get("verticalhorizontal", False))
        self.setwordhoveruse(globalconfig.get("word_hover_action_usewb2", False))
        self.set_word_hover_show_word_info(
            globalconfig.get("word_hover_show_word_info", False)
        )
        self.setbackgroudimageandopt()
        self.refreshcontent()

    # js api
    def setbackgroudimageandopt(self):
        use = not ui_settings.get("backtransparent", False)
        opt = ui_settings.get("transparent_pic", 0) / 100 if use else 0
        url: str = ui_settings.get(
            "backgroundpic", "https://image.lunatranslator.org/luna.jpg"
        )
        if not any((url.lower().startswith(_)) for _ in ("https://", "http://")):
            url = os.path.abspath(url).replace("\\", "/")
        self.debugeval('setbackgroudimageandopt(  "{}",{});'.format(quote(url), opt))

    def sethovercolor(self, color):
        self.debugeval('sethovercolor("{}")'.format(self._qcolor_as_rgba(color)))

    def setdisplayrank(self, rank):
        self.debugeval("setdisplayrank({})".format(int(rank)))

    def setselectable(self, b):
        self.debugeval("setselectable({})".format(int(b)))

    def showatcenter(self, show):
        self.debugeval("showatcenter({})".format(int(show)))

    def showtextareabackground(self, show):
        self.debugeval("showtextareabackground({})".format(int(show)))

    def setTextAreaBackStyle(self, **_):
        # 颜色自带 alpha（#AARRGGBB）；SVG fill 不认该序，转成 rgba()
        c = QColor(ui_settings.get("text_area_background_color", "#d9ffc0cb"))
        self.debugeval(
            "setTextAreaBackStyle({}, {}, {}, 'rgba({},{},{},{})')".format(
                ui_settings.get("text_area_background_r", 5),
                ui_settings.get("text_area_background_w", 5),
                ui_settings.get("text_area_background_h", 5),
                c.red(),
                c.green(),
                c.blue(),
                c.alphaF(),
            )
        )

    def showhidert(self, show):
        self.debugeval("showhidert({})".format(int(show)))

    def showhideclick(self, _=None):
        self.debugeval(
            "showhideclick({},{})".format(
                int(self._clickhovershow), int(self._clickable)
            )
        )

    def showhidename(self, show):
        self.debugeval("showhidename({})".format(int(show)))

    def showhidetranslate(self, show):
        self.debugeval("showhidetranslate({})".format(int(show)))

    def showhideorigin(self, show):
        self.debugeval("showhideorigin({})".format(int(show)))

    def setwordhoveruse(self, v):
        self.debugeval("setwordhoveruse({})".format(int(v)))

    def verticalhorizontal(self, v):
        self.debugeval("verticalhorizontal({})".format(int(v)))

    def set_word_hover_show_word_info(self, action):
        self.debugeval('set_word_hover_show_word_info("{}")'.format(action))

    def showhideerror(self, show):
        self.debugeval("showhideerror({})".format(int(show)))

    def _qcolor_as_rgba(self, color: str):
        c = QColor(color)
        return "#{:02x}{:02x}{:02x}{:02x}".format(
            c.red(), c.green(), c.blue(), c.alpha()
        )

    def settooltipsstyle(self, c1, c2, pd, r):
        self.debugeval(
            'settooltipsstyle("{}","{}",{},{})'.format(
                self._qcolor_as_rgba(c1), self._qcolor_as_rgba(c2), pd, r
            )
        )

    # native api end
    def setfontstyle(self):
        def updateextra(args: dict, lhdict: dict):
            if lhdict:
                args.update(
                    lineHeight=lhdict.get("lineHeight", 0),
                    lineHeightNormal=lhdict.get("lineHeightNormal", True),
                    marginTop=lhdict.get("marginTop", 0),
                    marginBottom=lhdict.get("marginBottom", 0),
                )

        def loadfont(info: FontInfo, lhdict=None):
            args = info.dict
            updateextra(args, lhdict)
            return args

        extra = {}
        for klass, data in self.ts_klass.items():
            klassextra = {}
            if (not data.get("fontfamily_df", True)) and ("fontfamily" in data):
                klassextra["fontFamily"] = data["fontfamily"]
            if (not data.get("fontsize_df", True)) and ("fontsize" in data):
                klassextra["fontSize"] = data["fontsize"]
            if (not data.get("showbold_df", True)) and ("showbold" in data):
                klassextra["bold"] = data["showbold"]
            if (not data.get("showitalic_df", True)) and ("showitalic" in data):
                klassextra["italic"] = data["showitalic"]
            if not data.get("lineheight_df", True):
                updateextra(klassextra, data)
            extra[klass] = klassextra
        origin = loadfont(
            self._getfontinfo(TextType.Origin), globalconfig["lineheights"]
        )
        trans = loadfont(
            self._getfontinfo(TextType.Translate), globalconfig["lineheightstrans"]
        )
        hira = loadfont(self._getfontinfo_kana())
        args = dict(origin=origin, trans=trans, hira=hira, extra=extra)
        args = quote(json.dumps(args))
        self.debugeval('setfontstyle("{}");'.format(args))

    def create_div_line_id(self, _id, texttype: TextType, klass: str):
        args = quote(json.dumps(dict(klass=klass, texttype=texttype)))
        self.debugeval('create_div_line_id("{}","{}")'.format(_id, args))

    def scrolltoend(self):
        self.debugeval("scrollend()")

    def clear_all(self):
        self.debugeval("clear_all()")

    def create_internal_text(self, clear, style, styleargs, _id, name, text, args):
        name = quote(name)
        text = quote(text)
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            'create_internal_text({},"{}","{}","{}","{}","{}","{}");'.format(
                int(clear), style, styleargs, _id, name, text, args
            )
        )

    def create_internal_rubytext(
        self, clear, style, styleargs, _id, tag: "list[wordwithcolor]", args
    ):
        tag = quote(json.dumps(tuple(_.as_dict() for _ in tag)))
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            'create_internal_rubytext({},"{}","{}","{}","{}","{}");'.format(
                int(clear), style, styleargs, _id, tag, args
            )
        )

    def updatetext(self, texttype: TextType, text, hira, color: ColorControl):
        self.append(False, False, texttype, "", text, hira, color, None)

    def iter_append(
        self,
        clear,
        iter_context_class,
        texttype: TextType,
        name,
        text,
        color: ColorControl,
        klass,
    ):
        _id = self.createtextlineid(texttype, klass)
        self._webview_append(clear, _id, name, text, [], color)

    def createtextlineid(self, texttype: TextType, klass: str):
        self.setfontextra(klass)
        _id = "luna_{}".format(
            hashlib.md5((str(texttype) + str(klass)).encode()).hexdigest()
        )
        self.create_div_line_id(_id, texttype, klass)
        return _id

    def append(
        self,
        updateTranslate,
        clear,
        texttype: TextType,
        name,
        text,
        tag,
        color: ColorControl,
        klass,
    ):
        _id = self.createtextlineid(texttype, klass)
        if updateTranslate:
            if clear:
                self.debugeval('cleartranslate("{}")'.format(_id))
            return
        self._webview_append(clear, _id, name, text, tag, color)

    def _getstylevalid(self):
        currenttype = globalconfig["rendertext_using_internal"]["webview"]
        if currenttype not in static_data["textrender"]["webview"]:
            currenttype = static_data["textrender"]["webview"][0]
            globalconfig["rendertext_using_internal"]["webview"] = static_data[
                "textrender"
            ]["webview"][0]
        return currenttype

    def _webview_append(
        self,
        clear,
        _id,
        name,
        text: str,
        tag: "list[WordSegResult]",
        color: ColorControl,
    ):
        self._setcolors(color)
        style = self._getstylevalid()
        styleargs = globalconfig["rendertext"]["webview"][style].get("args", {})
        if len(tag):
            tagx: "list[wordwithcolor]" = []
            for word in tag:
                color1 = FenciColor(word)
                wordx = wordwithcolor(word, color1.asklass())
                tagx.append(wordx)
                self._setcolors(color1)
            self._setcolors(SpecialColor.KanaColor)
            args = dict(
                color=color.asklass(),
                kanacolor=SpecialColor.KanaColor.asklass(),
            )
            self.create_internal_rubytext(clear, style, styleargs, _id, tagx, args)
        else:
            sig = "LUNASHOWHTML"
            userawhtml = text.startswith(sig)
            if userawhtml:
                text = text[len(sig) :]
            args = dict(color=color.asklass(), userawhtml=userawhtml)
            self.create_internal_text(clear, style, styleargs, _id, name, text, args)

    def clear(self):

        self.clear_all()

    def _setcolors(self, color: ColorControl = None):
        if color in self.colorset:
            return
        self.colorset.add(color)
        self.setcolorstyle()

    def setcolorstyle(self, _=None):
        mp = {}
        for color in self.colorset:
            mp[color.asklass()] = color.get()
        style = self._getstylevalid()
        styleargs = globalconfig["rendertext"]["webview"][style].get("args", {})
        infos = dict(color=mp, style=style, styleargs=styleargs)
        self.debugeval("setcolorstyle('{}')".format(quote(json.dumps(infos))))

    def setfontextra(self, klass: str):
        if not klass:
            return
        setting: dict = globalconfig["fanyi"].get(klass)
        if not setting:
            return
        curr = copy.deepcopy(setting.get("privatefont", {}))
        if curr == self.ts_klass.get(klass, None):
            return
        self.ts_klass[klass] = curr
        self.setfontstyle()

    def resetstyle(self):
        self.refreshcontent()
        self.setcolorstyle()

    ########

    @staticmethod
    def loadex_(extra=None):
        if not extra:
            extra = webview_common.loadextra()
        basepath = r"LunaTranslator\htmlcode\uiwebview\mainui.html"
        if not extra:
            return os.path.abspath(basepath)
        with open(basepath, "r", encoding="utf8") as ff:
            html = ff.read() + extra
        path = gobject.gettempdir("mainui.html")
        with open(path, "w", encoding="utf8") as ff:
            ff.write(html)
        return os.path.abspath(path)

    @staticmethod
    def loadextra():
        if not globalconfig.get("useextrahtml", False):
            return
        for _ in [
            gobject.getconfig("extrahtml.html"),
            r"LunaTranslator\htmlcode\uiwebview\extrahtml\mainui.html",
        ]:
            if not os.path.exists(_):
                continue
            with open(_, "r", encoding="utf8") as ff:
                return ff.read()
