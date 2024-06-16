from qtsymbols import *
import functools
from myutils.config import globalconfig, magpie_config, static_data, _TRL
from gui.inputdialog import getsomepath1
from gui.usefulwidget import (
    D_getsimplecombobox,
    makegrid,
    D_getspinbox,
    getvboxwidget,
    D_getcolorbutton,
    makesubtab_lazy,
    makescrollgrid,
    D_getsimpleswitch,
)


def makescalew(self, lay):

    commonfsgrid = [
        [
            ("缩放方式", 4),
            (
                D_getsimplecombobox(
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
                D_getcolorbutton(
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
            ("", 10),
        ]
    ]

    innermagpie = [
        [("常规", -1)],
        [
            ("", 1),
            ("缩放模式", 4),
            (
                D_getsimplecombobox(
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
                D_getsimplecombobox(
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
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "3DGameMode",
                )
            ),
        ],
        [("性能", -1)],
        [
            ("", 1),
            ("显示帧率", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "showFPS",
                )
            ),
        ],
        [
            ("", 1),
            ("限制帧率", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "frameRateLimiterEnabled",
                )
            ),
        ],
        [
            ("", 1),
            ("最大帧率", 4),
            (
                D_getspinbox(
                    0,
                    9999,
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "maxFrameRate",
                ),
                2,
            ),
        ],
        [("源窗口", -1)],
        [
            ("", 1),
            ("缩放时禁用窗口大小调整", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "disableWindowResizing",
                )
            ),
        ],
        [
            ("", 1),
            ("捕获标题栏", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "captureTitleBar",
                )
            ),
        ],
        [
            ("", 1),
            ("自定义剪裁", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "croppingEnabled",
                )
            ),
        ],
        [("光标", -1)],
        [
            ("", 1),
            ("绘制光标", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "drawCursor",
                )
            ),
        ],
        [
            ("", 1),
            ("绘制光标_缩放系数", 4),
            (
                D_getsimplecombobox(
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
                D_getsimplecombobox(
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
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "adjustCursorSpeed",
                )
            ),
        ],
        [("高级", -1)],
        [
            ("", 1),
            ("禁用DirectFlip", 4),
            (
                D_getsimpleswitch(
                    magpie_config["profiles"][globalconfig["profiles_index"]],
                    "disableDirectFlip",
                )
            ),
        ],
        [
            ("", 1),
            ("允许缩放最大化或全屏的窗口", 4),
            (D_getsimpleswitch(magpie_config, "allowScalingMaximized")),
        ],
        [
            ("", 1),
            ("缩放时模拟独占全屏", 4),
            (D_getsimpleswitch(magpie_config, "simulateExclusiveFullscreen")),
        ],
        [
            ("", 1),
            ("内联效果参数", 4),
            (D_getsimpleswitch(magpie_config, "inlineParams")),
        ],
        [("开发者选项", -1)],
        [
            ("", 1),
            ("调试模式", 4),
            (
                D_getsimpleswitch(
                    magpie_config,
                    "debugMode",
                )
            ),
        ],
        [
            ("", 1),
            ("禁用效果缓存", 4),
            (
                D_getsimpleswitch(
                    magpie_config,
                    "disableEffectCache",
                )
            ),
        ],
        [
            ("", 1),
            ("禁用字体缓存", 4),
            (
                D_getsimpleswitch(
                    magpie_config,
                    "disableFontCache",
                )
            ),
        ],
        [
            ("", 1),
            ("解析效果时保存源代码", 4),
            (
                D_getsimpleswitch(
                    magpie_config,
                    "saveEffectSources",
                )
            ),
        ],
        [
            ("", 1),
            ("编译效果时将警告视为错误", 4),
            (
                D_getsimpleswitch(
                    magpie_config,
                    "warningsAreErrors",
                )
            ),
        ],
        [
            ("", 1),
            ("检测重复帧", 4),
            (
                D_getsimplecombobox(
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
                D_getsimpleswitch(
                    magpie_config,
                    "enableStatisticsForDynamicDetection",
                )
            ),
        ],
    ]

    vw, vl = getvboxwidget()
    lay.addWidget(vw)
    gw, gd = makegrid(commonfsgrid, delay=True)
    vl.addWidget(gw)
    tw, td = makesubtab_lazy(
        _TRL(["Magpie", "外部缩放软件"]),
        [
            functools.partial(makescrollgrid, innermagpie),
            functools.partial(makescrollgrid, losslessgrid),
        ],
        delay=True,
    )
    vl.addWidget(tw)
    gd()
    td()
