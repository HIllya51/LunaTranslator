from qtsymbols import *
import functools
import gobject, os
from myutils.config import globalconfig, static_data, ui_settings
from myutils.wrapper import tryprint
from myutils.utils import translate_exits, _TR, getannotatedapiname
from gui.usefulwidget import (
    getsimplecombobox,
    D_getsimplecombobox,
    Singleton,
    saveposwindow,
    D_getspinbox,
    clearlayout,
    getboxlayout,
    getboxwidget,
    D_getcolorbutton,
    ColorButton,
    saveposwindow,
    create_centered_rect,
    listediter,
    getIconButton,
    D_getIconSwitch,
    getsimpleswitch,
    D_getsimpleswitch,
    FocusFontCombo,
    SuperCombo,
    D_getIconButton,
    getspinbox,
    getsmalllabel,
    SplitLine,
    PopupWidget,
    Exteditor,
    GroupCardWidget,
    makegrid,
    makecardrow,
)
from gui.dynalang import LPushButton, LFormLayout, LLabel
from gui.fluent.expander import ExExpander


def __changeuibuttonstate(x):
    gobject.base.translation_ui.refreshtoolicon()
    gobject.base.translation_ui.translate_text.showhideorigin(x)
    gobject.base.fenyinsettings.emit(x)
    gobject.base.fencisettings.emit(x)


def mayberealtimesetfont(_=None):
    gobject.base.translation_ui.translate_text.setfontstyle()


def createtextfontcom(key, df):
    def _f(key, x):
        globalconfig[key] = x
        mayberealtimesetfont()

    font_comboBox = FocusFontCombo(sizeX=True)
    font_comboBox.setCurrentFont(QFont(globalconfig.get(key, df)))
    font_comboBox.currentTextChanged.connect(functools.partial(_f, key))
    return font_comboBox


