from qtsymbols import *
import functools
import qtawesome, winsharedutils, threading
from myutils.config import globalconfig
from myutils.utils import get_time_stamp
from gui.usefulwidget import closeashidewindow
from gui.dynalang import LAction


class transhist(closeashidewindow):

    getnewsentencesignal = pyqtSignal(str)
    getnewtranssignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(transhist, self).__init__(parent, globalconfig["hist_geo"])
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.getnewtranssignal.connect(self.getnewtrans)
        self.hiderawflag = False
        self.hideapiflag = False
        self.hidetime = True
        self.trace = []
        self.lock = threading.Lock()
        self.setWindowTitle("历史翻译")

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"))

        textOutput = QPlainTextEdit()
        textOutput.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        textOutput.customContextMenuRequested.connect(
            functools.partial(self.showmenu, textOutput)
        )
        textOutput.setUndoRedoEnabled(False)
        textOutput.setReadOnly(True)

        self.textOutput = textOutput
        self.setCentralWidget(self.textOutput)


    def showmenu(self, tb, p):
        menu = QMenu(self)
        qingkong = LAction("清空")
        baocun = LAction("保存")
        copy = LAction("复制")
        hideshowraw = LAction("显示原文")
        hideshowraw.setCheckable(True)
        hideshowraw.setChecked(not self.hiderawflag)
        hideshowapi = LAction("显示翻译器名称")
        hideshowapi.setCheckable(True)
        hideshowapi.setChecked(not self.hideapiflag)
        hidetime = LAction("显示时间")
        hidetime.setCheckable(True)
        hidetime.setChecked(not self.hidetime)
        scrolltoend = LAction("滚动到最后")
        if len(self.textOutput.textCursor().selectedText()):
            menu.addAction(copy)
            menu.addSeparator()
        menu.addAction(qingkong)
        menu.addAction(baocun)
        menu.addAction(scrolltoend)
        menu.addSeparator()
        menu.addAction(hideshowraw)
        menu.addAction(hideshowapi)
        menu.addAction(hidetime)

        action = menu.exec(QCursor.pos())
        if action == qingkong:
            tb.clear()
        elif action == copy:
            winsharedutils.clipboard_set(self.textOutput.textCursor().selectedText())
        elif action == baocun:
            ff = QFileDialog.getSaveFileName(self, directory="save.txt")
            if ff[0] == "":
                return
            with open(ff[0], "w", encoding="utf8") as ff:
                ff.write(tb.toPlainText())
        elif action == hideshowraw:
            self.hiderawflag = not self.hiderawflag
            self.refresh()
        elif action == hidetime:
            self.hidetime = not self.hidetime
            self.refresh()
        elif action == hideshowapi:
            self.hideapiflag = not self.hideapiflag
            self.refresh()
        elif action == scrolltoend:
            scrollbar = self.textOutput.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def refresh(self):
        with self.lock:
            self.textOutput.setPlainText(
                "\n".join(self.visline(line) for line in self.trace)
            )

    def visline(self, line):
        ii, line = line
        if ii == 0:
            tm, sentence = line
            if self.hiderawflag:
                sentence = ""
            else:
                if not self.hidetime:
                    sentence = tm + " " + sentence
                sentence = "\n" + sentence
            return sentence
        elif ii == 1:
            tm, api, sentence = line
            if not self.hideapiflag:
                sentence = api + " " + sentence
            if not self.hidetime:
                sentence = tm + " " + sentence
            return sentence

    def getnewsentence(self, sentence):
        with self.lock:
            tm = get_time_stamp()
            self.trace.append((0, (tm, sentence)))
            self.textOutput.appendPlainText(self.visline(self.trace[-1]))

    def getnewtrans(self, api, sentence):
        with self.lock:
            tm = get_time_stamp()
            self.trace.append((1, (tm, api, sentence)))
            self.textOutput.appendPlainText(self.visline(self.trace[-1]))
