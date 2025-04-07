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
    selectcolor,
    FocusFontCombo,
    D_getsimpleswitch,
    getsimpleswitch,
    getboxlayout,
    makesubtab_lazy,
    makescrollgrid,
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
        [self.horizontal_slider_tool, self.horizontal_slider_tool_label],
        makewidget=True,
    )


def createfontcombo():

    sfont_comboBox = FocusFontCombo()

    def callback(x):
        globalconfig.__setitem__("settingfonttype", x)
        gobject.baseobject.setcommonstylesheet()

    sfont_comboBox.setCurrentFont(QFont(globalconfig["settingfonttype"]))
    sfont_comboBox.currentTextChanged.connect(callback)
    return sfont_comboBox


def maybesetstyle(_dark):
    if _dark == nowisdark():
        gobject.baseobject.setcommonstylesheet()


def wrapedsetstylecallback(_dark, self, func):
    try:
        func(self, functools.partial(maybesetstyle, _dark))
    except:
        print_exc()


def checkthemeissetable(self, dark: bool):
    try:
        darklight = ["light", "dark"][dark]
        name = globalconfig[darklight + "theme2"]
        _fn = None
        for n in static_data["themes"][darklight]:
            if n["name"] == name:
                _fn = n["file"]
                break

        if not _fn:
            return None

        if _fn.endswith(".py"):
            try:
                return functools.partial(
                    wrapedsetstylecallback,
                    dark,
                    self,
                    importlib.import_module(
                        "files.LunaTranslator_qss." + _fn[:-3].replace("/", ".")
                    ).get_setting_window,
                )
            except:
                return None
        elif _fn.endswith(".qss"):
            return None
    except:
        print_exc()
        return None


def checkthemesettingvisandapply_1(self, _dark):
    try:
        if _dark:

            darksetting = checkthemeissetable(self, True)
            self.darksetting = darksetting
            if not self.darksetting:
                self.btnthemedark.hide()
            else:
                self.btnthemedark.show()
                try:
                    self.btnthemedark.clicked.disconnect()
                except:
                    pass
                self.btnthemedark.clicked.connect(self.darksetting)
        else:

            lightsetting = checkthemeissetable(self, False)
            self.lightsetting = lightsetting
            if not self.lightsetting:
                self.btnthemelight.hide()
            else:
                self.btnthemelight.show()
                try:
                    self.btnthemelight.clicked.disconnect()
                except:
                    pass
                self.btnthemelight.clicked.connect(self.lightsetting)

    except:
        print_exc()


def createbtnthemelight(self):
    lightsetting = checkthemeissetable(self, False)
    self.lightsetting = lightsetting
    self.btnthemelight = getIconButton()
    try:
        if not self.lightsetting:
            self.btnthemelight.hide()
        else:
            try:
                self.btnthemelight.clicked.disconnect()
            except:
                pass
            self.btnthemelight.clicked.connect(self.lightsetting)
    except:
        pass
    return self.btnthemelight


def createbtnthemedark(self):
    darksetting = checkthemeissetable(self, True)
    self.darksetting = darksetting
    self.btnthemedark = getIconButton()
    try:
        if not self.darksetting:
            self.btnthemedark.hide()
        else:
            try:
                self.btnthemedark.clicked.disconnect()
            except:
                pass
            self.btnthemedark.clicked.connect(self.darksetting)
    except:
        pass
    return self.btnthemedark


def checkthemesettingvisandapply(self, _dark, _):
    checkthemesettingvisandapply_1(self, _dark)
    maybesetstyle(_dark)


