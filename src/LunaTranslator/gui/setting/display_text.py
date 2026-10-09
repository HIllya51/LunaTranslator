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
from gui.fluent.colorpicker import ColorPickerButton
from gui.ocrtranslationoverlay import refresh_overlays


def __changeuibuttonstate(x):
    gobject.base.translation_ui.refreshtoolicon()
    gobject.base.translation_ui.translate_text.showhideorigin(x)
    gobject.base.fenyinsettings.emit(x)
    gobject.base.fencisettings.emit(x)


def mayberealtimesetfont(_=None):
    gobject.base.translation_ui.translate_text.setfontstyle()
    # 原地显示翻译覆盖层跟随译文（字号/字体/加粗）
    refresh_overlays()


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
        self.vistext = QTextEdit()
        self.vistext.setAcceptRichText(False)
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


def createinternalfontsettings(self, expander, group, _type):
    """所选样式组的参数 → 字体样式折叠卡的子项；无参数的样式
    （普通字体）时折叠卡退化为普通卡。"""
    need = globalconfig["rendertext_using_internal"][group] != _type
    globalconfig["rendertext_using_internal"][group] = _type
    if need:
        gobject.base.translation_ui.translate_text.resetstyle()
    __internal = globalconfig["rendertext"][group][_type]
    dd = __internal.get("args", {})
    expander.clearContentWidgets()
    for key in dd:
        line = __internal["argstype"][key]
        name = line["name"]
        t = line["type"]
        if key in ["width", "shadowR_ex"]:
            if key == "width":
                keyx = "width_rate"
            elif key == "shadowR_ex":
                keyx = "shadowR"
            widthline = __internal["argstype"].get(keyx, None)
            if widthline is not None:
                expander.addContentWidget(
                    getboxwidget(
                        [
                            name,
                            1,
                            getspinbox(
                                widthline.get("min", 0),
                                widthline.get("max", 100),
                                dd,
                                keyx,
                                True,
                                widthline.get("step", 0.1),
                                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
                            ),
                            getsmalllabel("x_大小_+")(),
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
                    )
                )
                continue
        elif key in ["width_rate", "shadowR"]:
            continue
        if t == "colorselect":
            lineW = ColorButton(
                self,
                dd,
                key,
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )
        elif t in ["spin", "intspin"]:
            lineW = getspinbox(
                line.get("min", 0),
                line.get("max", 100),
                dd,
                key,
                t == "spin",
                line.get("step", (1, 0.1)[t == "spin"]),
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )
        elif t == "switch":
            lineW = getsimpleswitch(
                d=dd,
                key=key,
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )
        else:
            continue
        expander.addContentWidget(getboxwidget([name, 1, lineW]))
    # 无参数样式（普通字体）退化为普通卡（默认关闭）
    expander.setFoldable(bool(dd))


def resetgroudswitchcallback(self, group):
    # 显示引擎折叠卡：引擎专属设置为子项（仅 webview；Qt 引擎退化为普通卡）
    self.engineexpander.clearContentWidgets()
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
        self.engineexpander.addContentWidget(
            getboxwidget(["附加HTML", 1, switch, _btn])
        )
        self.engineexpander.addContentWidget(
            getboxwidget(["附加浏览器插件", 1, switch2, _btn2])
        )
        self.engineexpander.addContentWidget(
            getboxwidget(
                [
                    "显示方向",
                    1,
                    getsimplecombobox(
                        ["横向", "竖向"],
                        globalconfig,
                        "verticalhorizontal",
                        callback=gobject.base.translation_ui.verticalhorizontal,
                        default=False,
                    ),
                ]
            )
        )
    self.engineexpander.setFoldable(group == "webview")

    # 字体样式折叠卡：头部（标题+样式组下拉）随引擎一并重建；内容由
    # createinternalfontsettings 按所选样式建为子项
    goodfontgroupswitch = SuperCombo()
    header = QWidget()
    hlay = QHBoxLayout(header)
    hlay.setContentsMargins(0, 12, 0, 12)
    hlay.setSpacing(8)
    titlelabel = LLabel("字体样式")
    titlefont = titlelabel.font()
    titlefont.setPixelSize(15)
    titlelabel.setFont(titlefont)
    hlay.addWidget(titlelabel)
    hlay.addStretch(1)
    hlay.addWidget(goodfontgroupswitch)
    self.fontstyleexpander.setHeaderWidget(header)

    goodfontgroupswitch.currentIndexChanged.connect(
        lambda idx: createinternalfontsettings(
            self, self.fontstyleexpander, group, static_data["textrender"][group][idx]
        )
    )
    # addItems 会触发 index 0 的信号——若不屏蔽，会把保存的样式覆写成
    # 序号 0 的样式（普通字体），且保存序号为 0 时 setCurrentIndex 不发
    # 信号导致子项不刷新。屏蔽后按保存值显式构建一次，行为确定。
    goodfontgroupswitch.blockSignals(True)
    goodfontgroupswitch.addItems(
        [
            globalconfig["rendertext"][group][x]["name"]
            for x in static_data["textrender"][group]
        ]
    )
    saved_idx = static_data["textrender"][group].index(
        globalconfig["rendertext_using_internal"][group]
    )
    goodfontgroupswitch.setCurrentIndex(saved_idx)
    goodfontgroupswitch.blockSignals(False)
    createinternalfontsettings(
        self, self.fontstyleexpander, group, static_data["textrender"][group][saved_idx]
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


def __textbackexpander(self):
    """文字区域背景折叠卡：头部 = 标题 + 开关，内容 = 各设置为子项
    （同 自动录音 折叠卡：每项一行 addContentWidget）。"""
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
    exp.addContentWidget(
        getboxwidget(
            [
                "颜色",
                1,
                ColorButton(
                    self,
                    ui_settings,
                    "text_area_background_color",
                    callback=gobject.base.translation_ui.translate_text.setTextAreaBackStyle,
                    default="pink",
                ),
            ]
        )
    )
    exp.addContentWidget(
        getboxwidget(
            [
                "不透明度",
                1,
                getspinbox(
                    0,
                    100,
                    ui_settings,
                    "text_area_background_alpha",
                    callback=gobject.base.translation_ui.translate_text.setTextAreaBackStyle,
                    default=85,
                ),
            ]
        )
    )
    for text, key in (
        ("圆角", "text_area_background_r"),
        ("延展宽度", "text_area_background_w"),
        ("延展高度", "text_area_background_h"),
    ):
        exp.addContentWidget(
            getboxwidget(
                [
                    text,
                    1,
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
                ]
            )
        )
    return exp


def __engineexpander(self):
    """显示引擎折叠卡：头部 = 标题 + 引擎下拉；内容（webview 的
    附加HTML等）由 resetgroudswitchcallback 建为子项。注意字体样式卡
    需先于本卡创建——引擎下拉初值变化触发的回调会重建两张卡。"""
    exp = ExExpander()
    self.engineexpander = exp
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
    resetgroudswitchcallback(self, globalconfig["rendertext_using"])
    return exp


def __fontstyleexpander(self):
    """字体样式折叠卡（从显示引擎中抽出）：头部（标题+样式组下拉）随
    引擎、内容（所选样式参数）随样式由 createinternalfontsettings
    重建为子项；无参数样式（普通字体）退化为普通卡。"""
    exp = ExExpander()
    self.fontstyleexpander = exp
    return exp


def xianshigrid_style(self):
    # 原文/译文：有标题分组卡（最原始形态），显示开关在字体前，
    # 间距行为隐藏行（齿轮展开）
    yuanwen = dict(
        title="原文",
        type="grid",
        hiderows=[1],
        name="yuanwenobject",
        parent=self,
        grid=(
            [
                getsmalllabel("显示"),
                __xianshi,
                "",
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
    yiwen = dict(
        title="译文",
        type="grid",
        hiderows=[1],
        name="yiwenobject",
        parent=self,
        grid=(
            [
                getsmalllabel("显示"),
                _showhidefy,
                "",
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
                lambda: _translate_color_button(self),
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
        [yuanwen],
        [yiwen],
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
    ]
    # 字体样式卡需先建（引擎下拉初值变化触发的回调会写它），放置顺序在后
    textbackexp = __textbackexpander(self)
    fontexp = __fontstyleexpander(self)
    engineexp = __engineexpander(self)
    textgrid.append([(engineexp, 0)])
    textgrid.append([(fontexp, 0)])
    # 文字区域背景 倒数第四
    textgrid.append([(textbackexp, 0)])
    # 显示顺序 倒数第三、固定翻译显示顺序 倒数第二
    textgrid.append(
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
        ]
    )
    textgrid.append(
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
        ]
    )
    # 次要行为开关放最下面
    textgrid.append(
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
        ]
    )
    return textgrid


def _current_translate_color():
    """当前显示顺序里第一个启用的译器颜色（与渲染端 TranslateColor
    的取值口径一致）。"""

    for uid in globalconfig["fix_translate_rank_rank"]:
        if (
            uid in globalconfig["fanyi"]
            and globalconfig["fanyi"][uid].get("use")
            and translate_exits(uid)
        ):
            return globalconfig["fanyi"][uid].get("color", "#ff0000")
    return "#ff0000"


def _translate_color_button(parent):
    """译文颜色的指示按钮：外观同 ColorPickerButton（色块+箭头），
    色块显示当前生效译器的颜色；不带取色功能，点击跳转翻译设置
    （switchtotspage）。"""

    btn = ColorPickerButton()
    btn.setSelectedColor(QColor(_current_translate_color()))
    act = QAction(btn)
    act.triggered.connect(gobject.base.switchtotspage.emit)
    btn.setDefaultAction(act)
    btn.setToolTip(_TR("颜色"))
    return btn
