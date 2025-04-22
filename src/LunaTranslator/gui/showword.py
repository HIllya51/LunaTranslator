from qtsymbols import *
import json, time, functools, os, base64, uuid
from urllib.parse import quote
from traceback import print_exc
import qtawesome, requests, gobject, windows, NativeUtils
import myutils.ankiconnect as anki
from myutils.hwnd import grabwindow
from myutils.config import globalconfig, static_data, _TR
from myutils.utils import (
    dynamiccishuname,
    loopbackrecorder,
    selectdebugfile,
    parsekeystringtomodvkcode,
    getimageformatlist,
    getimagefilefilter,
    checkmd5reloadmodule,
    getimageformat,
)
from sometypes import WordSegResult
from myutils.mecab import mecab
from myutils.wrapper import threader, tryprint
from myutils.ocrutil import imageCut, ocr_run
from gui.rangeselect import rangeselct_function
from gui.usefulwidget import (
    closeashidewindow,
    auto_select_webview,
    WebviewWidget,
    IconButton,
    getboxlayout,
    getboxwidget,
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
    threeswitch,
    VisLFormLayout,
)
from gui.dynalang import LPushButton, LLabel, LTabWidget, LTabBar, LAction
from myutils.audioplayer import bass_code_cast
from tts.basettsclass import TTSResult


