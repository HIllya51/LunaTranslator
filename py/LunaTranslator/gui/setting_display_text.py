from qtsymbols import *
import functools
import gobject, os
from myutils.config import globalconfig, static_data, _TR, get_platform
from myutils.wrapper import tryprint
from myutils.utils import translate_exits, getannotatedapiname
from gui.usefulwidget import (
    getsimplecombobox,
    Singleton_close,
    saveposwindow,
    D_getspinbox,
    D_getIconButton,
    clearlayout,
    getboxlayout,
    D_getcolorbutton,
    getcolorbutton,
    MySwitch,
    getsimpleswitch,
    D_getsimpleswitch,
    selectcolor,
    listediter,
    FocusFontCombo,
    SuperCombo,
    getspinbox,
    getsmalllabel,
    SplitLine,
)
from gui.dynalang import LPushButton, LFormLayout


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.translation_ui.translate_text.textbrowser.showhideorigin(x)
    try:
        self.fenyinsettings.setEnabled(x)
    except:
        pass


def changeshowerrorstate(self, x):
    gobject.baseobject.translation_ui.translate_text.textbrowser.showhideerror(x)


def mayberealtimesetfont(_=None):
    gobject.baseobject.translation_ui.translate_text.textbrowser.setfontstyle()


def createtextfontcom(key):
    def _f(key, x):
        globalconfig[key] = x
        mayberealtimesetfont()

    font_comboBox = FocusFontCombo()
    font_comboBox.currentTextChanged.connect(functools.partial(_f, key))
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
        gobject.baseobject.translation_ui.translate_text.textbrowser.loadex(
            self.vistext.toPlainText()
        )

    def savehtml(self):
        with open(
            gobject.getuserconfigdir("extrahtml.html"), "w", encoding="utf8"
        ) as ff:
            ff.write(self.vistext.toPlainText())

    def __init__(self, parent) -> None:
        super().__init__(parent, poslist=globalconfig["geo_extrahtml"])
        self.setWindowTitle("额外的html")

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


def mayberefreshe():
    gobject.baseobject.translation_ui.translate_text.refreshcontent()


def createinternalfontsettings(self, forml: LFormLayout, group, _type):
    need = globalconfig["rendertext_using_internal"][group] != _type
    globalconfig["rendertext_using_internal"][group] = _type
    if need:
        gobject.baseobject.translation_ui.translate_text.refreshcontent()
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
                __ = getsmalllabel("x_字体大小_+")()
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
                                callback=lambda _: mayberefreshe(),
                            ),
                            __,
                            getspinbox(
                                line.get("min", 0),
                                line.get("max", 100),
                                dd,
                                key,
                                True,
                                line.get("step", 0.1),
                                callback=lambda _: mayberefreshe(),
                            ),
                        ]
                    ),
                )
                continue
        elif key in ["width_rate", "shadowR"]:
            continue
        if _type == "colorselect":
            lineW = getcolorbutton(
                dd,
                key,
                callback=functools.partial(
                    lambda dd, key: selectcolor(
                        self,
                        dd,
                        key,
                        self.miaobian_color_button,
                        callback=mayberefreshe,
                    ),
                    dd,
                    key,
                ),
                name="miaobian_color_button",
                parent=self,
            )
        elif _type in ["spin", "intspin"]:
            lineW = getspinbox(
                line.get("min", 0),
                line.get("max", 100),
                dd,
                key,
                _type == "spin",
                line.get("step", 0.1),
                callback=lambda _: mayberefreshe(),
            )
        elif _type == "switch":
            lineW = MySwitch(sign=dd[key])

            def __(dd, key, x):
                dd[key] = x
                mayberefreshe()

            lineW.clicked.connect(functools.partial(__, dd, key))
        forml.addRow(
            name,
            lineW,
        )


