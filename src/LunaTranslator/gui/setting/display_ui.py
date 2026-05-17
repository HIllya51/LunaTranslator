from qtsymbols import *
import functools, importlib
from traceback import print_exc
import gobject
from myutils.config import globalconfig, static_data
from myutils.utils import nowisdark, getimagefilefilter
from gui.flowsearchword import createsomecontrols
from gui.qevent import DarkLightSettingChangedEvent
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getcolorbutton,
    getIconButton,
    FocusFontCombo,
    D_getsimpleswitch,
    D_getIconButton,
    getsmalllabel,
    getboxlayout,
    DarkLightAutoResetIconHelper,
    getsimpleswitch,
    getsimplepatheditor,
)
from myutils.wrapper import Singleton
import qtawesome
from gui.dynalang import LDialog, LFormLayout


def changeHorizontal_pic(
    horizontal_slider_tool: QSlider, horizontal_slider_tool_label: QLabel
):

    globalconfig["transparent_pic"] = horizontal_slider_tool.value()
    horizontal_slider_tool_label.setText(
        "{}%".format(globalconfig.get("transparent_pic", 0))
    )
    gobject.base.translation_ui.translate_text.setbackgroudimageandopt()


def createhorizontal_slider_pic():

    horizontal_slider = QSlider()
    horizontal_slider.setMaximum(100)
    horizontal_slider.setMinimum(0)
    horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    horizontal_slider.setValue(globalconfig.get("transparent_pic", 0))

    horizontal_slider_label = QLabel()
    horizontal_slider.valueChanged.connect(
        functools.partial(
            changeHorizontal_pic, horizontal_slider, horizontal_slider_label
        )
    )
    horizontal_slider_label.setText(
        "{}%".format(globalconfig.get("transparent_pic", 0))
    )

    gobject.base.backtransparentstatus_2.connect(
        lambda x: (
            horizontal_slider.setEnabled(x),
            horizontal_slider_label.setEnabled(x),
        )
    )

    return getboxlayout([horizontal_slider, horizontal_slider_label])


def changeHorizontal(
    horizontal_slider_tool: QSlider, horizontal_slider_tool_label: QLabel
):

    globalconfig["transparent"] = horizontal_slider_tool.value()
    horizontal_slider_tool_label.setText("{}%".format(globalconfig["transparent"]))
    gobject.base.translation_ui.set_color_transparency()


def createhorizontal_slider():

    horizontal_slider = QSlider()
    horizontal_slider.setMaximum(100)
    horizontal_slider.setMinimum(1)
    horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    horizontal_slider.setValue(globalconfig.get("transparent", 10))

    horizontal_slider_label = QLabel()
    horizontal_slider.valueChanged.connect(
        functools.partial(changeHorizontal, horizontal_slider, horizontal_slider_label)
    )
    horizontal_slider_label.setText("{}%".format(globalconfig.get("transparent", 10)))

    gobject.base.backtransparentstatus.connect(
        lambda x: (
            horizontal_slider.setEnabled(x),
            horizontal_slider_label.setEnabled(x),
        )
    )

    return getboxlayout([horizontal_slider, horizontal_slider_label])


def changeHorizontal_tool(
    horizontal_slider_tool: QSlider, horizontal_slider_tool_label: QLabel
):

    globalconfig["transparent_tool"] = horizontal_slider_tool.value()
    horizontal_slider_tool_label.setText(
        "{}%".format(globalconfig.get("transparent_tool", 50))
    )
    #
    gobject.base.translation_ui.enterfunction()
    gobject.base.translation_ui.set_color_transparency()


def toolcolorchange():
    gobject.base.translation_ui.refreshtooliconsignal.emit()
    gobject.base.translation_ui.enterfunction()
    gobject.base.translation_ui.setbuttonsizeX()
    gobject.base.translation_ui.set_color_transparency()


def createhorizontal_slider_tool():

    horizontal_slider_tool = QSlider()
    horizontal_slider_tool.setMaximum(100)
    horizontal_slider_tool.setMinimum(1)
    horizontal_slider_tool.setOrientation(Qt.Orientation.Horizontal)
    horizontal_slider_tool.setValue(0)
    horizontal_slider_tool.setValue(globalconfig.get("transparent_tool", 50))

    horizontal_slider_tool_label = QLabel()
    horizontal_slider_tool.valueChanged.connect(
        functools.partial(
            changeHorizontal_tool, horizontal_slider_tool, horizontal_slider_tool_label
        )
    )
    horizontal_slider_tool_label.setText(
        "{}%".format(globalconfig.get("transparent_tool", 50))
    )
    return getboxlayout([horizontal_slider_tool, horizontal_slider_tool_label])


