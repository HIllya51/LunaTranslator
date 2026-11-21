from qtsymbols import *
from myutils.config import magpie_config
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getsimpleswitch,
    getsimplepatheditor,
    getboxlayout,
    getboxwidget,
    getsimpleswitch,
    makecardrow,
    SuperCombo,
    getsimplecombobox,
)
from gui.dynalang import LPushButton, LLabel
from gui.fluent.expander import makeexpander
import functools, os, json, gobject
from myutils.magpie_builtin import AdapterService


class SuperCombo__1(SuperCombo):
    signal = pyqtSignal(list)


def adapterchangedcallback(profile, combo: SuperCombo, adapterinfos: list):
    combo.blockSignals(True)
    combo.clear()
    print(adapterinfos)
    infosx = list(_[:3] for _ in adapterinfos)
    visx = list(_[3] for _ in adapterinfos)
    default = "默认"
    if visx:
        default = "默认_[[({})]]".format(visx[0])
    for i in range(len(visx)):
        visx[i] = "[[{}]]".format(visx[i])
    combo.addItems([default] + visx, [[-1, 0, 0]] + infosx)
    combo.blockSignals(False)
    graphicsCardId: dict = profile["graphicsCardId"]
    curr = (
        graphicsCardId["idx"],
        graphicsCardId["vendorId"],
        graphicsCardId["deviceId"],
    )
    combo.setCurrentData(list(curr))


def __changed(profile, combo: SuperCombo, idx):
    data = combo.getIndexData(idx)
    graphicsCardId: dict = profile["graphicsCardId"]
    graphicsCardId.update(idx=data[0], vendorId=data[1], deviceId=data[2])


def createadaptercombo(profile):
    # AdapterServic对于不使用的人来说，开销太大了，太浪费。
    # 因此偷懒起见，如果不修改显示卡，则直接使用配置里的设置去调用，不去加载AdapterService以检查有效性。
    # 仅在使用这个修改显示卡时，才加载AdapterService
    combo = SuperCombo__1()
    combo.signal.connect(functools.partial(adapterchangedcallback, profile, combo))
    combo.currentIndexChanged.connect(functools.partial(__changed, profile, combo))
    AdapterService.init(combo.signal.emit)
    gobject.AdapterServiceInited = True
    return combo


def _getsavedir(profile):
    screenshotsDir = profile["screenshotsDir"]
    if not screenshotsDir:
        return os.path.expanduser("~/Pictures/Screenshots")
    return screenshotsDir


def __select(combo: SuperCombo):
    p = os.path.expanduser("~/AppData/Local/Magpie/config")
    if not os.path.isdir(p):
        p = None
    f = QFileDialog.getOpenFileName(directory=p, filter="config.json")
    res = f[0]
    if res:
        with open(res, "r", encoding="utf8") as ff:
            __ = json.load(ff)
        combo.clear()
        combo.addItems([_["name"] for _ in __["scalingModes"]])
        combo.setCurrentIndex(__["profiles"][0]["scalingMode"])
        magpie_config["scalingModes"] = __["scalingModes"]


def __layout(isglobal, profile):
    combo = getsimplecombobox(
        [_["name"] for _ in magpie_config["scalingModes"]],
        profile,
        "scalingMode",
        static=True,
    )
    if not isglobal:
        return combo
    btn = LPushButton("导入")
    btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    btn.clicked.connect(functools.partial(__select, combo))
    return getboxlayout([combo, btn])


def _widenctl(w):
    """行内 combobox/spinbox 统一最小宽度（170）对齐。"""
    for c in w.findChildren(QComboBox):
        c.setMinimumWidth(170)
    for c in w.findChildren(QAbstractSpinBox):
        c.setMinimumWidth(170)
    return w


