from qtsymbols import *
import functools
import gobject
from myutils.config import globalconfig, ui_settings
from myutils.utils import getimagefilefilter
from gui.flowsearchword import createsomecontrols
from gui.qevent import DarkLightSettingChangedEvent
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getcolorbutton,
    D_getsimpleswitch,
    getsimpleswitch,
    getsmalllabel,
    getboxlayout,
    getboxwidget,
    makecardrow,
    getsimplepatheditor,
    D_getIconSwitch,
)
from gui.fluent.expander import ExExpander
from gui.dynalang import LLabel


def changeHorizontal_pic(
    horizontal_slider_tool: QSlider, horizontal_slider_tool_label: QLabel
):

    ui_settings["transparent_pic"] = horizontal_slider_tool.value()
    horizontal_slider_tool_label.setText(
        "{}%".format(ui_settings.get("transparent_pic", 0))
    )
    gobject.base.translation_ui.translate_text.setbackgroudimageandopt()


def createhorizontal_slider_pic():

    horizontal_slider = QSlider()
    horizontal_slider.setMaximum(100)
    horizontal_slider.setMinimum(0)
    horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    horizontal_slider.setValue(ui_settings.get("transparent_pic", 0))

    horizontal_slider_label = QLabel()
    horizontal_slider.valueChanged.connect(
        functools.partial(
            changeHorizontal_pic, horizontal_slider, horizontal_slider_label
        )
    )
    horizontal_slider_label.setText("{}%".format(ui_settings.get("transparent_pic", 0)))

    def dosomething(x):
        horizontal_slider.setEnabled(x)
        horizontal_slider_label.setText(
            "{}%".format(ui_settings.get("transparent_pic", 0) if x else 0)
        )

    gobject.base.backtransparentstatus_2.connect(dosomething)
    dosomething(not ui_settings.get("backtransparent", False))
    return getboxlayout([horizontal_slider, horizontal_slider_label])


def changeHorizontal(
    horizontal_slider_tool: QSlider, horizontal_slider_tool_label: QLabel
):

    ui_settings["transparent"] = horizontal_slider_tool.value()
    horizontal_slider_tool_label.setText("{}%".format(ui_settings["transparent"]))
    gobject.base.translation_ui.set_color_transparency()


def createhorizontal_slider():

    horizontal_slider = QSlider()
    horizontal_slider.setMaximum(100)
    horizontal_slider.setMinimum(1 - ui_settings.get("transparent_EX", False))
    horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
    horizontal_slider.setValue(ui_settings.get("transparent", 10))
    horizontal_slider_label = QLabel()
    horizontal_slider.valueChanged.connect(
        functools.partial(changeHorizontal, horizontal_slider, horizontal_slider_label)
    )

    horizontal_slider_label.setText("{}%".format(ui_settings.get("transparent", 10)))

    l = getsmalllabel("  EX")()

    def dosomething(en):
        horizontal_slider.setEnabled(en)
        horizontal_slider_label.setText(
            "{}%".format(
                ui_settings.get("transparent", 10)
                if en
                else (1 - ui_settings.get("transparent_EX", False))
            )
        )

    sw = getsimpleswitch(
        ui_settings,
        "transparent_EX",
        callback=lambda ex: (
            horizontal_slider.setMinimum(1 - ex),
            gobject.base.translation_ui.set_color_transparency(),
            dosomething(not ui_settings.get("backtransparent", False)),
        ),
        default=False,
    )

    gobject.base.backtransparentstatus.connect(dosomething)

    dosomething(not ui_settings.get("backtransparent", False))
    return getboxlayout([horizontal_slider, horizontal_slider_label, l, sw])


def changeHorizontal_tool(
    horizontal_slider_tool: QSlider, horizontal_slider_tool_label: QLabel
):

    ui_settings["transparent_tool"] = horizontal_slider_tool.value()
    horizontal_slider_tool_label.setText(
        "{}%".format(ui_settings.get("transparent_tool", 50))
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
    horizontal_slider_tool.setValue(ui_settings.get("transparent_tool", 50))

    horizontal_slider_tool_label = QLabel()
    horizontal_slider_tool.valueChanged.connect(
        functools.partial(
            changeHorizontal_tool, horizontal_slider_tool, horizontal_slider_tool_label
        )
    )
    horizontal_slider_tool_label.setText(
        "{}%".format(ui_settings.get("transparent_tool", 50))
    )
    return getboxlayout([horizontal_slider_tool, horizontal_slider_tool_label])


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
        dic=ui_settings,
        kRdf=0,
    )
    return getboxlayout(
        [
            "窗口特效",
            lay,
            "",
            getsmalllabel("圆角"),
            spin,
        ]
    )