def resetgroudswitchcallback(self, group):
    clearlayout(self.goodfontsettingsformlayout)

    goodfontgroupswitch = SuperCombo()
    if group == "webview":
        _btn = LPushButton("编辑")
        _btn.clicked.connect(lambda: extrahtml(self))
        switch = getsimpleswitch(
            globalconfig,
            "useextrahtml",
            callback=lambda x: [
                gobject.baseobject.translation_ui.translate_text.textbrowser.loadex(),
                _btn.setEnabled(x),
            ],
        )
        _btn.setEnabled(globalconfig["useextrahtml"])
        self.goodfontsettingsformlayout.addRow(
            "额外的html",
            getboxlayout([switch, _btn]),
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

    self.goodfontsettingsWidget = QGroupBox()
    self.goodfontsettingsWidget.setStyleSheet(
        "QGroupBox{ margin-top:0px;} QGroupBox:title {margin-top: 0px;}"
    )
    self.goodfontsettingsformlayout = LFormLayout(self.goodfontsettingsWidget)
    resetgroudswitchcallback(self, globalconfig["rendertext_using"])
    return self.goodfontsettingsWidget


def _createseletengeinecombo(self):

    visengine = ["Qt", "Webview2"]
    visengine_internal = ["textbrowser", "webview"]
    if get_platform() == "xp":
        visengine.pop(1)
        visengine_internal.pop(1)
    self.seletengeinecombo = getsimplecombobox(
        visengine,
        globalconfig,
        "rendertext_using",
        internal=visengine_internal,
        callback=functools.partial(resetgroudswitchcallback, self),
        static=True,
    )
    return self.seletengeinecombo


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
    )


def xianshigrid_style(self):
    textgrid = [
        [
            (
                dict(
                    title="字体",
                    type="grid",
                    grid=(
                        [
                            (
                                dict(
                                    title="原文",
                                    type="grid",
                                    grid=(
                                        [
                                            "字体",
                                            (
                                                functools.partial(
                                                    createtextfontcom, "fonttype"
                                                ),
                                                0,
                                            ),
                                            "",
                                            "字体大小",
                                            D_getspinbox(
                                                5,
                                                100,
                                                globalconfig,
                                                "fontsizeori",
                                                double=True,
                                                step=0.1,
                                                callback=mayberealtimesetfont,
                                            ),
                                        ],
                                        [
                                            "行间距",
                                            D_getspinbox(
                                                -100,
                                                100,
                                                globalconfig,
                                                "extra_space",
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
                                            "颜色",
                                            D_getcolorbutton(
                                                globalconfig,
                                                "rawtextcolor",
                                                callback=lambda: selectcolor(
                                                    self,
                                                    globalconfig,
                                                    "rawtextcolor",
                                                    self.original_color_button,
                                                    callback=gobject.baseobject.translation_ui.translate_text.textbrowser.setcolors,
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
                                    title="译文",
                                    type="grid",
                                    grid=(
                                        [
                                            "字体",
                                            (
                                                functools.partial(
                                                    createtextfontcom, "fonttype2"
                                                ),
                                                0,
                                            ),
                                            "",
                                            "字体大小",
                                            D_getspinbox(
                                                1,
                                                100,
                                                globalconfig,
                                                "fontsize",
                                                double=True,
                                                step=0.1,
                                                callback=mayberealtimesetfont,
                                            ),
                                        ],
                                        [
                                            "行间距",
                                            D_getspinbox(
                                                -100,
                                                100,
                                                globalconfig,
                                                "extra_space_trans",
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
                                            "",
                                            "",
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
        [
            (
                dict(
                    title="内容",
                    type="grid",
                    grid=(
                        [
                            "居中显示",
                            D_getsimpleswitch(
                                globalconfig,
                                "showatcenter",
                                callback=lambda x: gobject.baseobject.translation_ui.translate_text.textbrowser.showatcenter(
                                    x
                                ),
                            ),
                            "",
                            "收到翻译时才刷新",
                            D_getsimpleswitch(globalconfig, "refresh_on_get_trans"),
                            "",
                            "固定翻译显示顺序",
                            D_getsimpleswitch(globalconfig, "fix_translate_rank"),
                            D_getIconButton(
                                functools.partial(vistranslate_rank, self),
                                "fa.gear",
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
                            "显示错误信息",
                            D_getsimpleswitch(
                                globalconfig,
                                "showtranexception",
                                callback=lambda x: changeshowerrorstate(self, x),
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
