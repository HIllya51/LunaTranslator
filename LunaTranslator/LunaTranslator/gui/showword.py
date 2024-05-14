from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTextBrowser,
    QLineEdit,
    QMenu,
    QAction,
    QPushButton,
    QTextEdit,
    QTabWidget,
    QDialog,
    QLabel,
)
from traceback import print_exc
import requests
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
import qtawesome, functools, os
import threading, gobject, uuid
from myutils.config import globalconfig
from myutils.config import globalconfig, _TR, _TRL
import myutils.ankiconnect as anki
from gui.usefulwidget import closeashidewindow, getQMessageBox, getboxlayout

from myutils.ocrutil import imageCut
from gui.rangeselect import rangeselct_function


class AnkiWindow(QDialog):
    setcurrenttext = pyqtSignal(str)
    appenddictionary = pyqtSignal(str)

    def langdu(self):
        if gobject.baseobject.reader:
            self.audiofile = gobject.baseobject.reader.syncttstofile(
                self.wordedit.text()
            )

    def crop(self):
        def ocroncefunction(rect):
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            fname = "./cache/ocr/cropforanki.png"
            os.makedirs("./cache/ocr", exist_ok=True)
            img.save(fname)
            self.cropedimagepath = os.path.abspath(fname)

        rangeselct_function(self, ocroncefunction, False, False)

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.setWindowTitle("Anki Connect")
        self.audiofile = None
        self.cropedimagepath = None
        layout = QVBoxLayout()
        self.setLayout(layout)
        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        cropbutton = QPushButton(qtawesome.icon("fa.crop"), "")
        cropbutton.clicked.connect(self.crop)
        self.wordedit = QLineEdit()
        layout.addLayout(
            getboxlayout([QLabel(_TR("Word")), self.wordedit, soundbutton, cropbutton])
        )
        self.textedit = QTextEdit()
        layout.addWidget(self.textedit)

        btn = QPushButton(_TR("添加"))
        btn.clicked.connect(self.errorwrap)
        layout.addWidget(btn)
        self.setcurrenttext.connect(self.reset)
        self.appenddictionary.connect(self.textedit.append)

    def reset(self, text):
        self.wordedit.setText(text)
        self.textedit.clear()
        self.cropedimagepath = None
        self.audiofile = None

    def errorwrap(self):
        try:
            self.addanki()
            getQMessageBox(self, _TR("成功"), _TR("成功"))
        except requests.NetWorkException:
            getQMessageBox(self, _TR("错误"), _TR("无法连接到anki"))
        except anki.AnkiException as e:
            getQMessageBox(self, _TR("错误"), str(e))
        except:
            print_exc()

    def addanki(self):
        word = self.wordedit.text()
        explain = self.textedit.toHtml()
        anki.Deck.create(anki.DeckName)
        try:
            model = anki.Model.create(
                anki.ModelName,
                anki.model_fileds,
                anki.model_css,
                False,
                [
                    {
                        "Name": "LUNACARDTEMPLATE1",
                        "Front": anki.model_htmlfront,
                        "Back": anki.model_htmlback,
                    }
                ],
            )
        except anki.AnkiModelExists:
            model = anki.Model(anki.ModelName)
            model.updateStyling(anki.model_css)
            model.updateTemplates(
                {
                    "LUNACARDTEMPLATE1": {
                        "Front": anki.model_htmlfront,
                        "Back": anki.model_htmlback,
                    }
                }
            )
        media = []
        tempfiles=[]
        for k, _ in [("audio", self.audiofile), ("image", self.cropedimagepath)]:
            if _:
                media.append(
                    [
                        {
                            "path": _,
                            "filename": str(uuid.uuid4()) + os.path.basename(_),
                            "fields": [k],
                        }
                    ]
                )
                tempfiles.append(_)
            else:
                media.append([])

        anki.Note.add(
            anki.DeckName,
            anki.ModelName,
            {
                "word": word,
                "explain": explain,
            },
            False,
            [],
            media[0],
            media[1],
        )
        for _ in tempfiles:
            try:
                os.remove(_)
            except:
                pass

