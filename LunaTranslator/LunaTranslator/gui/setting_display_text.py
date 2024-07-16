from qtsymbols import *
import functools, platform
import gobject, os, zipfile, shutil
from myutils.config import globalconfig, _TRL, _TR, static_data
from gui.inputdialog import multicolorset, autoinitdialog
from myutils.wrapper import tryprint
from myutils.utils import dynamiclink
from gui.usefulwidget import (
    D_getsimplecombobox,
    getsimplecombobox,
    Singleton_close,
    saveposwindow,
    getQMessageBox,
    D_getspinbox,
    D_getIconButton,
    D_getcolorbutton,
    getcolorbutton,
    MySwitch,
    D_getsimpleswitch,
    selectcolor,
    listediter,
    FocusFontCombo,
    FocusCombo,
    FocusDoubleSpin,
    FocusSpin,
)


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    try:
        self.fenyinsettings.setEnabled(x)
    except:
        pass


def createtextfontcom(key):
    font_comboBox = FocusFontCombo()
    font_comboBox.currentTextChanged.connect(lambda x: globalconfig.__setitem__(key, x))
    font_comboBox.setCurrentFont(QFont(globalconfig[key]))
    return font_comboBox


@Singleton_close
class extrahtml(saveposwindow):
    def tryload(self):

        use = "userconfig/extrahtml.html"
        if os.path.exists(use) == False:
            use = r"LunaTranslator\rendertext\exampleextrahtml.html"
        with open(use, "r", encoding="utf8") as ff:
            self.vistext.setPlainText(ff.read())

    @tryprint
    def applyhtml(self, _):
        gobject.baseobject.translation_ui.translate_text.textbrowser.set_extra_html(
            self.vistext.toPlainText()
        )

    def savehtml(self):
        with open(
            gobject.getuserconfigdir("extrahtml.html"), "w", encoding="utf8"
        ) as ff:
            ff.write(self.vistext.toPlainText())

    def __init__(self, parent) -> None:
        super().__init__(parent, poslist=globalconfig["geo_extrahtml"])
        self.setWindowTitle(_TR("额外的html"))

        self.btn_save = QPushButton(_TR("保存"))
        self.btn_save.clicked.connect(self.savehtml)
        self.btn_apply = QPushButton(_TR("测试"))
        self.btn_apply.clicked.connect(self.applyhtml)
        self.vistext = QPlainTextEdit()
        lay = QVBoxLayout()
        hl = QHBoxLayout()
        hl.addWidget(self.btn_save)
        hl.addWidget(self.btn_apply)
        lay.addWidget(self.vistext)
        lay.addLayout(hl)
        w = QWidget()
        w.setLayout(lay)
        self.setCentralWidget(w)
        self.tryload()
        self.show()


def clearlayout(ll: QLayout):
    while ll.count():
        item = ll.takeAt(0)
        if not item:
            continue
        ll.removeItem(item)
        w = item.widget()
        if w:
            w.deleteLater()
            continue
        l = item.layout()
        if l:
            clearlayout(l)
            l.deleteLater()
            continue


def createinternalfontsettings(self, forml, group, _type):

    globalconfig["rendertext_using_internal"][group] = _type
    __internal = globalconfig["rendertext"][group][_type]
    dd = __internal.get("args", {})

    clearlayout(forml)

    for key in dd:
        line = __internal["argstype"][key]
        name = line["name"]
        _type = line["type"]
        if _type == "colorselect":
            lineW = getcolorbutton(
                dd,
                key,
                transparent=False,
                callback=functools.partial(
                    lambda dd, key, _: selectcolor(
                        self, dd, key, self.miaobian_color_button
                    ),
                    dd,
                    key,
                ),
                name="miaobian_color_button",
                parent=self,
            )
        elif _type == "spin":
            lineW = FocusDoubleSpin()
            lineW.setMinimum(line.get("min", 0))
            lineW.setMaximum(line.get("max", 100))
            lineW.setSingleStep(line.get("step", 0.1))
            lineW.setValue(dd[key])
            lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))

        elif _type == "intspin":
            lineW = FocusSpin()
            lineW.setMinimum(line.get("min", 0))
            lineW.setMaximum(line.get("max", 100))
            lineW.setSingleStep(line.get("step", 1))
            lineW.setValue(dd[key])
            lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))
        elif _type == "switch":
            lineW = MySwitch(sign=dd[key])
            lineW.clicked.connect(functools.partial(dd.__setitem__, key))
        forml.addRow(
            _TR(name),
            lineW,
        )


def copytree(src, dst, copy_function=shutil.copy2):
    names = os.listdir(src)

    os.makedirs(dst, exist_ok=True)
    for name in names:

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, copy_function)
            else:
                copy_function(srcname, dstname)
        except:
            pass


def doinstallqweb(self, dd, base):
    if not dd["k"].endswith(base):
        getQMessageBox(self, "错误", f"请选择_{base}")
        return
    with zipfile.ZipFile(dd["k"]) as zipf:
        target = gobject.gettempdir("QWebEngine/")
        zipf.extractall(target)
        bit = ["x86", "x64"][platform.architecture()[0] == "64bit"]
        copytree(f"{target}/{bit}/PyQt5", "LunaTranslator/runtime/PyQt5")

    gobject.baseobject.showtraymessage("", "安装成功")


