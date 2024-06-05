from qtsymbols import *
import threading, windows, time
import gobject, qtawesome
from myutils.config import globalconfig, _TR, _TRL
from myutils.utils import str2rgba
from myutils.wrapper import Singleton_close, threader
from gui.usefulwidget import saveposwindow, getsimplecombobox


@Singleton_close
class edittext(saveposwindow):
    getnewsentencesignal = pyqtSignal(str)

    def closeEvent(self, e):
        gobject.baseobject.edittextui = None
        super().closeEvent(e)

    def __init__(self, parent, cached):
        super().__init__(parent, globalconfig, "edit_geo")
        self.setupUi()

        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowTitle(_TR("编辑"))
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
        qingkong = QAction(_TR("清空"))
        menu.addAction(qingkong)
        action = menu.exec(QCursor.pos())
        if action == qingkong:
            self.textOutput.clear()

    def getnewsentence(self, sentence):
        if gobject.baseobject.edittextui_sync:
            self.textOutput.setPlainText(sentence)


@Singleton_close
class edittrans(QMainWindow):

    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setupUi()
        self.idx = 0
        self.trykeeppos()

    def trykeeppos(self):
        self.followhwnd = gobject.baseobject.textsource.hwnd
        rect = windows.GetWindowRect(self.followhwnd)
        if rect is None:
            raise
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.follow)
        t.start(0)

    def follow(self):
        rect = windows.GetWindowRect(self.followhwnd)
        if rect is None:
            return
        self.move((QPoint(rect[0], rect[3])) / self.devicePixelRatioF())
        self.resize((QSize(rect[2] - rect[0], 1)) / self.devicePixelRatioF())
        if self.idx == 0:
            self.show()
        self.idx += 1

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"))

        self.textOutput = QPlainTextEdit(self)
        qv = QHBoxLayout()
        w = QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)

        submit = QPushButton(_TR("确定"))
        qv.addWidget(self.textOutput)
        qv.addWidget(
            getsimplecombobox(
                _TRL([globalconfig["fanyi"][x]["name"] for x in globalconfig["fanyi"]]),
                globalconfig,
                "realtime_edit_target",
                internallist=list(globalconfig["fanyi"]),
            )
        )
        qv.addWidget(submit)
        submit.clicked.connect(self.submitfunction)

    def submitfunction(self):
        text = self.textOutput.toPlainText()
        if len(text) == 0:
            return
        try:
            gobject.baseobject.textsource.sqlqueueput(
                (
                    gobject.baseobject.currenttext,
                    globalconfig["realtime_edit_target"],
                    text,
                )
            )
            displayreskwargs = dict(
                name=globalconfig["fanyi"]["realtime_edit"]["name"],
                color=globalconfig["fanyi"]["realtime_edit"]["color"],
                res=text,
                onlytrans=False,
                iter_context=(1, "realtime_edit_directvis_fakeclass"),
            )
            gobject.baseobject.translation_ui.displayres.emit(displayreskwargs)
            displayreskwargs.update(
                dict(iter_context=(2, "realtime_edit_directvis_fakeclass"))
            )  # 显示到历史翻译
            gobject.baseobject.translation_ui.displayres.emit(displayreskwargs)
            self.textOutput.clear()
        except:
            pass