class searchwordW(closeashidewindow):
    getnewsentencesignal = pyqtSignal(str, bool)
    searchthreadsignal = pyqtSignal(str, dict, str)
    showtabsignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(searchwordW, self).__init__(parent, globalconfig, "sw_geo")
        self.ankiwindow = AnkiWindow(self)
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowTitle(_TR("查词"))

    def showresfun(self, k, res):
        first = res.split("<hr>")[0]

        self.textbs[k].insertHtml(first)
        self.textbs[k].firsttext = self.textbs[k].toPlainText()
        self.textbs[k].insertHtml(res[len(first) :])

        scrollbar = self.textbs[k].verticalScrollBar()
        scrollbar.setValue(0)
        self.tab.setTabVisible(self._k.index(k), True)

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"))

        self.showtabsignal.connect(self.showresfun)

        self.centralWidget = QWidget(self)
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.hboxlayout = QHBoxLayout(self.centralWidget)
        self.vboxlayout = QVBoxLayout()

        self.searchlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchlayout)
        self.searchtext = QLineEdit()
        # self.searchtext.setFont(font)
        self.searchlayout.addWidget(self.searchtext)
        searchbutton = QPushButton(qtawesome.icon("fa.search"), "")  # _TR("搜索"))

        searchbutton.clicked.connect(lambda: self.search((self.searchtext.text())))
        self.searchlayout.addWidget(searchbutton)

        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        self.searchlayout.addWidget(soundbutton)

        ankiconnect = QPushButton(qtawesome.icon("fa.adn"), "")
        ankiconnect.clicked.connect(self.ankiwindow.show)
        self.searchlayout.addWidget(ankiconnect)

        self.tab = QTabWidget(self)

        self.vboxlayout.addWidget(self.tab)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.setCentralWidget(self.centralWidget)

        self.textbs = {}

        _k = []
        _name = []
        for cishu in globalconfig["cishu"]:
            _name.append(globalconfig["cishu"][cishu]["name"])
            _k.append(cishu)
        self._k = _k
        _name = _TRL(_name)

        for i in range(len(_name)):

            textOutput = QTextBrowser(self)
            # textOutput.setFont(font)
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            textOutput.setOpenLinks(False)
            self.tab.addTab(textOutput, _name[i])
            self.tab.setTabVisible(i, False)

            self.textbs[self._k[i]] = textOutput
            textOutput.setContextMenuPolicy(Qt.CustomContextMenu)
            textOutput.customContextMenuRequested.connect(
                functools.partial(self.showmenu, textOutput)
            )
        self.hiding = True
        self.searchthreadsignal.connect(self.searchthread)

    def langdu(self):
        if gobject.baseobject.reader:
            gobject.baseobject.reader.read(self.searchtext.text(), True)

    def showmenu(self, tb, point):
        menu = QMenu(tb)
        append = QAction(_TR("追加"))
        menu.addAction(append)
        print(point, (tb.pos()), self.mapToGlobal(tb.pos()))
        action = menu.exec(QCursor.pos())
        if action == append:
            self.ankiwindow.appenddictionary.emit(tb.toHtml())

    def getnewsentence(self, sentence, append):
        self.showNormal()
        if append:
            sentence = self.searchtext.text() + sentence
        self.searchtext.setText(sentence)

        self.search(sentence)

    def searchthread(self, k, _mp, sentence):

        _mp[k].callback = functools.partial(self.showtabsignal.emit, k)
        _mp[k].search(sentence)

    def search(self, sentence):
        if sentence == "":
            return
        self.ankiwindow.setcurrenttext.emit(sentence)
        _mp = {}
        _mp.update(gobject.baseobject.cishus)

        for k in self._k:
            self.tab.setTabVisible(self._k.index(k), False)
            self.textbs[k].clear()
            if k in _mp:
                threading.Thread(
                    target=self.searchthreadsignal.emit, args=(k, _mp, sentence)
                ).start()
