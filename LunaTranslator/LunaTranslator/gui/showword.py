from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTextBrowser,
    QLineEdit,
    QPlainTextEdit,
    QFormLayout,
    QSizePolicy,
    QPushButton,
    QTextEdit,
    QTabWidget,
    QFileDialog,
    QTabBar,
    QLabel,
)
from PyQt5.QtGui import QPixmap, QImage
from traceback import print_exc
import requests, json, subprocess, time
from PyQt5.QtCore import pyqtSignal, Qt
import qtawesome, functools, os, base64
import gobject, uuid, signal
from myutils.config import globalconfig, _TR, static_data
import myutils.ankiconnect as anki
from gui.usefulwidget import (
    closeashidewindow,
    getQMessageBox,
    auto_select_webview,
    getboxlayout,
    getspinbox,
    getlineedit,
    getsimpleswitch,
    getcolorbutton,
    tabadd_lazy,
)
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run
from gui.rangeselect import rangeselct_function


class ffmpeg_virtual_audio_capturer:
    def __init__(self):
        os.makedirs("./cache/tts", exist_ok=True)
        self.file = os.path.abspath(
            os.path.join("./cache/tts", str(time.time()) + ".mp3")
        )
        try:
            self.engine = subprocess.Popen(
                os.path.join(
                    globalconfig["ffmpeg"],
                    f'ffmpeg.exe -f dshow -i audio="virtual-audio-capturer" "{self.file}"',
                ),
                stdin=subprocess.PIPE,
            )
        except:
            print_exc()

    def end(self):
        try:
            self.engine.stdin.write(b"q")
            self.engine.stdin.flush()
        except:
            pass


class statusbutton(QPushButton):
    statuschanged1 = pyqtSignal(int)
    statuschanged2 = pyqtSignal(int)

    def __init__(self, icons, colors):
        super().__init__()
        self.idx = 0
        self.icons = icons
        self.colors = colors
        self.clicked.connect(self.setChecked)
        self.seticon()

    def seticon(self):
        self.setIcon(
            qtawesome.icon(
                self.icons[(self.idx) % len(self.icons)],
                color=self.colors[(self.idx) % len(self.colors)],
            )
        )

    def setChecked(self, a0):
        super().setChecked(a0)
        self.idx += 1
        self.statuschanged1.emit((self.idx) % len(self.icons))
        self.statuschanged2.emit((self.idx) % len(self.colors))
        self.seticon()


