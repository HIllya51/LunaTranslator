from qtsymbols import *
from myutils.config import globalconfig
import importlib, copy
from webviewpy import webview_exception
from gui.usefulwidget import getQMessageBox
from traceback import print_exc


class Textbrowser(QFrame):
    contentsChanged = pyqtSignal(QSize)

    def resizeEvent(self, event: QResizeEvent):
        self.textbrowser.resize(event.size())

    def _contentsChanged(self, size: QSize):
        self.contentsChanged.emit(size)

    def loadinternal(self):
        __ = globalconfig["rendertext_using"]
        if self.curr_eng == __:
            return
        self.curr_eng = __
        size = self.size()
        if self.textbrowser:
            self.textbrowser.hide()
            self.textbrowser.contentsChanged.disconnect()
            self.textbrowser.deleteLater()
        if __ == "QWebEngine":
            __ = "webview"
        try:
            tb = importlib.import_module(f"rendertext.{__}").TextBrowser
            self.textbrowser = tb(self)
        except Exception as e:
            if isinstance(e, webview_exception):
                getQMessageBox(
                    None,
                    "错误",
                    "can't find Webview2 runtime!",
                )
            elif isinstance(e, (ImportError, ModuleNotFoundError)):
                getQMessageBox(
                    None,
                    "错误",
                    "can't find QWebEngine!",
                )
            else:
                print_exc()
            globalconfig["rendertext_using"] = "textbrowser"
            tb = importlib.import_module(f"rendertext.textbrowser").TextBrowser
            self.textbrowser = tb(self)
        self.textbrowser.move(0, 0)
        self.textbrowser.setMouseTracking(True)
        self.textbrowser.contentsChanged.connect(self._contentsChanged)
        self.textbrowser.resize(size)
        self.textbrowser.show()
        self.textbrowser.setselectable(globalconfig["selectable"])
        self.textbrowser.showhideorigin(globalconfig["isshowrawtext"])
        self.textbrowser.showhidetranslate(globalconfig["showfanyi"])
        self.refreshcontent()

    def refreshcontent(self):
        traces = self.trace.copy()
        self.clear()
        for t, trace in traces:
            if t == 0:
                self.append(*trace)
            elif t == 1:
                self.iter_append(*trace)

    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.textbrowser = None
        self.cleared = True
        self.curr_eng = None
        self.trace = []
        self.loadinternal()

    def iter_append(self, iter_context_class, origin, atcenter, text, color):
        self.trace.append((1, (iter_context_class, origin, atcenter, text, color)))
        self.cleared = False
        self.textbrowser.iter_append(iter_context_class, origin, atcenter, text, color)

    def append(self, origin, atcenter, text, tag, flags, color):
        self.trace.append(
            (0, (origin, atcenter, text, copy.deepcopy(tag), flags, color))
        )
        self.cleared = False
        self.textbrowser.append(origin, atcenter, text, tag, flags, color)

    def clear(self):
        self.cleared = True
        self.trace.clear()
        self.textbrowser.clear()
