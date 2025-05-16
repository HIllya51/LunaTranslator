from qtsymbols import *
import functools, importlib
from traceback import print_exc
import gobject
from myutils.config import globalconfig, static_data
from myutils.utils import nowisdark
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getcolorbutton,
    getIconButton,
    FocusFontCombo,
    D_getsimpleswitch,
    getsimpleswitch,
    getsmalllabel,
    getboxlayout,
)


def changeHorizontal(self):

    globalconfig["transparent"] = self.horizontal_slider.value()
    try:
        self.horizontal_slider_label.setText("{}%".format(globalconfig["transparent"]))
    except:
        pass
    #
    gobject.baseobject.translation_ui.set_color_transparency()


def __exswitch(self, ex):
    self.horizontal_slider.setMinimum(1 - ex)
    gobject.baseobject.translation_ui.set_color_transparency()


def createhorizontal_slider(self):

    self.horizontal_slider = QSlider()
    self.horizontal_slider.setMaximum(100)
    self.horizontal_slider.setMinimum(1 - globalconfig["transparent_EX"])
    self.horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    self.horizontal_slider.setValue(globalconfig["transparent"])
    self.horizontal_slider.valueChanged.connect(
        functools.partial(changeHorizontal, self)
    )
    w = QWidget()
    hb = QHBoxLayout(w)
    hb.setContentsMargins(0, 0, 0, 0)

    self.horizontal_slider_label = QLabel()
    self.horizontal_slider_label.setText("{}%".format(globalconfig["transparent"]))
    hb.addWidget(self.horizontal_slider)
    hb.addWidget(self.horizontal_slider_label)

    l = getsmalllabel("  EX")()
    hb.addWidget(l)
    sw = getsimpleswitch(
        globalconfig,
        "transparent_EX",
        callback=functools.partial(__exswitch, self),
    )

    hb.addWidget(sw)
    self.horizontal_slider.setEnabled(not globalconfig["backtransparent"])
    self.horizontal_slider_label.setEnabled(not globalconfig["backtransparent"])
    return w


def changeHorizontal_tool(self):

    globalconfig["transparent_tool"] = self.horizontal_slider_tool.value()
    try:
        self.horizontal_slider_tool_label.setText(
            "{}%".format(globalconfig["transparent_tool"])
        )
    except:
        pass
    #
    gobject.baseobject.translation_ui.enterfunction()
    gobject.baseobject.translation_ui.set_color_transparency()


def toolcolorchange():
    gobject.baseobject.translation_ui.refreshtooliconsignal.emit()
    gobject.baseobject.translation_ui.enterfunction()
    gobject.baseobject.translation_ui.setbuttonsizeX()
    gobject.baseobject.translation_ui.set_color_transparency()


def createhorizontal_slider_tool(self):

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
    return getboxlayout(
        [self.horizontal_slider_tool, self.horizontal_slider_tool_label]
    )


def createfontcombo():

    sfont_comboBox = FocusFontCombo()

    def callback(x):
        globalconfig.__setitem__("settingfonttype", x)
        gobject.baseobject.setcommonstylesheet()

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
        get_setting_window(self, gobject.baseobject.setcommonstylesheet, nowisdark())
    except:
        print_exc()


def createbtnthemelight(self):
    self.btnthemelight = getIconButton(functools.partial(opensettingwindow, self))
    return self.btnthemelight


def checkthemesettingvisandapply(self, _):
    lightsetting = getget_setting_window()
    self.btnthemelight.setVisible(bool(lightsetting))
    gobject.baseobject.setcommonstylesheet()


