from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QAction,
    QMenu,
    QHBoxLayout,
    QMainWindow,
    QLineEdit,
    QWidget,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize
import qtawesome
import threading, windows
import gobject, time
from myutils.config import globalconfig, _TR
from gui.usefulwidget import closeashidewindow, saveposwindow
from myutils.config import globalconfig
from myutils.wrapper import Singleton_close, threader


class edittext(closeashidewindow):
    getnewsentencesignal = pyqtSignal(str)

    def __init__(self, parent):
        super(edittext, self).__init__(parent, globalconfig, "edit_geo")
        self.sync = True
        self.setupUi()

        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowTitle(_TR("编辑"))

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"))

        self.textOutput = QPlainTextEdit(self)

        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)

        self.textOutput.customContextMenuRequested.connect(self.showmenu)
        # self.setCentralWidget(self.textOutput)

        self.textOutput.setUndoRedoEnabled(True)
        self.textOutput.setReadOnly(False)

        qv = QHBoxLayout()
        w = QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)

        bt1 = QPushButton(
            icon=qtawesome.icon("fa.rotate-right", color=globalconfig["buttoncolor"])
        )
        bt2 = QPushButton(
            icon=qtawesome.icon(
                "fa.forward" if self.sync else "fa.play",
                color="#FF69B4" if self.sync else globalconfig["buttoncolor"],
            )
        )

        self.bt2 = bt2
        self.bt1 = bt1
        bt2.clicked.connect(self.changestate)
        bt1.clicked.connect(self.run)
        qvb = QVBoxLayout()
        qvb.addWidget(bt1)
        qvb.addWidget(bt2)

        qv.addLayout(qvb)
        qv.addWidget(self.textOutput)

    def run(self):
        threading.Thread(
            target=gobject.baseobject.textgetmethod,
            args=(self.textOutput.toPlainText(), False),
        ).start()

    def changestate(self):
        self.sync = not self.sync
        self.bt2.setIcon(
            qtawesome.icon(
                "fa.forward" if self.sync else "fa.play",
                color="#FF69B4" if self.sync else globalconfig["buttoncolor"],
            )
        )

    def showmenu(self, point: QPoint):
        menu = QMenu(self.textOutput)
        qingkong = QAction(_TR("清空"))
        menu.addAction(qingkong)
        action = menu.exec(QCursor.pos())
        if action == qingkong:
            self.textOutput.clear()

    def getnewsentence(self, sentence):
        if self.sync:
            self.textOutput.setPlainText(sentence)


@Singleton_close
class edittrans(QMainWindow):
    rssignal = pyqtSignal(QSize)
    mvsignal = pyqtSignal(QPoint)

    def __init__(self, parent):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setupUi()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            "background-color: rgba(%s, %s, %s, %s)"
            % (
                int(globalconfig["backcolor"][1:3], 16),
                int(globalconfig["backcolor"][3:5], 16),
                int(globalconfig["backcolor"][5:7], 16),
                globalconfig["transparent"],
            )
        )
        self.rssignal.connect(self.resize)
        self.mvsignal.connect(self.move)
        self.trykeeppos()

    def trykeeppos(self):
        try:
            self.followhwnd = gobject.baseobject.textsource.hwnd
            self.follow()
            self.show()
        except:
            pass

    @threader
    def follow(self):
        while True:
            rect = windows.GetWindowRect(self.followhwnd)
            self.mvsignal.emit((QPoint(rect[0], rect[3])) / self.devicePixelRatioF())
            self.rssignal.emit((QSize(rect[2] - rect[0], 1)) / self.devicePixelRatioF())
            time.sleep(0.3)

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"))

        self.textOutput = QLineEdit(self)

        qv = QHBoxLayout()
        w = QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)

        submit = QPushButton(_TR("确定"))
        qv.addWidget(self.textOutput)
        qv.addWidget(submit)

        submit.clicked.connect(self.submitfunction)

    def submitfunction(self):
        text = self.textOutput.text()
        if len(text) == 0:
            return
        try:
            gobject.baseobject.textsource.sqlqueueput(
                (gobject.baseobject.currenttext, "realtime_edit", text)
            )
            displayreskwargs = dict(
                color="red",
                res=text,
                onlytrans=False,
            )
            gobject.baseobject.translation_ui.displayres.emit(displayreskwargs)
            self.textOutput.clear()
        except:
            pass