class AnkiWindow(QWidget):
    __ocrsettext = pyqtSignal(str)
    refreshhtml = pyqtSignal()

    def callbacktts(self, edit, data):
        fname = "./cache/tts/" + str(uuid.uuid4()) + ".mp3"
        os.makedirs("./cache/tts", exist_ok=True)
        with open(fname, "wb") as ff:
            ff.write(data)
        edit.setText(os.path.abspath(fname))

    def langdu(self):
        if gobject.baseobject.reader:
            gobject.baseobject.reader.ttscallback(
                self.currentword, functools.partial(self.callbacktts, self.audiopath)
            )

    def langdu2(self):
        if gobject.baseobject.reader:
            gobject.baseobject.reader.ttscallback(
                self.example.toPlainText(),
                functools.partial(self.callbacktts, self.audiopath_sentence),
            )

    @threader
    def asyncocr(self, img):
        self.__ocrsettext.emit(ocr_run(img))

    def crop(self):
        def ocroncefunction(rect):
            img = imageCut(
                0, rect[0][0], rect[0][1], rect[1][0], rect[1][1], False, True
            )
            fname = "./cache/ocr/cropforanki.png"
            os.makedirs("./cache/ocr", exist_ok=True)
            img.save(fname)
            self.editpath.setText("")
            self.editpath.setText(os.path.abspath(fname))
            if globalconfig["ankiconnect"]["ocrcroped"]:
                self.asyncocr(img)

        rangeselct_function(self, ocroncefunction, False, False)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Anki Connect")
        self.currentword = ""
        self.tabs = QTabWidget()
        self.tabs.addTab(self.createaddtab(), _TR("添加"))
        tabadd_lazy(self.tabs, "设置", self.creatsetdtab)
        tabadd_lazy(self.tabs, "模板", self.creattemplatetab)

        l = QHBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)
        l.addWidget(self.tabs)
        self.setLayout(l)
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
        layout.setSpacing(0)
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
                [self.previewtab, self.htmlbrowser],
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
        word = self.currentword
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
            try:
                with open(self.editpath.text(), "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                encoded_string = '<img src="data:image/png;base64,{}">'.format(
                    encoded_string
                )
            except:
                encoded_string = ""
        else:
            encoded_string = ""
        if len(self.audiopath.text()):
            try:
                with open(self.audiopath.text(), "rb") as image_file:
                    encoded_string2 = base64.b64encode(image_file.read()).decode(
                        "utf-8"
                    )
                encoded_string2 = """<button onclick='document.getElementById("audio1111").play()'>play audio<audio controls id="audio1111" style="display: none"><source src="data:audio/mpeg;base64,{}"></audio></button>""".format(
                    encoded_string2
                )
            except:
                encoded_string2 = ""
        else:
            encoded_string2 = ""
        if len(self.audiopath_sentence.text()):
            try:
                with open(self.audiopath_sentence.text(), "rb") as image_file:
                    encoded_string3 = base64.b64encode(image_file.read()).decode(
                        "utf-8"
                    )
                encoded_string3 = """<button onclick='document.getElementById("audio2222").play()'>play audio_sentence<audio controls id="audio2222" style="display: none"><source src="data:audio/mpeg;base64,{}"></audio></button>""".format(
                    encoded_string3
                )
            except:

                encoded_string3 = ""
        else:
            encoded_string3 = ""
        fields = {
            "audio": encoded_string2,
            "audio_sentence": encoded_string3,
            "image": encoded_string,
        }
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
            _TR("端口号"), getspinbox(0, 65536, globalconfig["ankiconnect"], "port")
        )
        layout.addRow(
            _TR("DeckName"), getlineedit(globalconfig["ankiconnect"], "DeckName")
        )
        layout.addRow(
            _TR("ModelName"), getlineedit(globalconfig["ankiconnect"], "ModelName2")
        )

        layout.addRow(
            _TR("允许重复"),
            getsimpleswitch(globalconfig["ankiconnect"], "allowDuplicate"),
        )
        layout.addRow(
            _TR("添加时更新模板"),
            getsimpleswitch(globalconfig["ankiconnect"], "autoUpdateModel"),
        )
        layout.addRow(
            _TR("截图后进行OCR"),
            getsimpleswitch(globalconfig["ankiconnect"], "ocrcroped"),
        )

        layout.addWidget(QLabel())
        layout.addRow(_TR("录音"), QLabel())
        lb = QLabel()
        lb.setOpenExternalLinks(True)
        lb.setText(
            '<a href="https://github.com/HIllya51/RESOURCES/releases/download/softwares/virtual-audio.zip">virtual-audio-capturer</a>'
        )
        layout.addRow(_TR("安装录音驱动"), lb)
        ffmpegpath = getlineedit(globalconfig, "ffmpeg", readonly=True)

        def selectpath():
            f = QFileDialog.getExistingDirectory()
            if f != "":
                ffmpegpath.setText(f)

        layout.addRow(
            _TR("ffmpeg"),
            getboxlayout(
                [
                    ffmpegpath,
                    getcolorbutton(
                        "",
                        "",
                        selectpath,
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ],
                makewidget=True,
            ),
        )

        return wid

    def startorendrecord(self, target: QLineEdit, idx):
        if idx == 1:
            self.recorder = ffmpeg_virtual_audio_capturer()
        else:
            self.recorder.end()
            target.setText(self.recorder.file)

    def createaddtab(self):
        layout = QVBoxLayout()
        wid = QWidget()
        wid.setLayout(layout)
        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        soundbutton2 = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton2.clicked.connect(self.langdu2)
        cropbutton = QPushButton(qtawesome.icon("fa.crop"), "")
        cropbutton.clicked.connect(self.crop)

        self.audiopath = QLineEdit()
        self.audiopath.setReadOnly(True)
        self.audiopath_sentence = QLineEdit()
        self.audiopath_sentence.setReadOnly(True)
        self.editpath = QLineEdit()
        self.editpath.setReadOnly(True)
        self.viewimagelabel = QLabel()
        self.editpath.textChanged.connect(self.wrappedpixmap)
        self.example = QPlainTextEdit()
        self.remarks = QTextEdit()
        recordbtn1 = statusbutton(icons=["fa.microphone", "fa.stop"], colors=[""])
        recordbtn1.statuschanged1.connect(
            functools.partial(self.startorendrecord, self.audiopath)
        )
        recordbtn2 = statusbutton(icons=["fa.microphone", "fa.stop"], colors=[""])
        recordbtn2.statuschanged1.connect(
            functools.partial(self.startorendrecord, self.audiopath_sentence)
        )
        layout.addLayout(
            getboxlayout(
                [
                    getboxlayout(
                        [
                            getboxlayout(
                                [QLabel(_TR("例句")), self.example],
                                QVBoxLayout,
                                margin0=True,
                            ),
                            getboxlayout(
                                [QLabel(_TR("备注")), self.remarks],
                                QVBoxLayout,
                                margin0=True,
                            ),
                        ],
                        QVBoxLayout,
                    ),
                    getboxlayout(
                        [
                            getboxlayout(
                                [
                                    QLabel(_TR("语音")),
                                    self.audiopath,
                                    recordbtn1,
                                    soundbutton,
                                    getcolorbutton(
                                        "",
                                        "",
                                        functools.partial(
                                            self.selecfile, self.audiopath
                                        ),
                                        icon="fa.gear",
                                        constcolor="#FF69B4",
                                    ),
                                ]
                            ),
                            getboxlayout(
                                [
                                    QLabel(_TR("语音_例句")),
                                    self.audiopath_sentence,
                                    recordbtn2,
                                    soundbutton2,
                                    getcolorbutton(
                                        "",
                                        "",
                                        functools.partial(
                                            self.selecfile, self.audiopath_sentence
                                        ),
                                        icon="fa.gear",
                                        constcolor="#FF69B4",
                                    ),
                                ]
                            ),
                            getboxlayout(
                                [
                                    QLabel(_TR("截图")),
                                    self.editpath,
                                    cropbutton,
                                    getcolorbutton(
                                        "",
                                        "",
                                        functools.partial(
                                            self.selecfile, self.editpath
                                        ),
                                        icon="fa.gear",
                                        constcolor="#FF69B4",
                                    ),
                                ]
                            ),
                            self.viewimagelabel,
                        ],
                        QVBoxLayout,
                    ),
                ]
            )
        )

        self.tagsedit = QLineEdit()
        layout.addLayout(getboxlayout([QLabel(_TR("Tags(split by |)")), self.tagsedit]))

        btn = QPushButton(_TR("添加"))
        btn.clicked.connect(self.errorwrap)
        layout.addWidget(btn)

        self.__ocrsettext.connect(self.example.appendPlainText)

        self.reset("")
        return wid

    def wrappedpixmap(self, src):
        if not src:
            return
        pix = QPixmap.fromImage(QImage(src))
        rate = self.devicePixelRatioF()
        pix.setDevicePixelRatio(rate)
        if (
            pix.width() > self.viewimagelabel.width()
            or pix.height() > self.viewimagelabel.height()
        ):
            pix = pix.scaled(self.viewimagelabel.size() * rate, Qt.KeepAspectRatio)
        self.viewimagelabel.setPixmap(pix)

    def selecfile(self, item):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            item.setText(res)

    def reset(self, text):
        self.currentword = text
        if text and len(text):
            self.ruby = json.dumps(gobject.baseobject.translation_ui.parsehira(text))
        else:
            self.ruby = ""
        self.editpath.clear()
        self.audiopath.clear()
        self.audiopath_sentence.clear()

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
        autoUpdateModel = globalconfig["ankiconnect"]["autoUpdateModel"]
        allowDuplicate = globalconfig["ankiconnect"]["allowDuplicate"]
        anki.global_port = globalconfig["ankiconnect"]["port"]
        ModelName = globalconfig["ankiconnect"]["ModelName2"]
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
            if autoUpdateModel:
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
        for k, _ in [
            ("audio", self.audiopath.text()),
            ("audio_sentence", self.audiopath_sentence.text()),
            ("image", self.editpath.text()),
        ]:
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
            media[0] + media[1],
            media[2],
        )


