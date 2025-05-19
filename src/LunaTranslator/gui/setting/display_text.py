from qtsymbols import *
import functools
import gobject, os
from myutils.config import globalconfig, static_data
from myutils.wrapper import tryprint
from myutils.utils import translate_exits, _TR, getannotatedapiname
from gui.usefulwidget import (
    getsimplecombobox,
    Singleton,
    saveposwindow,
    D_getspinbox,
    clearlayout,
    getboxlayout,
    getboxwidget,
    D_getcolorbutton,
    getcolorbutton,
    saveposwindow,
    listediter,
    getIconButton,
    getsimpleswitch,
    D_getsimpleswitch,
    FocusFontCombo,
    SuperCombo,
    NQGroupBox,
    D_getIconButton,
    getspinbox,
    getsmalllabel,
    SplitLine,
    PopupWidget,
    Exteditor,
)
from gui.dynalang import LPushButton, LFormLayout


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.translation_ui.translate_text.showhideorigin(x)
    try:
        self.fenyinsettings.setEnabled(x)
    except:
        pass


def changeshowerrorstate(self, x):
    gobject.baseobject.translation_ui.translate_text.showhideerror(x)


def mayberealtimesetfont(_=None):
    gobject.baseobject.translation_ui.translate_text.setfontstyle()


def createtextfontcom(key):
    def _f(key, x):
        globalconfig[key] = x
        mayberealtimesetfont()

    font_comboBox = FocusFontCombo()
    font_comboBox.setCurrentFont(QFont(globalconfig[key]))
    font_comboBox.currentTextChanged.connect(functools.partial(_f, key))
    return font_comboBox


@Singleton
class extrahtml(saveposwindow):
    def tryload(self):

        use = gobject.getuserconfigdir(self.fn)
        if os.path.exists(use) == False:
            use = self.fneg
        with open(use, "r", encoding="utf8") as ff:
            self.vistext.setPlainText(ff.read())

    @tryprint
    def applyhtml(self, _):
        self.tester.loadex(self.vistext.toPlainText())

    def savehtml(self):
        with open(gobject.getuserconfigdir(self.fn), "w", encoding="utf8") as ff:
            ff.write(self.vistext.toPlainText())

    def __init__(self, parent, fn, fneg, tester) -> None:
        super().__init__(parent, poslist=globalconfig["geo_extrahtml"])
        self.setWindowTitle("附加HTML")
        self.tester = tester
        self.fneg = fneg
        self.fn = fn
        self.btn_save = LPushButton("保存")
        self.btn_save.clicked.connect(self.savehtml)
        self.btn_apply = LPushButton("测试")
        self.btn_apply.clicked.connect(self.applyhtml)
        self.vistext = QPlainTextEdit()
        w = QWidget()
        lay = QVBoxLayout(w)
        hl = QHBoxLayout()
        hl.addWidget(self.btn_save)
        hl.addWidget(self.btn_apply)
        lay.addWidget(self.vistext)
        lay.addLayout(hl)
        self.setCentralWidget(w)
        self.tryload()
        self.show()


def createinternalfontsettings(self, forml: LFormLayout, group, _type):
    need = globalconfig["rendertext_using_internal"][group] != _type
    globalconfig["rendertext_using_internal"][group] = _type
    if need:
        gobject.baseobject.translation_ui.translate_text.resetstyle()
    __internal = globalconfig["rendertext"][group][_type]
    dd = __internal.get("args", {})

    clearlayout(forml)

    for key in dd:
        line = __internal["argstype"][key]
        name = line["name"]
        _type = line["type"]
        if key in ["width", "shadowR_ex"]:
            if key == "width":
                keyx = "width_rate"
            elif key == "shadowR_ex":
                keyx = "shadowR"
            widthline = __internal["argstype"].get(keyx, None)
            if widthline is not None:
                __ = getsmalllabel("x_大小_+")()
                forml.addRow(
                    name,
                    getboxlayout(
                        [
                            getspinbox(
                                widthline.get("min", 0),
                                widthline.get("max", 100),
                                dd,
                                keyx,
                                True,
                                widthline.get("step", 0.1),
                                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                            ),
                            __,
                            getspinbox(
                                line.get("min", 0),
                                line.get("max", 100),
                                dd,
                                key,
                                True,
                                line.get("step", 0.1),
                                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                            ),
                        ]
                    ),
                )
                continue
        elif key in ["width_rate", "shadowR"]:
            continue
        if _type == "colorselect":
            lineW = getcolorbutton(
                self,
                dd,
                key,
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
            )
        elif _type in ["spin", "intspin"]:
            lineW = getspinbox(
                line.get("min", 0),
                line.get("max", 100),
                dd,
                key,
                _type == "spin",
                line.get("step", 0.1),
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
            )
        elif _type == "switch":
            lineW = getsimpleswitch(
                d=dd,
                key=key,
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
            )

        forml.addRow(
            name,
            lineW,
        )


