from qtsymbols import *
import json, time, functools, os, base64, uuid
from urllib.parse import quote
from traceback import print_exc
import qtawesome, requests, gobject, windows, winsharedutils
import myutils.ankiconnect as anki
from myutils.hwnd import grabwindow
from myutils.config import globalconfig, _TR, static_data
from myutils.utils import loopbackrecorder, parsekeystringtomodvkcode
from myutils.wrapper import threader, tryprint
from myutils.ocrutil import imageCut, ocr_run
from gui.rangeselect import rangeselct_function
from gui.usefulwidget import (
    closeashidewindow,
    statusbutton,
    getQMessageBox,
    auto_select_webview,
    getboxlayout,
    getspinbox,
    getsimplecombobox,
    getlineedit,
    listediter,
    listediterline,
    pixmapviewer,
    FQPlainTextEdit,
    FQLineEdit,
    getsimpleswitch,
    makesubtab_lazy,
    getIconButton,
    saveposwindow,
    tabadd_lazy,
)
from gui.dynalang import (
    LPushButton,
    LLabel,
    LTabWidget,
    LTabBar,
    LFormLayout,
    LLabel,
    LMainWindow,
    LAction,
)


def getimageformatlist():
    _ = [_.data().decode() for _ in QImageWriter.supportedImageFormats()]
    if globalconfig["imageformat"] == -1 or globalconfig["imageformat"] >= len(_):
        globalconfig["imageformat"] = _.index("png")
    return _


def getimageformat():

    return getimageformatlist()[globalconfig["imageformat"]]