def installqwebdialog(self, link):
    dd = {"k": ""}
    base = link.split("/")[-1]
    autoinitdialog(
        self,
        "安装_QWebEngine",
        800,
        [
            {
                "type": "file",
                "name": "路径",
                "d": dd,
                "k": "k",
                "dir": False,
                "filter": base,
            },
            {
                "type": "okcancel",
                "callback": functools.partial(doinstallqweb, self, dd, base),
            },
        ],
    )


def on_not_find_qweb(self):
    def _okcallback():

        link = [
            dynamiclink("{main_server}/Resource/QWebEngine_x86.zip"),
            dynamiclink("{main_server}/Resource/QWebEngine_x64.zip"),
        ][platform.architecture()[0] == "64bit"]
        os.startfile(link)
        installqwebdialog(self, link)

    getQMessageBox(
        self,
        _TR("错误"),
        "未找到QWebEngine，点击确定前往下载QWebEngine",
        True,
        True,
        okcallback=_okcallback,
    )


def resetgroudswitchcallback(self, _2, group):

    if group == "QWebEngine" and not gobject.testuseqwebengine():
        self.seletengeinecombo.blockSignals(True)
        visengine_internal = ["textbrowser", "webview", "QWebEngine"]
        globalconfig["rendertext_using"] = visengine_internal[
            self.seletengeinecombo.lastindex
        ]
        self.seletengeinecombo.setCurrentIndex(self.seletengeinecombo.lastindex)
        self.seletengeinecombo.blockSignals(False)
        on_not_find_qweb(self)
        return
    if _2:
        gobject.baseobject.showneedrestart("显示引擎", 0)
    clearlayout(self.goodfontsettingsformlayout)

    goodfontgroupswitch = FocusCombo()
    self.seletengeinecombo.lastindex = self.seletengeinecombo.currentIndex()
    if group == "webview" or group == "QWebEngine":
        _btn = QPushButton(_TR("额外的html"))
        self.goodfontsettingsformlayout.addRow(_btn)
        _btn.clicked.connect(lambda: extrahtml(self))
    if group == "QWebEngine":
        group = "webview"
    __form = QFormLayout()
    __form.addRow(_TR("字体样式"), goodfontgroupswitch)
    self.goodfontsettingsformlayout.addRow(__form)
    forml = QFormLayout()
    __form.addRow(forml)

    goodfontgroupswitch.addItems(
        _TRL(
            [
                globalconfig["rendertext"][group][x]["name"]
                for x in static_data["textrender"][group]
            ]
        )
    )
    goodfontgroupswitch.currentIndexChanged.connect(
        lambda idx: createinternalfontsettings(
            self, forml, group, static_data["textrender"][group][idx]
        )
    )
    goodfontgroupswitch.setCurrentIndex(
        static_data["textrender"][group].index(
            globalconfig["rendertext_using_internal"][group]
        )
    )


def creategoodfontwid(self):

    self.goodfontsettingsWidget = QGroupBox()
    self.goodfontsettingsWidget.setStyleSheet(
        "QGroupBox{ margin-top:0px;} QGroupBox:title {margin-top: 0px;}"
    )
    self.goodfontsettingsformlayout = QFormLayout()
    self.goodfontsettingsWidget.setLayout(self.goodfontsettingsformlayout)
    resetgroudswitchcallback(self, False, globalconfig["rendertext_using"])
    return self.goodfontsettingsWidget


def _createseletengeinecombo(self):

    visengine = ["Qt", "Webview2", "QWebEngine"]
    visengine_internal = ["textbrowser", "webview", "QWebEngine"]
    self.seletengeinecombo = getsimplecombobox(
        visengine,
        globalconfig,
        "rendertext_using",
        internallist=visengine_internal,
        callback=functools.partial(resetgroudswitchcallback, self, True),
    )
    self.seletengeinecombo.lastindex = self.seletengeinecombo.currentIndex()
    return self.seletengeinecombo


def __changeselectablestate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.translation_ui.translate_text.textbrowser.setselectable(x)


def vistranslate_rank(self):
    listediter(
        self,
        _TR("显示顺序"),
        _TR("显示顺序"),
        globalconfig["fix_translate_rank_rank"],
        isrankeditor=True,
        namemapfunction=lambda k: globalconfig["fanyi"][k]["name"],
    )