def developerexpander():
    """开发者选项折叠卡：展开/收起状态写入 magpie 的 developerMode
    （保持原折叠区语义），默认折叠、不恢复上次状态。"""
    return _fold(
        "开发者选项",
        [
            ["调试模式", 1, D_getsimpleswitch(magpie_config, "debugMode")],
            ["性能测试模式", 1, D_getsimpleswitch(magpie_config, "benchmarkMode")],
            ["禁用缩放窗口置顶", 1, D_getsimpleswitch(magpie_config, "disableTopmost")],
            ["禁用效果缓存", 1, D_getsimpleswitch(magpie_config, "disableEffectCache")],
            [
                "解析效果时保存源代码",
                1,
                D_getsimpleswitch(magpie_config, "saveEffectSources"),
            ],
            [
                "编译效果时将警告视为错误",
                1,
                D_getsimpleswitch(magpie_config, "warningsAreErrors"),
            ],
            [
                "禁止在着色器中使用 FP16",
                1,
                D_getsimpleswitch(magpie_config, "disableFP16"),
            ],
            ["禁用字体缓存", 1, D_getsimpleswitch(magpie_config, "disableFontCache")],
            [
                "检测重复帧",
                1,
                D_getsimplecombobox(
                    ["总是检测", "动态检测", "从不检测"],
                    magpie_config,
                    "duplicateFrameDetectionMode",
                ),
            ],
            [
                "启用动态检测统计",
                1,
                D_getsimpleswitch(magpie_config, "enableStatisticsForDynamicDetection"),
            ],
        ],
        expandedchanged=lambda v: magpie_config.__setitem__("developerMode", v),
    )


def _srow(title):
    """分节标题。"""
    lab = LLabel(title)
    font = lab.font()
    font.setBold(True)
    font.setPixelSize(15)
    lab.setFont(font)
    return [[(lab, 0)]]


def _cardrow(label, *controls):
    """设置行卡片：makecardrow + 控件加宽，包装为行列表（便于 + 拼接）。"""
    return [[(_widenctl(makecardrow(label, *controls)), 0)]]


def _fold(label, rows, headerctl=None, pad=None, expandedchanged=None):
    """折叠设置卡（makeexpander 的网格行适配）：
    - rows：内容行，单行可直接传 [标题, 1, 控件]，多行传
      [[标题, 1, 控件], ...]（getboxwidget 约定：int 为 stretch、
      callable 会调用）
    - headerctl：折叠条右侧控件（开关/combobox 等；省略为纯标题卡）
    - pad：内容右侧让出折叠按钮区，默认随 headerctl 有无推断——
      有控件时让位与控件对齐
    - expandedchanged：展开/收起回调（developerMode 这类联动用）"""
    if rows and not isinstance(rows[0], list):
        rows = [rows]
    if pad is None:
        pad = headerctl is not None
    exp = makeexpander(
        label,
        trailing=headerctl,
        content=[_widenctl(getboxwidget(row)) for row in rows],
        pad=pad,
        expandedchanged=expandedchanged,
    )
    return [[(exp, 0)]]