def uisetting(self):
    __ = [
        [
            dict(
                title="主界面",
                type="grid",
                grid=[
                    [
                        dict(
                            type="grid",
                            grid=(
                                [
                                    getsmalllabel("窗口特效"),
                                    functools.partial(createxxx, self),
                                    "",
                                    getsmalllabel("圆角_半径"),
                                    D_getspinbox(
                                        0,
                                        100,
                                        globalconfig,
                                        "yuanjiao_r",
                                        callback=lambda _: gobject.baseobject.translation_ui.set_color_transparency(),
                                    ),
                                    "",
                                    getsmalllabel("任务栏中显示"),
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "showintab",
                                        callback=lambda _: gobject.baseobject.setshowintab(),
                                    ),
                                ],
                            ),
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
                                    D_getsimpleswitch(globalconfig, "autodisappear"),
                                    lambda: createdynamicswitch(self),
                                    lambda: createdynamicdelay(self),
                                    "(s)",
                                ],
                                [
                                    "游戏失去焦点时取消置顶",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "focusnotop",
                                    ),
                                    "",
                                    "自动调整高度",
                                    D_getsimpleswitch(globalconfig, "adaptive_height"),
                                    D_getsimplecombobox(
                                        ["向上", "向下"], globalconfig, "top_align"
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
                                        step=0.1,
                                        callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                                    ),
                                    "",
                                    getsmalllabel("加粗"),
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "settingfontbold",
                                        callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                                    ),
                                ]
                            ],
                        )
                    ],
                    [
                        dict(
                            type="grid",
                            grid=[
                                [
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
                                        callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                                        static=True,
                                    ),
                                    "",
                                    getsmalllabel("强制直角"),
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "force_rect",
                                        callback=lambda _: gobject.baseobject.cornerornot(),
                                    ),
                                    "",
                                    getsmalllabel("任务栏中显示"),
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "showintab_sub",
                                        callback=lambda _: gobject.baseobject.setshowintab(),
                                    ),
                                ]
                            ],
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
                                            gobject.baseobject.setcommonstylesheet(),
                                            switch_webview2_darklight(),
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


def switch_webview2_darklight():
    for widget in QApplication.allWidgets():
        QApplication.postEvent(widget, QEvent(QEvent.Type.User + 1))


def createdynamicswitch(self):
    def __(x):
        self.disappear_delay.setMinimum([1, 0][x])
        globalconfig["disappear_delay"] = max(
            globalconfig["disappear_delay"], [1, 0][x]
        )

    return D_getsimplecombobox(
        ["窗口", "文本"], globalconfig, "autodisappear_which", callback=__
    )()


def createdynamicdelay(self):
    self.disappear_delay = D_getspinbox(
        [1, 0][globalconfig["autodisappear_which"]],
        100,
        globalconfig,
        "disappear_delay",
    )()
    return self.disappear_delay


def mainuisetting(self):

    return [
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
                            callback=gobject.baseobject.translation_ui.set_color_transparency,
                        ),
                        "",
                        "不透明度",
                        functools.partial(createhorizontal_slider, self),
                    ],
                ),
            ),
        ],
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
                            callback=toolcolorchange,
                        ),
                        "",
                        "不透明度",
                        functools.partial(createhorizontal_slider_tool, self),
                    ]
                ],
            ),
        ],
    ]


def themelist():
    return [_["name"] for _ in static_data["themes"]]


def createxxx(self):
    self.__shadowxx = QLabel("阴影")
    self.__shadowxx.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    self.__shadowxx2 = getsimpleswitch(
        globalconfig,
        "WindowEffect_shadow",
        callback=lambda _: [
            gobject.baseobject.translation_ui.set_color_transparency(),
            gobject.baseobject.translation_ui.seteffect(),
        ],
    )
    if globalconfig["WindowEffect"] == 0:
        self.__shadowxx.hide()
        self.__shadowxx2.hide()
    return getboxlayout(
        [
            D_getsimplecombobox(
                ["Disable", "Acrylic", "Aero"],
                globalconfig,
                "WindowEffect",
                callback=lambda _: [
                    gobject.baseobject.translation_ui.set_color_transparency(),
                    gobject.baseobject.translation_ui.seteffect(),
                    self.__shadowxx.setVisible(_ != 0),
                    self.__shadowxx2.setVisible(_ != 0),
                    gobject.baseobject.translation_ui.changeextendstated(),
                ],
                static=True,
            ),
            self.__shadowxx,
            self.__shadowxx2,
        ],
    )