def switch_darklight():
    darklight = ui_settings.get("darklight2", 0)
    for widget in QApplication.allWidgets():
        QApplication.postEvent(widget, DarkLightSettingChangedEvent(darklight))


def uisetting(self):
    # 自动隐藏：折叠卡（子项 = 隐藏目标/隐藏延迟）。先建延迟控件——
    # 隐藏目标下拉的初值回调会引用 self.disappear_delay
    delay = createdynamicdelay(self)
    target = createdynamicswitch(self)
    autohideexp = ExExpander()
    header = QWidget()
    hlay = QHBoxLayout(header)
    hlay.setContentsMargins(0, 12, 0, 12)
    hlay.setSpacing(8)
    titlelabel = LLabel("自动隐藏")
    titlefont = titlelabel.font()
    titlefont.setPixelSize(15)
    titlelabel.setFont(titlefont)
    hlay.addWidget(titlelabel)
    hlay.addStretch(1)
    hlay.addWidget(
        D_getsimpleswitch(globalconfig, "autodisappear", default=False)()
    )
    autohideexp.setHeaderWidget(header)
    autohideexp.addContentWidget(getboxwidget(["隐藏目标", 1, target]))
    autohideexp.addContentWidget(getboxwidget(["隐藏延迟_(s)", 1, delay]))

    # 自动调整高度：折叠卡（子项 = 最小高度）
    adaptiveexp = ExExpander()
    header = QWidget()
    hlay = QHBoxLayout(header)
    hlay.setContentsMargins(0, 12, 0, 12)
    hlay.setSpacing(8)
    titlelabel = LLabel("自动调整高度")
    titlefont = titlelabel.font()
    titlefont.setPixelSize(15)
    titlelabel.setFont(titlefont)
    hlay.addWidget(titlelabel)
    hlay.addStretch(1)
    hlay.addWidget(
        D_getsimpleswitch(globalconfig, "adaptive_height", default=True)()
    )
    adaptiveexp.setHeaderWidget(header)
    adaptiveexp.addContentWidget(
        getboxwidget(
            [
                "最小高度_(px)",
                1,
                D_getspinbox(0, 9999, ui_settings, "min_auto_height", default=0, callback=lambda _: gobject.base.translation_ui.titlebar.adjustminwidth())(),
            ]
        )
    )

    __ = mainuisetting(self) + [
        [
            dict(
                type="grid",
                card=True,
                grid=([__rs],),
            )
        ],
        [
            (
                makecardrow(
                    "任务栏中显示",
                    D_getsimpleswitch(
                        globalconfig,
                        "showintab",
                        callback=lambda _: gobject.base.setshowintab(),
                        default=True,
                    ),
                ),
                0,
            )
        ],
        [
            (
                makecardrow(
                    "游戏窗口移动时同步移动",
                    D_getsimpleswitch(globalconfig, "movefollow", default=True),
                ),
                0,
            )
        ],
        [
            (
                makecardrow(
                    "游戏失去焦点时取消置顶",
                    D_getsimpleswitch(globalconfig, "focusnotop", default=False),
                ),
                0,
            )
        ],
        [(autohideexp, 0)],
        [(adaptiveexp, 0)],
    ]

    return __


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
                            ui_settings,
                            "backcolor_tool",
                            callback=lambda _: toolcolorchange(),
                            default="#ffaaff",
                            tips="背景颜色",
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
                hiderows=[2],
                name="textareaobject",
                parent=self,
                grid=(
                    [
                        "背景颜色",
                        D_getcolorbutton(
                            self,
                            ui_settings,
                            "backcolor",
                            callback=lambda _: gobject.base.translation_ui.set_color_transparency(),
                            default="#ffaaff",
                            tips="背景颜色",
                        ),
                        "",
                        "不透明度",
                        createhorizontal_slider,
                    ],
                    [
                        "背景图片",
                        D_getIconSwitch(
                            icon="fa.picture-o",
                            checkablechangecolor=False,
                            callback=lambda x: self.textareaobject.layout().setRowVisible(
                                2, x
                            ),
                            tips="背景图片",
                        ),
                        "",
                        "不透明度",
                        createhorizontal_slider_pic,
                    ],
                    [
                        "图片",
                        (
                            lambda: getsimplepatheditor(
                                ui_settings.get(
                                    "backgroundpic",
                                    "https://image.lunatranslator.org/luna.jpg",
                                ),
                                False,
                                False,
                                filter1=getimagefilefilter(),
                                callback=lambda _: (
                                    ui_settings.__setitem__("backgroundpic", _),
                                    gobject.base.translation_ui.translate_text.setbackgroudimageandopt(),
                                ),
                                clearable=False,
                                icons=("fa.folder-open",),
                                editable=True,
                                btnatleft=True,
                            ),
                            0,
                        ),
                    ],
                ),
            ),
        ],
    ]
