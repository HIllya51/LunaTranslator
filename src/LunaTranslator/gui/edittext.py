from qtsymbols import *
import threading, windows
import gobject, qtawesome, os, json
from myutils.config import globalconfig, savehook_new_data, translatorsetting
from myutils.wrapper import Singleton
from gui.usefulwidget import (
    saveposwindow,
    getsimplecombobox,
    getIconButton,
    IconButton,
)
from gui.rendertext.texttype import TranslateColor
from gui.dynalang import LPushButton, LMainWindow
from myutils.utils import translate_exits, getannotatedapiname


def sortAwithB(l1, l2):
    sorted_pairs = sorted(zip(l1, l2))
    return [x[1] for x in sorted_pairs], [x[0] for x in sorted_pairs]


def loadvalidtss():

    alltransvis = []
    alltrans = []
    for x in globalconfig["fanyi"]:
        if x == "premt":
            continue
        if not translate_exits(x):
            continue
        alltransvis.append(getannotatedapiname(x))
        alltrans.append(x)
    return sortAwithB(alltransvis, alltrans)


@Singleton
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

        w = QWidget()
        qv = QHBoxLayout(w)
        self.setCentralWidget(w)

        bt1 = getIconButton(icon="fa.rotate-right")
        bt2 = IconButton(icon=["fa.play", "fa.forward"], checkable=True)
        bt2.setChecked(True)
        self.bt2 = bt2
        self.bt1 = bt1
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

    def getnewsentence(self, sentence):
        if self.bt2.isChecked():
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


@Singleton
class edittrans(LMainWindow):
    dispatch = pyqtSignal(str, str)

    def __init__(self, parent):
        self.followhwnd = gobject.baseobject.hwnd
        rect = windows.GetWindowRect(self.followhwnd)
        if rect is None:
            super().__init__(parent)
        else:
            super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("编辑_翻译记录")
        self.setupUi()
        if rect is None:
            return self.show()
        self.idx = 0
        self.dispatch.connect(self.dispatchF)
        self.trykeeppos()
        gobject.edittrans = self

    def dispatchF(self, klass, ts):
        if globalconfig["realtime_edit_target"] != klass:
            return
        self.textOutput.setPlainText(ts)

    def trykeeppos(self):
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.follow)
        t.timeout.emit()
        t.start()

    def follow(self):
        rect = windows.GetWindowRect(self.followhwnd)
        if rect is None:
            return
        self.move(QPoint(rect[0], rect[3]) / self.devicePixelRatioF())
        self.resize(QSize(rect[2] - rect[0], 1) / self.devicePixelRatioF())
        if self.idx == 0:
            self.show()
        self.idx += 1

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.edit"))

        self.textOutput = ctrlenter(self)
        w = QWidget()
        qv = QHBoxLayout(w)
        self.setCentralWidget(w)
        self.textOutput.enterpressed.connect(self.submitfunction)
        submit = LPushButton("确定")
        inter, vis = loadvalidtss()
        qv.addWidget(self.textOutput)
        qv.addWidget(
            getsimplecombobox(
                vis,
                globalconfig,
                "realtime_edit_target",
                internal=inter,
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
                color=TranslateColor("realtime_edit"),
                klass="realtime_edit",
                res=text,
                iter_context=(1, "realtime_edit_directvis_fakeclass"),
            )
            gobject.baseobject.translation_ui.displayres.emit(displayreskwargs)
            displayreskwargs.update(
                dict(iter_context=(2, "realtime_edit_directvis_fakeclass"))
            )
            gobject.baseobject.translation_ui.displayres.emit(displayreskwargs)
            self.textOutput.clear()
            if globalconfig["realtime_edit_target"] == "rengong":
                # 当json文件唯一时，才记录，否则不管。
                __ = None
                for _ in (
                    self.unsafegetcurrentgameconfig()
                    + translatorsetting["rengong"]["args"]["jsonfile"]
                ):
                    if os.path.exists(_):
                        if __:
                            return
                        __ = _
                if __:
                    with open(__, "r", encoding="utf8") as f:
                        __j = json.load(f)
                        __j[gobject.baseobject.currenttext] = text
                    with open(__, "w", encoding="utf8") as f:
                        json.dump(__j, f, ensure_ascii=False, indent=4)

        except:
            pass

    def unsafegetcurrentgameconfig(self):
        try:
            gameuid = gobject.baseobject.gameuid
            _path = savehook_new_data[gameuid]["gamejsonfile"]
            if isinstance(_path, str):
                _path = [_path]
            return _path
        except:
            return None
