from qtsymbols import *
from rendertext.somefunctions import dataget
import gobject, uuid, json, os, functools, windows, time
from urllib.parse import quote
from myutils.utils import threader
from myutils.config import globalconfig, static_data, _TR
from myutils.wrapper import tryprint, threader
from gui.usefulwidget import WebivewWidget
from gui.textbrowser import TextType

testsavejs = False


class TextBrowser(QWidget, dataget):
    dropfilecallback = pyqtSignal(str)
    contentsChanged = pyqtSignal(QSize)
    _padding = 5

    def __makeborder(self, size: QSize):
        _padding = self._padding
        self.masklabel_top.setGeometry(0, 0, size.width(), _padding)

        self.masklabel_left.setGeometry(0, 0, _padding, size.height())
        self.masklabel_right.setGeometry(
            self.width() - _padding, 0, _padding, size.height()
        )
        self.masklabel_bottom.setGeometry(
            0, size.height() - _padding, size.width(), _padding
        )

    @tryprint
    def resizeEvent(self, event: QResizeEvent):
        self.webivewwidget.setGeometry(
            self._padding,
            self._padding,
            event.size().width() - 2 * self._padding,
            event.size().height() - 2 * self._padding,
        )
        self.__makeborder(event.size())

    def setselectable(self, b):
        self.selectable = b
        self.debugeval("setselectable({})".format(int(b)))

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.selectable = False
        # webview2当会执行alert之类的弹窗js时，若qt窗口不可视，会卡住
        self.webivewwidget = WebivewWidget(self)

        webviewhwnd = self.webivewwidget.get_hwnd()
        self.wndproc = windows.WNDPROCTYPE(
            functools.partial(
                self.extrahandle,
                windows.GetWindowLongPtr(webviewhwnd, windows.GWLP_WNDPROC),
            )
        )
        windows.SetWindowLongPtr(webviewhwnd, windows.GWLP_WNDPROC, self.wndproc)
        self.webivewwidget.add_menu(
            0,
            _TR("朗读"),
            lambda w: gobject.baseobject.read_text(w.replace("\n", "").strip()),
        )
        self.webivewwidget.add_menu(
            0,
            _TR("翻译"),
            lambda w: gobject.baseobject.textgetmethod(w.replace("\n", "").strip()),
        )
        self.webivewwidget.add_menu(
            0,
            _TR("查词"),
            threader(
                lambda w: gobject.baseobject.searchwordW.search_word.emit(
                    w.replace("\n", "").strip(), False
                )
            ),
        )
        self.masklabel_left = QLabel(self)
        self.masklabel_left.setMouseTracking(True)
        # self.masklabel_left.setStyleSheet('background-color:red')
        self.masklabel_right = QLabel(self)
        # self.masklabel_right.setStyleSheet('background-color:red')
        self.masklabel_right.setMouseTracking(True)
        self.masklabel_bottom = QLabel(self)
        self.masklabel_bottom.setMouseTracking(True)
        self.masklabel_top = QLabel(self)
        self.masklabel_top.setMouseTracking(True)
        # self.masklabel_bottom.setStyleSheet('background-color:red')
        self.webivewwidget.navigate(
            os.path.abspath(r"LunaTranslator\rendertext\webview.html")
        )
        self.webivewwidget.set_transparent_background()
        self.webivewwidget.dropfilecallback.connect(self.dropfilecallback)
        self.webivewwidget.bind(
            "calllunaclickedword", gobject.baseobject.clickwordcallback
        )
        self.webivewwidget.bind("calllunaheightchange", self.calllunaheightchange)
        self.saveiterclasspointer = {}
        self.isfirst = True

    @threader
    def trackingthread(self):
        pos = gobject.baseobject.translation_ui.pos()
        gobject.baseobject.translation_ui._move_drag = True
        cus = QCursor.pos()
        while True:
            keystate = windows.GetKeyState(windows.VK_LBUTTON)
            if keystate >= 0:
                break
            gobject.baseobject.translation_ui.move_signal.emit(
                pos + QCursor.pos() - cus
            )
            time.sleep(0.01)
        gobject.baseobject.translation_ui._move_drag = False

    def extrahandle(self, orig, hwnd, msg, wp, lp):
        if wp == windows.WM_LBUTTONDOWN:
            # 因为有父窗口，所以msg是WM_PARENTNOTIFY，wp才是WM_LBUTTONDOWN
            # 而且SetCapture后会立即被父窗口把capture夺走，无法后面的释放&移动，所以只能开个线程来弄
            if not self.selectable:
                self.trackingthread()
        return windows.WNDPROCTYPE_1(orig)(hwnd, msg, wp, lp)

    @tryprint
    def showEvent(self, e):
        if not self.isfirst:
            return
        if not isinstance(self.webivewwidget, WebivewWidget):
            return
        self.isfirst = False
        self.loadextra(0)
        self.webivewwidget.on_load.connect(self.loadextra)

    def loadextra(self, _):
        for _ in [
            "userconfig/extrahtml.html",
            r"LunaTranslator\rendertext\exampleextrahtml.html",
        ]:
            if not os.path.exists(_):
                continue
            with open(_, "r", encoding="utf8") as ff:
                self.set_extra_html(ff.read())
            break

    def debugeval(self, js):
        # print(js)
        self.webivewwidget.eval(js)

    # js api
    def showatcenter(self, show):
        self.debugeval('showatcenter("{}")'.format(int(show)))

    def showhidetranslate(self, show):
        self.debugeval('showhidetranslate("{}")'.format(int(show)))

    def showhideorigin(self, show):
        self.debugeval('showhideorigin("{}")'.format(int(show)))

    def showhideerror(self, show):
        self.debugeval('showhideerror("{}")'.format(int(show)))

    def create_div_line_id(self, _id, textype: TextType):
        self.debugeval('create_div_line_id("{}",{})'.format(_id, textype))

    def clear_all(self):
        self.debugeval("clear_all()")

    def set_extra_html(self, html):
        if not globalconfig["useextrahtml"]:
            self.debugeval('set_extra_html("")')
            return
        html = quote(html)
        self.debugeval('set_extra_html("{}")'.format(html))

    def create_internal_text(self, style, styleargs, _id, text, args):
        text = quote(text)
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            'create_internal_text("{}","{}","{}","{}","{}");'.format(
                style, styleargs, _id, text, args
            )
        )

    def create_internal_rubytext(self, style, styleargs, _id, tag, args):
        tag = quote(json.dumps(tag))
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            'create_internal_rubytext("{}","{}","{}","{}","{}");'.format(
                style, styleargs, _id, tag, args
            )
        )

    def calllunaheightchange(self, h):
        extra_space = globalconfig["extra_space"]
        extra_space_trans = globalconfig["extra_space_trans"]
        h += -min(0, extra_space, extra_space_trans)
        self.contentsChanged.emit(
            QSize(
                self._padding * 2 + self.width(),
                1 + self._padding * 2 + int(h * self.webivewwidget.get_zoom()),
            )
        )

    # native api end

    def iter_append(self, iter_context_class, textype: TextType, text, color):

        if iter_context_class not in self.saveiterclasspointer:
            _id = self.createtextlineid(textype)
            self.saveiterclasspointer[iter_context_class] = _id

        _id = self.saveiterclasspointer[iter_context_class]
        self._webview_append(_id, textype, text, [], [], color)

    def createtextlineid(self, textype: TextType):

        _id = "luna_{}".format(uuid.uuid4())
        self.create_div_line_id(_id, textype)
        return _id

    def append(self, textype: TextType, text, tag, flags, color):
        _id = self.createtextlineid(textype)
        self._webview_append(_id, textype, text, tag, flags, color)

    def measureH(self, font_family, font_size):
        font = QFont()
        font.setFamily(font_family)
        font.setPointSizeF(font_size)
        fmetrics = QFontMetrics(font)

        return fmetrics.height()

    def _getstylevalid(self):
        currenttype = globalconfig["rendertext_using_internal"]["webview"]
        if currenttype not in static_data["textrender"]["webview"]:
            currenttype = static_data["textrender"]["webview"][0]
            globalconfig["rendertext_using_internal"]["webview"] = static_data[
                "textrender"
            ]["webview"][0]
        return currenttype

    def _webview_append(self, _id, textype: TextType, text: str, tag, flags, color):
        fmori, fsori, boldori = self._getfontinfo(textype)
        fmkana, fskana, boldkana = self._getfontinfo_kana()
        kanacolor = self._getkanacolor()
        line_height = self.measureH(fmori, fsori) + (
            globalconfig["extra_space"]
            if (textype == TextType.Origin)
            else globalconfig["extra_space_trans"]
        )
        style = self._getstylevalid()

        styleargs = globalconfig["rendertext"]["webview"][style].get("args", {})
        if len(tag):
            isshowhira, isshow_fenci, isfenciclick = flags
            if isshow_fenci:
                for word in tag:
                    color1 = self._randomcolor(word)
                    word["color"] = color1
            args = dict(
                fmori=fmori,
                fsori=fsori,
                boldori=boldori,
                color=color,
                fmkana=fmkana,
                fskana=fskana,
                boldkana=boldkana,
                kanacolor=kanacolor,
                isshowhira=isshowhira,
                isshow_fenci=isshow_fenci,
                isfenciclick=isfenciclick,
                line_height=line_height,
            )
            self.create_internal_rubytext(style, styleargs, _id, tag, args)
        else:
            sig = "LUNASHOWHTML"
            userawhtml = text.startswith(sig)
            if userawhtml:
                text = text[len(sig) :]

            args = dict(
                fontFamily=fmori,
                fontSize=fsori,
                bold=boldori,
                color=color,
                lineHeight=line_height,
                userawhtml=userawhtml,
            )

            self.create_internal_text(style, styleargs, _id, text, args)

    def clear(self):

        self.clear_all()
        self.saveiterclasspointer.clear()