class searchwordW(closeashidewindow):
    getnewsentencesignal = pyqtSignal(str, bool)
    showtabsignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(searchwordW, self).__init__(parent, globalconfig, "sw_geo")
        self.ankiwindow = AnkiWindow()
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowTitle(_TR("查词"))

    def showresfun(self, k, res):
        self.cache_results[k] = res

        thisp = globalconfig["cishu"][k]["args"]["priority"]
        idx = 0
        for kk in self.tabks:
            if globalconfig["cishu"][kk]["args"]["priority"] >= thisp:
                idx += 1
        self.tabks.insert(idx, k)
        self.tab.insertTab(idx, _TR(globalconfig["cishu"][k]["name"]))

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"))

        self.showtabsignal.connect(self.showresfun)

        ww = QWidget(self)
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.vboxlayout = QVBoxLayout()
        ww.setLayout(self.vboxlayout)
        self.searchlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchlayout)
        self.searchtext = QLineEdit()
        self.searchtext.textChanged.connect(self.ankiwindow.reset)
        self.searchlayout.addWidget(self.searchtext)
        searchbutton = QPushButton(qtawesome.icon("fa.search"), "")  # _TR("搜索"))

        searchbutton.clicked.connect(lambda: self.search((self.searchtext.text())))
        self.searchlayout.addWidget(searchbutton)

        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        self.searchlayout.addWidget(soundbutton)

        ankiconnect = statusbutton(icons=["fa.adn"], colors=["", "#FF69B4"])
        ankiconnect.statuschanged2.connect(self.onceaddankiwindow)
        self.searchlayout.addWidget(ankiconnect)

        self.tab = QTabBar(self)
        self.tab.currentChanged.connect(
            lambda idx: self.textOutput.setHtml(self.cache_results[self.tabks[idx]])
        )
        self.tabks = []
        self.setCentralWidget(ww)

        textOutput = QTextBrowser(self)
        textOutput.setUndoRedoEnabled(False)
        textOutput.setReadOnly(True)
        textOutput.setOpenLinks(False)
        self.textOutput = textOutput
        self.cache_results = {}
        self.hiding = True

        tablayout = QVBoxLayout()
        tablayout.addWidget(self.tab)
        tablayout.addWidget(textOutput)
        tablayout.setContentsMargins(0, 0, 0, 0)
        tablayout.setSpacing(0)
        self.vboxlayout.addLayout(tablayout)
        self.isfirstshowanki = True

    def onceaddankiwindow(self, idx):
        if idx == 1:
            if self.isfirstshowanki:
                self.vboxlayout.addWidget(self.ankiwindow)
            else:
                self.ankiwindow.show()
        else:
            self.ankiwindow.hide()
        self.isfirstshowanki = False

    def langdu(self):
        if gobject.baseobject.reader:
            gobject.baseobject.reader.read(self.searchtext.text(), True)

    def generate_explains(self):
        res = []
        tabks = []
        for k, v in self.cache_results.items():
            if len(v) == 0:
                continue
            thisp = globalconfig["cishu"][k]["args"]["priority"]
            idx = 0
            for i in tabks:
                if i >= thisp:
                    idx += 1
            k = _TR(globalconfig["cishu"][k]["name"])
            tabks.append(thisp)
            res.insert(idx, {"source": k, "content": v})
        return res

    def getnewsentence(self, sentence, append):
        self.showNormal()
        if append:
            sentence = self.searchtext.text() + sentence
        self.searchtext.setText(sentence)

        self.ankiwindow.example.setPlainText(gobject.baseobject.currenttext)
        self.search(sentence)

    def search(self, sentence):
        if sentence == "":
            return
        self.ankiwindow.reset(sentence)
        for i in range(self.tab.count()):
            self.tab.removeTab(0)
        self.tabks.clear()
        self.cache_results.clear()
        for k, cishu in gobject.baseobject.cishus.items():
            cishu.callback = functools.partial(self.showtabsignal.emit, k)
            cishu.safesearch(sentence)
