from qtsymbols import *
import functools
import gobject
from myutils.config import globalconfig, _TRL
from gui.inputdialog import multicolorset
from gui.usefulwidget import (
    D_getsimplecombobox,
    getsimpleswitch,
    D_getspinbox,
    getspinbox,
    D_getcolorbutton,
    D_getsimpleswitch,
    selectcolor,
    FocusFontCombo
)


def maybehavefontsizespin(self, t):
    if "fontSize_spinBox" in dir(self):
        self.fontSize_spinBox.setValue(self.fontSize_spinBox.value() + 0.5 * t)
    else:
        globalconfig["fontsize"] += 0.5 * t


def createfontsizespin(self):
    self.fontSize_spinBox = getspinbox(
        1, 100, globalconfig, "fontsize", double=True, step=0.1
    )
    return self.fontSize_spinBox


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    try:
        self.show_hira_switch.setEnabled(x)
        self.show_fenciswitch.setEnabled(x)
    except:
        pass


def createtextfontcom(key):
    font_comboBox = FocusFontCombo()
    font_comboBox.currentTextChanged.connect(lambda x: globalconfig.__setitem__(key, x))
    font_comboBox.setCurrentFont(QFont(globalconfig[key]))
    return font_comboBox


def createshoworiginswitch(self):
    self.show_original_switch = getsimpleswitch(
        globalconfig, "isshowrawtext", callback=lambda x: __changeuibuttonstate(self, x)
    )
    return self.show_original_switch


def createhiraswitch(self):

    self.show_hira_switch = getsimpleswitch(
        globalconfig, "isshowhira", enable=globalconfig["isshowrawtext"]
    )
    return self.show_hira_switch


def createfenciwitch(self):
    self.show_fenciswitch = getsimpleswitch(
        globalconfig, "show_fenci", enable=globalconfig["isshowrawtext"]
    )
    return self.show_fenciswitch


def xianshigrid(self):

    textgrid = [
        [
            ("原文字体", 3),
            (functools.partial(createtextfontcom, "fonttype"), 6),
            ("", 5),
        ],
        [
            ("译文字体", 3),
            (functools.partial(createtextfontcom, "fonttype2"), 6),
        ],
        [
            ("字体大小", 3),
            (functools.partial(createfontsizespin, self), 3),
            "",
            ("额外的行间距", 3),
            (D_getspinbox(-100, 100, globalconfig, "extra_space"), 3),
        ],
        [
            ("居中显示", 5),
            D_getsimpleswitch(globalconfig, "showatcenter"),
            "",
            ("加粗字体", 5),
            D_getsimpleswitch(globalconfig, "showbold"),
        ],
        [
            "",
        ],
        [
            ("字体样式", 3),
            (
                D_getsimplecombobox(
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
            D_getcolorbutton(
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
                D_getspinbox(
                    0.1, 100, globalconfig, "miaobianwidth", double=True, step=0.1
                ),
                3,
            ),
            "",
            ("描边宽度", 3),
            (
                D_getspinbox(
                    0.1, 100, globalconfig, "miaobianwidth2", double=True, step=0.1
                ),
                3,
            ),
        ],
        [
            ("发光亮度", 3),
            (D_getspinbox(1, 100, globalconfig, "shadowforce"), 3),
            "",
            ("投影距离", 3),
            (
                D_getspinbox(
                    0.1, 100, globalconfig, "traceoffset", double=True, step=0.1
                ),
                3,
            ),
        ],
        [],
        [
            ("显示原文", 5),
            functools.partial(createshoworiginswitch, self),
            "",
            ("显示翻译", 5),
            (D_getsimpleswitch(globalconfig, "showfanyi"), 1),
        ],
        [
            ("原文颜色", 5),
            D_getcolorbutton(
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
            (D_getsimpleswitch(globalconfig, "showfanyisource"), 1),
        ],
        [
            ("最长显示字数", 3),
            (D_getspinbox(0, 1000000, globalconfig, "maxoriginlength"), 3),
        ],
        [],
        [
            ("显示日语注音", 5),
            functools.partial(createhiraswitch, self),
        ],
        [
            ("注音颜色", 5),
            D_getcolorbutton(
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
                D_getspinbox(
                    0.05, 1, globalconfig, "kanarate", double=True, step=0.05, dec=2
                ),
                3,
            ),
        ],
        [
            ("语法加亮", 5),
            functools.partial(createfenciwitch, self),
            "",
            ("词性颜色(需要Mecab)", 5),
            D_getcolorbutton(
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
            D_getsimpleswitch(globalconfig, "refresh_on_get_trans"),
        ],
    ]
    return textgrid