class AnkiWindow(QWidget):
    __ocrsettext = pyqtSignal(str)
    refreshhtml = pyqtSignal()
    settextsignal = pyqtSignal(QObject, str)

    def settextsignalf(self, obj, text):
        obj.setText(text)

    def callbacktts(self, edit, sig, data):
        if sig != edit.sig:
            return
        fname = gobject.gettempdir(str(uuid.uuid4()) + ".mp3")
        with open(fname, "wb") as ff:
            ff.write(data)
        self.settextsignal.emit(edit, os.path.abspath(fname))
        # 这几个settext有一定概率触发谜之bug，导致直接秒闪退无log

    def langdu(self):
        self.audiopath.sig = uuid.uuid4()
        if gobject.baseobject.reader:
            gobject.baseobject.reader.ttscallback(
                self.currentword,
                functools.partial(self.callbacktts, self.audiopath, self.audiopath.sig),
            )

    def langdu2(self):
        self.audiopath_sentence.sig = uuid.uuid4()
        if gobject.baseobject.reader:
            gobject.baseobject.reader.ttscallback(
                self.example.toPlainText(),
                functools.partial(
                    self.callbacktts,
                    self.audiopath_sentence,
                    self.audiopath_sentence.sig,
                ),
            )

    @threader
    def asyncocr(self, img):
        self.__ocrsettext.emit(ocr_run(img)[0])

    def crop(self):
        def ocroncefunction(rect):
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            fname = gobject.gettempdir(str(uuid.uuid4()) + "." + getimageformat())
            img.save(fname)
            self.settextsignal.emit(self.editpath, os.path.abspath(fname))
            if globalconfig["ankiconnect"]["ocrcroped"]:
                self.asyncocr(img)

        rangeselct_function(ocroncefunction, False)

    def __init__(self, p) -> None:
        super().__init__()
        self.refsearchw: searchwordW = p
        self.settextsignal.connect(self.settextsignalf)
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

        spliter = QSplitter()
        baselay.addWidget(spliter)
        edittemptab = LTabWidget()
        self.previewtab = LTabBar()
        revertbtn = LPushButton("恢复")
        revertbtn.clicked.connect(self.loadedits)
        savebtn = LPushButton("保存")
        savebtn.clicked.connect(self.saveedits)

        spliter.addWidget(
            getboxlayout(
                [
                    edittemptab,
                    getboxlayout([revertbtn, savebtn], makewidget=True),
                ],
                lc=QVBoxLayout,
                margin0=True,
                makewidget=True,
            )
        )

        self.htmlbrowser = auto_select_webview(self, True)
        self.htmlbrowser.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        spliter.addWidget(
            getboxlayout(
                [self.previewtab, self.htmlbrowser],
                lc=QVBoxLayout,
                margin0=True,
                makewidget=True,
            )
        )
        self.fronttext = FQPlainTextEdit()
        self.backtext = FQPlainTextEdit()
        self.csstext = FQPlainTextEdit()
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

    def makedictionaryHTML(self, dictionarys):
        if not dictionarys:
            return ""
        htmlcontents = ""
        for iiii in range(len(dictionarys)):
            htmlcontents += f'<div id="luna_dict_tab_{dictionarys[iiii]["dict"]}" class="tab-pane">{dictionarys[iiii]["content"]}</div>'
        return htmlcontents

    def loadfileds(self):
        word = self.currentword
        dictionarys = self.refsearchw.generate_dictionarys()
        remarks = self.remarks.toPlainText()
        example = self.example.toPlainText()
        if globalconfig["ankiconnect"]["boldword"]:
            if self.example.hiras is None:
                self.example.hiras = gobject.baseobject.parsehira(example)
            collect = []
            for hira in self.example.hiras:
                if hira["orig"] == word or hira.get("origorig", None) == word:
                    collect.append(f'<b>{hira["orig"]}</b>')
                else:
                    collect.append(hira["orig"])
            example = "".join(collect)
        ruby = self.zhuyinedit.toPlainText()
        dictionaryInfo = []
        dictionaryContent = {}
        for _ in dictionarys:
            dictionaryInfo.append(
                {"dict": _["dict"], "name": globalconfig["cishu"][_["dict"]]["name"]}
            )
            dictionaryContent[_["dict"]] = quote(_["content"])
        fields = {
            "word": word,
            "rubytextHtml": ruby,
            "dictionaryContent": json.dumps(dictionaryContent),
            "dictionaryInfo": json.dumps(dictionaryInfo, ensure_ascii=False),
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
            "audio_for_word": encoded_string2,
            "audio_for_example_sentence": encoded_string3,
            "screenshot": encoded_string,
        }
        return fields

    def saveedits(self):
        model_htmlfront = self.fronttext.toPlainText()
        model_htmlback = self.backtext.toPlainText()
        model_css = self.csstext.toPlainText()
        with open(
            gobject.getuserconfigdir("anki_2/back.html"), "w", encoding="utf8"
        ) as ff:
            ff.write(model_htmlback)
        with open(
            gobject.getuserconfigdir("anki_2/front.html"), "w", encoding="utf8"
        ) as ff:
            ff.write(model_htmlfront)
        with open(
            gobject.getuserconfigdir("anki_2/style.css"), "w", encoding="utf8"
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
        layout.addRow(
            "ModelName", getlineedit(globalconfig["ankiconnect"], "ModelName6")
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
            "不添加辞书",
            getIconButton(self.vistranslate_rank, "fa.gear"),
        )
        layout.addRow(
            "成功添加后关闭窗口",
            getsimpleswitch(globalconfig["ankiconnect"], "addsuccautoclose"),
        )

    def vistranslate_rank(self):
        listediter(
            self,
            "不添加辞书",
            "不添加辞书",
            globalconfig["ignoredict"],
            candidates=list(globalconfig["cishu"].keys()),
            namemapfunction=lambda k: globalconfig["cishu"][k]["name"],
        )

    @threader
    def simulate_key(self, i):
        try:
            keystring = globalconfig["ankiconnect"]["simulate_key"][str(i)]["keystring"]
        except:
            return
        if not keystring:
            return
        try:
            windows.SetForegroundWindow(gobject.baseobject.hwnd)
            time.sleep(0.1)
        except:
            pass
        try:
            modes, vkcode = parsekeystringtomodvkcode(keystring, modes=True)
        except:
            return
        for mode in modes:
            windows.keybd_event(mode, 0, 0, 0)
        windows.keybd_event(vkcode, 0, 0, 0)
        time.sleep(0.1)
        windows.keybd_event(vkcode, 0, windows.KEYEVENTF_KEYUP, 0)
        for mode in modes:
            windows.keybd_event(mode, 0, windows.KEYEVENTF_KEYUP, 0)

    def startorendrecord(self, ii, target: QLineEdit, idx):
        if idx == 1:
            self.recorders[ii] = loopbackrecorder()
            self.simulate_key(ii)
        else:
            self.recorders[ii].end(
                callback=functools.partial(self.settextsignal.emit, target)
            )

    def createaddtab(self):
        self.recorders = {}
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
            lambda: grabwindow(
                getimageformat(),
                functools.partial(self.settextsignal.emit, self.editpath),
            )
        )

        self.audiopath = QLineEdit()
        self.audiopath.setReadOnly(True)
        self.audiopath_sentence = QLineEdit()
        self.audiopath_sentence.setReadOnly(True)
        self.editpath = QLineEdit()
        self.editpath.setReadOnly(True)
        self.viewimagelabel = pixmapviewer()
        self.editpath.textChanged.connect(self.wrappedpixmap)
        self.example = FQPlainTextEdit()
        self.zhuyinedit = FQPlainTextEdit()
        self.example.hiras = None

        def __():
            self.example.hiras = None

        self.example.textChanged.connect(__)
        self.remarks = FQPlainTextEdit()
        recordbtn1 = statusbutton(icons=["fa.microphone", "fa.stop"], colors=["", ""])
        recordbtn1.statuschanged.connect(
            functools.partial(self.startorendrecord, 1, self.audiopath)
        )
        recordbtn2 = statusbutton(icons=["fa.microphone", "fa.stop"], colors=["", ""])
        recordbtn2.statuschanged.connect(
            functools.partial(self.startorendrecord, 2, self.audiopath_sentence)
        )
        self.recordbtn1 = recordbtn1
        self.recordbtn2 = recordbtn2

        combox = getsimplecombobox(
            globalconfig["ankiconnect"]["DeckNameS"],
            globalconfig["ankiconnect"],
            "DeckName_i",
        )

        def refreshcombo(combo: QComboBox):
            combo.clear()
            if len(globalconfig["ankiconnect"]["DeckNameS"]) == 0:
                globalconfig["ankiconnect"]["DeckNameS"].append("lunadeck")
            combo.addItems(globalconfig["ankiconnect"]["DeckNameS"])

        lb = QLabel("DeckName")
        lb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        folder_open = QPushButton(qtawesome.icon("fa.folder-open"), "")
        folder_open.clicked.connect(functools.partial(self.selecfile, self.audiopath))
        folder_open2 = QPushButton(qtawesome.icon("fa.folder-open"), "")
        folder_open2.clicked.connect(
            functools.partial(self.selecfile, self.audiopath_sentence)
        )
        folder_open3 = QPushButton(qtawesome.icon("fa.folder-open"), "")
        folder_open3.clicked.connect(functools.partial(self.selecfile, self.editpath))
        layout.addLayout(
            getboxlayout(
                [
                    getboxlayout(
                        [
                            getboxlayout(
                                [
                                    lb,
                                    getboxlayout(
                                        [
                                            getIconButton(
                                                lambda: listediter(
                                                    self,
                                                    "DeckName",
                                                    "DeckName",
                                                    globalconfig["ankiconnect"][
                                                        "DeckNameS"
                                                    ],
                                                    closecallback=functools.partial(
                                                        refreshcombo, combox
                                                    ),
                                                ),
                                                icon="fa.gear",
                                            ),
                                            combox,
                                        ]
                                    ),
                                ]
                            ),
                            getboxlayout(
                                [LLabel("注音"), self.zhuyinedit],
                                QVBoxLayout,
                                margin0=True,
                            ),
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
                            getboxlayout(
                                [
                                    LLabel("标签"),
                                    listediterline(
                                        "标签",
                                        "标签",
                                        globalconfig["ankiconnect"]["tags"],
                                    ),
                                ]
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
                                    folder_open,
                                ]
                            ),
                            getboxlayout(
                                [
                                    LLabel("语音_例句"),
                                    self.audiopath_sentence,
                                    recordbtn2,
                                    soundbutton2,
                                    folder_open2,
                                ]
                            ),
                            getboxlayout(
                                [
                                    LLabel("截图"),
                                    self.editpath,
                                    cropbutton,
                                    grabwindowbtn,
                                    folder_open3,
                                ]
                            ),
                            self.viewimagelabel,
                        ],
                        QVBoxLayout,
                    ),
                ]
            )
        )

        class LRButton(LPushButton):
            rightclick = pyqtSignal()

            def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
                if self.rect().contains(ev.pos()):
                    if ev.button() == Qt.MouseButton.RightButton:
                        self.rightclick.emit()
                return super().mouseReleaseEvent(ev)

        btn = LRButton("添加")
        btn.clicked.connect(functools.partial(self.errorwrap, False))
        btn.rightclick.connect(functools.partial(self.errorwrap, True))
        layout.addWidget(btn)

        self.__ocrsettext.connect(self.example.appendPlainText)

        self.reset("")
        return wid

    def wrappedpixmap(self, src):
        if os.path.exists(src) == False:
            pix = QPixmap()
        else:
            pix = QPixmap.fromImage(QImage(src))
        self.viewimagelabel.showpixmap(pix)

    def selecfile(self, item):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            item.setText(res)

    def makerubyhtml(self, ruby):
        if not ruby:
            return ""
        html = ""
        for i in range(len(ruby)):
            html += ruby[i]["orig"]
            if ruby[i]["orig"] != ruby[i]["hira"]:
                html += "<rt>" + ruby[i]["hira"] + "</rt>"
            else:
                html += "<rt></rt>"
        html = "<ruby>" + html + "</ruby>"
        return html

    def reset(self, text):
        self.currentword = text
        if text and len(text):
            self.zhuyinedit.setPlainText(
                self.makerubyhtml(gobject.baseobject.parsehira(text))
            )
        else:
            self.zhuyinedit.clear()
        self.editpath.clear()
        self.audiopath.clear()
        self.audiopath_sentence.clear()

    def errorwrap(self, close=False):
        try:
            self.addanki()
            if close or globalconfig["ankiconnect"]["addsuccautoclose"]:
                self.refsearchw.close()
            else:
                QToolTip.showText(QCursor.pos(), "添加成功", self)
        except requests.RequestException:
            getQMessageBox(self.refsearchw, "错误", "无法连接到anki")
        except anki.AnkiException as e:
            getQMessageBox(self.refsearchw, "错误", str(e))
        except:
            print_exc()

    def tryloadankitemplates(self):
        try:
            with open("userconfig/anki_2/back.html", "r", encoding="utf8") as ff:
                model_htmlback = ff.read()
            with open("userconfig/anki_2/front.html", "r", encoding="utf8") as ff:
                model_htmlfront = ff.read()
            with open("userconfig/anki_2/style.css", "r", encoding="utf8") as ff:
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
        ModelName = globalconfig["ankiconnect"]["ModelName6"]
        try:
            DeckName = globalconfig["ankiconnect"]["DeckNameS"][
                globalconfig["ankiconnect"]["DeckName_i"]
            ]
        except:
            DeckName = "lunadeck"
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
            ("audio_for_word", self.audiopath.text()),
            ("audio_for_example_sentence", self.audiopath_sentence.text()),
            ("screenshot", self.editpath.text()),
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