def createfontcombo():

    sfont_comboBox = FocusFontCombo()

    def callback(x):
        globalconfig.__setitem__("settingfonttype", x)
        gobject.base.setcommonstylesheet()

    sfont_comboBox.setCurrentFont(QFont(globalconfig["settingfonttype"]))
    sfont_comboBox.currentTextChanged.connect(callback)
    return sfont_comboBox


def getget_setting_window():
    try:
        name = globalconfig["theme3"]
        _fn = None
        for n in static_data["themes"]:
            if n["name"] == name:
                _fn = n["file"].get("setting")
                break

        if not _fn:
            return None
        try:
            return importlib.import_module(
                "files.LunaTranslator_qss." + _fn[:-3].replace("/", ".")
            ).get_setting_window
        except:
            return None
    except:
        print_exc()
        return None


def opensettingwindow(self):
    get_setting_window = getget_setting_window()
    try:
        get_setting_window(self, gobject.base.setcommonstylesheet, nowisdark())
    except:
        print_exc()


def createbtnthemelight(self):
    self.btnthemelight = getIconButton(functools.partial(opensettingwindow, self))
    lightsetting = getget_setting_window()
    if not bool(lightsetting):
        self.btnthemelight.hide()
    return self.btnthemelight


def checkthemesettingvisandapply(self, _):
    lightsetting = getget_setting_window()
    if not bool(lightsetting):
        self.btnthemelight.hide()
    gobject.base.setcommonstylesheet()


def __rs():
    spin, lay = createsomecontrols(
        gobject.base.translation_ui.set_color_transparency,
        gobject.base.translation_ui.seteffect,
        "yuanjiao_r",
        "yuanjiao_sys",
        False,
        "WindowEffect",
        "WindowEffect_shadow",
        True,
    )
    return getboxlayout(
        [
            "窗口特效",
            lay,
            "",
            "圆角",
            spin,
            "",
            getsmalllabel("任务栏中显示"),
            D_getsimpleswitch(
                globalconfig,
                "showintab",
                callback=lambda _: gobject.base.setshowintab(),
            ),
        ]
    )


def switch_darklight():
    darklight = globalconfig["darklight2"]
    for widget in QApplication.allWidgets():
        QApplication.postEvent(widget, DarkLightSettingChangedEvent(darklight))


def uisetting(self):
    windoweffects = [
        getsmalllabel("窗口特效"),
        D_getsimplecombobox(
            [
                "Solid",
                "Acrylic",
                "Mica",
                "MicaAlt",
            ],
            globalconfig,
            "WindowBackdrop",
            callback=lambda _: gobject.base.setcommonstylesheet(),
            static=True,
            default=3,
        ),
        "",
        getsmalllabel("强制直角"),
        D_getsimpleswitch(
            globalconfig,
            "force_rect",
            callback=lambda _: gobject.base.cornerornot(),
        ),
        "",
        getsmalllabel("任务栏中显示"),
        D_getsimpleswitch(
            globalconfig,
            "showintab_sub",
            callback=lambda _: gobject.base.setshowintab(),
        ),
    ]
    if not gobject.sys_ge_win_11:
        list(windoweffects.append(("", windoweffects.pop(3))[0]) for _ in range(3))
    __ = [
        [
            dict(
                title="主界面",
                type="grid",
                grid=[
                    [
                        dict(
                            type="grid",
                            grid=([__rs],),
                        )
                    ],
                    [
                        dict(
                            type="grid",
                            grid=(
                                [
                                    "游戏窗口移动时同步移动",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "movefollow",
                                    ),
                                    "",
                                    "自动隐藏",
                                    D_getsimpleswitch(
                                        globalconfig, "autodisappear", default=False
                                    ),
                                    lambda: createdynamicswitch(self),
                                    getboxlayout(
                                        [lambda: createdynamicdelay(self), "(s)"]
                                    ),
                                ],
                                [
                                    "游戏失去焦点时取消置顶",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "focusnotop",
                                    ),
                                    "",
                                    "自动调整高度",
                                    D_getsimpleswitch(
                                        globalconfig, "adaptive_height", default=True
                                    ),
                                    D_getsimplecombobox(
                                        ["向上", "向下"],
                                        globalconfig,
                                        "top_align",
                                        default=0,
                                    ),
                                    getboxlayout(
                                        [
                                            "最小高度",
                                            D_getspinbox(
                                                0, 9999, globalconfig, "min_auto_height"
                                            ),
                                            "px",
                                        ]
                                    ),
                                ],
                            ),
                        ),
                    ],
                ],
            )
        ],
        [
            dict(
                type="grid",
                title="其他界面",
                grid=(
                    [
                        dict(
                            type="grid",
                            grid=[
                                [
                                    getsmalllabel("字体"),
                                    createfontcombo,
                                    "",
                                    getsmalllabel("大小"),
                                    D_getspinbox(
                                        5,
                                        100,
                                        globalconfig,
                                        "settingfontsize",
                                        double=True,
                                        callback=lambda _: gobject.base.setcommonstylesheet(),
                                    ),
                                    "",
                                    getsmalllabel("加粗"),
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "settingfontbold",
                                        callback=lambda _: gobject.base.setcommonstylesheet(),
                                    ),
                                ]
                            ],
                        )
                    ],
                    [
                        dict(
                            type="grid",
                            grid=[windoweffects],
                        )
                    ],
                    [
                        dict(
                            grid=[
                                [
                                    "明暗",
                                    D_getsimplecombobox(
                                        ["跟随系统", "明亮", "黑暗"],
                                        globalconfig,
                                        "darklight2",
                                        lambda _: (
                                            gobject.base.setcommonstylesheet(),
                                            switch_darklight(),
                                        ),
                                    ),
                                ],
                                [
                                    "主题",
                                    getboxlayout(
                                        [
                                            D_getsimplecombobox(
                                                ["默认"] + themelist(),
                                                globalconfig,
                                                "theme3",
                                                functools.partial(
                                                    checkthemesettingvisandapply, self
                                                ),
                                                internal=["default"] + themelist(),
                                            ),
                                            functools.partial(
                                                createbtnthemelight, self
                                            ),
                                        ],
                                    ),
                                ],
                            ],
                        )
                    ],
                ),
            ),
        ],
    ]

    return mainuisetting(self) + __


