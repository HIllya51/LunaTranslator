from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QTextBrowser, QAction, QMenu, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
import qtawesome, functools

from gui.usefulwidget import closeashidewindow, textbrowappendandmovetoend
from myutils.config import globalconfig, _TR


class transhist(closeashidewindow):

    getnewsentencesignal = pyqtSignal(str)
    getnewtranssignal = pyqtSignal(str, str)
    getdebuginfosignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(transhist, self).__init__(parent, globalconfig, "hist_geo")
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.getnewtranssignal.connect(self.getnewtrans)
        self.getdebuginfosignal.connect(self.debugprint)
        self.hiderawflag = False
        self.hideapiflag = False

        self.setWindowTitle(_TR("历史翻译和调试输出"))

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"))
        self.tabwidget = QTabWidget()
        self.tabwidget.setTabPosition(QTabWidget.East)
        self.setCentralWidget(self.tabwidget)

        def gettb(_type):
            textOutput = QTextBrowser()
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
            textOutput.customContextMenuRequested.connect(
                functools.partial(self.showmenu, textOutput, _type)
            )
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            textOutput.setObjectName("textOutput")
            return textOutput

        self.textOutput = gettb(1)
        self.tabwidget.addTab(self.textOutput, _TR("历史翻译"))
        self.debugoutputs = {}
        for _text in ["stderr", "stdout"]:
            _x = gettb(0)
            self.tabwidget.addTab(_x, _TR(_text))
            self.debugoutputs[_text] = _x
        self.hiding = True

    def showmenu(self, tb, flag, p):
        menu = QMenu(self)
        qingkong = QAction(_TR("清空"))
        baocun = QAction(_TR("保存"))
        hideshowraw = QAction(_TR("显示原文" if self.hiderawflag else "不显示原文"))
        hideshowapi = QAction(_TR("显示api" if self.hideapiflag else "不显示api"))
        menu.addAction(qingkong)
        menu.addAction(baocun)
        if flag == 1:
            menu.addAction(hideshowraw)
            menu.addAction(hideshowapi)

        action = menu.exec(self.mapToGlobal(p))
        if action == qingkong:
            tb.clear()
        elif action == baocun:
            ff = QFileDialog.getSaveFileName(self, directory="save.txt")
            if ff[0] == "":
                return
            with open(ff[0], "w", encoding="utf8") as ff:
                ff.write(tb.toPlainText())
        elif action == hideshowraw:

            self.hiderawflag = not self.hiderawflag
        elif action == hideshowapi:

            self.hideapiflag = not self.hideapiflag

    def debugprint(self, idx, sentence):
        textbrowappendandmovetoend(self.debugoutputs[idx], sentence, False)

    def getnewsentence(self, sentence):

        sentence = "<hr>" if globalconfig["hist_split"] else "\n" + sentence
        if self.hiderawflag:
            sentence = ""
        self.textOutput.append(sentence)

    def getnewtrans(self, api, sentence):
        if self.hideapiflag:
            res = sentence
        else:
            res = api + "  " + sentence
        self.textOutput.append(res)