def makescalew(profile=None):
    isglobal = profile is None
    if profile is None:
        profile = magpie_config["profiles"][0]
    __getsavedir = functools.partial(_getsavedir, profile)
    innermagpie = (
        _srow("常规")
        + _cardrow("缩放模式", functools.partial(__layout, isglobal, profile))
        + _cardrow(
            "捕获模式",
            D_getsimplecombobox(
                [
                    "Graphics Capture",
                    "Desktop Duplication",
                    "GDI",
                    "DwmSharedSurface",
                ],
                profile,
                "captureMethod",
                static=True,
            ),
        )
        + _cardrow("3D游戏模式", D_getsimpleswitch(profile, "3DGameMode"))
        + _srow("工具栏")
        + _fold(
            "工具栏初始状态",
            [
                [
                    "全屏模式缩放",
                    1,
                    D_getsimplecombobox(
                        ["关闭", "始终显示", "自动隐藏"],
                        profile,
                        "fullscreenInitialToolbarState",
                    ),
                ],
                [
                    "窗口模式缩放",
                    1,
                    D_getsimplecombobox(
                        ["关闭", "始终显示", "自动隐藏"],
                        profile,
                        "windowedInitialToolbarState",
                    ),
                ],
            ],
        )
        + _cardrow(
            "截图保存目录",
            functools.partial(
                getsimplepatheditor,
                text=__getsavedir(),
                isdir=True,
                clearset=__getsavedir,
                callback=functools.partial(
                    profile.__setitem__,
                    "screenshotsDir",
                ),
            ),
        )
        + _srow("窗口模式缩放")
        + _cardrow(
            "初始缩放倍数",
            D_getsimplecombobox(
                [
                    "自动",
                    "1.25x",
                    "1.5x",
                    "1.75x",
                    "2x",
                    "3x",
                    "自定义",
                ],
                profile,
                "initialWindowedScaleFactor",
            ),
        )
        + _srow("性能")
        + _cardrow("显示卡", functools.partial(createadaptercombo, profile))
        + _fold(
            "帧率限制",
            ["最大帧率", 1, D_getspinbox(0, 9999, profile, "maxFrameRate")],
            getsimpleswitch(profile, "frameRateLimiterEnabled"),
        )
        + _srow("源窗口")
        + _cardrow("捕获标题栏", D_getsimpleswitch(profile, "captureTitleBar"))
        + _cardrow("自定义剪裁", D_getsimpleswitch(profile, "croppingEnabled"))
        + _srow("光标")
        + _fold(
            "缩放系数",
            [
                "插值算法",
                1,
                D_getsimplecombobox(
                    ["最邻近", "双线性"], profile, "cursorInterpolationMode"
                ),
            ],
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
                profile,
                "cursorScaling",
            ),
        )
        + _fold(
            "光标静止时自动隐藏",
            [
                "隐藏延迟（秒）",
                1,
                D_getspinbox(
                    0.1,
                    5,
                    profile,
                    "autoHideCursorDelay",
                    double=True,
                ),
            ],
            getsimpleswitch(profile, "autoHideCursorEnabled"),
        )
        + _cardrow(
            "缩放时调整光标速度", D_getsimpleswitch(profile, "adjustCursorSpeed")
        )
        + _srow("高级")
        + (
            _cardrow(
                "允许缩放最大化或全屏的窗口",
                D_getsimpleswitch(magpie_config, "allowScalingMaximized"),
            )
            if isglobal
            else []
        )
        + (
            _cardrow(
                "缩放期间保持屏幕常亮",
                D_getsimpleswitch(magpie_config, "keepScreenOn"),
            )
            if isglobal
            else []
        )
        + (
            _cardrow(
                "模拟独占全屏",
                D_getsimpleswitch(magpie_config, "simulateExclusiveFullscreen"),
            )
            if isglobal
            else []
        )
        + (
            _cardrow(
                "内联效果参数",
                D_getsimpleswitch(magpie_config, "inlineParams"),
            )
            if isglobal
            else []
        )
        + (
            _cardrow(
                "最小帧率",
                D_getsimplecombobox(
                    ["0", "5", "10", "15", "20", "30", "60"],
                    magpie_config,
                    "minFrameRate",
                    internal=[0, 5, 10, 15, 20, 30, 60],
                ),
            )
            if isglobal
            else []
        )
        + _cardrow(
            "输出画面位置",
            D_getsimplecombobox(
                [
                    "左上角",
                    "顶部居中",
                    "右上角",
                    "左对齐",
                    "居中",
                    "右对齐",
                    "左下角",
                    "底部居中",
                    "右下角",
                ],
                profile,
                "outputAlignment",
            ),
        )
        + _cardrow("禁用DirectFlip", D_getsimpleswitch(profile, "disableDirectFlip"))
        + (developerexpander() if isglobal else [])
    )

    return innermagpie
