from qtsymbols import *
import threading, windows
import gobject, qtawesome
from myutils.config import globalconfig
from myutils.wrapper import Singleton_close
from gui.usefulwidget import saveposwindow, getsimplecombobox
from gui.dynalang import LPushButton, LMainWindow, LAction


@Singleton_close
class edittext(saveposwindow):
    getnewsentencesignal = pyqtSignal(str)

    def closeEvent(self, e):
        gobject.baseobject.edittextui = None
        super().closeEvent(e)

    def __init__(self, parent, cached):
        super().__init__(parent, poslist=globalconfig["edit_geo"])
        self.setupUi()

        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowTitle("编辑")
        if cached:
            self.getnewsentence(cached)

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"))

        self.textOutput = QPlainTextEdit(self)

        self.textOutput.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

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
                "fa.forward" if gobject.baseobject.edittextui_sync else "fa.play",
                color=(
                    "#FF69B4"
                    if gobject.baseobject.edittextui_sync
                    else globalconfig["buttoncolor"]
                ),
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
        gobject.baseobject.edittextui_sync = not gobject.baseobject.edittextui_sync
        self.bt2.setIcon(
            qtawesome.icon(
                "fa.forward" if gobject.baseobject.edittextui_sync else "fa.play",
                color=(
                    "#FF69B4"
                    if gobject.baseobject.edittextui_sync
                    else globalconfig["buttoncolor"]
                ),
            )
        )

    def showmenu(self, point: QPoint):
        menu = QMenu(self.textOutput)
        qingkong = LAction(("清空"))
        menu.addAction(qingkong)
        action = menu.exec(QCursor.pos())
        if action == qingkong:
            self.textOutput.clear()

    def getnewsentence(self, sentence):
        if gobject.baseobject.edittextui_sync:
            self.textOutput.setPlainText(sentence)