def xianshigrid_text(self):
    textgrid = [
        [
            (
                dict(
                    title="文本",
                    type="grid",
                    grid=(
                        [
                            "可选取的",
                            D_getsimpleswitch(
                                globalconfig,
                                "selectable",
                                callback=functools.partial(
                                    __changeselectablestate, self
                                ),
                                parent=self,
                                name="selectable_btn",
                            ),
                        ],
                        [
                            "显示原文",
                            D_getsimpleswitch(
                                globalconfig,
                                "isshowrawtext",
                                callback=lambda x: __changeuibuttonstate(self, x),
                                name="show_original_switch",
                                parent=self,
                            ),
                            "",
                            "最长显示字数",
                            D_getspinbox(0, 1000000, globalconfig, "maxoriginlength"),
                            "",
                        ],
                        [
                            "显示翻译",
                            D_getsimpleswitch(globalconfig, "showfanyi"),
                            "",
                            ("显示翻译器名称"),
                            D_getsimpleswitch(globalconfig, "showfanyisource"),
                            "",
                        ],
                        [
                            "收到翻译时才刷新",
                            D_getsimpleswitch(globalconfig, "refresh_on_get_trans"),
                            "",
                            "显示错误信息",
                            D_getsimpleswitch(globalconfig, "showtranexception"),
                            "",
                        ],
                        [
                            "固定翻译显示顺序",
                            D_getsimpleswitch(globalconfig, "fix_translate_rank"),
                            D_getIconButton(
                                functools.partial(vistranslate_rank, self), "fa.gear"
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="分词",
                    type="grid",
                    parent=self,
                    name="fenyinsettings",
                    enable=globalconfig["isshowrawtext"],
                    grid=(
                        [
                            (
                                dict(
                                    title="注音",
                                    type="grid",
                                    grid=(
                                        [
                                            ("显示"),
                                            D_getsimpleswitch(
                                                globalconfig,
                                                "isshowhira",
                                            ),
                                            "",
                                            ("颜色"),
                                            D_getcolorbutton(
                                                globalconfig,
                                                "jiamingcolor",
                                                callback=lambda: selectcolor(
                                                    self,
                                                    globalconfig,
                                                    "jiamingcolor",
                                                    self.jiamingcolor_b,
                                                ),
                                                name="jiamingcolor_b",
                                                parent=self,
                                            ),
                                            "",
                                        ],
                                        [
                                            "字体缩放",
                                            D_getspinbox(
                                                0.05,
                                                1,
                                                globalconfig,
                                                "kanarate",
                                                double=True,
                                                step=0.05,
                                                dec=2,
                                            ),
                                            "",
                                            "日语注音方案",
                                            D_getsimplecombobox(
                                                _TRL(
                                                    [
                                                        "平假名",
                                                        "片假名",
                                                        "罗马音",
                                                    ]
                                                ),
                                                globalconfig,
                                                "hira_vis_type",
                                            ),
                                        ],
                                    ),
                                ),
                                0,
                                "group",
                            )
                        ],
                        [
                            (
                                dict(
                                    type="grid",
                                    grid=(
                                        [
                                            ("语法加亮"),
                                            D_getsimpleswitch(
                                                globalconfig, "show_fenci"
                                            ),
                                            "",
                                            ("词性颜色"),
                                            D_getIconButton(
                                                callback=lambda: multicolorset(self),
                                                icon="fa.gear",
                                            ),
                                            "",
                                        ],
                                        [
                                            ("点击单词查词"),
                                            (
                                                D_getsimpleswitch(
                                                    globalconfig, "usesearchword"
                                                ),
                                                1,
                                            ),
                                            "",
                                            ("点击单词复制"),
                                            (
                                                D_getsimpleswitch(
                                                    globalconfig, "usecopyword"
                                                ),
                                                1,
                                            ),
                                        ],
                                        [
                                            ("使用原型查询"),
                                            (
                                                D_getsimpleswitch(
                                                    globalconfig, "usewordorigin"
                                                ),
                                                1,
                                            ),
                                        ],
                                    ),
                                ),
                                0,
                                "group",
                            )
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    return textgrid


def xianshigrid_style(self):
    textgrid = [
        [
            (
                dict(
                    title="字体",
                    type="grid",
                    grid=(
                        [
                            "原文字体",
                            (functools.partial(createtextfontcom, "fonttype"), 4),
                            "",
                            "字体大小",
                            D_getspinbox(
                                1,
                                100,
                                globalconfig,
                                "fontsizeori",
                                double=True,
                                step=0.1,
                            ),
                        ],
                        [
                            "译文字体",
                            (functools.partial(createtextfontcom, "fonttype2"), 4),
                            "",
                            "字体大小",
                            D_getspinbox(
                                1, 100, globalconfig, "fontsize", double=True, step=0.1
                            ),
                        ],
                        [
                            "加粗字体",
                            D_getsimpleswitch(globalconfig, "showbold"),
                            "",
                            "居中显示",
                            D_getsimpleswitch(globalconfig, "showatcenter"),
                            "",
                            "行间距",
                            D_getspinbox(-100, 100, globalconfig, "extra_space"),
                            "",
                        ],
                        [
                            "原文颜色",
                            D_getcolorbutton(
                                globalconfig,
                                "rawtextcolor",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "rawtextcolor",
                                    self.original_color_button,
                                ),
                                name="original_color_button",
                                parent=self,
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="样式",
                    grid=(
                        [
                            "显示引擎",
                            functools.partial(_createseletengeinecombo, self),
                        ],
                        [functools.partial(creategoodfontwid, self)],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    return textgrid
