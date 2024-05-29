import functools
from qtsymbols import *
from gui.inputdialog import multicolorset
from myutils.config import globalconfig, _TR, _TRL, magpie_config, static_data
from myutils.wrapper import Singleton
import qtawesome, gobject, json
from gui.inputdialog import getsomepath1
from gui.usefulwidget import (
    getsimplecombobox,
    makegrid,
    getspinbox,
    tabadd_lazy,
    makescroll,
    makevbox,
    getcolorbutton,
    makesubtab_lazy,
    getsimpleswitch,
    selectcolor,
)


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    self.show_hira_switch.setEnabled(x)
    self.show_fenciswitch.setEnabled(x)


def setTabThree_direct(self):
    self.fontSize_spinBox = getspinbox(
        1, 100, globalconfig, "fontsize", double=True, step=0.1
    )
    self.fontbigsmallsignal.connect(
        lambda t: self.fontSize_spinBox.setValue(
            self.fontSize_spinBox.value() + 0.5 * t
        )
    )
    self.show_original_switch = getsimpleswitch(
        globalconfig, "isshowrawtext", callback=lambda x: __changeuibuttonstate(self, x)
    )
    self.show_hira_switch = getsimpleswitch(
        globalconfig, "isshowhira", enable=globalconfig["isshowrawtext"]
    )
    self.show_fenciswitch = getsimpleswitch(
        globalconfig, "show_fenci", enable=globalconfig["isshowrawtext"]
    )


def setTabThree(self):

    tabadd_lazy(self.tab_widget, ("显示设置"), lambda: setTabThree_lazy(self))


def createbuttonwidget(self):
    # return table
    grids = [["显示", "", "", "对齐", "图标", "图标2", "说明"]]
    sortlist = globalconfig["toolbutton"]["rank2"]
    savelist = []
    savelay = []

    def doadjust():
        gobject.baseobject.translation_ui.enterfunction(delay=3)
        gobject.baseobject.translation_ui.adjustbuttons()

    def changerank(item, up):

        idx = sortlist.index(item)
        idx2 = idx + (-1 if up else 1)
        if idx2 < 0 or idx2 >= len(sortlist):
            return
        headoffset = 1
        idx2 = idx + (-1 if up else 1)
        sortlist[idx], sortlist[idx2] = sortlist[idx2], sortlist[idx]
        for i, ww in enumerate(savelist[idx + headoffset]):

            w1 = savelay[0].indexOf(ww)
            w2 = savelay[0].indexOf(savelist[idx2 + headoffset][i])
            p1 = savelay[0].getItemPosition(w1)
            p2 = savelay[0].getItemPosition(w2)
            savelay[0].removeWidget(ww)
            savelay[0].removeWidget(savelist[idx2 + headoffset][i])

            savelay[0].addWidget(savelist[idx2 + headoffset][i], *p1)
            savelay[0].addWidget(ww, *p2)
        savelist[idx + headoffset], savelist[idx2 + headoffset] = (
            savelist[idx2 + headoffset],
            savelist[idx + headoffset],
        )
        doadjust()

    for i, k in enumerate(sortlist):

        button_up = getcolorbutton(
            globalconfig,
            "",
            callback=functools.partial(changerank, k, True),
            icon="fa.arrow-up",
            constcolor="#FF69B4",
        )
        button_down = getcolorbutton(
            globalconfig,
            "",
            callback=functools.partial(changerank, k, False),
            icon="fa.arrow-down",
            constcolor="#FF69B4",
        )

        l = [
            getsimpleswitch(
                globalconfig["toolbutton"]["buttons"][k],
                "use",
                callback=lambda _: doadjust(),
            ),
            button_up,
            button_down,
            getsimplecombobox(
                _TRL(["居左", "居右", "居中"]),
                globalconfig["toolbutton"]["buttons"][k],
                "align",
                callback=lambda _: doadjust(),
                fixedsize=True,
            ),
            getcolorbutton(
                "",
                "",
                functools.partial(
                    dialog_selecticon,
                    self,
                    globalconfig["toolbutton"]["buttons"][k],
                    "icon",
                ),
                qicon=qtawesome.icon(
                    globalconfig["toolbutton"]["buttons"][k]["icon"],
                    color=globalconfig["buttoncolor"],
                ),
            ),
        ]
        if "icon2" in globalconfig["toolbutton"]["buttons"][k]:
            l.append(
                getcolorbutton(
                    "",
                    "",
                    functools.partial(
                        dialog_selecticon,
                        self,
                        globalconfig["toolbutton"]["buttons"][k],
                        "icon2",
                    ),
                    qicon=qtawesome.icon(
                        globalconfig["toolbutton"]["buttons"][k]["icon2"],
                        color=globalconfig["buttoncolor"],
                    ),
                ),
            )
        else:
            l.append("")
        if "belong" in globalconfig["toolbutton"]["buttons"][k]:
            belong = (
                "_"
                + "仅"
                + "_"
                + " ".join(globalconfig["toolbutton"]["buttons"][k]["belong"])
            )
        else:
            belong = ""
        l.append(globalconfig["toolbutton"]["buttons"][k]["tip"] + belong)
        grids.append(l)
    return makescroll(makegrid(grids, True, savelist, savelay))


