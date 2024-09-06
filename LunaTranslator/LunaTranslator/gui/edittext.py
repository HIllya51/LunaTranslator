from qtsymbols import *
import threading, windows
import gobject, qtawesome
from myutils.config import globalconfig
from myutils.wrapper import Singleton_close
from gui.usefulwidget import saveposwindow, getsimplecombobox
from gui.dynalang import LPushButton, LMainWindow


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

    def getnewsentence(self, sentence):
        if gobject.baseobject.edittextui_sync:
            self.textOutput.setPlainText(sentence)


class ctrlenter(QPlainTextEdit):
    enterpressed = pyqtSignal()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            if (
                e.modifiers() == Qt.KeyboardModifier.ControlModifier
                or e.modifiers() == Qt.KeyboardModifier.ShiftModifier
                or e.modifiers() == Qt.KeyboardModifier.AltModifier
            ):
                self.insertPlainText("\n")
            else:
                self.enterpressed.emit()
        else:
            super().keyPressEvent(e)


@Singleton_close
class edittrans(LMainWindow):

    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setupUi()
        self.idx = 0
        self.trykeeppos()

    def trykeeppos(self):
        self.followhwnd = gobject.baseobject.hwnd
        rect = windows.GetWindowRect(self.followhwnd)
        if rect is None:
            raise
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.follow)
        t.timeout.emit()
        t.start()

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

        self.textOutput = ctrlenter(self)
        qv = QHBoxLayout()
        w = QWidget()
        self.setCentralWidget(w)
        w.setLayout(qv)
        self.textOutput.enterpressed.connect(self.submitfunction)
        submit = LPushButton("确定")
        qv.addWidget(self.textOutput)
        qv.addWidget(
            getsimplecombobox(
                [globalconfig["fanyi"][x]["name"] for x in globalconfig["fanyi"]],
                globalconfig,
                "realtime_edit_target",
                internal=list(globalconfig["fanyi"]),
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