def __changeuibuttonstate2(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()

    gobject.baseobject.translation_ui.mousetransparent_check()


def __changeuibuttonstate3(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.translation_ui.setontopthread()


def __changeuibuttonstate(self, x):
    globalconfig["locktoolsEx"] = False
    gobject.baseobject.translation_ui.refreshtoolicon()

    gobject.baseobject.translation_ui.enterfunction()


def uisetting(self, l):
    tab, do = makesubtab_lazy(
        ["主界面", "其他界面"],
        [
            lambda l: makescrollgrid(mainuisetting(self), l),
            lambda l: makescrollgrid(otheruisetting(self), l),
        ],
        delay=True,
    )
    l.addWidget(tab)
    do()


def __changeselectablestate(self, x):
    globalconfig["selectableEx"] = False
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.translation_ui.translate_text.setselectable(x)


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

    return (
        [
            dict(
                title="文本区",
                type="grid",
                grid=(
                    [
                        "背景颜色",
                        D_getcolorbutton(
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
                        "不透明度",
                        (
                            functools.partial(createhorizontal_slider, self),
                            -1,
                        ),
                    ],
                    [
                        "可选取的",
                        D_getsimpleswitch(
                            globalconfig,
                            "selectable",
                            callback=functools.partial(__changeselectablestate, self),
                            parent=self,
                            name="selectable_btn",
                        ),
                        "",
                        "圆角_半径",
                        D_getspinbox(
                            0,
                            100,
                            globalconfig,
                            "yuanjiao_r",
                            callback=lambda _: gobject.baseobject.translation_ui.set_color_transparency(),
                        ),
                    ],
                ),
            ),
        ],
        [
            dict(
                title="工具栏",
                type="grid",
                grid=(
                    [
                        "背景颜色",
                        D_getcolorbutton(
                            globalconfig,
                            "backcolor_tool",
                            callback=lambda: selectcolor(
                                self,
                                globalconfig,
                                "backcolor_tool",
                                self.back_color_button_tool,
                                callback=toolcolorchange,
                            ),
                            name="back_color_button_tool",
                            parent=self,
                        ),
                        "",
                        "不透明度",
                        (
                            functools.partial(createhorizontal_slider_tool, self),
                            -1,
                        ),
                    ],
                    [
                        "锁定工具栏",
                        D_getsimpleswitch(
                            globalconfig,
                            "locktools",
                            callback=lambda x: __changeuibuttonstate(self, x),
                            name="locktoolsbutton",
                            parent=self,
                        ),
                        "",
                        "工具按钮大小",
                        D_getspinbox(
                            5,
                            100,
                            globalconfig,
                            "buttonsize",
                            callback=lambda _: toolcolorchange(),
                        ),
                        "",
                        "工具按钮颜色",
                        getboxlayout(
                            [
                                D_getcolorbutton(
                                    globalconfig,
                                    "buttoncolor",
                                    callback=lambda: selectcolor(
                                        self,
                                        globalconfig,
                                        "buttoncolor",
                                        self.buttoncolorbutton,
                                        callback=toolcolorchange,
                                    ),
                                    name="buttoncolorbutton",
                                    parent=self,
                                ),
                                D_getcolorbutton(
                                    globalconfig,
                                    "buttoncolor_1",
                                    callback=lambda: selectcolor(
                                        self,
                                        globalconfig,
                                        "buttoncolor_1",
                                        self.buttoncolorbutton_1,
                                        callback=toolcolorchange,
                                    ),
                                    name="buttoncolorbutton_1",
                                    parent=self,
                                ),
                                D_getcolorbutton(
                                    globalconfig,
                                    "button_color_normal",
                                    callback=lambda: selectcolor(
                                        self,
                                        globalconfig,
                                        "button_color_normal",
                                        self.buttoncolorbutton_hover,
                                        callback=toolcolorchange,
                                    ),
                                    name="buttoncolorbutton_hover",
                                    parent=self,
                                ),
                                D_getcolorbutton(
                                    globalconfig,
                                    "button_color_close",
                                    callback=lambda: selectcolor(
                                        self,
                                        globalconfig,
                                        "button_color_close",
                                        self.buttoncolorbutton_hover_close,
                                        callback=toolcolorchange,
                                    ),
                                    name="buttoncolorbutton_hover_close",
                                    parent=self,
                                ),
                            ],
                            makewidget=True,
                        ),
                    ],
                ),
            ),
        ],
        [dict(grid=[["窗口特效", functools.partial(createxxx, self)]])],
        [
            dict(
                type="grid",
                grid=(
                    [
                        "窗口置顶",
                        D_getsimpleswitch(
                            globalconfig,
                            "keepontop",
                            callback=lambda x: __changeuibuttonstate3(self, x),
                            parent=self,
                            name="keepontopbutton",
                        ),
                        "",
                        "自动调整高度",
                        D_getsimpleswitch(globalconfig, "adaptive_height"),
                        D_getsimplecombobox(
                            ["向上", "向下"], globalconfig, "top_align"
                        ),
                        "",
                        "任务栏中显示",
                        D_getsimpleswitch(
                            globalconfig,
                            "showintab",
                            callback=lambda _: gobject.baseobject.setshowintab(),
                        ),
                    ],
                    [
                        "鼠标穿透窗口",
                        D_getsimpleswitch(
                            globalconfig,
                            "mousetransparent",
                            callback=lambda x: __changeuibuttonstate2(self, x),
                            parent=self,
                            name="mousetransbutton",
                        ),
                        "",
                        "自动隐藏",
                        (
                            getboxlayout(
                                [
                                    D_getsimpleswitch(globalconfig, "autodisappear"),
                                    lambda: createdynamicswitch(self),
                                    lambda: createdynamicdelay(self),
                                    "(s)"
                                ],
                                makewidget=True,
                                margin0=True,
                            ),
                            0,
                        ),
                    ],
                ),
            ),
        ],
        [
            dict(
                title="跟随游戏窗口",
                type="grid",
                grid=(
                    [
                        "游戏失去焦点时取消置顶",
                        D_getsimpleswitch(
                            globalconfig,
                            "focusnotop",
                        ),
                        "",
                        "游戏窗口移动时同步移动",
                        D_getsimpleswitch(
                            globalconfig,
                            "movefollow",
                        ),
                        "",
                    ],
                ),
            ),
        ],
    )


def otheruisetting(self):

    def themelist(t):
        return [_["name"] for _ in static_data["themes"][t]]

    return (
        [
            dict(
                type="grid",
                grid=(
                    [
                        "字体",
                        createfontcombo,
                        "",
                        "字体大小",
                        D_getspinbox(
                            5,
                            100,
                            globalconfig,
                            "settingfontsize",
                            double=True,
                            step=0.1,
                            callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                        ),
                    ],
                ),
            ),
        ],
        [
            dict(
                title="主题",
                grid=(
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
                        "明亮主题",
                        (
                            D_getsimplecombobox(
                                ["默认"] + themelist("light"),
                                globalconfig,
                                "lighttheme2",
                                functools.partial(
                                    checkthemesettingvisandapply,
                                    self,
                                    False,
                                ),
                                internal=["default"] + themelist("light"),
                            ),
                            functools.partial(createbtnthemelight, self),
                        ),
                    ],
                    [
                        "黑暗主题",
                        (
                            D_getsimplecombobox(
                                themelist("dark"),
                                globalconfig,
                                "darktheme2",
                                functools.partial(
                                    checkthemesettingvisandapply,
                                    self,
                                    True,
                                ),
                                internal=themelist("dark"),
                            ),
                            functools.partial(createbtnthemedark, self),
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
                        "窗口特效",
                        (
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
                            0,
                        ),
                    ],
                    [
                        "强制直角",
                        D_getsimpleswitch(
                            globalconfig,
                            "force_rect",
                            callback=lambda _: gobject.baseobject.cornerornot(),
                        ),
                        "",
                        "任务栏中显示",
                        D_getsimpleswitch(
                            globalconfig,
                            "showintab_sub",
                            callback=lambda _: gobject.baseobject.setshowintab(),
                        ),
                        "",
                    ],
                ),
            ),
        ],
    )


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
        makewidget=True,
        margin0=True,
    )
