from PyQt5.QtWidgets import QWidget
from qtsymbols import *
from rendertext.somefunctions import dataget
import gobject, uuid, json, os
from urllib.parse import quote
from myutils.config import globalconfig
from gui.usefulwidget import WebivewWidget

testsavejs = False


class TextBrowser(QWidget, dataget):
    contentsChanged = pyqtSignal(QSize)

    def resizeEvent(self, event: QResizeEvent):
        self.webivewwidget.resize(event.size().width(), event.size().height())

    def __init__(self, parent) -> None:
        gobject.refwebview = self
        super().__init__(parent)
        self.webivewwidget = WebivewWidget(self)
        self.webivewwidget.navigate(
            os.path.abspath(r"LunaTranslator\rendertext\webview.html")
        )
        self.webivewwidget.set_transparent_background()
        self.webivewwidget.webview.bind("calllunaclickedword", self.calllunaclickedword)
        self.webivewwidget.webview.bind(
            "calllunaheightchange", self.calllunaheightchange
        )
        self.saveiterclasspointer = {}
        self.isfirst = True

    def showEvent(self, e):
        if not self.isfirst:
            return

        self.isfirst = False
        if os.path.exists("userconfig/extrahtml.html"):
            with open("userconfig/extrahtml.html", "r", encoding="utf8") as ff:
                self.set_extra_html(ff.read())

    def debugeval(self, js):
        # print(js)
        self.webivewwidget.webview.eval(js)

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

    def create_internal_rubytext(self, style, styleargs, _id, tag, args):
        tag = quote(json.dumps(tag))
        args = quote(json.dumps(args))
        styleargs = quote(json.dumps(styleargs))
        self.debugeval(
            f'create_internal_rubytext("{style}","{styleargs}","{_id}","{tag}","{args}");'
        )

    # js api end
    # native api

    def calllunaheightchange(self, h):
        self.contentsChanged.emit(
            QSize(self.width(), int(h * self.webivewwidget.get_ZoomFactor()))
        )

    def calllunaclickedword(self, packedwordinfo):
        gobject.baseobject.clickwordcallback(packedwordinfo, False)

    # native api end

    def setselectable(self, b):
        pass

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

    def _webview_append(self, _id, origin, atcenter, text, tag, flags, color):

        fmori, fsori, boldori = self._getfontinfo(origin)
        fmkana, fskana, boldkana = self._getfontinfo_kana()
        kanacolor = self._getkanacolor()
        line_height = self.measureH(fmori, fsori) + globalconfig["extra_space"]
        style = globalconfig["rendertext_using_internal"]["webview"]
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