from cishu.cishubase import DictTree

DictNodeRole = Qt.ItemDataRole.UserRole + 1
DeterminedhasChildren = DictNodeRole + 1
isWordNode = DeterminedhasChildren + 1
isLabeleddWord = isWordNode + 1


class DynamicTreeModel(QStandardItemModel):
    def __init__(self, ref):
        super().__init__()
        self.ref = ref

    def hasChildren(self, index):
        if self.data(index, isWordNode):
            return False
        _DeterminedhasChildren = self.data(index, DeterminedhasChildren)
        if _DeterminedhasChildren is not None:
            return _DeterminedhasChildren
        return self.data(index, DictNodeRole) is not None

    def loadChildren(self, index: QModelIndex):
        if not index.isValid():
            return
        if self.data(index, isWordNode):
            return
        if self.data(index, DeterminedhasChildren) is not None:
            return
        node: DictTree = self.data(index, DictNodeRole)
        if not node:
            return
        childs = node.childrens()
        self.setData(index, len(childs) > 0, DeterminedhasChildren)
        thisitem = self.itemFromIndex(index)
        maketuples = tuple((tuple(_) for _ in globalconfig["wordlabel"]))
        dump = set()
        for c in childs:
            if isinstance(c, str):
                if c in dump:
                    continue
                dump.add(c)
                t = c
                has = False
            else:
                t = c.text()
                has = True
            item = QStandardItem(t)
            if has:
                item.setData(c, DictNodeRole)
            else:
                item.setData(True, isWordNode)
            if (thisitem.text(), t) in maketuples:
                item.setData(True, isLabeleddWord)
                item.setData(
                    QBrush(Qt.GlobalColor.cyan), Qt.ItemDataRole.BackgroundRole
                )
            thisitem.appendRow([item])
        self.ref(index)

    def onDoubleClicked(self, index: QModelIndex):
        if not self.data(index, isWordNode):
            return
        gobject.baseobject.searchwordW.search_word.emit(
            self.itemFromIndex(index).text(), False
        )


