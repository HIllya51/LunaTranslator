from qtsymbols import *
from myutils.config import globalconfig, magpie_config
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    createfoldgrid,
    D_getsimpleswitch,
    getsimplepatheditor,
    SuperCombo,
)
from myutils.magpie_builtin import AdapterService
import functools, os


class SuperCombo__1(SuperCombo):
    signal = pyqtSignal(list)


def adapterchangedcallback(combo: SuperCombo, adapterinfos: list):
    combo.blockSignals(True)
    combo.clear()
    adapterinfos.sort(key=lambda _: _[0])
    infosx = list(_[:3] for _ in adapterinfos)
    visx = list(_[3] for _ in adapterinfos)
    default = "默认"
    if visx:
        default += "_[[(" + visx[0] + ")]]"
    combo.addItems([default] + visx, [(-1, 0, 0)] + infosx)
    combo.blockSignals(False)
    graphicsCardId: dict = magpie_config["profiles"][globalconfig["profiles_index"]][
        "graphicsCardId"
    ]
    curr = (
        graphicsCardId["idx"],
        graphicsCardId["vendorId"],
        graphicsCardId["deviceId"],
    )
    if curr not in infosx:
        combo.setCurrentIndex(0)
    else:
        combo.setCurrentIndex(infosx.index(curr) + 1)


def __changed(combo: SuperCombo, idx):
    data = combo.getIndexData(idx)
    graphicsCardId: dict = magpie_config["profiles"][globalconfig["profiles_index"]][
        "graphicsCardId"
    ]
    graphicsCardId.update(idx=data[0], vendorId=data[1], deviceId=data[2])


def createadaptercombo():
    # AdapterServic对于不使用的人来说，开销太大了，太浪费。
    # 因此偷懒起见，如果不修改显示卡，则直接使用配置里的设置去调用，不去加载AdapterService以检查有效性。
    # 仅在使用这个修改显示卡时，才加载AdapterService
    combo = SuperCombo__1()
    combo.signal.connect(functools.partial(adapterchangedcallback, combo))
    combo.currentIndexChanged.connect(functools.partial(__changed, combo))
    AdapterService().init(combo.signal.emit)
    return combo


def __getsavedir():
    screenshotsDir = magpie_config["overlay"]["screenshotsDir"]
    if not screenshotsDir:
        try:
            return os.path.join(os.environ["USERPROFILE"], r"Pictures\Screenshots")
        except:
            pass
    return screenshotsDir