class otherdisplaysetting(PopupWidget):

    def __init__(self, parent):
        super().__init__(parent)
        form = LFormLayout(self)
        form.addRow(
            "显示顺序",
            getsimplecombobox(
                ["原文_翻译", "翻译_原文"],
                globalconfig,
                "displayrank",
                callback=gobject.baseobject.translation_ui.translate_text.setdisplayrank,
            ),
        )
        form.addRow(
            "显示方向",
            getsimplecombobox(
                ["横向", "竖向"],
                globalconfig,
                "verticalhorizontal",
                callback=gobject.baseobject.translation_ui.verticalhorizontal,
            ),
        )
        form.addRow(
            "显示单词信息_在WebView2内显示",
            getsimpleswitch(
                globalconfig,
                "word_hover_action_usewb2",
                callback=gobject.baseobject.translation_ui.translate_text.setwordhoveruse,
            ),
        )
        self.display()


def resetgroudswitchcallback(self, group):
    clearlayout(self.goodfontsettingsformlayout)

    goodfontgroupswitch = SuperCombo()
    if group == "webview":
        _btn = getIconButton(
            callback=functools.partial(
                extrahtml,
                self,
                "extrahtml.html",
                r"LunaTranslator\htmlcode\uiwebview\extrahtml\mainui.html",
                gobject.baseobject.translation_ui.translate_text.textbrowser,
            ),
            icon="fa.edit",
        )
        switch = getsimpleswitch(
            globalconfig,
            "useextrahtml",
            callback=lambda x: gobject.baseobject.translation_ui.translate_text.textbrowser.loadex(),
        )
        _btn2 = getIconButton(
            callback=functools.partial(Exteditor, self),
            enable=globalconfig["webviewLoadExt"],
        )
        switch2 = getsimpleswitch(
            globalconfig,
            "webviewLoadExt",
            callback=lambda x: (
                gobject.baseobject.translation_ui.translate_text.loadinternal(
                    True, True
                ),
                _btn2.setEnabled(x),
            ),
        )
        self.goodfontsettingsformlayout.addRow(
            getboxlayout(
                [
                    "附加HTML",
                    switch,
                    _btn,
                    "",
                    "附加浏览器插件",
                    switch2,
                    _btn2,
                    "",
                    "其他",
                    D_getIconButton(functools.partial(otherdisplaysetting, self)),
                ]
            ),
        )
        self.goodfontsettingsformlayout.addRow(SplitLine())

    __form = LFormLayout()
    __form.addRow("字体样式", goodfontgroupswitch)
    self.goodfontsettingsformlayout.addRow(__form)
    forml = LFormLayout()
    __form.addRow(forml)

    goodfontgroupswitch.addItems(
        [
            globalconfig["rendertext"][group][x]["name"]
            for x in static_data["textrender"][group]
        ]
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
    gobject.baseobject.translation_ui.translate_text.loadinternal(shoudong=True)
    visengine_internal = ["textbrowser", "webview"]
    self.seletengeinecombo.setCurrentIndex(
        visengine_internal.index(globalconfig["rendertext_using"])
    )


def creategoodfontwid(self):

    self.goodfontsettingsWidget = NQGroupBox()
    self.goodfontsettingsformlayout = LFormLayout(self.goodfontsettingsWidget)
    resetgroudswitchcallback(self, globalconfig["rendertext_using"])
    return self.goodfontsettingsWidget


def _createseletengeinecombo(self):

    self.seletengeinecombo = getsimplecombobox(
        ["Qt", "Webview2"],
        globalconfig,
        "rendertext_using",
        internal=["textbrowser", "webview"],
        callback=functools.partial(resetgroudswitchcallback, self),
        static=True,
    )
    return self.seletengeinecombo


def GetFormForLineHeight(parent, dic, callback):
    form = LFormLayout(parent)
    form.addRow(
        "上边距",
        getspinbox(-9999, 9999, dic, "marginTop", callback=callback, default=0),
    )
    form.addRow(
        "下边距",
        getspinbox(-9999, 9999, dic, "marginBottom", callback=callback, default=0),
    )
    value = getboxwidget(
        [
            getspinbox(
                0,
                2,
                dic,
                "lineHeight",
                callback=callback,
                double=True,
                step=0.01,
                default=1,
            ),
            "倍",
        ],
    )
    value.setEnabled(not dic.get("lineHeightNormal", True))
    lineheigth = getboxlayout(
        [
            getboxlayout(
                [
                    "默认",
                    getsimpleswitch(
                        dic,
                        "lineHeightNormal",
                        callback=lambda _: (
                            value.setEnabled(not _),
                            callback(),
                        ),
                        default=True,
                    ),
                ],
            ),
            value,
        ],
        lc=QVBoxLayout,
    )
    form.addRow(SplitLine())
    form.addRow("行高", lineheigth)


class Spacesetting(PopupWidget):
    def __init__(self, parent, trans):
        super().__init__(parent)
        GetFormForLineHeight(
            self,
            globalconfig[["lineheights", "lineheightstrans"][trans]],
            mayberealtimesetfont,
        )
        self.display()


def vistranslate_rank(self):
    _not = []
    for i, k in enumerate(globalconfig["fix_translate_rank_rank"]):
        if not translate_exits(k):
            _not.append(i)
    for _ in reversed(_not):
        globalconfig["fix_translate_rank_rank"].pop(_)
    listediter(
        self,
        "显示顺序",
        globalconfig["fix_translate_rank_rank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(getannotatedapiname(k)),
        exec=True,
    )


def __changeuibuttonstate2(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.maybeneedtranslateshowhidetranslate()


def xianshigrid_style(self):
    textgrid = [
        [
            dict(
                title="原文",
                type="grid",
                grid=(
                    [
                        "字体",
                        (
                            getboxlayout(
                                [
                                    functools.partial(
                                        createtextfontcom,
                                        "fonttype",
                                    ),
                                    "",
                                    "颜色",
                                    D_getcolorbutton(
                                        self,
                                        globalconfig,
                                        "rawtextcolor",
                                        callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                                    ),
                                ]
                            ),
                            0,
                        ),
                        "",
                        "显示",
                        D_getsimpleswitch(
                            globalconfig,
                            "isshowrawtext",
                            callback=lambda x: __changeuibuttonstate(self, x),
                            name="show_original_switch",
                            parent=self,
                        ),
                    ],
                    [
                        "大小",
                        D_getspinbox(
                            5,
                            100,
                            globalconfig,
                            "fontsizeori",
                            double=True,
                            step=0.1,
                            callback=mayberealtimesetfont,
                        ),
                        "",
                        "加粗",
                        D_getsimpleswitch(
                            globalconfig,
                            "showbold",
                            callback=mayberealtimesetfont,
                        ),
                        "",
                        "间距",
                        D_getIconButton(
                            callback=functools.partial(
                                Spacesetting,
                                self,
                                False,
                            )
                        ),
                    ],
                ),
            ),
        ],
        [
            dict(
                title="译文",
                type="grid",
                grid=(
                    [
                        "字体",
                        (functools.partial(createtextfontcom, "fonttype2"), 0),
                        "",
                        "显示",
                        D_getsimpleswitch(
                            globalconfig,
                            "showfanyi",
                            callback=lambda x: __changeuibuttonstate2(self, x),
                            name="show_fany_switch",
                            parent=self,
                        ),
                    ],
                    [
                        "大小",
                        D_getspinbox(
                            1,
                            100,
                            globalconfig,
                            "fontsize",
                            double=True,
                            step=0.1,
                            callback=mayberealtimesetfont,
                        ),
                        "",
                        "加粗",
                        D_getsimpleswitch(
                            globalconfig,
                            "showbold_trans",
                            callback=mayberealtimesetfont,
                        ),
                        "",
                        "间距",
                        D_getIconButton(
                            callback=functools.partial(Spacesetting, self, True)
                        ),
                    ],
                ),
            ),
        ],
        [
            dict(
                type="grid",
                grid=(
                    [
                        "居中显示",
                        D_getsimpleswitch(
                            globalconfig,
                            "showatcenter",
                            callback=gobject.baseobject.translation_ui.translate_text.showatcenter,
                        ),
                        "",
                        "显示错误信息",
                        D_getsimpleswitch(
                            globalconfig,
                            "showtranexception",
                            callback=lambda x: changeshowerrorstate(self, x),
                        ),
                        "",
                        "",
                        "收到翻译时才刷新",
                        D_getsimpleswitch(globalconfig, "refresh_on_get_trans"),
                    ],
                    [
                        "显示翻译器名称",
                        D_getsimpleswitch(
                            globalconfig,
                            "showfanyisource",
                            callback=gobject.baseobject.translation_ui.translate_text.showhidename,
                        ),
                        "",
                        "固定翻译显示顺序",
                        D_getsimpleswitch(globalconfig, "fix_translate_rank"),
                        D_getIconButton(functools.partial(vistranslate_rank, self)),
                    ],
                ),
            ),
        ],
        [
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
        ],
    ]
    return textgrid