class kpQTreeView(QTreeView):
    enterpressed = pyqtSignal(QModelIndex)

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            self.enterpressed.emit(self.currentIndex())
        else:
            super().keyPressEvent(e)


class showdiction(LMainWindow):
    def setwordfilter(self, index=None):
        w = self.word.text()
        if index is None:
            item = self.model.invisibleRootItem()
            index = self.model.indexFromItem(self.model.invisibleRootItem())
        else:
            item = self.model.itemFromIndex(index)
        for i in range(item.rowCount()):
            _item = item.child(i)
            isw = _item.data(isWordNode)
            if isw is None:
                isw = False
            self.tree.setRowHidden(i, index, isw and (w not in _item.text()))
            self.setwordfilter(self.model.indexFromItem(_item))

    def showmenu(self, _):
        idx = self.tree.currentIndex()
        if not idx.isValid():
            return
        isw = idx.data(isWordNode)
        item = self.model.itemFromIndex(idx)
        menu = QMenu(self)
        copy = LAction("复制")
        search = LAction("查词")
        label = LAction("标记")
        label.setCheckable(True)
        menu.addAction(copy)
        if isw:
            menu.addAction(search)
            menu.addAction(label)
            label.setChecked(bool(idx.data(isLabeleddWord)))
        action = menu.exec(QCursor.pos())
        if action == search:
            self.model.onDoubleClicked(idx)
        elif copy == action:
            winsharedutils.clipboard_set(item.text())
        elif action == label:
            if not idx.data(isLabeleddWord):
                item.setData(True, isLabeleddWord)
                item.setData(
                    QBrush(Qt.GlobalColor.cyan), Qt.ItemDataRole.BackgroundRole
                )
                globalconfig["wordlabel"].append(
                    (
                        self.model.itemFromIndex(self.model.parent(idx)).text(),
                        item.text(),
                    )
                )

            else:
                item.setData(False, isLabeleddWord)
                item.setData(None, Qt.ItemDataRole.BackgroundRole)
                try:
                    globalconfig["wordlabel"].remove(
                        (
                            self.model.itemFromIndex(self.model.parent(idx)).text(),
                            item.text(),
                        )
                    )
                except:
                    pass

    def __init__(self, parent: QWidget):
        super(showdiction, self).__init__(parent)
        wordfilter = QHBoxLayout()
        word = QLineEdit()
        self.word = word
        word.returnPressed.connect(self.setwordfilter)
        wordfilter.addWidget(word)
        butn = getIconButton(self.setwordfilter, "fa.filter")
        wordfilter.addWidget(butn)

        self.resize(400, parent.height())
        self.setWindowTitle("查看")
        self.tree = kpQTreeView(self)
        self.tree.setHeaderHidden(True)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        __c = QWidget()
        __lay = QVBoxLayout()
        __c.setLayout(__lay)
        __lay.setSpacing(0)
        __lay.setContentsMargins(0, 0, 0, 0)
        __lay.addLayout(wordfilter)
        __lay.addWidget(self.tree)
        self.setCentralWidget(__c)

        self.model = DynamicTreeModel(self.setwordfilter)
        self.tree.setModel(self.model)
        self.tree.expanded.connect(self.model.loadChildren)
        root = self.model.invisibleRootItem()
        self.tree.doubleClicked.connect(self.model.onDoubleClicked)
        self.tree.enterpressed.connect(self.model.onDoubleClicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.showmenu)
        rows = []
        for k in globalconfig["cishuvisrank"]:
            cishu = gobject.baseobject.cishus[k]

            if not hasattr(cishu, "tree"):
                continue
            try:
                tree = cishu.tree()
            except:
                continue
            if not tree:
                continue

            item = QStandardItem(globalconfig["cishu"][k]["name"])
            item.setData(tree, DictNodeRole)
            rows.append(item)
        root.appendRows(rows)
        root.setData(len(rows) > 0, DeterminedhasChildren)


