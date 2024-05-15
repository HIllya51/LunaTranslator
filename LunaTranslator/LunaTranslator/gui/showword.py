from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTextBrowser,
    QLineEdit,
    QPlainTextEdit,
    QFormLayout,
    QAction,
    QSizePolicy,
    QStylePainter,
    QStyleOptionTab,
    QStyle,
    QPushButton,
    QTextEdit,
    QTabWidget,QFileDialog,
    QTabBar,
    QLabel,
)
from traceback import print_exc
import requests, json
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
import qtawesome, functools, os, re, base64
import threading, gobject, uuid
from myutils.config import globalconfig, _TR, _TRL, static_data
import myutils.ankiconnect as anki
from gui.usefulwidget import (
    closeashidewindow,
    getQMessageBox,
    auto_select_webview,
    getboxlayout,
    getspinbox,
    getlineedit,
    saveposwindow,
    getsimpleswitch,getcolorbutton,
    tabadd_lazy,
)
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run
from gui.rangeselect import rangeselct_function


class AnkiWindow(closeashidewindow):
    setcurrenttext = pyqtSignal(str)
    __ocrsettext = pyqtSignal(str)
    refreshhtml = pyqtSignal()

    def langdu(self):
        if gobject.baseobject.reader:
            self.audiopath.setText(gobject.baseobject.reader.syncttstofile(
                self.wordedit.text()
            ))

    @threader
    def asyncocr(self, fname):
        self.__ocrsettext.emit(ocr_run(fname))

    def crop(self):
        def ocroncefunction(rect):
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            fname = "./cache/ocr/cropforanki.png"
            os.makedirs("./cache/ocr", exist_ok=True)
            img.save(fname)
            self.editpath.setText(os.path.abspath(fname))
            self.asyncocr(fname)

        rangeselct_function(self, ocroncefunction, False, False)

    def __init__(self, parent) -> None:
        super().__init__(parent, globalconfig, "ankiwindow")
        self.setWindowTitle("Anki Connect")

        self.tabs = QTabWidget()
        self.tabs.addTab(self.createaddtab(), _TR("添加"))
        tabadd_lazy(self.tabs, "设置", self.creatsetdtab)
        tabadd_lazy(self.tabs, "模板", self.creattemplatetab)
        self.setCentralWidget(self.tabs)
        self.refreshhtml.connect(self.refreshhtmlfunction)
        self.tabs.currentChanged.connect(self.ifshowrefresh)

    def ifshowrefresh(self, idx):
        try:
            w = self.tabs.currentWidget()
            if "lazyfunction" in dir(w):
                w.lazyfunction()
                delattr(w, "lazyfunction")
        except:
            print_exc()
        if idx == 2:
            self.refreshhtml.emit()

    def parse_template(self, template, data):
        result = ""
        i = 0
        while i < len(template):
            if template[i : i + 2] == "{{":
                end_index = template.find("}}", i + 2)
                if end_index != -1:
                    field = template[i + 2 : end_index].strip()
                    if field in data:
                        result += str(data[field])
                    else:
                        result += template[i : end_index + 2]
                    i = end_index + 2
                else:
                    result += template[i:]
                    break
            else:
                result += template[i]
                i += 1
        return result

    def refreshhtmlfunction(self):
        html = (self.fronttext, self.backtext)[
            self.previewtab.currentIndex()
        ].toPlainText()
        model_css = self.csstext.toPlainText()
        fields = self.loadfileds()
        fields.update(self.loadfakefields())
        html = self.parse_template(html, fields)
        html = "<style>" + model_css + "</style>" + html
        self.htmlbrowser.set_html(html)

    def creattemplatetab(self):

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        wid = QWidget()
        wid.setLayout(layout)

        edittemptab = QTabWidget()
        self.previewtab = QTabBar()
        revertbtn = QPushButton(_TR("恢复"))
        revertbtn.clicked.connect(self.loadedits)
        savebtn = QPushButton(_TR("保存"))
        savebtn.clicked.connect(self.saveedits)
        layout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("编辑")),
                    edittemptab,
                    getboxlayout([revertbtn, savebtn], makewidget=True),
                ],
                lc=QVBoxLayout,
                margin0=True,
            )
        )

        self.htmlbrowser = auto_select_webview(self)
        self.htmlbrowser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addLayout(
            getboxlayout(
                [QLabel(_TR("预览")), self.previewtab, self.htmlbrowser],
                lc=QVBoxLayout,
                margin0=True,
            )
        )
        self.fronttext = QPlainTextEdit()
        self.backtext = QPlainTextEdit()
        self.csstext = QPlainTextEdit()
        edittemptab.addTab(self.fronttext, _TR("正面"))
        edittemptab.addTab(self.backtext, _TR("背面"))
        edittemptab.addTab(self.csstext, _TR("样式"))
        self.previewtab.addTab(_TR("正面"))
        self.previewtab.addTab(_TR("背面"))
        self.loadedits()
        self.fronttext.textChanged.connect(lambda: self.refreshhtml.emit())
        self.backtext.textChanged.connect(lambda: self.refreshhtml.emit())
        self.csstext.textChanged.connect(lambda: self.refreshhtml.emit())
        self.previewtab.currentChanged.connect(lambda: self.refreshhtml.emit())
        return wid

    def loadedits(self):
        for text, object in zip(
            self.tryloadankitemplates(), (self.fronttext, self.backtext, self.csstext)
        ):
            object.setPlainText(text)

    def loadfileds(self):
        word = self.wordedit.text()
        explain = json.dumps(gobject.baseobject.searchwordW.generate_explains())
        remarks = self.remarks.toHtml()
        example = self.example.toPlainText()
        ruby = self.ruby
        fields = {
            "word": word,
            "rubytext": ruby,
            "explain": explain,
            "example_sentence": example,
            "remarks": remarks,
        }
        return fields

    def loadfakefields(self):
        if len(self.editpath.text()):
            with open(self.editpath.text(), "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            encoded_string = '<img src="data:image/png;base64,{}">'.format(
                encoded_string
            )
        else:
            encoded_string = ""
        if len(self.audiopath.text()):
            with open(self.audiopath.text(), "rb") as image_file:
                encoded_string2 = base64.b64encode(image_file.read()).decode("utf-8")
            encoded_string2 = '<audio controls><source src="data:audio/mpeg;base64,{}"></audio>'.format(
                encoded_string2
            )
        else:
            encoded_string2 = ""
        fields = {"audio": encoded_string2, "image": encoded_string}
        return fields

    def saveedits(self):
        model_htmlfront = self.fronttext.toPlainText()
        model_htmlback = self.backtext.toPlainText()
        model_css = self.csstext.toPlainText()
        os.makedirs("userconfig/anki", exist_ok=True)
        with open("userconfig/anki/back.html", "w", encoding="utf8") as ff:
            ff.write(model_htmlback)
        with open("userconfig/anki/front.html", "w", encoding="utf8") as ff:
            ff.write(model_htmlfront)
        with open("userconfig/anki/style.css", "w", encoding="utf8") as ff:
            ff.write(model_css)

    def creatsetdtab(self):
        layout = QFormLayout()
        wid = QWidget()
        wid.setLayout(layout)
        layout.addRow(
            _TR("port"), getspinbox(0, 65536, globalconfig["ankiconnect"], "port")
        )
        layout.addRow(
            _TR("DeckName"), getlineedit(globalconfig["ankiconnect"], "DeckName")
        )
        layout.addRow(
            _TR("ModelName"), getlineedit(globalconfig["ankiconnect"], "ModelName")
        )

        layout.addRow(
            _TR("allowDuplicate"),
            getsimpleswitch(globalconfig["ankiconnect"], "allowDuplicate"),
        )

        return wid

    def createaddtab(self):
        layout = QVBoxLayout()
        wid = QWidget()
        wid.setLayout(layout)
        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        cropbutton = QPushButton(qtawesome.icon("fa.crop"), "")
        cropbutton.clicked.connect(self.crop)
        self.wordedit = QLineEdit()
        self.wordedit.textEdited.connect(self.reset)
        layout.addLayout(
            getboxlayout([QLabel(_TR("Word")), self.wordedit])
        )
        self.example = QPlainTextEdit()
        layout.addWidget(QLabel(_TR("例句")))
        layout.addWidget(self.example)
        self.remarks = QTextEdit()
        layout.addWidget(QLabel(_TR("备注")))
        layout.addWidget(self.remarks)

        self.tagsedit = QLineEdit()
        layout.addLayout(getboxlayout([QLabel(_TR("Tags(split by |)")), self.tagsedit]))
        
        self.audiopath = QLineEdit()
        self.audiopath.setReadOnly(True)
        layout.addLayout(getboxlayout([QLabel(_TR("语音")),self.audiopath,soundbutton,getcolorbutton(
                        "",
                        "",
                        functools.partial(self.selectaudio),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    )]))
        
        self.editpath = QLineEdit()
        self.editpath.setReadOnly(True)
        layout.addLayout(getboxlayout([QLabel(_TR("截图")),self.editpath,cropbutton,getcolorbutton(
                        "",
                        "",
                        functools.partial(self.selectimage),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    )]))
        btn = QPushButton(_TR("添加"))
        btn.clicked.connect(self.errorwrap)
        layout.addWidget(btn)

        self.setcurrenttext.connect(self.reset)

        self.__ocrsettext.connect(self.example.insertPlainText)

        self.reset("")
        return wid
    def selectimage(self):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            self.editpath.setText(res)
    def selectaudio(self):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            self.audiopath.setText(res)
    def reset(self, text):
        self.wordedit.setText(text)
        if text and len(text):
            self.ruby = json.dumps(gobject.baseobject.translation_ui.parsehira(text))
        else:
            self.ruby = ""
        self.editpath.clear()
        self.audiopath.clear()
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

    def tryloadankitemplates(self):
        try:
            with open("userconfig/anki/back.html", "r", encoding="utf8") as ff:
                model_htmlback = ff.read()
            with open("userconfig/anki/front.html", "r", encoding="utf8") as ff:
                model_htmlfront = ff.read()
            with open("userconfig/anki/style.css", "r", encoding="utf8") as ff:
                model_css = ff.read()
        except:
            with open("files/anki/back.html", "r", encoding="utf8") as ff:
                model_htmlback = ff.read()
            with open("files/anki/front.html", "r", encoding="utf8") as ff:
                model_htmlfront = ff.read()
            with open("files/anki/style.css", "r", encoding="utf8") as ff:
                model_css = ff.read()
        return model_htmlfront, model_htmlback, model_css

    def addanki(self):
        allowDuplicate = globalconfig["ankiconnect"]["allowDuplicate"]
        anki.global_port = globalconfig["ankiconnect"]["port"]
        ModelName = globalconfig["ankiconnect"]["ModelName"]
        DeckName = globalconfig["ankiconnect"]["DeckName"]
        model_htmlfront, model_htmlback, model_css = self.tryloadankitemplates()
        try:
            tags = self.tagsedit.text().split("|")
        except:
            tags = []
        anki.Deck.create(DeckName)
        try:
            model = anki.Model.create(
                ModelName,
                static_data["model_fileds"],
                model_css,
                False,
                [
                    {
                        "Name": "LUNACARDTEMPLATE1",
                        "Front": model_htmlfront,
                        "Back": model_htmlback,
                    }
                ],
            )
        except anki.AnkiModelExists:
            model = anki.Model(ModelName)
            model.updateStyling(model_css)
            model.updateTemplates(
                {
                    "LUNACARDTEMPLATE1": {
                        "Front": model_htmlfront,
                        "Back": model_htmlback,
                    }
                }
            )
        media = []
        tempfiles = []
        for k, _ in [("audio", self.audiopath.text()), ("image", self.editpath.text())]:
            if len(_):
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
            DeckName,
            ModelName,
            self.loadfileds(),
            allowDuplicate,
            tags,
            media[0],
            media[1],
        )


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
        self.hiding = True
        self.searchthreadsignal.connect(self.searchthread)

    def langdu(self):
        if gobject.baseobject.reader:
            gobject.baseobject.reader.read(self.searchtext.text(), True)

    def generate_explains(self):
        res = []
        for i in range(len(self._k)):
            if len(self.textbs[self._k[i]].toPlainText()) == 0:
                continue

            res.append(
                {"source": self._k[i], "content": self.textbs[self._k[i]].toHtml()}
            )
        return res

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
