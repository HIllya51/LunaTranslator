from qtsymbols import *
import functools
import qtawesome, winsharedutils
from myutils.config import globalconfig, _TR
from myutils.utils import get_time_stamp
from gui.usefulwidget import closeashidewindow


class transhist(closeashidewindow):

    getnewsentencesignal = pyqtSignal(str)
    getnewtranssignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(transhist, self).__init__(parent, globalconfig, "hist_geo")
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.getnewtranssignal.connect(self.getnewtrans)
        self.hiderawflag = False
        self.hideapiflag = False
        self.hidetime = True

        self.setWindowTitle(_TR("历史翻译"))

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"))

        def gettb(_type):
            textOutput = QPlainTextEdit()
            textOutput.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            textOutput.customContextMenuRequested.connect(
                functools.partial(self.showmenu, textOutput, _type)
            )
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            return textOutput

        self.textOutput = gettb(1)
        self.setCentralWidget(self.textOutput)

        self.hiding = True

    def showmenu(self, tb, flag, p):
        menu = QMenu(self)
        qingkong = QAction(_TR("清空"))
        baocun = QAction(_TR("保存"))
        copy = QAction(_TR("复制到剪贴板"))
        hideshowraw = QAction(_TR("显示原文" if self.hiderawflag else "不显示原文"))
        hideshowapi = QAction(_TR("显示api" if self.hideapiflag else "不显示api"))
        hidetime = QAction(_TR("显示时间" if self.hidetime else "不显示时间"))
        menu.addAction(qingkong)
        menu.addAction(baocun)
        if len(self.textOutput.textCursor().selectedText()):
            menu.addAction(copy)
        if flag == 1:
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
        elif action == hidetime:

            self.hidetime = not self.hidetime
        elif action == hideshowapi:

            self.hideapiflag = not self.hideapiflag

    def getnewsentence(self, sentence):

        if self.hiderawflag:
            sentence = ""
        else:
            if not self.hidetime:
                sentence = get_time_stamp() + " " + sentence
            sentence = "\n" + sentence
        self.textOutput.appendPlainText(sentence)

    def getnewtrans(self, api, sentence):
        if not self.hideapiflag:
            sentence = api + " " + sentence
        if not self.hidetime:
            sentence = get_time_stamp() + " " + sentence

        self.textOutput.appendPlainText(sentence)