@Singleton
class dialog_selecticon(QDialog):
    def __init__(self, parent, dict, key, _nouse_for_click_arg) -> None:

        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.dict = dict
        self.key = key
        self.setWindowTitle(_TR("选择图标"))
        with open(
            "./files/fonts/fontawesome4.7-webfont-charmap.json", "r", encoding="utf8"
        ) as ff:
            js = json.load(ff)

        layout = QGridLayout()
        self.setLayout(layout)
        for i, name in enumerate(js):
            layout.addWidget(
                getcolorbutton(
                    "",
                    "",
                    functools.partial(self.selectcallback, "fa." + name),
                    qicon=qtawesome.icon(
                        "fa." + name, color=globalconfig["buttoncolor"]
                    ),
                ),
                i // 30,
                i % 30,
            )
        self.show()

    def selectcallback(self, _):
        print(_)
        self.dict[self.key] = _
        self.close()


def setTabThree_lazy(self):

    self.horizontal_slider = QSlider()
    self.horizontal_slider.setMaximum(100)
    self.horizontal_slider.setMinimum(1)
    self.horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    self.horizontal_slider.setValue(0)
    self.horizontal_slider.setValue(globalconfig["transparent"])
    self.horizontal_slider.valueChanged.connect(
        functools.partial(changeHorizontal, self)
    )
    self.horizontal_slider_label = QLabel()
    self.horizontal_slider_label.setText("{}%".format(globalconfig["transparent"]))

    self.horizontal_slider_tool = QSlider()
    self.horizontal_slider_tool.setMaximum(100)
    self.horizontal_slider_tool.setMinimum(1)
    self.horizontal_slider_tool.setOrientation(Qt.Orientation.Horizontal)
    self.horizontal_slider_tool.setValue(0)
    self.horizontal_slider_tool.setValue(globalconfig["transparent_tool"])
    self.horizontal_slider_tool.valueChanged.connect(
        functools.partial(changeHorizontal_tool, self)
    )
    self.horizontal_slider_tool_label = QLabel()
    self.horizontal_slider_tool_label.setText(
        "{}%".format(globalconfig["transparent_tool"])
    )

    self.font_comboBox = QFontComboBox()
    self.font_comboBox.currentTextChanged.connect(
        lambda x: globalconfig.__setitem__("fonttype", x)
    )
    self.font_comboBox.setCurrentFont(QFont(globalconfig["fonttype"]))
    self.font_comboBox2 = QFontComboBox()
    self.font_comboBox2.currentTextChanged.connect(
        lambda x: globalconfig.__setitem__("fonttype2", x)
    )
    self.font_comboBox2.setCurrentFont(QFont(globalconfig["fonttype2"]))

    self.sfont_comboBox = QFontComboBox()

    def callback(x):
        globalconfig.__setitem__("settingfonttype", x)
        gobject.baseobject.setcommonstylesheet()

    self.sfont_comboBox.currentTextChanged.connect(callback)
    self.sfont_comboBox.setCurrentFont(QFont(globalconfig["settingfonttype"]))

    textgrid = [
        [("原文字体", 3), (self.font_comboBox, 6), ("", 5)],
        [
            ("译文字体", 3),
            (self.font_comboBox2, 6),
        ],
        [
            ("字体大小", 3),
            (self.fontSize_spinBox, 3),
            "",
            ("额外的行间距", 3),
            (getspinbox(-100, 100, globalconfig, "extra_space"), 3),
        ],
        [
            ("居中显示", 5),
            getsimpleswitch(globalconfig, "showatcenter"),
            "",
            ("加粗字体", 5),
            getsimpleswitch(globalconfig, "showbold"),
        ],
        [
            "",
        ],
        [
            ("字体样式", 3),
            (
                getsimplecombobox(
                    _TRL(
                        [
                            "普通字体",
                            "空心字体",
                            "描边字体",
                            "描边字体_2",
                            "描边字体_2_投影",
                            "发光字体",
                        ]
                    ),
                    globalconfig,
                    "zitiyangshi2",
                ),
                6,
            ),
        ],
        [
            ("特殊字体样式填充颜色", 5),
            getcolorbutton(
                globalconfig,
                "miaobiancolor",
                transparent=False,
                callback=lambda: selectcolor(
                    self, globalconfig, "miaobiancolor", self.miaobian_color_button
                ),
                name="miaobian_color_button",
                parent=self,
            ),
        ],
        [
            ("空心线宽", 3),
            (
                getspinbox(
                    0.1, 100, globalconfig, "miaobianwidth", double=True, step=0.1
                ),
                3,
            ),
            "",
            ("描边宽度", 3),
            (
                getspinbox(
                    0.1, 100, globalconfig, "miaobianwidth2", double=True, step=0.1
                ),
                3,
            ),
        ],
        [
            ("发光亮度", 3),
            (getspinbox(1, 100, globalconfig, "shadowforce"), 3),
            "",
            ("投影距离", 3),
            (
                getspinbox(
                    0.1, 100, globalconfig, "traceoffset", double=True, step=0.1
                ),
                3,
            ),
        ],
        [],
        [
            ("显示原文", 5),
            self.show_original_switch,
            "",
            ("显示翻译", 5),
            (getsimpleswitch(globalconfig, "showfanyi"), 1),
        ],
        [
            ("原文颜色", 5),
            getcolorbutton(
                globalconfig,
                "rawtextcolor",
                callback=lambda: selectcolor(
                    self, globalconfig, "rawtextcolor", self.original_color_button
                ),
                name="original_color_button",
                parent=self,
            ),
            "",
            ("显示翻译器名称", 5),
            (getsimpleswitch(globalconfig, "showfanyisource"), 1),
        ],
        [
            ("最长显示字数", 3),
            (getspinbox(0, 1000000, globalconfig, "maxoriginlength"), 3),
        ],
        [],
        [
            ("显示日语注音", 5),
            self.show_hira_switch,
        ],
        [
            ("注音颜色", 5),
            getcolorbutton(
                globalconfig,
                "jiamingcolor",
                callback=lambda: selectcolor(
                    self, globalconfig, "jiamingcolor", self.jiamingcolor_b
                ),
                name="jiamingcolor_b",
                parent=self,
            ),
            "",
            ("注音字体缩放", 3),
            (
                getspinbox(
                    0.05, 1, globalconfig, "kanarate", double=True, step=0.05, dec=2
                ),
                3,
            ),
        ],
        [
            ("语法加亮", 5),
            self.show_fenciswitch,
            "",
            ("词性颜色(需要Mecab)", 5),
            getcolorbutton(
                globalconfig,
                "",
                callback=lambda: multicolorset(self),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        ],
        [],
        [
            ("收到翻译结果时才刷新", 5),
            getsimpleswitch(globalconfig, "refresh_on_get_trans"),
        ],
    ]

    def themelist(t):
        return [_["name"] for _ in static_data["themes"][t]]

    xingweigrid = [
        [("游戏最小化时窗口隐藏", 6), (getsimpleswitch(globalconfig, "minifollow"), 1)],
        [
            ("游戏失去焦点时窗口隐藏", 6),
            (getsimpleswitch(globalconfig, "focusfollow"), 1),
        ],
        [
            ("游戏失去焦点时取消置顶", 6),
            (getsimpleswitch(globalconfig, "focusnotop"), 1),
        ],
        [
            ("游戏窗口移动时同步移动", 6),
            (getsimpleswitch(globalconfig, "movefollow"), 1),
        ],
        [
            ("固定窗口尺寸", 6),
            getsimpleswitch(globalconfig, "fixedheight"),
        ],
        [
            ("自动隐藏窗口", 6),
            (getsimpleswitch(globalconfig, "autodisappear"), 1),
            "",
            ("隐藏延迟(s)", 3),
            (getspinbox(1, 100, globalconfig, "disappear_delay"), 2),
        ],
        [
            ("任务栏中显示_翻译窗口", 6),
            getsimpleswitch(
                globalconfig,
                "showintab",
                callback=lambda _: gobject.baseobject.setshowintab(),
            ),
        ],
        [
            ("任务栏中显示_其他", 6),
            getsimpleswitch(
                globalconfig,
                "showintab_sub",
                callback=lambda _: gobject.baseobject.setshowintab(),
            ),
        ],
        [
            ("选择文本窗口中文本框只读", 6),
            getsimpleswitch(
                globalconfig,
                "textboxreadonly",
                callback=lambda x: gobject.baseobject.hookselectdialog.textOutput.setReadOnly(
                    x
                ),
            ),
        ],
        [
            ("可选取模式", 6),
            getsimpleswitch(
                globalconfig,
                "selectable",
                callback=lambda x: gobject.baseobject.translation_ui.translate_text.setselectable(),
            ),
        ],
    ]
    uigrid = [
        [("设置界面字体", 4), (self.sfont_comboBox, 5)],
        [
            ("字体大小", 4),
            (
                getspinbox(
                    1,
                    100,
                    globalconfig,
                    "settingfontsize",
                    callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                ),
                2,
            ),
        ],
        [
            ("不透明度_翻译窗口", 4),
            (self.horizontal_slider, 8),
            (self.horizontal_slider_label, 2),
        ],
        [
            ("不透明度_工具栏", 4),
            (self.horizontal_slider_tool, 8),
            (self.horizontal_slider_tool_label, 2),
        ],
        [
            ("背景颜色_翻译窗口", 4),
            getcolorbutton(
                globalconfig,
                "backcolor",
                callback=lambda: selectcolor(
                    self,
                    globalconfig,
                    "backcolor",
                    self.back_color_button,
                    callback=gobject.baseobject.translation_ui.set_color_transparency,
                ),
                name="back_color_button",
                parent=self,
            ),
            "",
            "",
            ("背景颜色_工具栏", 4),
            getcolorbutton(
                globalconfig,
                "backcolor_tool",
                callback=lambda: selectcolor(
                    self,
                    globalconfig,
                    "backcolor_tool",
                    self.back_color_button_tool,
                    callback=gobject.baseobject.translation_ui.set_color_transparency,
                ),
                name="back_color_button_tool",
                parent=self,
            ),
        ],
        [
            ("工具按钮颜色", 4),
            getcolorbutton(
                globalconfig,
                "buttoncolor",
                callback=lambda: selectcolor(
                    self,
                    globalconfig,
                    "buttoncolor",
                    self.buttoncolorbutton,
                    callback=lambda: gobject.baseobject.translation_ui.refreshtooliconsignal.emit(),
                ),
                name="buttoncolorbutton",
                parent=self,
            ),
            "",
            "",
            ("工具按钮大小", 4),
            (
                getspinbox(
                    5,
                    100,
                    globalconfig,
                    "buttonsize",
                    callback=lambda _: gobject.baseobject.translation_ui.refreshtooliconsignal.emit(),
                ),
                2,
            ),
        ],
        [
            ("圆角_半径", 4),
            (
                getspinbox(
                    0,
                    100,
                    globalconfig,
                    "yuanjiao_r",
                    callback=lambda _: gobject.baseobject.translation_ui.set_color_transparency(),
                ),
                2,
            ),
            "",
            ("圆角_合并", 4),
            getsimpleswitch(
                globalconfig,
                "yuanjiao_merge",
                callback=lambda _: gobject.baseobject.translation_ui.set_color_transparency(),
            ),
        ],
        [],
        [
            ("明暗", 4),
            (
                getsimplecombobox(
                    _TRL(["明亮", "黑暗", "跟随系统"]),
                    globalconfig,
                    "darklight",
                    callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                ),
                5,
            ),
        ],
        [
            ("明亮主题", 4),
            (
                getsimplecombobox(
                    _TRL(["默认"]) + themelist("light"),
                    globalconfig,
                    "lighttheme",
                    callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                ),
                5,
            ),
        ],
        [
            ("黑暗主题", 4),
            (
                getsimplecombobox(
                    themelist("dark"),
                    globalconfig,
                    "darktheme",
                    callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                ),
                5,
            ),
        ],
        [],
        [
            ("窗口特效_翻译窗口", 4),
            (
                getsimplecombobox(
                    ["Disable", "Acrylic", "Aero"],
                    globalconfig,
                    "WindowEffect",
                    callback=lambda _: [
                        gobject.baseobject.translation_ui.set_color_transparency(),
                        gobject.baseobject.translation_ui.seteffect(),
                    ],
                ),
                5,
            ),
        ],
        [
            ("窗口特效_其他", 4),
            (
                getsimplecombobox(
                    ["Solid", "Acrylic", "Mica", "MicaAlt"],
                    globalconfig,
                    "WindowBackdrop",
                    callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                ),
                5,
            ),
        ],
    ]

    innermagpie = [
        [("常规", 4)],
        [
            ("", 1),
            ("缩放模式", 4),
            (
                getsimplecombobox(
                    [_["name"] for _ in magpie_config["scalingModes"]],
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "scalingMode",
                ),
                6,
            ),
            "",
        ],
        [
            ("", 1),
            ("捕获模式", 4),
            (
                getsimplecombobox(
                    [
                        "Graphics Capture",
                        "Desktop Duplication",
                        "GDI",
                        "DwmSharedSurface",
                    ],
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "captureMethod",
                ),
                6,
            ),
        ],
        [
            ("", 1),
            ("3D游戏模式", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "3DGameMode",
                )
            ),
        ],
        [("性能", 4)],
        [
            ("", 1),
            ("显示帧率", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "showFPS",
                )
            ),
        ],
        [
            ("", 1),
            ("限制帧率", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "frameRateLimiterEnabled",
                )
            ),
        ],
        [
            ("", 1),
            ("最大帧率", 4),
            (
                getspinbox(
                    0,
                    9999,
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "maxFrameRate",
                ),
                2,
            ),
        ],
        [("源窗口", 4)],
        [
            ("", 1),
            ("缩放时禁用窗口大小调整", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "disableWindowResizing",
                )
            ),
        ],
        [
            ("", 1),
            ("捕获标题栏", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "captureTitleBar",
                )
            ),
        ],
        [
            ("", 1),
            ("自定义剪裁", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "croppingEnabled",
                )
            ),
        ],
        [("光标", 4)],
        [
            ("", 1),
            ("绘制光标", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "drawCursor",
                )
            ),
        ],
        [
            ("", 1),
            ("绘制光标_缩放系数", 4),
            (
                getsimplecombobox(
                    ["0.5x", "0.75x", "无缩放", "1.25x", "1.5x", "2x", "和源窗口相同"],
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "cursorScaling",
                ),
                6,
            ),
        ],
        [
            ("", 1),
            ("绘制光标_插值算法", 4),
            (
                getsimplecombobox(
                    ["最邻近", "双线性"],
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "cursorInterpolationMode",
                ),
                6,
            ),
        ],
        [
            ("", 1),
            ("缩放时调整光标速度", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "adjustCursorSpeed",
                )
            ),
        ],
        [("高级", 4)],
        [
            ("", 1),
            ("禁用DirectFlip", 4),
            (
                getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "disableDirectFlip",
                )
            ),
        ],
        [
            ("", 1),
            ("允许缩放最大化或全屏的窗口", 4),
            (getsimpleswitch(magpie_config, "allowScalingMaximized")),
        ],
        [
            ("", 1),
            ("缩放时模拟独占全屏", 4),
            (getsimpleswitch(magpie_config, "simulateExclusiveFullscreen")),
        ],
        [
            ("", 1),
            ("内联效果参数", 4),
            (getsimpleswitch(magpie_config, "inlineParams")),
        ],
        [("开发者选项", 4)],
        [
            ("", 1),
            ("调试模式", 4),
            (
                getsimpleswitch(
                    magpie_config,
                    "debugMode",
                )
            ),
        ],
        [
            ("", 1),
            ("禁用效果缓存", 4),
            (
                getsimpleswitch(
                    magpie_config,
                    "disableEffectCache",
                )
            ),
        ],
        [
            ("", 1),
            ("禁用字体缓存", 4),
            (
                getsimpleswitch(
                    magpie_config,
                    "disableFontCache",
                )
            ),
        ],
        [
            ("", 1),
            ("解析效果时保存源代码", 4),
            (
                getsimpleswitch(
                    magpie_config,
                    "saveEffectSources",
                )
            ),
        ],
        [
            ("", 1),
            ("编译效果时将警告视为错误", 4),
            (
                getsimpleswitch(
                    magpie_config,
                    "warningsAreErrors",
                )
            ),
        ],
        [
            ("", 1),
            ("检测重复帧", 4),
            (
                getsimplecombobox(
                    ["总是检测", "动态检测", "从不检测"],
                    magpie_config,
                    "duplicateFrameDetectionMode",
                ),
                6,
            ),
        ],
        [
            ("", 1),
            ("启用动态检测统计", 4),
            (
                getsimpleswitch(
                    magpie_config,
                    "enableStatisticsForDynamicDetection",
                )
            ),
        ],
    ]
    commonfsgrid = [
        [
            ("缩放方式", 4),
            (
                getsimplecombobox(
                    static_data["scalemethods_vis"],
                    globalconfig,
                    "fullscreenmethod_4",
                ),
                6,
            ),
        ]
    ]

    losslessgrid = [
        [
            ("Magpie_路径", 4),
            (
                getcolorbutton(
                    globalconfig,
                    "",
                    callback=lambda x: getsomepath1(
                        self,
                        "Magpie_路径",
                        globalconfig,
                        "magpiepath",
                        "Magpie_路径",
                        isdir=True,
                    ),
                    icon="fa.gear",
                    constcolor="#FF69B4",
                ),
                1,
            ),
        ],
        [
            ("Hook Magpie进程使其不会退出缩放", 4),
            getsimpleswitch(globalconfig, "hookmagpie"),
        ],
    ]
    tab = makesubtab_lazy(
        ["文本设置", "界面主题", "窗口行为", "工具按钮", "窗口缩放"],
        [
            lambda: makescroll(makegrid(textgrid)),
            lambda: makescroll(makegrid(uigrid)),
            lambda: makescroll(makegrid(xingweigrid)),
            lambda: createbuttonwidget(self),
            lambda: makevbox(
                [
                    makegrid(commonfsgrid),
                    makesubtab_lazy(
                        ["Magpie", "外部缩放软件"],
                        [
                            lambda: makescroll(makegrid(innermagpie)),
                            lambda: makescroll(makegrid(losslessgrid)),
                        ],
                    ),
                ]
            ),
        ],
    )

    return tab


def changeHorizontal(self):

    globalconfig["transparent"] = self.horizontal_slider.value()
    self.horizontal_slider_label.setText("{}%".format(globalconfig["transparent"]))
    #
    gobject.baseobject.translation_ui.set_color_transparency()


def changeHorizontal_tool(self):

    globalconfig["transparent_tool"] = self.horizontal_slider_tool.value()
    self.horizontal_slider_tool_label.setText(
        "{}%".format(globalconfig["transparent_tool"])
    )
    #
    gobject.baseobject.translation_ui.set_color_transparency()