def makescalew():
    innermagpie = [
        [
            dict(
                title="常规",
                grid=(
                    [
                        [
                            "缩放模式",
                            D_getsimplecombobox(
                                [_["name"] for _ in magpie_config["scalingModes"]],
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "scalingMode",
                                static=True,
                            ),
                        ],
                        [
                            "捕获模式",
                            D_getsimplecombobox(
                                [
                                    "Graphics Capture",
                                    "Desktop Duplication",
                                    "GDI",
                                    "DwmSharedSurface",
                                ],
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "captureMethod",
                                static=True,
                            ),
                        ],
                        [
                            "3D游戏模式",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "3DGameMode",
                            ),
                        ],
                    ]
                ),
            ),
        ],
        [
            dict(
                title="工具栏",
                grid=[
                    [
                        "工具栏初始状态",
                        D_getsimplecombobox(
                            ["关闭", "始终显示", "自动隐藏"],
                            magpie_config["overlay"],
                            "initialToolbarState",
                        ),
                    ],
                    [
                        "截图保存目录",
                        functools.partial(
                            getsimplepatheditor,
                            text=__getsavedir(),
                            isdir=True,
                            clearset=__getsavedir,
                            callback=functools.partial(
                                magpie_config["overlay"].__setitem__, "screenshotsDir"
                            ),
                        ),
                    ],
                ],
            )
        ],
        [
            dict(
                title="性能",
                type="grid",
                grid=(
                    [
                        ["显示卡", (createadaptercombo, 0)],
                        [
                            "帧率限制",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "frameRateLimiterEnabled",
                            ),
                            "",
                            "最大帧率",
                            D_getspinbox(
                                0,
                                9999,
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "maxFrameRate",
                            ),
                        ],
                    ]
                ),
            ),
        ],
        [
            dict(
                title="源窗口",
                grid=(
                    [
                        [
                            "缩放时禁用窗口大小调整",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "disableWindowResizing",
                            ),
                        ],
                        [
                            "捕获标题栏",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "captureTitleBar",
                            ),
                        ],
                        [
                            "自定义剪裁",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "croppingEnabled",
                            ),
                        ],
                    ]
                ),
            ),
        ],
        [
            dict(
                title="光标",
                grid=(
                    [
                        [
                            "缩放系数",
                            D_getsimplecombobox(
                                [
                                    "0.5x",
                                    "0.75x",
                                    "无缩放",
                                    "1.25x",
                                    "1.5x",
                                    "2x",
                                    "和源窗口相同",
                                ],
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "cursorScaling",
                            ),
                        ],
                        [
                            "插值算法",
                            D_getsimplecombobox(
                                ["最邻近", "双线性"],
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "cursorInterpolationMode",
                            ),
                        ],
                        [
                            "缩放时调整光标速度",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "adjustCursorSpeed",
                            ),
                        ],
                    ]
                ),
            ),
        ],
        [
            dict(
                title="高级",
                grid=(
                    [
                        [
                            "允许缩放最大化或全屏的窗口",
                            D_getsimpleswitch(
                                magpie_config,
                                "allowScalingMaximized",
                            ),
                        ],
                        [
                            "内联效果参数",
                            D_getsimpleswitch(
                                magpie_config,
                                "inlineParams",
                            ),
                        ],
                        [
                            "缩放时模拟独占全屏",
                            D_getsimpleswitch(
                                magpie_config,
                                "simulateExclusiveFullscreen",
                            ),
                        ],
                        [
                            "最小帧率",
                            D_getsimplecombobox(
                                ["0", "5", "10", "15", "20", "30", "60"],
                                magpie_config,
                                "minFrameRate",
                                internal=[0, 5, 10, 15, 20, 30, 60],
                            ),
                        ],
                        [
                            "禁用DirectFlip",
                            D_getsimpleswitch(
                                magpie_config["profiles"][
                                    globalconfig["profiles_index"]
                                ],
                                "disableDirectFlip",
                            ),
                        ],
                    ]
                ),
            ),
        ],
        [
            functools.partial(
                createfoldgrid,
                [
                    [
                        "调试模式",
                        D_getsimpleswitch(
                            magpie_config,
                            "debugMode",
                        ),
                    ],
                    [
                        "性能测试模式",
                        D_getsimpleswitch(
                            magpie_config,
                            "benchmarkMode",
                        ),
                    ],
                    [
                        "禁用效果缓存",
                        D_getsimpleswitch(
                            magpie_config,
                            "disableEffectCache",
                        ),
                    ],
                    [
                        "解析效果时保存源代码",
                        D_getsimpleswitch(
                            magpie_config,
                            "saveEffectSources",
                        ),
                    ],
                    [
                        "编译效果时将警告视为错误",
                        D_getsimpleswitch(
                            magpie_config,
                            "warningsAreErrors",
                        ),
                    ],
                    [
                        "禁止在着色器中使用 FP16",
                        D_getsimpleswitch(
                            magpie_config,
                            "disableFP16",
                        ),
                    ],
                    [
                        "禁用字体缓存",
                        D_getsimpleswitch(
                            magpie_config,
                            "disableFontCache",
                        ),
                    ],
                    [
                        "检测重复帧",
                        D_getsimplecombobox(
                            ["总是检测", "动态检测", "从不检测"],
                            magpie_config,
                            "duplicateFrameDetectionMode",
                        ),
                    ],
                    [
                        "启用动态检测统计",
                        D_getsimpleswitch(
                            magpie_config,
                            "enableStatisticsForDynamicDetection",
                        ),
                    ],
                ],
                "开发者选项",
                magpie_config,
                "developerMode",
            )
        ],
    ]

    return innermagpie
