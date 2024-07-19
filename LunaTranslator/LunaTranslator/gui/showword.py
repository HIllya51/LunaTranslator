from qtsymbols import *
import json, time, functools, os, base64, uuid
from urllib.parse import quote
from traceback import print_exc
import qtawesome, requests, gobject, windows
import myutils.ankiconnect as anki
from myutils.hwnd import grabwindow
from myutils.utils import parsekeystringtomodvkcode, unsupportkey
from myutils.config import globalconfig, _TR, static_data, savehook_new_data
from myutils.subproc import subproc_w
from myutils.wrapper import threader, tryprint
from myutils.ocrutil import imageCut, ocr_run_2
from gui.rangeselect import rangeselct_function
from gui.usefulwidget import (
    closeashidewindow,
    getQMessageBox,
    auto_select_webview,
    getboxlayout,
    getspinbox,
    getsimplecombobox,
    getlineedit,
    listediterline,
    getsimpleswitch,
    getsimplekeyseq,
    makesubtab_lazy,
    getIconButton,
    tabadd_lazy,
)
from gui.dynalang import LPushButton, LLabel, LTabWidget, LTabBar, LFormLayout, LLabel


def getimageformatlist():
    _ = [_.data().decode() for _ in QImageWriter.supportedImageFormats()]
    if globalconfig["imageformat"] == -1 or globalconfig["imageformat"] >= len(_):
        globalconfig["imageformat"] = _.index("png")
    return _


def getimageformat():

    return getimageformatlist()[globalconfig["imageformat"]]