@Singleton
class extrahtml(saveposwindow):
    def tryload(self):

        use = gobject.getconfig(self.fn)
        if os.path.exists(use) == False:
            use = self.fneg
        with open(use, "r", encoding="utf8") as ff:
            self.vistext.setPlainText(ff.read())

    @tryprint
    def applyhtml(self, _):
        self.tester.loadex(self.vistext.toPlainText())

    def savehtml(self):
        with open(gobject.getconfig(self.fn), "w", encoding="utf8") as ff:
            ff.write(self.vistext.toPlainText())

    def __init__(self, parent, fn, fneg, tester) -> None:
        super().__init__(
            parent,
            posinit=gobject.tempconfig.get(
                "geo_extrahtml",
                create_centered_rect(600, 400, gobject.base.settin_ui).getRect(),
            ),
            possave=functools.partial(gobject.tempconfig.__setitem__, "geo_extrahtml"),
        )
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
        gobject.base.translation_ui.translate_text.resetstyle()
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
                                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
                            ),
                            __,
                            getspinbox(
                                line.get("min", 0),
                                line.get("max", 100),
                                dd,
                                key,
                                True,
                                line.get("step", 0.1),
                                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
                            ),
                        ]
                    ),
                )
                continue
        elif key in ["width_rate", "shadowR"]:
            continue
        if _type == "colorselect":
            lineW = ColorButton(
                self,
                dd,
                key,
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )
        elif _type in ["spin", "intspin"]:
            lineW = getspinbox(
                line.get("min", 0),
                line.get("max", 100),
                dd,
                key,
                _type == "spin",
                line.get("step", (1, 0.1)[_type == "spin"]),
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )
        elif _type == "switch":
            lineW = getsimpleswitch(
                d=dd,
                key=key,
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
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
            "显示方向",
            getsimplecombobox(
                ["横向", "竖向"],
                globalconfig,
                "verticalhorizontal",
                callback=gobject.base.translation_ui.verticalhorizontal,
                default=False,
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
                gobject.base.translation_ui.translate_text.textbrowser,
            ),
            icon="fa.edit",
        )
        switch = getsimpleswitch(
            globalconfig,
            "useextrahtml",
            callback=lambda x: gobject.base.translation_ui.translate_text.textbrowser.loadex(),
            default=False,
        )
        _btn2 = getIconButton(
            callback=functools.partial(Exteditor, self),
            enable=globalconfig.get("webviewLoadExt", True),
        )
        switch2 = getsimpleswitch(
            globalconfig,
            "webviewLoadExt",
            callback=lambda x: (
                gobject.base.translation_ui.translate_text.loadinternal(True, True),
                _btn2.setEnabled(x),
            ),
            default=True,
        )
        self.goodfontsettingsformlayout.addRow(
            getboxlayout(
                [
                    "附加HTML",
                    switch,
                    _btn,
                    0,
                    "附加浏览器插件",
                    switch2,
                    _btn2,
                    0,
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
    gobject.base.translation_ui.translate_text.loadinternal(shoudong=True)


def _createseletengeinecombo(self):

    seletengeinecombo = getsimplecombobox(
        ["Qt", "Webview2"],
        globalconfig,
        "rendertext_using",
        internal=["textbrowser", "webview"],
        callback=functools.partial(resetgroudswitchcallback, self),
        static=True,
    )
    gobject.base.connectsignal(gobject.base.switchdisplayengine, seletengeinecombo.setCurrentData)
    return seletengeinecombo


def GetFormForLineHeight(parent, dic, callback, wide=False):
    form = LFormLayout(parent)
    __ = [
        "上边距",
        getspinbox(-9999, 9999, dic, "marginTop", callback=callback, default=0),
        "",
        "下边距",
        getspinbox(-9999, 9999, dic, "marginBottom", callback=callback, default=0),
    ]
    if wide:
        __[0] = getsmalllabel(__[0])
        __[3] = getsmalllabel(__[3])
        form.addRow(getboxlayout(__))
    else:
        form.addRow(__[0], __[1])
        form.addRow(__[3], __[4])
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
            getsmalllabel("倍"),
        ],
    )
    value.setEnabled(not dic.get("lineHeightNormal", True))
    __ = [
        getsmalllabel("默认"),
        getsimpleswitch(
            dic,
            "lineHeightNormal",
            callback=lambda _: (
                value.setEnabled(not _),
                callback(),
            ),
            default=True,
        ),
    ]
    if wide:
        __.append(value)
        lineheigth = getboxlayout(__)
    else:
        __.append("")
        lineheigth = getboxlayout(
            [
                getboxlayout(__),
                value,
            ],
            lc=QVBoxLayout,
        )
        form.addRow(SplitLine())
    form.addRow("行高", lineheigth)


class Spacesetting(GroupCardWidget):
    def __init__(self, parent, trans):
        super().__init__(parent=parent)
        GetFormForLineHeight(
            self.contentWidget(),
            globalconfig[["lineheights", "lineheightstrans"][trans]],
            mayberealtimesetfont,
            wide=True,
        )


def TextAreaBack(parent):
    w = QWidget()
    form = LFormLayout(w)
    form.addRow(
        "颜色",
        getboxlayout(
            [
                ColorButton(
                    parent,
                    ui_settings,
                    "text_area_background_color",
                    callback=gobject.base.translation_ui.translate_text.setTextAreaBackStyle,
                    default="pink",
                ),
                getsmalllabel("不透明度"),
                getspinbox(
                    0,
                    100,
                    ui_settings,
                    "text_area_background_alpha",
                    callback=gobject.base.translation_ui.translate_text.setTextAreaBackStyle,
                    default=85,
                ),
            ]
        ),
    )
    for text, key in (
        ("圆角", "text_area_background_r"),
        ("延展宽度", "text_area_background_w"),
        ("延展高度", "text_area_background_h"),
    ):
        form.addRow(
            text,
            getspinbox(
                0,
                50,
                ui_settings,
                key,
                double=True,
                step=0.2,
                callback=gobject.base.translation_ui.translate_text.setTextAreaBackStyle,
                default=5,
            ),
        )
    return w


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


def __changeuibuttonstate2(*_):
    gobject.base.translation_ui.refreshtoolicon()
    gobject.base.maybeneedtranslateshowhidetranslate()


def _showhidefy():
    btn = getsimpleswitch(
        globalconfig,
        "showfanyi",
        callback=__changeuibuttonstate2,
        default=True,
    )
    gobject.base.show_fany_switch.connect(btn.setChecked)
    return btn


def __xianshi():
    btn = getsimpleswitch(
        globalconfig,
        "isshowrawtext",
        callback=__changeuibuttonstate,
        default=True,
    )
    gobject.base.show_original_switch.connect(btn.setChecked)
    return btn


def __textstyleexpander(self, title, showswitch, grid):
    """原文/译文折叠卡（同 LICENSE 的 ExExpander）：
    头部 = 标题 + 「显示」标签和开关（折叠按钮左边），内容 = 字体等具体设置。"""
    exp = ExExpander()
    header = QWidget()
    hlay = QHBoxLayout(header)
    # 同 LICENSE：HeaderButton 自带 16px 左内边距与 chevron 预留区，只留上下边距
    hlay.setContentsMargins(0, 12, 0, 12)
    hlay.setSpacing(8)
    titlelabel = LLabel(title)
    titlefont = titlelabel.font()
    titlefont.setPixelSize(15)
    titlelabel.setFont(titlefont)
    hlay.addWidget(titlelabel)
    hlay.addStretch(1)
    hlay.addWidget(getsmalllabel("显示")())
    hlay.addWidget(showswitch)
    exp.setHeaderWidget(header)
    content = makegrid(grid, hiderows=[1])
    exp.addContentWidget(content)
    return exp, content


def __textbackexpander(self):
    """文字区域背景折叠卡：头部 = 标题 + 开关，内容 = 颜色/圆角等各项。"""
    exp = ExExpander()
    header = QWidget()
    hlay = QHBoxLayout(header)
    hlay.setContentsMargins(0, 12, 0, 12)
    hlay.setSpacing(8)
    titlelabel = LLabel("文字区域背景")
    titlefont = titlelabel.font()
    titlefont.setPixelSize(15)
    titlelabel.setFont(titlefont)
    hlay.addWidget(titlelabel)
    hlay.addStretch(1)
    hlay.addWidget(
        D_getsimpleswitch(
            ui_settings,
            "text_area_background",
            callback=gobject.base.translation_ui.translate_text.showtextareabackground,
            default=False,
        )()
    )
    exp.setHeaderWidget(header)
    exp.addContentWidget(TextAreaBack(self))
    return exp


def __engineexpander(self):
    """显示引擎折叠卡：头部 = 标题 + 引擎下拉，内容 = 所选引擎的样式设置。"""
    # 表单布局需先于下拉创建——下拉初值变化即触发 resetgroudswitchcallback
    content = QWidget()
    self.goodfontsettingsformlayout = LFormLayout(content)
    exp = ExExpander()
    header = QWidget()
    hlay = QHBoxLayout(header)
    hlay.setContentsMargins(0, 12, 0, 12)
    hlay.setSpacing(8)
    titlelabel = LLabel("显示引擎")
    titlefont = titlelabel.font()
    titlefont.setPixelSize(15)
    titlelabel.setFont(titlefont)
    hlay.addWidget(titlelabel)
    hlay.addStretch(1)
    hlay.addWidget(_createseletengeinecombo(self))
    exp.setHeaderWidget(header)
    exp.addContentWidget(content)
    resetgroudswitchcallback(self, globalconfig["rendertext_using"])
    return exp


def xianshigrid_style(self):
    yuanwenexp, self.yuanwenobject = __textstyleexpander(
        self,
        "原文",
        __xianshi(),
        (
            [
                getsmalllabel("字体"),
                functools.partial(
                    createtextfontcom,
                    "fonttype",
                    gobject.tempconfig.get("fonttype", ""),
                ),
                D_getspinbox(
                    5,
                    100,
                    globalconfig,
                    "fontsizeori",
                    double=True,
                    callback=mayberealtimesetfont,
                    default=16,
                ),
                D_getcolorbutton(
                    self,
                    globalconfig,
                    "rawtextcolor",
                    callback=gobject.base.translation_ui.translate_text.setcolorstyle,
                    default="#000000",
                ),
                D_getIconSwitch(
                    globalconfig,
                    "showbold",
                    callback=mayberealtimesetfont,
                    tips="加粗",
                    default=False,
                    icon="fa.bold",
                ),
                D_getIconSwitch(
                    globalconfig,
                    "showitalic",
                    callback=mayberealtimesetfont,
                    tips="倾斜",
                    default=False,
                    icon="fa.italic",
                ),
                "",
                getsmalllabel("间距"),
                D_getIconSwitch(
                    icon="fa.gear",
                    checkablechangecolor=False,
                    callback=lambda x: self.yuanwenobject.layout().setRowVisible(
                        1, x
                    ),
                    tips="间距_设置"
                ),
            ],
            [(functools.partial(Spacesetting, self, False), 0)],
        ),
    )
    yiwenexp, self.yiwenobject = __textstyleexpander(
        self,
        "译文",
        _showhidefy(),
        (
            [
                getsmalllabel("字体"),
                functools.partial(
                    createtextfontcom,
                    "fonttype2",
                    gobject.tempconfig.get("fonttype2", ""),
                ),
                D_getspinbox(
                    1,
                    100,
                    globalconfig,
                    "fontsize",
                    double=True,
                    callback=mayberealtimesetfont,
                    default=16,
                ),
                D_getIconButton(
                    icon="fa.paint-brush",
                    callback=gobject.base.switchtotspage.emit,
                    tips="颜色",
                ),
                D_getIconSwitch(
                    globalconfig,
                    "showbold_trans",
                    callback=mayberealtimesetfont,
                    tips="加粗",
                    default=False,
                    icon="fa.bold",
                ),
                D_getIconSwitch(
                    globalconfig,
                    "showitalic_trans",
                    callback=mayberealtimesetfont,
                    tips="倾斜",
                    default=False,
                    icon="fa.italic",
                ),
                "",
                getsmalllabel("间距"),
                D_getIconSwitch(
                    icon="fa.gear",
                    checkablechangecolor=False,
                    callback=lambda x: self.yiwenobject.layout().setRowVisible(
                        1, x
                    ),
                    tips="间距_设置"
                ),
            ],
            [(functools.partial(Spacesetting, self, True), 0)],
        ),
    )
    textgrid = [
        [yuanwenexp],
        [yiwenexp],
        [
            (
                makecardrow(
                    "居中显示",
                    D_getsimpleswitch(
                        globalconfig,
                        "showatcenter",
                        callback=gobject.base.translation_ui.translate_text.showatcenter,
                        default=True,
                    ),
                ),
                0,
            )
        ],
        [
            (
                makecardrow(
                    "显示翻译器名称",
                    D_getsimpleswitch(
                        globalconfig,
                        "showfanyisource",
                        callback=gobject.base.translation_ui.translate_text.showhidename,
                        default=False,
                    ),
                ),
                0,
            )
        ],
        [
            (
                makecardrow(
                    "收到翻译时才刷新",
                    D_getsimpleswitch(
                        globalconfig, "refresh_on_get_trans", default=False
                    ),
                ),
                0,
            )
        ],
        [
            (
                makecardrow(
                    "固定翻译显示顺序",
                    D_getsimpleswitch(
                        globalconfig, "fix_translate_rank", default=False
                    ),
                    D_getIconButton(functools.partial(vistranslate_rank, self)),
                ),
                0,
            )
        ],
        [
            (
                makecardrow(
                    "显示顺序",
                    D_getsimplecombobox(
                        ["原文_翻译", "翻译_原文"],
                        globalconfig,
                        "displayrank",
                        callback=gobject.base.translation_ui.translate_text.setdisplayrank,
                        default=0,
                    ),
                ),
                0,
            )
        ],
        [(__textbackexpander(self), 0)],
        [(__engineexpander(self), 0)],
    ]
    return textgrid