class searchwordW(closeashidewindow):
    search_word = pyqtSignal(str, bool)
    show_dict_result = pyqtSignal(float, str, str)

    def __init__(self, parent):
        super(searchwordW, self).__init__(parent, globalconfig["sw_geo"])
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.search_word.connect(self.__click_word_search_function)
        self.show_dict_result.connect(self.__show_dict_result_function)
        self.state = 0

    def __load(self):
        if self.state != 0:
            return
        self.state = 1
        self.setupUi()
        self.state = 2

    def showEvent(self, e):
        super().showEvent(e)
        self.__load()

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

    def _createnewwindowsearch(self, _):
        word = self.searchtext.text()

        class searchwordWx(searchwordW):
            def closeEvent(self1, event: QCloseEvent):
                self1.deleteLater()
                super(saveposwindow, self1).closeEvent(event)

        _ = searchwordWx(self.parent())
        _.show()
        _.searchtext.setText(word)
        _.__search_by_click_search_btn()

    def setupUi(self):
        self.setWindowTitle("查词")
        self.ankiwindow = AnkiWindow(self)
        self.setWindowIcon(qtawesome.icon("fa.search"))
        self.thisps = {}
        self.hasclicked = False

        ww = QWidget(self)
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.vboxlayout = QVBoxLayout()
        ww.setLayout(self.vboxlayout)
        self.searchlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchlayout)
        self.searchtext = FQLineEdit()
        self.searchtext.textChanged.connect(self.ankiwindow.reset)
        self.history_last_btn = statusbutton(
            icons=["fa.arrow-left", "fa.arrow-left"], colors=["", ""]
        )
        self.history_last_btn.clicked.connect(
            functools.partial(self.__move_history_search, -1)
        )
        self.history_next_btn = statusbutton(
            icons=["fa.arrow-right", "fa.arrow-right"], colors=["", ""]
        )
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
        searchbutton.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        searchbutton.customContextMenuRequested.connect(self._createnewwindowsearch)
        self.searchtext.returnPressed.connect(searchbutton.clicked.emit)

        searchbutton.clicked.connect(self.__search_by_click_search_btn)
        self.searchlayout.addWidget(searchbutton)

        soundbutton = QPushButton(qtawesome.icon("fa.music"), "")
        soundbutton.clicked.connect(self.langdu)
        self.soundbutton = soundbutton
        self.searchlayout.addWidget(soundbutton)

        ankiconnect = statusbutton(
            icons=["fa.adn", "fa.adn"], colors=["", globalconfig["buttoncolor2"]]
        )
        ankiconnect.statuschanged.connect(self.onceaddankiwindow)
        ankiconnect.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        ankiconnect.customContextMenuRequested.connect(
            lambda _: self.ankiwindow.errorwrap()
        )
        self.ankiconnect = ankiconnect
        self.searchlayout.addWidget(ankiconnect)

        self.tab = CustomTabBar()
        self.tab.tabBarClicked.connect(self.tabclicked)
        self.tabcurrentindex = -1

        def __(idx):
            if self.tabcurrentindex == idx:
                return
            self.tabcurrentindex = idx
            if idx == -1:
                return
            if not self.hasclicked:
                return
            self.tabclicked(idx)

        self.tab.currentChanged.connect(__)
        self.tabks = []
        self.setCentralWidget(ww)
        self.textOutput = auto_select_webview(self, True)
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
                self.ankiwindow.setMinimumHeight(1)
                self.ankiwindow.setMinimumWidth(1)
            else:
                self.ankiwindow.show()
        else:
            self.ankiwindow.hide()
        self.isfirstshowanki = False

    def langdu(self):
        if gobject.baseobject.reader:
            gobject.baseobject.audioplayer.timestamp = uuid.uuid4()
            gobject.baseobject.reader.read(
                self.searchtext.text(), True, gobject.baseobject.audioplayer.timestamp
            )

    def generate_dictionarys(self):
        res = []
        tabks = []
        for k, v in self.cache_results.items():
            if k in globalconfig["ignoredict"]:
                continue
            if len(v) == 0:
                continue
            thisp = self.thisps.get(k, 0)

            idx = 0
            for i in tabks:
                if i >= thisp:
                    idx += 1
            tabks.append(thisp)
            res.insert(idx, {"dict": k, "content": v})
        return res

    def __click_word_search_function(self, word, append):
        self.showNormal()
        if self.state != 2:
            return
        word = word.strip()
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
        self.ankiwindow.remarks.setPlainText(gobject.baseobject.currenttranslate)
        if globalconfig["ankiconnect"]["autocrop"]:
            grabwindow(
                getimageformat(),
                functools.partial(
                    self.ankiwindow.settextsignal.emit, self.ankiwindow.editpath
                ),
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
