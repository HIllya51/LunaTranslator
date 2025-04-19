from qtsymbols import *
from gui.rendertext.texttype import (
    dataget,
    TextType,
    ColorControl,
    SpecialColor,
    FenciColor,
)
import gobject, hashlib, json, os, functools
from urllib.parse import quote
from myutils.config import globalconfig, static_data, _TR
from myutils.wrapper import threader
import copy, uuid
from gui.usefulwidget import WebviewWidget
from sometypes import WordSegResult


class wordwithcolor:
    def __init__(self, word: WordSegResult, color: str):
        self.word = word
        self.color = color

    def as_dict(self):
        d = self.word.as_dict()
        d.update(color=self.color)
        return d


class somecommon(dataget):
    def __init__(self):
        self.colorset = set()
        self.ts_klass = {}
        self.saveiterclasspointer = {}

    def debugeval(self, js: str): ...
    def refreshcontent(self): ...
    def calllunaloadready(self):
        self.colorset.clear()
        self.ts_klass.clear()
        self.setselectable(globalconfig["selectable"])
        self.showhideerror(globalconfig["showtranexception"])
        self.showhideorigin(globalconfig["isshowrawtext"])
        self.showhidetranslate(globalconfig["showfanyi"])
        self.showhidename(globalconfig["showfanyisource"])
        self.showatcenter(globalconfig["showatcenter"])
        self.showhideclick()
        self.showhidert(globalconfig["isshowhira"])
        self.setfontstyle()
        self.setdisplayrank(globalconfig["displayrank"])
        self.sethovercolor(globalconfig["hovercolor"])
        self.verticalhorizontal(globalconfig["verticalhorizontal"])
        self.refreshcontent()

    # js api
    def sethovercolor(self, color):
        self.debugeval('sethovercolor("{}")'.format(quote(color)))

    def setdisplayrank(self, rank):
        self.debugeval("setdisplayrank({})".format(int(rank)))

    def setselectable(self, b):
        self.debugeval("setselectable({})".format(int(b)))

    def showatcenter(self, show):
        self.debugeval("showatcenter({})".format(int(show)))

    def showhidert(self, show):
        self.debugeval("showhidert({})".format(int(show)))

    def showhideclick(self, _=None):
        show = globalconfig["usesearchword"] or globalconfig["usecopyword"]
        self.debugeval("showhideclick({})".format(int(show)))

    def showhidename(self, show):
        self.debugeval("showhidename({})".format(int(show)))

    def showhidetranslate(self, show):
        self.debugeval("showhidetranslate({})".format(int(show)))

    def showhideorigin(self, show):
        self.debugeval("showhideorigin({})".format(int(show)))

    def verticalhorizontal(self, v):
        self.debugeval("verticalhorizontal({})".format(int(v)))

    def showhideerror(self, show):
        self.debugeval("showhideerror({})".format(int(show)))

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

        def loadfont(argc, lhdict=None):
            fm, fs, bold = argc
            args = dict(fontFamily=fm, fontSize=fs, bold=bold)
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

    def clear_all(self):
        self.debugeval("clear_all()")

    def create_internal_text(self, style, styleargs, _id, name, text, args):
        name = quote(name)
        text = quote(text)
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            'create_internal_text("{}","{}","{}","{}","{}","{}");'.format(
                style, styleargs, _id, name, text, args
            )
        )

    def create_internal_rubytext(
        self, style, styleargs, _id, tag: "list[wordwithcolor]", args
    ):
        tag = quote(json.dumps(tuple(_.as_dict() for _ in tag)))
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            'create_internal_rubytext("{}","{}","{}","{}","{}");'.format(
                style, styleargs, _id, tag, args
            )
        )

    def iter_append(
        self,
        iter_context_class,
        texttype: TextType,
        name,
        text,
        color: ColorControl,
        klass,
    ):

        if iter_context_class not in self.saveiterclasspointer:
            _id = self.createtextlineid(texttype, klass)
            self.saveiterclasspointer[iter_context_class] = _id

        _id = self.saveiterclasspointer[iter_context_class]
        self._webview_append(_id, name, text, [], color)

    def createtextlineid(self, texttype: TextType, klass: str):
        self.setfontextra(klass)
        _id = "luna_{}".format(uuid.uuid4())
        self.create_div_line_id(_id, texttype, klass)
        return _id

    def append(self, texttype: TextType, name, text, tag, color: ColorControl, klass):
        _id = self.createtextlineid(texttype, klass)
        self._webview_append(_id, name, text, tag, color)

    def _getstylevalid(self):
        currenttype = globalconfig["rendertext_using_internal"]["webview"]
        if currenttype not in static_data["textrender"]["webview"]:
            currenttype = static_data["textrender"]["webview"][0]
            globalconfig["rendertext_using_internal"]["webview"] = static_data[
                "textrender"
            ]["webview"][0]
        return currenttype

    def _webview_append(
        self, _id, name, text: str, tag: "list[WordSegResult]", color: ColorControl
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
            self.create_internal_rubytext(style, styleargs, _id, tagx, args)
        else:
            sig = "LUNASHOWHTML"
            userawhtml = text.startswith(sig)
            if userawhtml:
                text = text[len(sig) :]

            args = dict(color=color.asklass(), userawhtml=userawhtml)

            self.create_internal_text(style, styleargs, _id, name, text, args)

    def clear(self):

        self.clear_all()
        self.saveiterclasspointer.clear()

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
        curr = copy.deepcopy(globalconfig["fanyi"][klass].get("privatefont", {}))
        if curr == self.ts_klass.get(klass, None):
            return
        self.ts_klass[klass] = curr
        self.setfontstyle()

    def resetstyle(self):
        self.refreshcontent()
        self.setcolorstyle()


class TextBrowser(WebviewWidget, somecommon):
    contentsChanged = pyqtSignal(QSize)
    _switchcursor = pyqtSignal(Qt.CursorShape)
    _isDragging = pyqtSignal(bool)

    def __init__(self, parent) -> None:
        super().__init__(parent, transp=True, loadext=globalconfig["webviewLoadExt"])
        # webview2当会执行alert之类的弹窗js时，若qt窗口不可视，会卡住
        self.setMouseTracking(True)
        nexti = self.add_menu(
            0,
            lambda: _TR("查词"),
            threader(
                lambda w: gobject.baseobject.searchwordW.search_word.emit(
                    w.replace("\n", "").strip(), False
                )
            ),
        )
        nexti = self.add_menu(
            nexti,
            lambda: _TR("翻译"),
            lambda w: gobject.baseobject.textgetmethod(w.replace("\n", "").strip()),
        )
        nexti = self.add_menu(
            nexti,
            lambda: _TR("朗读"),
            lambda w: gobject.baseobject.read_text(w.replace("\n", "").strip()),
        )
        self.add_menu_noselect(0, lambda: _TR("清空"), self.___cleartext)
        self.bind("calllunaclickedword", gobject.baseobject.clickwordcallback)
        self.bind("calllunaMouseMove", self.calllunaMouseMove)
        self.bind("calllunaMousePress", self.calllunaMousePress)
        self.bind("calllunaMouseRelease", self.calllunaMouseRelease)
        self.bind("calllunaheightchange", self.calllunaheightchange)
        self.bind("calllunaEnter", self.calllunaEnter)
        self.bind("calllunaLeave", self.calllunaLeave)
        self.bind("calllunaloadready", self.calllunaloadready)
        self.set_zoom(globalconfig.get("ZoomFactor2", 1))
        self.on_ZoomFactorChanged.connect(
            functools.partial(globalconfig.__setitem__, "ZoomFactor2")
        )
        self.isfirst = True
        self.window().cursorSet.connect(self._switchcursor)
        self._switchcursor.connect(self.switchcursor)
        self.window().isDragging.connect(self._isDragging)
        self._isDragging.connect(
            lambda b: self.setselectable(False if b else globalconfig["selectable"])
        )
        self.loadex()

    def ___cleartext(self):
        self.parent().clear()
        gobject.baseobject.currenttext = ""

    def refreshcontent(self):
        gobject.baseobject.translation_ui.translate_text.refreshcontent()

    def refreshcontent_before(self):
        self.debugeval("refreshcontent_before()")

    def refreshcontent_after(self):
        self.debugeval("refreshcontent_after()")

    def switchcursor(self, cursor):
        cursor_map = {
            Qt.CursorShape.ArrowCursor: "default",
            Qt.CursorShape.UpArrowCursor: "n-resize",
            Qt.CursorShape.CrossCursor: "crosshair",
            Qt.CursorShape.WaitCursor: "wait",
            Qt.CursorShape.IBeamCursor: "text",
            Qt.CursorShape.SizeVerCursor: "ns-resize",
            Qt.CursorShape.SizeHorCursor: "ew-resize",
            Qt.CursorShape.SizeBDiagCursor: "nesw-resize",
            Qt.CursorShape.SizeFDiagCursor: "nwse-resize",
            Qt.CursorShape.SizeAllCursor: "move",
            Qt.CursorShape.BlankCursor: "none",
            Qt.CursorShape.SplitVCursor: "row-resize",
            Qt.CursorShape.SplitHCursor: "col-resize",
            Qt.CursorShape.PointingHandCursor: "pointer",
            Qt.CursorShape.ForbiddenCursor: "not-allowed",
            Qt.CursorShape.WhatsThisCursor: "help",
            Qt.CursorShape.BusyCursor: "progress",
            Qt.CursorShape.OpenHandCursor: "grab",
            Qt.CursorShape.ClosedHandCursor: "grabbing",
        }
        self.eval('switchcursor("{}")'.format(cursor_map.get(cursor, "default")))

    def loadex(self, extra=None):
        self.navigate(self.loadex_(extra=extra))

    @staticmethod
    def loadex_(extra=None):
        if not extra:
            extra = TextBrowser.loadextra()
        basepath = r"files\html\uiwebview\mainui.html"
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
        if not globalconfig["useextrahtml"]:
            return
        for _ in [
            "userconfig/extrahtml.html",
            r"files\html\uiwebview\extrahtml\mainui.html",
        ]:
            if not os.path.exists(_):
                continue
            with open(_, "r", encoding="utf8") as ff:
                return ff.read()

    def debugeval(self, js):
        # print(js)
        self.eval(js)

    def calllunaheightchange(self, h):
        self.contentsChanged.emit(
            QSize(
                self.width(),
                int(h * self.get_zoom()),
            )
        )

    def parsemousebutton(self, i):
        btn_map = {
            0: Qt.MouseButton.LeftButton,
            1: Qt.MouseButton.MiddleButton,
            2: Qt.MouseButton.RightButton,
            3: Qt.MouseButton.BackButton,
            4: Qt.MouseButton.ForwardButton,
        }
        return btn_map.get(i, Qt.MouseButton.NoButton)

    def parsexyaspos(self, x, y):
        zoom = self.get_zoom()
        x = zoom * x
        y = zoom * y
        return QPointF(x, y)

    def calllunaMousePress(self, btn, x, y):
        pos = self.parsexyaspos(x, y)
        btn = self.parsemousebutton(btn)
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            pos,
            btn,
            btn,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(self, event)

    def calllunaEnter(self):
        QApplication.sendEvent(self.window(), QEvent(QEvent.Type.Enter))

    def calllunaLeave(self):
        QApplication.sendEvent(self.window(), QEvent(QEvent.Type.Leave))

    def calllunaMouseRelease(self, btn, x, y):
        pos = self.parsexyaspos(x, y)
        btn = self.parsemousebutton(btn)
        event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            pos,
            btn,
            btn,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(self, event)

    def calllunaMouseMove(self, x, y):
        if globalconfig["selectable"] and globalconfig["selectableEx"]:
            return
        pos = self.parsexyaspos(x, y)
        event = QMouseEvent(
            QEvent.Type.MouseMove,
            pos,
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(self, event)

    def GetSelectedText(self):
        ret = []
        self.eval("getCleanSelectionText()", ret.append)
        if ret:
            return json.loads(ret[0])
