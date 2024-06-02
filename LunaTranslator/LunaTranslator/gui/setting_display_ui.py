from qtsymbols import *
import functools
import gobject
from myutils.config import globalconfig, _TRL, static_data
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getcolorbutton,
    D_getsimpleswitch,
    selectcolor,
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
    
    sfont_comboBox = QFontComboBox()

    def callback(x):
        globalconfig.__setitem__("settingfonttype", x)
        gobject.baseobject.setcommonstylesheet()

    sfont_comboBox.setCurrentFont(QFont(globalconfig["settingfonttype"]))
    sfont_comboBox.currentTextChanged.connect(callback)
    return sfont_comboBox


def uisetting(self):

    def themelist(t):
        return [_["name"] for _ in static_data["themes"][t]]

    uigrid = [
        [("设置界面字体", 4), (createfontcombo, 5)],
        [
            ("字体大小", 4),
            (
                D_getspinbox(
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
            (functools.partial(createhorizontal_slider, self), 8),
            (functools.partial(createhorizontal_slider_label, self), 2),
        ],
        [
            ("不透明度_工具栏", 4),
            (functools.partial(createhorizontal_slider_tool, self), 8),
            (functools.partial(createhorizontal_slider_tool_label, self), 2),
        ],
        [
            ("背景颜色_翻译窗口", 4),
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
            "",
            ("背景颜色_工具栏", 4),
            D_getcolorbutton(
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
            D_getcolorbutton(
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
                D_getspinbox(
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
                D_getspinbox(
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
            D_getsimpleswitch(
                globalconfig,
                "yuanjiao_merge",
                callback=lambda _: gobject.baseobject.translation_ui.set_color_transparency(),
            ),
        ],
        [],
        [
            ("明暗", 4),
            (
                D_getsimplecombobox(
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
                D_getsimplecombobox(
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
                D_getsimplecombobox(
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
                D_getsimplecombobox(
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
                D_getsimplecombobox(
                    ["Solid", "Acrylic", "Mica", "MicaAlt"],
                    globalconfig,
                    "WindowBackdrop",
                    callback=lambda _: gobject.baseobject.setcommonstylesheet(),
                ),
                5,
            ),
        ],
    ]
    return uigrid