def createdynamicswitch(self):
    def __(x):
        self.disappear_delay.setMinimum([1, 0][x])
        globalconfig["disappear_delay"] = max(
            globalconfig["disappear_delay"], [1, 0][x]
        )

    return D_getsimplecombobox(
        ["窗口", "文本"],
        globalconfig,
        "autodisappear_which",
        callback=__,
        default=0,
    )()


def createdynamicdelay(self):
    self.disappear_delay = D_getspinbox(
        [1, 0][globalconfig.get("autodisappear_which", 0)],
        100,
        globalconfig,
        "disappear_delay",
    )()
    return self.disappear_delay


@Singleton
class picselector(LDialog, DarkLightAutoResetIconHelper):
    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("背景图片")
        self.setWindowIcon(qtawesome.icon("fa.picture-o"))
        self.resize(QSize(600, 10))
        form = LFormLayout(self)
        form.addRow(
            "图片",
            getsimplepatheditor(
                globalconfig.get(
                    "backgroundpic", "https://image.lunatranslator.org/luna.jpg"
                ),
                False,
                False,
                filter1=getimagefilefilter(),
                callback=lambda _: (
                    globalconfig.__setitem__("backgroundpic", _),
                    gobject.base.translation_ui.translate_text.setbackgroudimageandopt(),
                ),
                clearable=False,
                icons=("fa.folder-open",),
                editable=True,
            ),
        )
        self.show()


def mainuisetting(self):

    return [
        [
            dict(
                title="工具栏",
                type="grid",
                grid=[
                    [
                        "背景颜色",
                        D_getcolorbutton(
                            self,
                            globalconfig,
                            "backcolor_tool",
                            callback=lambda _: toolcolorchange(),
                        ),
                        "",
                        "不透明度",
                        createhorizontal_slider_tool,
                    ]
                ],
            ),
        ],
        [
            dict(
                title="文本区",
                type="grid",
                grid=(
                    [
                        "背景颜色",
                        D_getcolorbutton(
                            self,
                            globalconfig,
                            "backcolor",
                            callback=lambda _: gobject.base.translation_ui.set_color_transparency(),
                        ),
                        "",
                        "不透明度",
                        createhorizontal_slider,
                    ],
                    [
                        "背景图片",
                        D_getIconButton(
                            icon="fa.picture-o",
                            tips="背景图片",
                            callback=lambda: picselector(self),
                        ),
                        "",
                        "不透明度",
                        createhorizontal_slider_pic,
                    ],
                ),
            ),
        ],
    ]


def themelist():
    return [_["name"] for _ in static_data["themes"]]
