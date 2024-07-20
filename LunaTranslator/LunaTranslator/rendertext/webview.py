from qtsymbols import *
from rendertext.somefunctions import dataget
import gobject, uuid, json, os, functools, windows, time
from urllib.parse import quote
from myutils.config import globalconfig, static_data
from myutils.wrapper import tryprint, threader
from gui.usefulwidget import WebivewWidget, QWebWrap

testsavejs = False


class TextBrowser(QWidget, dataget):
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
        self.masklabel.resize(event.size())
        self.__makeborder(event.size())

    def setselectable(self, b):
        self.masklabel.setHidden(b)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        if globalconfig["rendertext_using"] == "QWebEngine":
            self.webivewwidget = QWebWrap(self)
            self.webivewwidget.on_load.connect(self.__loadextra)
        else:
            # webview2当会执行alert之类的弹窗js时，若qt窗口不可视，会卡住
            self.webivewwidget = WebivewWidget(self, usedarklight=False)

            # webview2无法接收qt事件。
            webviewhwnd = self.webivewwidget.get_hwnd()
            self.wndproc = windows.WNDPROCTYPE(
                functools.partial(
                    self.extrahandle,
                    windows.GetWindowLongPtr(webviewhwnd, windows.GWLP_WNDPROC),
                )
            )
            windows.SetWindowLongPtr(webviewhwnd, windows.GWLP_WNDPROC, self.wndproc)
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

        self.masklabel = QLabel(self.webivewwidget)
        self.masklabel.setMouseTracking(True)
        self.webivewwidget.navigate(
            os.path.abspath(r"LunaTranslator\rendertext\webview.html")
        )
        self.webivewwidget.set_transparent_background()
        self.webivewwidget.bind("calllunaclickedword", self.calllunaclickedword)
        self.webivewwidget.bind("calllunaheightchange", self.calllunaheightchange)
        self.saveiterclasspointer = {}
        self.isfirst = True
        self._qweb_query_word()

    @threader
    def trackingthread(self):
        pos = gobject.baseobject.translation_ui.pos()
        cus = QCursor.pos()
        while True:
            keystate = windows.GetKeyState(windows.VK_LBUTTON)
            if keystate >= 0:
                break
            gobject.baseobject.translation_ui.move_signal.emit(
                pos + QCursor.pos() - cus
            )
            time.sleep(0.01)

    def extrahandle(self, orig, hwnd, msg, wp, lp):
        if wp == windows.WM_LBUTTONDOWN:
            # 因为有父窗口，所以msg是WM_PARENTNOTIFY，wp才是WM_LBUTTONDOWN
            # 而且SetCapture后会立即被父窗口把capture夺走，无法后面的释放&移动，所以只能开个线程来弄
            if self.masklabel.isVisible():
                self.trackingthread()
        return windows.WNDPROCTYPE(orig)(hwnd, msg, wp, lp)

    @tryprint
    def showEvent(self, e):
        if not self.isfirst:
            return
        if not isinstance(self.webivewwidget, WebivewWidget):
            return
        self.isfirst = False
        self.__loadextra(0)
        self.webivewwidget.on_load.connect(self.__loadextra)

    def __loadextra(self, _):
        if os.path.exists("userconfig/extrahtml.html"):
            with open("userconfig/extrahtml.html", "r", encoding="utf8") as ff:
                self.set_extra_html(ff.read())

    def debugeval(self, js):
        # print(js)
        self.webivewwidget.eval(js)

    # js api

    def create_div_line_id(self, _id):
        self.debugeval(f'create_div_line_id("{_id}");')

    def clear_all(self):
        self.debugeval(f"clear_all()")

    def set_extra_html(self, html):
        html = quote(html)
        self.debugeval(f'set_extra_html("{html}")')

    def create_internal_text(self, style, styleargs, _id, text, args):
        text = quote(text)
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            f'create_internal_text("{style}","{styleargs}","{_id}","{text}","{args}");'
        )
        self._qweb_query_h()

    def create_internal_rubytext(self, style, styleargs, _id, tag, args):
        tag = quote(json.dumps(tag))
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            f'create_internal_rubytext("{style}","{styleargs}","{_id}","{tag}","{args}");'
        )

        self._qweb_query_h()

    # js api end
    # native api
    def _qweb_query_value_callback(self, name, callback):

        def __receiver(callback, value):
            if not value:
                return
            self.webivewwidget.eval(f"{name}=null")
            callback(value)

        self.webivewwidget.eval(name, functools.partial(__receiver, callback))

    def _qweb_query_h(self):
        if not isinstance(self.webivewwidget, QWebWrap):
            return
        self._qweb_query_value_callback("window.__resolve_h", self.calllunaheightchange)

    def _qweb_query_word(self):
        if not isinstance(self.webivewwidget, QWebWrap):
            return
        t = QTimer(self)
        t.setInterval(100)

        def __intervaledqueryword():

            self._qweb_query_value_callback(
                "window.__resolve_word", self.calllunaclickedword
            )

        t.timeout.connect(__intervaledqueryword)
        t.timeout.emit()
        t.start()

    def calllunaheightchange(self, h):
        self.contentsChanged.emit(
            QSize(
                self._padding * 2 + self.width(),
                1 + self._padding * 2 + int(h * self.webivewwidget.get_zoom()),
            )
        )

    def calllunaclickedword(self, wordinfo):
        gobject.baseobject.clickwordcallback(wordinfo, False)

    # native api end

    def iter_append(self, iter_context_class, origin, atcenter, text, color, cleared):

        if iter_context_class not in self.saveiterclasspointer:
            _id = self.createtextlineid()
            self.saveiterclasspointer[iter_context_class] = _id

        _id = self.saveiterclasspointer[iter_context_class]
        self._webview_append(_id, origin, atcenter, text, [], [], color)

    def createtextlineid(self):

        _id = f"luna_{uuid.uuid4()}"
        self.create_div_line_id(_id)
        return _id

    def append(self, origin, atcenter, text, tag, flags, color, cleared):

        _id = self.createtextlineid()
        self._webview_append(_id, origin, atcenter, text, tag, flags, color)

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

    def _webview_append(self, _id, origin, atcenter, text, tag, flags, color):

        fmori, fsori, boldori = self._getfontinfo(origin)
        fmkana, fskana, boldkana = self._getfontinfo_kana()
        kanacolor = self._getkanacolor()
        line_height = self.measureH(fmori, fsori) + globalconfig["extra_space"]
        style = self._getstylevalid()

        styleargs = globalconfig["rendertext"]["webview"][style].get("args", {})
        if len(tag):
            isshowhira, isshow_fenci, isfenciclick = flags
            if isshow_fenci:
                for word in tag:
                    color1 = self._randomcolor(word)
                    word["color"] = color1
            args = dict(
                atcenter=atcenter,
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
            args = dict(
                atcenter=atcenter,
                fm=fmori,
                fs=fsori,
                bold=boldori,
                color=color,
                line_height=line_height,
            )
            self.create_internal_text(style, styleargs, _id, text, args)

    def clear(self):

        self.clear_all()
        self.saveiterclasspointer.clear()
