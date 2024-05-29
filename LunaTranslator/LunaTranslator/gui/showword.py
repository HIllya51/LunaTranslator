from qtsymbols import *
from myutils.hwnd import grabwindow

from urllib.parse import quote
from traceback import print_exc
import requests, json, time
import qtawesome, functools, os, base64
import gobject, uuid, windows
from myutils.utils import getimageformat, parsekeystringtomodvkcode, unsupportkey
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
    getsimplekeyseq,
    getcolorbutton,
    tabadd_lazy,
)
from myutils.subproc import subproc_w
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run
from gui.rangeselect import rangeselct_function


class loopbackrecorder:
    def __init__(self):
        os.makedirs("cache/temp", exist_ok=True)
        self.file = os.path.abspath(
            os.path.join("cache/temp", str(time.time()) + ".wav")
        )
        try:
            self.waitsignal = str(time.time())
            self.engine = subproc_w(
                './files/plugins/loopbackaudio.exe "{}"  "{}"'.format(
                    self.file, self.waitsignal
                ),
            )
        except:
            print_exc()

    @threader
    def end(self, callback):
        windows.SetEvent(
            windows.AutoHandle(windows.CreateEvent(False, False, self.waitsignal))
        )
        self.engine.wait()
        filewav = self.file
        if os.path.exists(filewav) == False:
            callback("")
            return
        filemp3 = filewav.replace(".wav", ".mp3")
        subproc_w(
            './files/plugins/shareddllproxy32.exe mainmp3 "{}"  "{}"'.format(
                filewav, filemp3
            ),
            run=True,
        )
        if os.path.exists(filemp3):
            os.remove(filewav)
            callback(filemp3)
        else:
            callback(filewav)


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
        fname = "cache/temp/" + str(uuid.uuid4()) + ".mp3"
        os.makedirs("cache/temp", exist_ok=True)
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
            fname = "cache/temp/" + str(uuid.uuid4()) + "." + getimageformat()
            os.makedirs("cache/temp", exist_ok=True)
            img.save(fname)
            self.editpath.setText(os.path.abspath(fname))
            if globalconfig["ankiconnect"]["ocrcroped"]:
                self.asyncocr(img)

        rangeselct_function(self, ocroncefunction, False, False)

    def __init__(self) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        html = f'<style>{model_css}</style><div class="card">{html}</div>'
        self.htmlbrowser.setHtml(html)

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
        self.htmlbrowser.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
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
        explain = quote(json.dumps(gobject.baseobject.searchwordW.generate_explains()))

        remarks = self.remarks.toPlainText()
        example = self.example.toPlainText()
        if globalconfig["ankiconnect"]["boldword"]:
            if self.example.hiras is None:
                self.example.hiras = gobject.baseobject.translation_ui.parsehira(
                    example
                )
            collect = []
            for hira in self.example.hiras:
                if hira["orig"] == word or hira.get("origorig", None) == word:
                    collect.append(f'<b>{hira["orig"]}</b>')
                else:
                    collect.append(hira["orig"])
            example = "".join(collect)
        ruby = self.ruby
        fields = {
            "word": word,
            "rubytext": ruby,
            "explain": explain,
            "example_sentence": example.replace("\n", "<br>"),
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
            _TR("ModelName"), getlineedit(globalconfig["ankiconnect"], "ModelName5")
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

        layout.addRow(
            _TR("自动TTS"),
            getsimpleswitch(globalconfig["ankiconnect"], "autoruntts"),
        )
        layout.addRow(
            _TR("自动TTS_例句"),
            getsimpleswitch(globalconfig["ankiconnect"], "autoruntts2"),
        )
        layout.addRow(
            _TR("自动截图"),
            getsimpleswitch(globalconfig["ankiconnect"], "autocrop"),
        )
        layout.addRow(
            _TR("例句中加粗单词"),
            getsimpleswitch(globalconfig["ankiconnect"], "boldword"),
        )

        layout.addRow(
            _TR("录音时模拟按键"),
            getboxlayout(
                [
                    getsimpleswitch(
                        globalconfig["ankiconnect"]["simulate_key"]["1"], "use"
                    ),
                    getsimplekeyseq(
                        globalconfig["ankiconnect"]["simulate_key"]["1"], "keystring"
                    ),
                ],
                margin0=True,
                makewidget=True,
            ),
        )
        layout.addRow(
            _TR("录音时模拟按键_例句"),
            getboxlayout(
                [
                    getsimpleswitch(
                        globalconfig["ankiconnect"]["simulate_key"]["2"], "use"
                    ),
                    getsimplekeyseq(
                        globalconfig["ankiconnect"]["simulate_key"]["2"], "keystring"
                    ),
                ],
                margin0=True,
                makewidget=True,
            ),
        )
        return wid

    @threader
    def simulate_key(self, i):
        if not globalconfig["ankiconnect"]["simulate_key"][i]["use"]:
            return
        windows.SetForegroundWindow(gobject.baseobject.textsource.hwnd)
        time.sleep(0.1)
        try:
            modes, vkcode = parsekeystringtomodvkcode(
                globalconfig["ankiconnect"]["simulate_key"][i]["keystring"], modes=True
            )
        except unsupportkey as e:
            print("不支持的键")
            return
        for mode in modes:
            windows.keybd_event(mode, 0, 0, 0)
        windows.keybd_event(vkcode, 0, 0, 0)
        time.sleep(0.1)
        windows.keybd_event(vkcode, 0, windows.KEYEVENTF_KEYUP, 0)
        for mode in modes:
            windows.keybd_event(mode, 0, windows.KEYEVENTF_KEYUP, 0)

    def startorendrecord(self, i, target: QLineEdit, idx):
        if idx == 1:
            self.recorder = loopbackrecorder()
            self.simulate_key(i)
        else:
            self.recorder.end(callback=target.setText)

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
        self.example.hiras = None

        def __():
            self.example.hiras = None

        self.example.textChanged.connect(__)
        self.remarks = QPlainTextEdit()
        recordbtn1 = statusbutton(icons=["fa.microphone", "fa.stop"], colors=[""])
        recordbtn1.statuschanged1.connect(
            functools.partial(self.startorendrecord, "1", self.audiopath)
        )
        recordbtn2 = statusbutton(icons=["fa.microphone", "fa.stop"], colors=[""])
        recordbtn2.statuschanged1.connect(
            functools.partial(self.startorendrecord, "2", self.audiopath_sentence)
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
        if os.path.exists(src) == False:
            pix = QPixmap()
        else:
            pix = QPixmap.fromImage(QImage(src))
        rate = self.devicePixelRatioF()
        pix.setDevicePixelRatio(rate)
        if (
            pix.width() > self.viewimagelabel.width()
            or pix.height() > self.viewimagelabel.height()
        ):
            pix = pix.scaled(
                self.viewimagelabel.size() * rate, Qt.AspectRatioMode.KeepAspectRatio
            )
        self.viewimagelabel.setPixmap(pix)

    def selecfile(self, item):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            item.setText(res)

    def reset(self, text):
        self.currentword = text
        if text and len(text):
            self.ruby = quote(
                json.dumps(
                    gobject.baseobject.translation_ui.parsehira(text),
                    ensure_ascii=False,
                )
            )
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
        ModelName = globalconfig["ankiconnect"]["ModelName5"]
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


class selectviewer(QWidget):
    def createviewer(self):
        if globalconfig["searchwordusewebview"] == False:

            textOutput = QTextBrowser(self)

            def openlink(url):
                try:
                    if url.url().lower().startswith("http"):
                        os.startfile(url.url())
                except:
                    pass

            textOutput.anchorClicked.connect(openlink)
            textOutput.setUndoRedoEnabled(False)
            textOutput.setReadOnly(True)
            textOutput.setOpenLinks(False)
        else:
            textOutput = auto_select_webview(self)
        return textOutput

    def __init__(self, parent) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.context = globalconfig["searchwordusewebview"]

        self.internal = self.createviewer()
        layout.addWidget(self.internal)

    def clear(self):
        self.internal.clear()

    def setHtml(self, html):
        if (globalconfig["searchwordusewebview"]) != self.context:
            self.context = globalconfig["searchwordusewebview"]
            self.layout().removeWidget(self.internal)
            self.internal = self.createviewer()
            self.layout().addWidget(self.internal)
        self.internal.setHtml(html)


class searchwordW(closeashidewindow):
    getnewsentencesignal = pyqtSignal(str, bool)
    showtabsignal = pyqtSignal(float, str, str)

    def __init__(self, parent):
        super(searchwordW, self).__init__(parent, globalconfig, "sw_geo")
        self.ankiwindow = AnkiWindow()
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.setWindowTitle(_TR("查词"))

    def showresfun(self, timestamp, k, res):
        if self.current != timestamp:
            return
        self.cache_results[k] = res

        thisp = globalconfig["cishu"][k]["args"]["priority"]
        idx = 0
        for kk in self.tabks:
            if globalconfig["cishu"][kk]["args"]["priority"] >= thisp:
                idx += 1
        self.tabks.insert(idx, k)
        self.tab.insertTab(idx, _TR(globalconfig["cishu"][k]["name"]))
        if len(self.tabks) == 1:
            self.tab.tabBarClicked.emit(0)

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

        self.tab.tabBarClicked.connect(
            lambda idx: self.textOutput.setHtml(self.cache_results[self.tabks[idx]])
        )
        self.tabks = []
        self.setCentralWidget(ww)
        self.textOutput = selectviewer(self)
        self.cache_results = {}
        self.hiding = True

        self.spliter = QSplitter()

        tablayout = QVBoxLayout()
        tablayout.setContentsMargins(0, 0, 0, 0)
        tablayout.setSpacing(0)
        tablayout.addWidget(self.tab)
        tablayout.addWidget(self.textOutput)
        w = QWidget()
        w.setLayout(tablayout)
        self.vboxlayout.addWidget(self.spliter)
        self.isfirstshowanki = True
        self.spliter.setOrientation(Qt.Orientation.Vertical)

        self.spliter.addWidget(w)

    def onceaddankiwindow(self, idx):
        if idx == 1:
            if self.isfirstshowanki:
                self.spliter.addWidget(self.ankiwindow)
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
        sentence = sentence.strip()
        self.showNormal()
        if append:
            sentence = self.searchtext.text() + sentence
        self.searchtext.setText(sentence)

        self.search(sentence)

        self.ankiwindow.example.setPlainText(gobject.baseobject.currenttext)
        if globalconfig["ankiconnect"]["autoruntts"]:
            self.ankiwindow.langdu()
        if globalconfig["ankiconnect"]["autoruntts2"]:
            self.ankiwindow.langdu2()

        if globalconfig["ankiconnect"]["autocrop"]:
            grabwindow(
                getimageformat(),
                self.ankiwindow.editpath.setText,
            )

    def search(self, sentence):
        current = time.time()
        self.current = current
        sentence = sentence.strip()
        if sentence == "":
            return
        self.ankiwindow.reset(sentence)
        for i in range(self.tab.count()):
            self.tab.removeTab(0)
        self.tabks.clear()
        self.textOutput.clear()
        self.cache_results.clear()
        for k, cishu in gobject.baseobject.cishus.items():
            cishu.safesearch(
                sentence, functools.partial(self.showtabsignal.emit, current, k)
            )
