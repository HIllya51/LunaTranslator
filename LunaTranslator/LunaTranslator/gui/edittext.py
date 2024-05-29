from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QAction,
    QMenu,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import qtawesome
import threading, windows
import gobject
from myutils.config import globalconfig, _TR
from gui.usefulwidget import closeashidewindow, saveposwindow
from myutils.config import globalconfig
from myutils.wrapper import Singleton_close


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
class edittrans(saveposwindow):
    def __init__(self, parent):
        super().__init__(parent, globalconfig, "edit_geo")
        self.setupUi()

        self.setWindowTitle(_TR("编辑_翻译"))
        self.trykeeppos()
        self.show()

    def trykeeppos(self):
        try:
            rect = windows.GetWindowRect(gobject.baseobject.textsource.hwnd)

            self.move((QPoint(rect[0], rect[3])) / self.devicePixelRatioF())
        except:
            pass

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"))

        self.textOutput = QPlainTextEdit(self)

        self.textOutput.setUndoRedoEnabled(True)
        self.textOutput.setReadOnly(False)

        qv = QHBoxLayout()
        w = QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)

        submit = QPushButton(_TR("确定"))
        qv.addWidget(self.textOutput)
        qv.addWidget(submit)

        submit.clicked.connect(self.submitfunction)

    def submitfunction(self):
        text = self.textOutput.toPlainText()
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
