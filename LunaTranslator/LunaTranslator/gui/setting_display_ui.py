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
)


def changeHorizontal(self):

    globalconfig["transparent"] = self.horizontal_slider.value()
    try:
        self.horizontal_slider_label.setText("{}%".format(globalconfig["transparent"]))
    except:
        pass
    #
    gobject.baseobject.translation_ui.set_color_transparency()


def createhorizontal_slider(self):

    self.horizontal_slider = QSlider()
    self.horizontal_slider.setMaximum(100)
    self.horizontal_slider.setMinimum(1)
    self.horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    self.horizontal_slider.setValue(0)
    self.horizontal_slider.setValue(globalconfig["transparent"])
    self.horizontal_slider.valueChanged.connect(
        functools.partial(changeHorizontal, self)
    )
    return self.horizontal_slider


def createhorizontal_slider_label(self):
    self.horizontal_slider_label = QLabel()
    self.horizontal_slider_label.setText("{}%".format(globalconfig["transparent"]))
    return self.horizontal_slider_label


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
    return self.horizontal_slider_tool


def createhorizontal_slider_tool_label(self):

    self.horizontal_slider_tool_label = QLabel()
    self.horizontal_slider_tool_label.setText(
        "{}%".format(globalconfig["transparent_tool"])
    )
    return self.horizontal_slider_tool_label


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
        idx = globalconfig[darklight + "theme"] - int(not dark)
        if idx == -1:
            return None
        _fn = static_data["themes"][darklight][idx]["file"]

        if _fn.endswith(".py"):
            try:
                return functools.partial(
                    wrapedsetstylecallback,
                    dark,
                    self,
                    importlib.import_module(
                        "files.themes." + _fn[:-3].replace("/", ".")
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
    self.btnthemelight = getIconButton(icon="fa.gear")
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
    self.btnthemedark = getIconButton(
        icon="fa.gear",
    )
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


def mainuisetting(self):

    return (
        [
            (
                dict(
                    title="文本区",
                    type="grid",
                    grid=(
                        [
                            "不透明度",
                            (
                                functools.partial(createhorizontal_slider, self),
                                0,
                            ),
                            functools.partial(createhorizontal_slider_label, self),
                        ],
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
                            "圆角_半径",
                            D_getspinbox(
                                0,
                                100,
                                globalconfig,
                                "yuanjiao_r",
                                callback=lambda _: gobject.baseobject.translation_ui.set_color_transparency(),
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
        [
            (
                dict(
                    title="工具栏",
                    type="grid",
                    grid=(
                        [
                            "不透明度",
                            (
                                functools.partial(createhorizontal_slider_tool, self),
                                0,
                            ),
                            functools.partial(
                                createhorizontal_slider_tool_label,
                                self,
                            ),
                        ],
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
                                ],
                                makewidget=True,
                            ),
                            "",
                            "进入时才显示",
                            D_getsimpleswitch(globalconfig, "toolviswhenenter"),
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
                            "延申",
                            D_getsimpleswitch(
                                globalconfig,
                                "extendtools",
                                callback=gobject.baseobject.translation_ui.changeextendstated_1,
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
                    grid=(
                        [
                            "窗口特效",
                            functools.partial(createxxx, self),
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
                            "窗口置顶",
                            D_getsimpleswitch(
                                globalconfig,
                                "keepontop",
                                callback=lambda x: __changeuibuttonstate3(self, x),
                                parent=self,
                                name="keepontopbutton",
                            ),
                            "",
                            "",
                            "",
                            "",
                            "",
                        ],
                        [
                            "自动调整高度",
                            D_getsimpleswitch(globalconfig, "adaptive_height"),
                            "",
                        ],
                        [
                            "任务栏中显示",
                            D_getsimpleswitch(
                                globalconfig,
                                "showintab",
                                callback=lambda _: gobject.baseobject.setshowintab(),
                            ),
                            "",
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
                            "增强效果",
                            D_getsimpleswitch(globalconfig, "mousetransparent_ex"),
                        ],
                        [
                            "自动隐藏窗口",
                            D_getsimpleswitch(globalconfig, "autodisappear"),
                            "",
                            "隐藏延迟(s)",
                            D_getspinbox(
                                1,
                                100,
                                globalconfig,
                                "disappear_delay",
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
                0,
                "group",
            )
        ],
    )


def otheruisetting(self):

    def themelist(t):
        return [_["name"] for _ in static_data["themes"][t]]

    return (
        [
            (
                dict(
                    type="grid",
                    grid=(
                        [
                            "字体",
                            (createfontcombo, 0),
                            "",
                            "字体大小",
                            D_getspinbox(
                                1,
                                100,
                                globalconfig,
                                "settingfontsize",
                                double=True,
                                step=0.1,
                                callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                            ),
                        ],
                        [
                            "按钮颜色",
                            D_getcolorbutton(
                                globalconfig,
                                "buttoncolor2",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "buttoncolor2",
                                    self.buttoncolorbutton2,
                                ),
                                name="buttoncolorbutton2",
                                parent=self,
                            ),
                            D_getcolorbutton(
                                globalconfig,
                                "buttoncolor3",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "buttoncolor3",
                                    self.buttoncolorbutton3,
                                ),
                                name="buttoncolorbutton3",
                                parent=self,
                            ),
                            "",
                            "按钮大小",
                            D_getspinbox(5, 100, globalconfig, "buttonsize2"),
                            "",
                            "任务栏中显示",
                            D_getsimpleswitch(
                                globalconfig,
                                "showintab_sub",
                                callback=lambda _: gobject.baseobject.setshowintab(),
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
                    title="主题",
                    grid=(
                        [
                            "明暗",
                            D_getsimplecombobox(
                                ["跟随系统", "明亮", "黑暗"],
                                globalconfig,
                                "darklight2",
                                lambda _: gobject.baseobject.setcommonstylesheet(),
                            ),
                        ],
                        [
                            "明亮主题",
                            (
                                D_getsimplecombobox(
                                    ["默认"] + themelist("light"),
                                    globalconfig,
                                    "lighttheme",
                                    functools.partial(
                                        checkthemesettingvisandapply,
                                        self,
                                        False,
                                    ),
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
                                    "darktheme",
                                    functools.partial(
                                        checkthemesettingvisandapply,
                                        self,
                                        True,
                                    ),
                                ),
                                functools.partial(createbtnthemedark, self),
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
                    grid=(
                        [
                            "窗口特效",
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
                        ],
                    ),
                ),
                0,
                "group",
            )
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
                ],
                static=True,
            ),
            self.__shadowxx,
            self.__shadowxx2,
        ],
        makewidget=True,
        margin0=True,
    )
