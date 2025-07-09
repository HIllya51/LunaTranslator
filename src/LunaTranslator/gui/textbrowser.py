from qtsymbols import *
from myutils.config import globalconfig
import importlib, copy, os
from traceback import print_exc
from gui.usefulwidget import WebviewWidget
from myutils.mecab import mecab
from gui.rendertext.texttype import TextType, ColorControl
from gui.rendertext.webview import TextBrowser as WebviewTextbrowser
from gui.rendertext.textbrowser import TextBrowser as QtTextbrowser
from network.server.servicecollection_1 import mainuiwsoutputsave, WSForEach
import NativeUtils
import gobject


def checkusewhich():
    if "rendertext_using" not in globalconfig:
        webview2version = NativeUtils.detect_webview2_version()
        if gobject.sys_ge_win8:
            if WebviewWidget.findFixedRuntime():
                # 如果手动放置，那一定选手动的，不管功能完不完整。
                globalconfig["rendertext_using"] = "webview"
            else:
                if webview2version and webview2version >= (100, 0, 0, 0):
                    # <=99的功能不完整
                    globalconfig["rendertext_using"] = "webview"
                else:
                    globalconfig["rendertext_using"] = "textbrowser"
        else:
            # win7上无边框窗口渲染有问题，所以一定不优先
            globalconfig["rendertext_using"] = "textbrowser"


class Textbrowser(QFrame):
    contentsChanged = pyqtSignal(QSize)
    dropfilecallback = pyqtSignal(str)

    def resizeEvent(self, event: QResizeEvent):
        self.textbrowser.resize(event.size())

    def _contentsChanged(self, size: QSize):
        size.setHeight(max(size.height(), globalconfig["min_auto_height"]))
        self.contentsChanged.emit(size)

    def loadinternal(self, shoudong=False, forceReload=False):
        checkusewhich()
        __ = globalconfig["rendertext_using"]
        if (not forceReload) and (self.curr_eng == __):
            return
        self.curr_eng = __
        size = self.size()
        if self.textbrowser:
            self.textbrowser.hide()
            self.textbrowser.contentsChanged.disconnect()
            self.textbrowser.dropfilecallback.disconnect()
            self.textbrowser.deleteLater()
        try:
            tb = {"webview": WebviewTextbrowser, "textbrowser": QtTextbrowser}[__]
            self.textbrowser: QtTextbrowser = tb(self)
        except Exception as e:
            print_exc()
            if shoudong:
                WebviewWidget.showError(e)
            globalconfig["rendertext_using"] = "textbrowser"
            tb = importlib.import_module("gui.rendertext.textbrowser").TextBrowser
            self.textbrowser = tb(self)

        if gobject.sys_le_win7:
            # win7不可以同时FramelessWindowHint和WA_TranslucentBackground，否则会导致无法显示
            # win8没问题
            self.window().setAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground,
                globalconfig["rendertext_using"] == "textbrowser",
            )
        self.textbrowser.move(0, 0)
        self.textbrowser.setMouseTracking(True)
        self.textbrowser.contentsChanged.connect(self._contentsChanged)
        self.textbrowser.dropfilecallback.connect(self.normdropfilepath)
        self.textbrowser.resize(size)
        self.textbrowser.show()
        self.refreshcontent()

    def normdropfilepath(self, file):
        self.dropfilecallback.emit(os.path.normpath(file))

    def refreshcontent(self):
        self.textbrowser.refreshcontent_before()
        traces = self.trace.copy()
        self.clear()
        for t, trace in traces:
            if t == 0:
                self.append(*trace)
            elif t == 1:
                self.iter_append(*trace)
            elif t == 2:
                self.updatetext(*trace)
        self.textbrowser.refreshcontent_after()

    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.textbrowser = None
        self.cleared = True
        self.curr_eng = None
        self.trace = []

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
        self.trace.append(
            (1, (clear, iter_context_class, texttype, name, text, color, klass))
        )
        self.cleared = False
        self.textbrowser.iter_append(
            clear, iter_context_class, texttype, name, text, color, klass
        )
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.iter_append(
                clear, iter_context_class, texttype, name, text, color, klass
            ),
        )

    def scrolltoend(self):
        self.textbrowser.scrolltoend()

    def updatetext(self, texttype: TextType, text, hira, color: ColorControl):
        self.cleared = False
        self.textbrowser.updatetext(texttype, text, mecab.parseastarget(hira), color)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.updatetext(texttype, text, mecab.parseastarget(hira), color),
        )

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
        if clear:
            self.trace.clear()
        self.trace.append(
            (
                0,
                (
                    updateTranslate,
                    clear,
                    texttype,
                    name,
                    text,
                    copy.deepcopy(tag),
                    color,
                    klass,
                ),
            )
        )
        self.cleared = False
        self.textbrowser.append(
            updateTranslate,
            clear,
            texttype,
            name,
            text,
            mecab.parseastarget(tag),
            color,
            klass,
        )
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.append(
                updateTranslate,
                clear,
                texttype,
                name,
                text,
                mecab.parseastarget(tag),
                color,
                klass,
            ),
        )

    def clear(self, isauto=True):
        self.cleared = isauto
        self.trace.clear()
        self.textbrowser.clear()
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.clear(),
        )

    def setcolorstyle(self, _=None):
        self.textbrowser.setcolorstyle()
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.setcolorstyle(),
        )

    def setfontstyle(self, _=None):
        self.textbrowser.setfontstyle()
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.setfontstyle(),
        )

    def setfontextra(self, klass):
        self.textbrowser.setfontextra(klass)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.setfontextra(klass),
        )

    def showhidert(self, _):
        self.textbrowser.showhidert(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showhidert(_),
        )

    def showhideclick(self, _=None):
        self.textbrowser.showhideclick(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showhideclick(_),
        )

    def showhidename(self, _):
        self.textbrowser.showhidename(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showhidename(_),
        )

    def showatcenter(self, _):
        self.textbrowser.showatcenter(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showatcenter(_),
        )

    def showhidetranslate(self, _):
        self.textbrowser.showhidetranslate(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showhidetranslate(_),
        )

    def setselectable(self, _):
        self.textbrowser.setselectable(_)

    def showhideorigin(self, _):
        self.textbrowser.showhideorigin(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showhideorigin(_),
        )

    def settooltipsstyle(self, *_):
        self.textbrowser.settooltipsstyle(*_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.settooltipsstyle(*_),
        )

    def showhideerror(self, _):
        self.textbrowser.showhideerror(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.showhideerror(_),
        )

    def resetstyle(self):
        self.textbrowser.resetstyle()
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.resetstyle(),
        )

    def setdisplayrank(self, type):
        self.textbrowser.setdisplayrank(type)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.setdisplayrank(type),
        )

    def GetSelectedText(self):
        return self.textbrowser.GetSelectedText()

    def sethovercolor(self, color):
        self.textbrowser.sethovercolor(color)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.sethovercolor(color),
        )

    def verticalhorizontal(self, _):
        self.textbrowser.verticalhorizontal(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.verticalhorizontal(_),
        )

    def setwordhoveruse(self, _):
        self.textbrowser.setwordhoveruse(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.setwordhoveruse(_),
        )

    def set_word_hover_show_word_info(self, _):
        self.textbrowser.set_word_hover_show_word_info(_)
        WSForEach(
            mainuiwsoutputsave,
            lambda _1: _1.set_word_hover_show_word_info(_),
        )