class loopbackrecorder:
    def __init__(self):
        self.file = gobject.gettempdir(str(time.time()) + ".wav")
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
        fname = gobject.gettempdir(str(uuid.uuid4()) + ".mp3")
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
        self.__ocrsettext.emit(ocr_run_2(img))

    def crop(self):
        def ocroncefunction(rect):
            img = imageCut(
                0, rect[0][0], rect[0][1], rect[1][0], rect[1][1], False, True
            )
            fname = gobject.gettempdir(str(uuid.uuid4()) + "." + getimageformat())
            img.save(fname)
            self.editpath.setText(os.path.abspath(fname))
            if globalconfig["ankiconnect"]["ocrcroped"]:
                self.asyncocr(img)

        rangeselct_function(ocroncefunction, False, False)

    def __init__(self) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWindowTitle("Anki Connect")
        self.currentword = ""
        self.tabs = makesubtab_lazy(callback=self.ifshowrefresh)
        self.tabs.addTab(self.createaddtab(), "添加")
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

    def creattemplatetab(self, baselay):

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        wid = QWidget()
        wid.setLayout(layout)
        baselay.addWidget(wid)
        edittemptab = LTabWidget()
        self.previewtab = LTabBar()
        revertbtn = LPushButton("恢复")
        revertbtn.clicked.connect(self.loadedits)
        savebtn = LPushButton("保存")
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
        edittemptab.addTab(self.fronttext, "正面")
        edittemptab.addTab(self.backtext, "背面")
        edittemptab.addTab(self.csstext, "样式")
        self.previewtab.addTab("正面")
        self.previewtab.addTab("背面")
        self.loadedits()
        self.fronttext.textChanged.connect(lambda: self.refreshhtml.emit())
        self.backtext.textChanged.connect(lambda: self.refreshhtml.emit())
        self.csstext.textChanged.connect(lambda: self.refreshhtml.emit())
        self.previewtab.currentChanged.connect(lambda: self.refreshhtml.emit())

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
            "remarks": remarks.replace("\n", "<br>"),
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
        with open(
            gobject.getuserconfigdir("anki/back.html"), "w", encoding="utf8"
        ) as ff:
            ff.write(model_htmlback)
        with open(
            gobject.getuserconfigdir("anki/front.html"), "w", encoding="utf8"
        ) as ff:
            ff.write(model_htmlfront)
        with open(
            gobject.getuserconfigdir("anki/style.css"), "w", encoding="utf8"
        ) as ff:
            ff.write(model_css)

    def creatsetdtab(self, baselay):
        layout = LFormLayout()
        wid = QWidget()
        wid.setLayout(layout)
        baselay.addWidget(wid)
        layout.addRow(
            "端口号", getspinbox(0, 65536, globalconfig["ankiconnect"], "port")
        )
        layout.addRow("DeckName", getlineedit(globalconfig["ankiconnect"], "DeckName"))
        layout.addRow(
            "ModelName", getlineedit(globalconfig["ankiconnect"], "ModelName5")
        )

        layout.addRow(
            "允许重复",
            getsimpleswitch(globalconfig["ankiconnect"], "allowDuplicate"),
        )
        layout.addRow(
            "添加时更新模板",
            getsimpleswitch(globalconfig["ankiconnect"], "autoUpdateModel"),
        )
        layout.addRow(
            "截图后进行OCR",
            getsimpleswitch(globalconfig["ankiconnect"], "ocrcroped"),
        )

        layout.addRow(
            "自动TTS",
            getsimpleswitch(globalconfig["ankiconnect"], "autoruntts"),
        )
        layout.addRow(
            "自动TTS_例句",
            getsimpleswitch(globalconfig["ankiconnect"], "autoruntts2"),
        )
        layout.addRow(
            "自动截图",
            getsimpleswitch(globalconfig["ankiconnect"], "autocrop"),
        )
        layout.addRow(
            "截图保存格式",
            getsimplecombobox(
                getimageformatlist(), globalconfig, "imageformat", static=True
            ),
        )
        layout.addRow(
            "例句中加粗单词",
            getsimpleswitch(globalconfig["ankiconnect"], "boldword"),
        )
        layout.addRow(
            "备注中自动填入翻译",
            getsimpleswitch(globalconfig["ankiconnect"], "fillmaksastrans"),
        )

        layout.addRow(
            "录音时模拟按键",
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
            "录音时模拟按键_例句",
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

    @threader
    def simulate_key(self, i):
        def __internal__keystring(i):
            try:
                for _ in (0,):

                    if not gobject.baseobject.textsource:
                        break

                    gameuid = gobject.baseobject.textsource.gameuid
                    if not gameuid:
                        break
                    if savehook_new_data[gameuid]["follow_default_ankisettings"]:
                        break
                    if not savehook_new_data[gameuid][f"anki_simulate_key_{i}_use"]:
                        return None
                    return savehook_new_data[gameuid][
                        f"anki_simulate_key_{i}_keystring"
                    ]
            except:
                pass
            return globalconfig["ankiconnect"]["simulate_key"][i]["keystring"]

        keystring = __internal__keystring(i)
        if not keystring:
            return
        windows.SetForegroundWindow(gobject.baseobject.textsource.hwnd)
        time.sleep(0.1)
        try:
            modes, vkcode = parsekeystringtomodvkcode(keystring, modes=True)
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

        grabwindowbtn = QPushButton(qtawesome.icon("fa.camera"), "")
        grabwindowbtn.clicked.connect(
            lambda: grabwindow(getimageformat(), self.editpath.setText)
        )

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
                                [LLabel("例句"), self.example],
                                QVBoxLayout,
                                margin0=True,
                            ),
                            getboxlayout(
                                [LLabel("备注"), self.remarks],
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
                                    LLabel("语音"),
                                    self.audiopath,
                                    recordbtn1,
                                    soundbutton,
                                    getIconButton(
                                        functools.partial(
                                            self.selecfile, self.audiopath
                                        ),
                                        icon="fa.gear",
                                    ),
                                ]
                            ),
                            getboxlayout(
                                [
                                    LLabel("语音_例句"),
                                    self.audiopath_sentence,
                                    recordbtn2,
                                    soundbutton2,
                                    getIconButton(
                                        functools.partial(
                                            self.selecfile, self.audiopath_sentence
                                        ),
                                        icon="fa.gear",
                                    ),
                                ]
                            ),
                            getboxlayout(
                                [
                                    LLabel("截图"),
                                    self.editpath,
                                    cropbutton,
                                    grabwindowbtn,
                                    getIconButton(
                                        functools.partial(
                                            self.selecfile, self.editpath
                                        ),
                                        icon="fa.gear",
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

        layout.addLayout(
            getboxlayout(
                [
                    LLabel("标签"),
                    listediterline("标签", "标签", globalconfig["ankiconnect"]["tags"]),
                ]
            )
        )

        btn = LPushButton("添加")
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
                self.viewimagelabel.size() * rate,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
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
            if globalconfig["ankiconnect"]["addsuccautoclose"]:
                self.parent().parent().parent().close()
            else:
                QToolTip.showText(QCursor.pos(), "添加成功", self)
        except requests.RequestException:
            getQMessageBox(self, "错误", "无法连接到anki")
        except anki.AnkiException as e:
            getQMessageBox(self, "错误", str(e))
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

        def __internal__DeckName():
            try:
                for _ in (0,):

                    if not gobject.baseobject.textsource:
                        break

                    gameuid = gobject.baseobject.textsource.gameuid
                    if not gameuid:
                        break
                    if savehook_new_data[gameuid]["follow_default_ankisettings"]:
                        break

                    return savehook_new_data[gameuid]["anki_DeckName"]
            except:
                pass
            return globalconfig["ankiconnect"]["DeckName"]

        autoUpdateModel = globalconfig["ankiconnect"]["autoUpdateModel"]
        allowDuplicate = globalconfig["ankiconnect"]["allowDuplicate"]
        anki.global_port = globalconfig["ankiconnect"]["port"]
        ModelName = globalconfig["ankiconnect"]["ModelName5"]
        DeckName = __internal__DeckName()
        model_htmlfront, model_htmlback, model_css = self.tryloadankitemplates()
        tags = globalconfig["ankiconnect"]["tags"]
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


class CustomTabBar(LTabBar):
    def __init__(self) -> None:
        super().__init__()
        self.savesizehint = QSize()

    def sizeHint(self):
        size_hint = super().sizeHint()
        if size_hint.height():
            self.savesizehint = size_hint
        return self.savesizehint


class QLineEdit1(QLineEdit):
    def mousePressEvent(self, a0: qtawesome.QMouseEvent) -> None:
        # 点击浏览器后，无法重新获取焦点。
        windows.SetFocus(int(self.winId()))
        return super().mousePressEvent(a0)


class searchwordW(closeashidewindow):
    search_word = pyqtSignal(str, bool)
    show_dict_result = pyqtSignal(float, str, str)

    def __init__(self, parent):
        super(searchwordW, self).__init__(parent, globalconfig["sw_geo"])
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.search_word.connect(self.__click_word_search_function)
        self.show_dict_result.connect(self.__show_dict_result_function)

        self.setWindowTitle("查词")
        self.ankiwindow = AnkiWindow()
        self.setupUi()

    @tryprint
    def __show_dict_result_function(self, timestamp, k, res):
        if self.current != timestamp:
            return
        if not res:
            if (
                not self.hasclicked
                and self.thisps[k] == max(self.thisps.values())
                and len(self.cache_results)
            ):
                self.tab.setCurrentIndex(0)
                self.tab.tabBarClicked.emit(0)
                self.hasclicked = True
            self.thisps.pop(k)
            return
        self.cache_results[k] = res

        thisp = self.thisps.get(k, 0)
        idx = 0
        for kk in self.tabks:
            if self.thisps.get(kk, 0) >= thisp:
                idx += 1
        self.tabks.insert(idx, k)
        self.tab.insertTab(idx, (globalconfig["cishu"][k]["name"]))
        if not self.hasclicked:
            if thisp == max(self.thisps.values()):
                self.tab.setCurrentIndex(0)
                self.tab.tabBarClicked.emit(0)
                self.hasclicked = True

    def tabclicked(self, idx):
        self.hasclicked = True
        try:
            html = self.cache_results[self.tabks[idx]]
        except:
            return
        self.textOutput.setHtml(html)

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.search"))
        self.thisps = {}
        self.hasclicked = False

        ww = QWidget(self)
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.vboxlayout = QVBoxLayout()
        ww.setLayout(self.vboxlayout)
        self.searchlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchlayout)
        self.searchtext = QLineEdit1()
        self.searchtext.textChanged.connect(self.ankiwindow.reset)

        self.history_last_btn = QPushButton(qtawesome.icon("fa.arrow-left"), "")
        self.history_last_btn.clicked.connect(
            functools.partial(self.__move_history_search, -1)
        )
        self.history_next_btn = QPushButton(qtawesome.icon("fa.arrow-right"), "")
        self.history_next_btn.clicked.connect(
            functools.partial(self.__move_history_search, 1)
        )

        self.trace_history = []
        self.trace_history_idx = -1
        self.__set_history_btn_able()
        self.searchlayout.addWidget(self.history_last_btn)
        self.searchlayout.addWidget(self.history_next_btn)
        self.searchlayout.addWidget(self.searchtext)
        searchbutton = QPushButton(qtawesome.icon("fa.search"), "")

        searchbutton.clicked.connect(self.__search_by_click_search_btn)
        self.searchlayout.addWidget(searchbutton)

        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        self.searchlayout.addWidget(soundbutton)

        ankiconnect = statusbutton(
            icons=["fa.adn"], colors=["", globalconfig["buttoncolor2"]]
        )
        ankiconnect.statuschanged2.connect(self.onceaddankiwindow)
        self.searchlayout.addWidget(ankiconnect)

        self.tab = CustomTabBar()
        self.tab.tabBarClicked.connect(self.tabclicked)
        self.tabks = []
        self.setCentralWidget(ww)
        self.textOutput = auto_select_webview(self)
        self.textOutput.set_zoom(globalconfig["ZoomFactor"])
        self.textOutput.on_ZoomFactorChanged.connect(
            functools.partial(globalconfig.__setitem__, "ZoomFactor")
        )
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
            thisp = self.thisps.get(k, 0)
            idx = 0
            for i in tabks:
                if i >= thisp:
                    idx += 1
            k = _TR(globalconfig["cishu"][k]["name"])
            tabks.append(thisp)
            res.insert(idx, {"source": k, "content": v})
        return res

    def __click_word_search_function(self, word, append):
        word = word.strip()
        self.showNormal()
        if append:
            word = self.searchtext.text() + word
        self.searchtext.setText(word)

        self.search(word)
        if len(self.trace_history) == 0 or self.trace_history[-1] != word:
            self.trace_history.append(word)
        self.trace_history_idx = len(self.trace_history) - 1
        self.__set_history_btn_able()
        self.ankiwindow.example.setPlainText(gobject.baseobject.currenttext)
        if globalconfig["ankiconnect"]["autoruntts"]:
            self.ankiwindow.langdu()
        if globalconfig["ankiconnect"]["autoruntts2"]:
            self.ankiwindow.langdu2()
        if globalconfig["ankiconnect"]["fillmaksastrans"]:
            self.ankiwindow.remarks.setPlainText(gobject.baseobject.currenttranslate)
        if globalconfig["ankiconnect"]["autocrop"]:
            grabwindow(
                getimageformat(),
                self.ankiwindow.editpath.setText,
            )

    def __set_history_btn_able(self):
        self.history_next_btn.setEnabled(
            self.trace_history_idx < len(self.trace_history) - 1
        )
        self.history_last_btn.setEnabled(self.trace_history_idx > 0)

    def __move_history_search(self, offset):
        self.trace_history_idx += offset
        word = self.trace_history[self.trace_history_idx]
        self.__set_history_btn_able()
        self.searchtext.setText(word)
        self.search(word)

    def __search_by_click_search_btn(self):
        word = self.searchtext.text()
        self.search(word)

        if len(self.trace_history) == 0 or self.trace_history[-1] != word:
            self.trace_history.append(word)
        self.trace_history_idx = len(self.trace_history) - 1
        self.__set_history_btn_able()

    def search(self, word):
        current = time.time()
        self.current = current
        word = word.strip()
        if word == "":
            return
        self.ankiwindow.reset(word)
        for i in range(self.tab.count()):
            self.tab.removeTab(0)
        self.tabks.clear()
        self.textOutput.clear()
        self.cache_results.clear()

        self.thisps.clear()
        self.hasclicked = False
        pxx = 999
        for k in globalconfig["cishuvisrank"]:
            self.thisps[k] = pxx
            pxx -= 1
        for k, cishu in gobject.baseobject.cishus.items():
            cishu.safesearch(
                word, functools.partial(self.show_dict_result.emit, current, k)
            )
