from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QTextBrowser,
    QAction,
    QMenu,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import qtawesome
import threading
import gobject
from myutils.config import globalconfig, _TR
from gui.usefulwidget import closeashidewindow
from myutils.config import globalconfig


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

        self.textOutput = QTextBrowser(self)

        self.textOutput.setContextMenuPolicy(Qt.CustomContextMenu)

        self.charformat = self.textOutput.currentCharFormat()
        self.textOutput.customContextMenuRequested.connect(self.showmenu)
        # self.setCentralWidget(self.textOutput)

        self.textOutput.setUndoRedoEnabled(True)
        self.textOutput.setReadOnly(False)
        self.textOutput.setObjectName("textOutput")

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

        self.hiding = True

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
        action = menu.exec(self.mapToGlobal(self.textOutput.pos()) + point)
        if action == qingkong:
            self.textOutput.clear()

    def getnewsentence(self, sentence):
        if self.sync:
            self.textOutput.setCurrentCharFormat(self.charformat)
            self.textOutput.setPlainText(sentence)