class AnkiWindow(QWidget):
    __ocrsettext = pyqtSignal(str)
    refreshhtml = pyqtSignal()
    settextsignal = pyqtSignal(QObject, str)

    def settextsignalf(self, obj: QLineEdit, text):
        obj.setText(text)

    def callbacktts(self, edit, sig, data: TTSResult):
        if not data:
            return
        if sig != edit.sig:
            return
        data, ext = bass_code_cast(data.data, data.ext)
        fname = gobject.gettempdir(str(uuid.uuid4()) + "." + ext)
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
        self.__ocrsettext.emit(ocr_run(img).textonly)

    def crophide(self, s=False):
        currpos = gobject.baseobject.translation_ui.pos()
        currpos2 = self.window().pos()
        # hide会有隐藏动画残影
        if s:
            self.window().move(-9999, -9999)
            gobject.baseobject.translation_ui.move(-9999, -9999)

        def ocroncefunction(rect, img=None):
            if not img:
                img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            if img.isNull():
                return
            fname = gobject.gettempdir(str(uuid.uuid4()) + "." + getimageformat())
            img.save(fname)
            self.settextsignal.emit(self.editpath, os.path.abspath(fname))
            if globalconfig["ankiconnect"]["ocrcroped"]:
                self.asyncocr(img)

        def __ocroncefunction(rect, img=None):
            ocroncefunction(rect, img=img)
            if s:
                gobject.baseobject.translation_ui.move(currpos)
                self.window().move(currpos2)

        rangeselct_function(__ocroncefunction)

    def __init__(self, p) -> None:
        super().__init__()
        self.refsearchw: searchwordW = p
        self.settextsignal.connect(self.settextsignalf)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWindowTitle("Anki Connect")
        self.currentword = ""
        self.lastankid = None
        self.lastankiword = None
        self.tabs = makesubtab_lazy(callback=self.ifshowrefresh)
        self.tabs.addTab(self.createaddtab(), "添加")
        tabadd_lazy(self.tabs, "设置", self.creatsetdtab)
        tabadd_lazy(self.tabs, "模板", self.creattemplatetab)

        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)
        l.addWidget(self.tabs)
        self.refreshhtml.connect(self.refreshhtmlfunction)
        self.tabs.currentChanged.connect(self.ifshowrefresh)
        self.orientswitch = threeswitch(self, icons=["fa.arrows-h", "fa.arrows-v"])
        self.orientswitch.selectlayout(globalconfig["anki_Orientation_V"])
        self.orientswitch.btnclicked.connect(self.selectlayout)
        self.orientswitch.sizeChanged.connect(self.do_resize)

    def selectlayout(self, i):
        globalconfig["anki_Orientation_V"] = i
        self.refsearchw.spliter.setOrientation(
            Qt.Orientation.Vertical
            if globalconfig["anki_Orientation_V"]
            else Qt.Orientation.Horizontal
        )

    def resizeEvent(self, e: QResizeEvent):
        self.do_resize()

    def do_resize(self, _=None):
        x = self.width() - self.orientswitch.width()
        self.orientswitch.move(x, 0)

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
                    # else:
                    #     result += template[i : end_index + 2]
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
        text_fields, audios, pictures = self.getfieldsdataall()
        text_fields.update(self.parseaudiopictures(audios, pictures))
        html = self.parse_template(html, text_fields)
        html = '<style>{}</style><div class="card">{}</div>'.format(model_css, html)
        self.htmlbrowser.setHtml(html)

    def creattemplatetab(self, baselay: QVBoxLayout):

        spliter = QSplitter()
        baselay.addWidget(spliter)
        edittemptab = LTabWidget()
        self.previewtab = LTabBar()
        revertbtn = LPushButton("恢复")
        revertbtn.clicked.connect(self.loadedits)
        savebtn = LPushButton("保存")
        savebtn.clicked.connect(self.saveedits)

        spliter.addWidget(
            getboxwidget(
                [
                    edittemptab,
                    getboxlayout([revertbtn, savebtn]),
                ],
                lc=QVBoxLayout,
            )
        )

        self.htmlbrowser = auto_select_webview(self, True)
        self.htmlbrowser.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        spliter.addWidget(
            getboxwidget([self.previewtab, self.htmlbrowser], lc=QVBoxLayout)
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
            htmlcontents += (
                '<div id="luna_dict_tab_{}" class="tab-pane">{}</div>'.format(
                    dictionarys[iiii]["dict"], dictionarys[iiii]["content"]
                )
            )
        return htmlcontents

    def loadfileds(self):
        word = self.currentword
        dictionarys = self.refsearchw.generate_dictionarys()
        remarks = self.remarks.toPlainText()
        example = self.example.toPlainText()
        if globalconfig["ankiconnect"]["boldword"]:
            if self.example_hiras is None:
                _hs = gobject.baseobject.parsehira(example)
                self.example_hiras = mecab.parseastarget(_hs)
            collect = []
            for hira in self.example_hiras:
                if hira.word == word or hira.prototype == word:
                    collect.append("<b>{}</b>".format(hira.word))
                else:
                    collect.append(hira.word)
            example = "".join(collect)
        ruby = self.zhuyinedit.toPlainText()
        dictionaryInfo = []
        dictionaryContent = {}
        for _ in dictionarys:
            dictionaryInfo.append(
                {"dict": _["dict"], "name": dynamiccishuname(_["dict"])}
            )

            dictionaryContent[_["dict"]] = quote(
                _["content"] + self.refsearchw.loadmdictfoldstate(_["dict"])
            )
        fields = {
            "word": word,
            "rubytextHtml": ruby,
            "dictionaryContent": json.dumps(dictionaryContent),
            "dictionaryInfo": json.dumps(dictionaryInfo, ensure_ascii=False),
            "example_sentence": example.replace("\n", "<br>"),
            "remarks": remarks.replace("\n", "<br>"),
        }
        return fields

    def parseaudiopictures(self, audios: list, pictures: list):
        fields = {}
        for i, targets in enumerate([audios, pictures]):
            for target in targets:
                b64 = target.get("data")
                if not b64:
                    continue
                uid = str(uuid.uuid4())
                if i == 0:
                    html = """<button onclick='document.getElementById("{uid}").play()'>play audio<audio controls id="{uid}" style="display: none"><source src="data:audio/mpeg;base64,{b64}"></audio></button>""".format(
                        b64=b64, uid=uid
                    )
                else:
                    html = '<img src="data:image/png;base64,{}">'.format(b64)
                for field in target["fields"]:
                    fields[field] = html
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

    def creatsetdtab(self, baselay: QVBoxLayout):
        wid = QWidget()
        layout = VisLFormLayout(wid)
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
            "自定义Anki生成脚本",
            getboxlayout(
                [
                    getsimpleswitch(globalconfig, "usecustomankigen"),
                    getIconButton(
                        callback=functools.partial(
                            selectdebugfile, "userconfig/myanki_v2.py"
                        ),
                        icon="fa.edit",
                    ),
                    "",
                ]
            ),
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
        layout.addRow("不添加辞书", getIconButton(self.vistranslate_rank))
        layout.addRow(
            "成功添加后关闭窗口",
            getsimpleswitch(globalconfig["ankiconnect"], "addsuccautoclose"),
        )
        layout.addRow(
            "成功添加后隐藏Anki页面",
            getsimpleswitch(globalconfig["ankiconnect"], "addsuccautocloseEx"),
        )
        cnt = layout.rowCount() + 1

        def __(xx):
            i = ["mp3", "opus"].index(xx)
            layout.setRowVisible(cnt + 0, False)
            layout.setRowVisible(cnt + 1, False)
            layout.setRowVisible(cnt + i, True)

        layout.addRow(
            "音频编码",
            getsimplecombobox(
                ["mp3", "opus(ogg)"],
                globalconfig,
                "audioformat",
                internal=["mp3", "opus"],
                callback=__,
            ),
        )

        layout.addRow(
            "MP3 bitrate",
            getsimplecombobox(
                [str(8 * i) for i in range(1, 320 // 8 + 1)],
                globalconfig,
                "mp3kbps",
                internal=[8 * i for i in range(1, 320 // 8 + 1)],
            ),
        )
        layout.addRow(
            "OPUS bitrate",
            getspinbox(6, 256, globalconfig, "opusbitrate"),
        )
        __(globalconfig["audioformat"])

    def vistranslate_rank(self):
        listediter(
            self,
            "不添加辞书",
            globalconfig["ignoredict"],
            candidates=list(globalconfig["cishu"].keys()),
            namemapfunction=lambda k: dynamiccishuname(k),
            exec=True,
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

    def startorendrecord(self, btn: QPushButton, ii, target: QLineEdit, idx):
        if idx:
            try:
                self.recorders[ii] = loopbackrecorder()
            except Exception as e:
                self.recorders[ii] = None
                QMessageBox.critical(self, _TR("错误"), str(e))
                btn.click()
                return
            self.simulate_key(ii)
        else:
            if not self.recorders[ii]:
                return
            file = self.recorders[ii].stop_save()
            self.recorders[ii] = None
            self.settextsignal.emit(target, file)

    def createaddtab(self):
        self.recorders = {}
        wid = QWidget()
        layout = QVBoxLayout(wid)
        soundbutton = IconButton("fa.music")
        soundbutton.clicked.connect(self.langdu)

        soundbutton2 = IconButton("fa.music")
        soundbutton2.clicked.connect(self.langdu2)
        cropbutton = getIconButton(
            icon="fa.crop",
            callback=functools.partial(self.crophide, False),
            callback2=functools.partial(self.crophide, True),
        )
        grabwindowbtn = getIconButton(
            icon="fa.camera",
            callback=lambda: grabwindow(
                getimageformat(),
                functools.partial(self.settextsignal.emit, self.editpath),
            ),
            callback2=lambda: grabwindow(
                getimageformat(),
                functools.partial(self.settextsignal.emit, self.editpath),
                usewgc=True,
            ),
        )

        def createtbn(target: QLineEdit):
            clearbtn = IconButton("fa.times")
            clearbtn.clicked.connect(lambda: target.clear())
            return clearbtn

        class ctrlbedit(FQPlainTextEdit):
            def keyPressEvent(self, e):
                if (
                    e.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and e.key() == Qt.Key.Key_B
                ):
                    cursor = self.textCursor()
                    if cursor.hasSelection():
                        selected_text = cursor.selectedText()
                        new_text = "<b>{}</b>".format(selected_text)

                        start = cursor.selectionStart()

                        cursor.beginEditBlock()
                        cursor.insertText(new_text)
                        cursor.endEditBlock()
                        cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
                        cursor.setPosition(
                            start + len(new_text), QTextCursor.MoveMode.KeepAnchor
                        )
                        self.setTextCursor(cursor)
                return super().keyPressEvent(e)

        self.audiopath = QLineEdit()
        self.audiopath.setReadOnly(True)
        self.audiopath_sentence = QLineEdit()
        self.audiopath_sentence.setReadOnly(True)
        self.editpath = QLineEdit()
        self.editpath.setReadOnly(True)
        self.viewimagelabel = pixmapviewer()
        self.editpath.textChanged.connect(self.wrappedpixmap)
        self.example = ctrlbedit()
        self.zhuyinedit = ctrlbedit()
        self.wordedit = FQLineEdit()
        self.wordedit.textChanged.connect(self.wordedit_t)
        self.example_hiras: "list[WordSegResult]" = None

        def __():
            self.example_hiras = None

        self.example.textChanged.connect(__)
        self.remarks = ctrlbedit()
        recordbtn1 = IconButton(icon=["fa.microphone", "fa.stop"], checkable=True)
        recordbtn1.clicked.connect(
            functools.partial(self.startorendrecord, recordbtn1, 1, self.audiopath)
        )
        recordbtn2 = IconButton(icon=["fa.microphone", "fa.stop"], checkable=True)
        recordbtn2.clicked.connect(
            functools.partial(
                self.startorendrecord, recordbtn2, 2, self.audiopath_sentence
            )
        )
        self.recordbtn1 = recordbtn1
        self.recordbtn2 = recordbtn2

        combox = getsimplecombobox(
            globalconfig["ankiconnect"]["DeckNameS"],
            globalconfig["ankiconnect"],
            "DeckName_i",
        )

        def refreshcombo(combo: QComboBox, changed):
            if not changed:
                return
            combo.clear()
            if len(globalconfig["ankiconnect"]["DeckNameS"]) == 0:
                globalconfig["ankiconnect"]["DeckNameS"].append("lunadeck")
            combo.addItems(globalconfig["ankiconnect"]["DeckNameS"])

        lb = QLabel("Deck")
        lb.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        folder_open = IconButton("fa.folder-open")
        folder_open.clicked.connect(functools.partial(self.selecfile, self.audiopath))
        folder_open2 = IconButton("fa.folder-open")
        folder_open2.clicked.connect(
            functools.partial(self.selecfile, self.audiopath_sentence)
        )
        folder_open3 = IconButton("fa.folder-open")
        folder_open3.clicked.connect(functools.partial(self.selecfile2, self.editpath))

        def createadd():
            btn = LPushButton("添加")
            btn.clicked.connect(functools.partial(self.errorwrap, False))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                functools.partial(self.errorwrap, True)
            )
            return btn

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
                                                    globalconfig["ankiconnect"][
                                                        "DeckNameS"
                                                    ],
                                                    closecallback=functools.partial(
                                                        refreshcombo, combox
                                                    ),
                                                )
                                            ),
                                            combox,
                                        ]
                                    ),
                                ]
                            ),
                            getboxlayout([LLabel("单词"), self.wordedit], QHBoxLayout),
                            getboxlayout(
                                [LLabel("注音"), self.zhuyinedit], QVBoxLayout
                            ),
                            getboxlayout([LLabel("例句"), self.example], QVBoxLayout),
                            getboxlayout([LLabel("备注"), self.remarks], QVBoxLayout),
                            getboxlayout(
                                [
                                    LLabel("标签"),
                                    listediterline(
                                        "标签", globalconfig["ankiconnect"]["tags"]
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
                                    functools.partial(createtbn, self.audiopath),
                                ]
                            ),
                            getboxlayout(
                                [
                                    LLabel("语音_例句"),
                                    self.audiopath_sentence,
                                    recordbtn2,
                                    soundbutton2,
                                    folder_open2,
                                    functools.partial(
                                        createtbn, self.audiopath_sentence
                                    ),
                                ]
                            ),
                            getboxlayout(
                                [
                                    LLabel("截图"),
                                    self.editpath,
                                    cropbutton,
                                    grabwindowbtn,
                                    folder_open3,
                                    functools.partial(createtbn, self.editpath),
                                ]
                            ),
                            self.viewimagelabel,
                            createadd,
                        ],
                        QVBoxLayout,
                    ),
                ]
            )
        )

        self.__ocrsettext.connect(self.example.appendPlainText)

        self.reset("")
        return wid

    def wrappedpixmap(self, src):
        if os.path.exists(src) == False:
            pix = QPixmap()
        else:
            pix = QPixmap.fromImage(QImage(src))
        self.viewimagelabel.showpixmap(pix)

    def selecfile2(self, item):
        f = QFileDialog.getOpenFileName(filter=getimagefilefilter() + ";;*")
        res = f[0]
        if res != "":
            item.setText(res)

    def selecfile(self, item: QLineEdit):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        if res != "":
            item.setText(res)

    def wordedit_t(self, text):
        self.currentword = text
        if text and len(text):
            _hs = gobject.baseobject.parsehira(text)
            self.zhuyinedit.setPlainText(mecab.makerubyhtml(_hs))
        else:
            self.zhuyinedit.clear()

    def maybereset(self, text):
        self.wordedit.setText(text)
        if gobject.baseobject.currenttext != self.example.toPlainText():
            self.editpath.clear()
            self.audiopath.clear()
            self.audiopath_sentence.clear()

    def reset(self, text):
        self.wordedit.setText(text)
        self.editpath.clear()
        self.audiopath.clear()
        self.audiopath_sentence.clear()

    def errorwrap(self, close=False):
        try:
            anki.global_port = globalconfig["ankiconnect"]["port"]
            anki.global_host = globalconfig["ankiconnect"]["host"]
            if self.currentword == self.lastankiword:
                response = QMessageBox.question(
                    self, "?", _TR("检测到存在重复，是否覆盖？")
                )
                if response == QMessageBox.StandardButton.Yes:
                    anki.Note.delete([self.lastankid])
            self.addanki()
            if globalconfig["ankiconnect"]["addsuccautocloseEx"] and self.isVisible():
                self.refsearchw.ankiconnect.click()
            if close or globalconfig["ankiconnect"]["addsuccautoclose"]:
                self.window().close()
            QToolTip.showText(QCursor.pos(), _TR("添加成功"), self)
        except requests.RequestException:
            QMessageBox.critical(self, _TR("错误"), _TR("无法连接到anki"))
        except anki.AnkiException as e:
            QMessageBox.critical(self, _TR("错误"), str(e))
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
            with open("files/html/anki/back.html", "r", encoding="utf8") as ff:
                model_htmlback = ff.read()
            with open("files/html/anki/front.html", "r", encoding="utf8") as ff:
                model_htmlfront = ff.read()
            with open("files/html/anki/style.css", "r", encoding="utf8") as ff:
                model_css = ff.read()
        return model_htmlfront, model_htmlback, model_css

    def addanki(self):

        autoUpdateModel = globalconfig["ankiconnect"]["autoUpdateModel"]
        allowDuplicate = globalconfig["ankiconnect"]["allowDuplicate"]
        anki.global_port = globalconfig["ankiconnect"]["port"]
        anki.global_host = globalconfig["ankiconnect"]["host"]
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
        fields = static_data["model_fileds"]
        if globalconfig["usecustomankigen"]:
            module = checkmd5reloadmodule("userconfig/myanki_v2.py", "myanki_v2")[1]
            if module:
                try:
                    fields = module.AnkiFields(fields)
                except:
                    print_exc()
        try:
            model = anki.Model.create(
                ModelName,
                fields,
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
        text_fields, audios, pictures = self.getfieldsdataall()
        self.lastankid = anki.Note.add(
            DeckName, ModelName, text_fields, allowDuplicate, tags, audios, pictures
        )
        self.lastankiword = self.currentword

    def getfieldsdataall(self):
        text_fields = self.loadfileds()
        audios, pictures = self.loadankilikemediafield()
        return self.custompass(text_fields, audios, pictures)

    def loadankilikemediafield(self):
        media = []
        for k, _ in [
            ("audio_for_word", self.audiopath.text()),
            ("audio_for_example_sentence", self.audiopath_sentence.text()),
            ("screenshot", self.editpath.text()),
        ]:
            if len(_):
                with open(_, "rb") as ff:
                    b64 = base64.b64encode(ff.read()).decode()
                media.append(
                    [
                        {
                            "data": b64,
                            "filename": str(uuid.uuid4()) + os.path.splitext(_)[1],
                            "fields": [k],
                        }
                    ]
                )
            else:
                media.append([])
        audios = media[0] + media[1]
        pictures = media[2]
        return audios, pictures

    def custompass(self, text_fields: dict, audios: list, pictures: list):
        if globalconfig["usecustomankigen"]:
            module = checkmd5reloadmodule("userconfig/myanki_v2.py", "myanki_v2")[1]
            if module:
                try:
                    text_fields, audios, pictures = module.ParseFieldsData(
                        text_fields, audios, pictures
                    )
                except:
                    print_exc()
        return text_fields, audios, pictures


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
OriginText = isLabeleddWord + 1


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
        rows = []
        for c in childs:
            if isinstance(c, str):
                t = c
                has = False
            else:
                t = c.text()
                has = True
            item = QStandardItem(t.replace("\n", ""))
            if has:
                item.setData(c, DictNodeRole)
            else:
                item.setData(True, isWordNode)
            if (thisitem.text(), t) in maketuples:
                item.setData(True, isLabeleddWord)
                item.setData(
                    QBrush(Qt.GlobalColor.cyan), Qt.ItemDataRole.BackgroundRole
                )
            rows.append(item)
        thisitem.appendRows(rows)
        self.ref(index, True)

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


class showdiction(QWidget):
    def setwordfilter(self, index: QModelIndex = None, first=False):
        if index is None:
            item = self.model.invisibleRootItem()
            index = self.model.indexFromItem(self.model.invisibleRootItem())
        else:
            item = self.model.itemFromIndex(index)
        w = self.word.text()

        if first:
            item.setData(item.text(), OriginText)
            if not w:
                item.setText(item.text() + " ({})".format((item.rowCount())))
                return
        cnt = 0
        for i in range(item.rowCount()):
            _item = item.child(i)
            isw = _item.data(isWordNode)
            if isw is None:
                isw = False
            hide = isw and (w not in _item.text())
            self.tree.setRowHidden(i, index, hide)
            cnt += 1 - hide
            self.setwordfilter(self.model.indexFromItem(_item))
        if item.data(OriginText):
            item.setText(item.data(OriginText) + " ({})".format(cnt))

    def showmenu(self, _):
        idx = self.tree.currentIndex()
        if not idx.isValid():
            return
        isw = idx.data(isWordNode)
        item = self.model.itemFromIndex(idx)
        menu = QMenu(self)
        copy = LAction("复制", menu)
        search = LAction("查词", menu)
        label = LAction("标记", menu)
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
            NativeUtils.ClipBoard.text = item.text()
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
        self.word = FQLineEdit()
        self.word.returnPressed.connect(self.setwordfilter)
        wordfilter.addWidget(self.word)
        butn = getIconButton(self.setwordfilter, "fa.search")
        wordfilter.addWidget(butn)
        refresh = getIconButton(self.refresh, "fa.refresh")
        wordfilter.addWidget(refresh)
        self.tree = kpQTreeView(self)
        self.tree.setUniformRowHeights(True)
        self.tree.setHeaderHidden(True)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        __lay = QVBoxLayout(self)
        __lay.setSpacing(0)
        __lay.setContentsMargins(0, 0, 0, 0)
        __lay.addLayout(wordfilter)
        __lay.addWidget(self.tree)

        self.model = DynamicTreeModel(self.setwordfilter)
        self.tree.setModel(self.model)
        self.tree.expanded.connect(self.model.loadChildren)
        self.tree.doubleClicked.connect(self.model.onDoubleClicked)
        self.tree.enterpressed.connect(self.model.onDoubleClicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.showmenu)
        self.refresh()

    def refresh(self):
        self.model.clear()
        root = self.model.invisibleRootItem()
        rows = []
        cishus = []
        for k in globalconfig["cishuvisrank"]:
            cishu = gobject.baseobject.cishus.get(k)
            if not hasattr(cishu, "tree"):
                continue
            cishus.append(cishu)
        if len(cishus) == 1:
            try:
                for node in cishus[0].tree().childrens():
                    item = QStandardItem(node.text().replace("\n", ""))
                    item.setData(node, DictNodeRole)
                    rows.append(item)
            except:
                print_exc()
        else:
            for cishu in cishus:
                try:
                    tree = cishu.tree()
                except:
                    continue
                if not tree:
                    continue

                item = QStandardItem(dynamiccishuname(k))
                item.setData(tree, DictNodeRole)
                rows.append(item)
        root.appendRows(rows)
        root.setData(len(rows) > 0, DeterminedhasChildren)


class showwordfastwebview(auto_select_webview):
    def _createwebview(self, *argc, **kw):
        web = super()._createwebview(*argc, **kw)
        if isinstance(web, WebviewWidget):
            web.html_limit = 1
        return web


class searchwordW(closeashidewindow):
    search_word = pyqtSignal(str, bool)
    show_dict_result = pyqtSignal(float, str, str)
    search_word_in_new_window = pyqtSignal(str)
    ocr_once_signal = pyqtSignal()

    def __init__(self, parent):
        super(searchwordW, self).__init__(parent, globalconfig["sw_geo"])
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.search_word.connect(self.__click_word_search_function)
        self.search_word_in_new_window.connect(self.searchwinnewwindow)
        self.show_dict_result.connect(self.__show_dict_result_function)
        self.ocr_once_signal.connect(lambda: rangeselct_function(self.ocr_do_function))
        self.state = 0

    @threader
    def ocr_do_function(self, rect, img=None):
        if not rect:
            return
        if not img:
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
        result = ocr_run(img)
        if result.error:
            return result.displayerror()
        self.search_word.emit(result.textonly, False)

    def __load(self):
        if self.state != 0:
            return
        self.state = 1
        self.setupUi()
        self.state = 2

    def showEvent(self, e):
        super().showEvent(e)
        self.__load()
        self.activate()

    def activate(self):
        self.activateWindow()
        self.searchtext.setFocus()

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
        self.tab.insertTab(idx, (dynamiccishuname(k)))
        if not self.hasclicked:
            if thisp == max(self.thisps.values()):
                self.tab.setCurrentIndex(0)
                self.tab.tabBarClicked.emit(0)
                self.hasclicked = True

    def tabclicked(self, idx):
        self.tab.setCurrentIndex(idx)
        self.hasclicked = True
        try:
            k = self.tabks[idx]
            html = self.cache_results_highlighted.get(k, self.cache_results[k])
        except:
            return
        path = r"files\html\uiwebview\dictionary.html"
        with open(path, "r", encoding="utf8") as ff:
            frame = ff.read()
        html = frame.replace("__luna_dict_internal_view__", html)
        html += self.loadmdictfoldstate(k)
        self.textOutput.setHtml(html)

    def loadmdictfoldstate(self, k):
        if k != "mdict":
            return ""
        if not self.savemdictfoldstate:
            return ""
        datas = []
        for _id, fold in self.savemdictfoldstate.items():
            datas.append(
                "document.getElementById('{}').nextElementSibling.style.display='{}';".format(
                    _id, ("block", "none")[fold]
                )
            )
        if not datas:
            return ""
        return """<script>{}</script>""".format("".join(datas))

    def searchwinnewwindow(self, word):

        class searchwordWx(searchwordW):
            def closeEvent(self1, event: QCloseEvent):
                self1.deleteLater()
                super(saveposwindow, self1).closeEvent(event)

        _ = searchwordWx(self.parent())
        _.move(_.pos() + QPoint(20, 20))
        _.show()
        _.search_word.emit(word, False)

    def _createnewwindowsearch(self, _):
        word = self.searchtext.text()
        self.searchwinnewwindow(word)

    def showmenu_auto_sound(self, _):

        menu = QMenu(self)
        auto = LAction("自动", menu)
        auto.setCheckable(True)
        auto.setChecked(globalconfig["is_search_word_auto_tts"])
        menu.addAction(auto)
        action = menu.exec(QCursor.pos())
        if action == auto:
            globalconfig["is_search_word_auto_tts"] = auto.isChecked()

    def historymenu(self):
        menu = QMenu(self)
        __ = []
        for word in self.historys[:16]:
            act = QAction(word, menu)
            __.append(act)
            menu.addAction(act)
        action = menu.exec(QCursor.pos())
        if action:
            self.searchtext.setText(action.text())
            self.search(action.text())

    def setupUi(self):
        self.setWindowTitle("查词")
        self.ankiwindow = AnkiWindow(self)
        self.setWindowIcon(qtawesome.icon("fa.search"))
        self.thisps = {}
        self.hasclicked = False
        ww = QWidget(self)
        self.vboxlayout = QVBoxLayout(ww)
        self.searchlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchlayout)
        self.searchtext = FQLineEdit()
        self.searchtext.textChanged.connect(self.ankiwindow.maybereset)

        self.dictbutton = IconButton(icon="fa.book", checkable=True)
        self.historys = []
        self.history_btn = IconButton(icon="fa.history")
        self.history_btn.setEnabled(False)
        self.history_btn.clicked.connect(self.historymenu)

        self.searchlayout.addWidget(self.dictbutton)
        self.searchlayout.addWidget(self.history_btn)
        self.searchlayout.addWidget(self.searchtext)
        searchbutton = getIconButton(
            icon="fa.search",
            callback=lambda: self.search(self.searchtext.text()),
            callback2=self._createnewwindowsearch,
        )
        self.searchtext.returnPressed.connect(searchbutton.clicked.emit)

        self.searchlayout.addWidget(searchbutton)

        self.soundbutton = getIconButton(
            icon="fa.music",
            callback=lambda: gobject.baseobject.read_text(self.searchtext.text()),
            callback2=self.showmenu_auto_sound,
        )
        self.searchlayout.addWidget(self.soundbutton)

        ankiconnect = IconButton(icon="fa.adn", checkable=True)
        ankiconnect.clicked.connect(self.onceaddankiwindow)
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
        self.textOutput = showwordfastwebview(self, True)
        nexti = self.textOutput.add_menu(
            0, lambda: _TR("查词"), lambda w: self.search_word.emit(w, False)
        )
        nexti = self.textOutput.add_menu(
            nexti,
            lambda: _TR("在新窗口中查词"),
            threader(self.search_word_in_new_window.emit),
        )
        nexti = self.textOutput.add_menu(
            nexti, lambda: _TR("翻译"), gobject.baseobject.textgetmethod
        )
        nexti = self.textOutput.add_menu(
            nexti, lambda: _TR("朗读"), gobject.baseobject.read_text
        )
        nexti = self.textOutput.add_menu(
            nexti,
            lambda: _TR("加亮"),
            lambda _: self.textOutput.eval("highlightSelection()"),
        )
        self.ishightlight = False
        nexti = self.textOutput.add_menu_noselect(
            0,
            lambda: _TR("加亮模式"),
            lambda: self.textOutput.eval("switch_hightlightmode()"),
            checkable=True,
            getchecked=lambda: self.callvalue(),
        )
        nexti = self.textOutput.add_menu_noselect(
            nexti, lambda: _TR("清除加亮"), self.clear_hightlight
        )
        self.textOutput.set_zoom(globalconfig.get("ZoomFactor", 1))
        self.textOutput.on_ZoomFactorChanged.connect(
            functools.partial(globalconfig.__setitem__, "ZoomFactor")
        )
        self.savemdictfoldstate = {}
        self.textOutput.bind(
            "switch_hightlightmode_callback", self.switch_hightlightmode_callback
        )
        self.textOutput.bind("mdict_fold_callback", self.mdict_fold_callback)
        self.textOutput.bind(
            "luna_recheck_current_html", self.luna_recheck_current_html
        )
        self.textOutput.bind(
            "luna_search_word", lambda word: self.search_word.emit(word, False)
        )
        self.textOutput.bind(
            "luna_audio_play_b64",
            lambda b64: gobject.baseobject.audioplayer.play(
                base64.b64decode(b64.encode()), force=True
            ),
        )
        self.cache_results = {}
        self.cache_results_highlighted = {}

        self.spliter = QSplitter()
        w = QWidget()
        tablayout = QVBoxLayout(w)
        tablayout.setContentsMargins(0, 0, 0, 0)
        tablayout.setSpacing(0)
        tablayout.addWidget(self.tab)
        tablayout.addWidget(self.textOutput)
        self.vboxlayout.addWidget(self.spliter)
        self.isfirstshowdictwidget = True
        self.spliter.setOrientation(
            Qt.Orientation.Vertical
            if globalconfig["anki_Orientation_V"]
            else Qt.Orientation.Horizontal
        )

        self.dict_textoutput_spl = QSplitter()
        self.dict_textoutput_spl.addWidget(w)
        self.spliter.addWidget(self.dict_textoutput_spl)
        self.dictbutton.clicked.connect(self.onceaddshowdictwidget)
        self.spliter.addWidget(self.ankiwindow)
        self.ankiwindow.setVisible(False)

        def __(_):
            globalconfig["ankisplit"] = self.spliter.sizes()

        self.spliter.setSizes(globalconfig["ankisplit"])
        self.spliter.splitterMoved.connect(__)
        self.spliter.setStretchFactor(0, 1)
        self.spliter.setStretchFactor(1, 0)
        self.ankiwindow.setMinimumHeight(1)
        self.ankiwindow.setMinimumWidth(1)

    def mdict_fold_callback(self, i, display):
        self.savemdictfoldstate[i] = display == "none"

    def callvalue(self):
        if isinstance(self.textOutput.internal, WebviewWidget):
            self.textOutput.eval("iswebview2=true")
            return self.ishightlight
        # mshtml会死锁。
        self.ishightlight = not self.ishightlight
        return self.ishightlight

    def switch_hightlightmode_callback(self, ishightlight):
        self.ishightlight = ishightlight

    def clear_hightlight(self):
        self.textOutput.eval("clear_hightlight()")
        k = self.tabks[self.tab.currentIndex()]
        if k in self.cache_results_highlighted:
            self.cache_results_highlighted.pop(k)

    def luna_recheck_current_html(self, html):
        self.cache_results_highlighted[self.tabks[self.tab.currentIndex()]] = html

    def onceaddshowdictwidget(self, idx):
        if idx:
            if self.isfirstshowdictwidget:
                self.showdictwidget = showdiction(self)
                self.dict_textoutput_spl.insertWidget(0, self.showdictwidget)
                self.dict_textoutput_spl.setStretchFactor(0, 0)
                self.dict_textoutput_spl.setStretchFactor(1, 1)

                def __(_):
                    globalconfig["mdictsplit"] = self.dict_textoutput_spl.sizes()

                self.dict_textoutput_spl.setSizes(globalconfig["mdictsplit"])
                self.dict_textoutput_spl.splitterMoved.connect(__)
            else:
                self.showdictwidget.show()
        else:
            self.showdictwidget.hide()
        self.isfirstshowdictwidget = False

    def onceaddankiwindow(self, idx):
        if idx:
            self.ankiwindow.show()
        else:
            self.ankiwindow.hide()

    def generate_dictionarys(self):
        res = []
        tabks = []
        for k in self.cache_results:
            if k in globalconfig["ignoredict"]:
                continue
            v = self.cache_results_highlighted.get(k, self.cache_results[k])
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

    def __click_word_search_function(self, word: str, append):
        self.showNormal()
        if self.state != 2:
            return
        word = word.strip()
        if append:
            word = self.searchtext.text() + word
        self.searchtext.setText(word)
        self.activate()
        self.search(word, append)
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

    def __parsehistory(self, word, append):
        if append and self.historys:
            self.historys.pop(0)
        if word in self.historys:
            self.historys.remove(word)
        self.historys.insert(0, word)
        self.history_btn.setEnabled(True)

    def search(self, word: str, append=False):
        current = time.time()
        self.current = current
        word = word.strip()
        if not word:
            return
        self.__parsehistory(word, append)
        if globalconfig["is_search_word_auto_tts"]:
            gobject.baseobject.read_text(self.searchtext.text())
        self.ankiwindow.maybereset(word)
        for i in range(self.tab.count()):
            self.tab.removeTab(0)
        self.tabks.clear()
        self.textOutput.clear()
        self.cache_results.clear()
        self.cache_results_highlighted.clear()
        self.savemdictfoldstate.clear()
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
