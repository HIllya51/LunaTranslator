from qtsymbols import *
import functools, os
from myutils.config import globalconfig, ocrsetting, ocrerrorfix
from myutils.utils import splitocrtypes, dynamiclink
from gui.inputdialog import autoinitdialog, postconfigdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    yuitsu_switch,
    D_getcolorbutton,
    D_getsimpleswitch,
    clearlayout,
    getboxlayout,
    selectcolor,
)
import gobject
from gui.dynalang import LFormLayout
from myutils.ocrutil import ocr_end, ocr_init
from myutils.wrapper import threader


def __label1(self):
    self.threshold1label = QLabel()
    return self.threshold1label


def __label2(self):
    self.threshold2label = QLabel()
    return self.threshold2label


@threader
def __directinitend(engine, _ok):
    if _ok:
        ocr_init()
    else:
        ocr_end()


def initgridsources(self, names):
    line = []
    i = 0
    grids_source = []
    for name in names:
        _f = "./Lunatranslator/ocrengines/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue
        if name in ocrsetting:
            items = autoinitdialog_items(ocrsetting[name])
            _3 = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog, self, globalconfig["ocr"][name]["name"], 800, items
                ),
                icon="fa.gear",
            )
        else:
            _3 = ""

        line += [
            globalconfig["ocr"][name]["name"],
            D_getsimpleswitch(
                globalconfig["ocr"][name],
                "use",
                name=name,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["ocr"],
                    "ocrswitchs",
                    name,
                    __directinitend,
                ),
                pair="ocrswitchs",
            ),
            _3,
        ]
        if i % 3 == 2:
            grids_source.append(line)
            line = []
        else:
            line += [""]
        i += 1
    if len(line):
        grids_source.append(line)
    return grids_source


def _ocrparam_create(self, idx):
    clearlayout(self._ocrparaml)
    if idx in [1, 2]:
        self._ocrparaml.addRow(
            "执行周期(s)",
            getboxlayout(
                [
                    D_getspinbox(
                        0.1,
                        100,
                        globalconfig,
                        "ocr_interval",
                        double=True,
                        step=0.1,
                    ),
                    QLabel,
                ]
            ),
        )
    if idx in [3]:
        self._ocrparaml.addRow(
            "延迟(s)",
            getboxlayout(
                [
                    D_getspinbox(
                        0,
                        100,
                        globalconfig,
                        "ocr_trigger_delay",
                        double=True,
                        step=0.1,
                    ),
                    QLabel,
                ]
            ),
        )
    if idx in [0, 2, 3]:
        self._ocrparaml.addRow(
            "图像稳定性阈值",
            getboxlayout(
                [
                    D_getspinbox(
                        0,
                        1,
                        globalconfig,
                        ("ocr_stable_sim", "ocr_stable_sim2")[idx == 3],
                        double=True,
                        step=0.001,
                        dec=3,
                    ),
                    functools.partial(__label1, self),
                ]
            ),
        )
    if idx in [0, 2]:
        self._ocrparaml.addRow(
            "图像一致性阈值",
            getboxlayout(
                [
                    D_getspinbox(
                        0,
                        1,
                        globalconfig,
                        "ocr_diff_sim",
                        double=True,
                        step=0.001,
                        dec=3,
                    ),
                    functools.partial(__label2, self),
                ]
            ),
        )
    if idx in [0, 1, 2]:
        self._ocrparaml.addRow(
            "文本相似度阈值",
            getboxlayout(
                [D_getspinbox(0, 100000, globalconfig, "ocr_text_diff"), QLabel]
            ),
        )


def _ocrparam(self):
    self._ocrparam = QGroupBox()
    self._ocrparam.setStyleSheet(
        "QGroupBox{ margin-top:0px;} QGroupBox:title {margin-top: 0px;}"
    )
    self._ocrparaml = LFormLayout()
    self._ocrparam.setLayout(self._ocrparaml)
    _ocrparam_create(self, globalconfig["ocr_auto_method"])
    return self._ocrparam


def getocrgrid(self):

    grids = []

    offline, online = splitocrtypes(globalconfig["ocr"])
    self.ocrswitchs = {}

    grids += [
        [
            (
                dict(
                    title="引擎",
                    type="grid",
                    grid=[
                        [
                            (
                                dict(
                                    title="离线",
                                    type="grid",
                                    grid=initgridsources(self, offline),
                                ),
                                0,
                                "group",
                            )
                        ],
                        [
                            (
                                dict(
                                    title="在线",
                                    type="grid",
                                    grid=initgridsources(self, online),
                                ),
                                0,
                                "group",
                            )
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    type="grid",
                    grid=[
                        [
                            "识别方向",
                            D_getsimplecombobox(
                                ["横向", "竖向", "自适应"], globalconfig, "verticalocr"
                            ),
                            ("", 4),
                        ]
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="后处理",
                    type="grid",
                    grid=[
                        [
                            (("合并多行识别结果"), 12),
                            D_getsimpleswitch(globalconfig, "ocrmergelines"),
                            ("", 12),
                        ],
                        [
                            (("易错内容修正"), 12),
                            D_getsimpleswitch(ocrerrorfix, "use"),
                            D_getIconButton(
                                callback=functools.partial(
                                    postconfigdialog,
                                    self,
                                    ocrerrorfix["args"]["替换内容"],
                                    "易错内容修正",
                                    ["原文内容", "替换为"],
                                ),
                                icon="fa.gear",
                            ),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="自动化执行",
                    type="grid",
                    grid=[
                        [
                            "自动化执行方法",
                            D_getIconButton(
                                callback=lambda: gobject.baseobject.openlink(
                                    dynamiclink("{docs_server}/#/zh/ocrparam")
                                ),
                                icon="fa.question",
                            ),
                            (
                                D_getsimplecombobox(
                                    [
                                        "分析图像更新",
                                        "周期执行",
                                        "分析图像更新+周期执行",
                                        "鼠标键盘触发+等待稳定",
                                    ],
                                    globalconfig,
                                    "ocr_auto_method",
                                    callback=functools.partial(_ocrparam_create, self),
                                ),
                                12,
                            ),
                        ],
                        [(functools.partial(_ocrparam, self), 0)],
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="其他",
                    type="grid",
                    grid=[
                        [
                            "多重区域模式",
                            D_getsimpleswitch(globalconfig, "multiregion"),
                        ],
                        [
                            "范围框颜色",
                            D_getcolorbutton(
                                globalconfig,
                                "ocrrangecolor",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "ocrrangecolor",
                                    self.ocrrangecolor_button,
                                    callback=lambda: gobject.baseobject.textsource.setstyle(),
                                ),
                                name="ocrrangecolor_button",
                                parent=self,
                            ),
                        ],
                        [
                            "范围框宽度",
                            (
                                D_getspinbox(
                                    1,
                                    100,
                                    globalconfig,
                                    "ocrrangewidth",
                                    callback=lambda x: gobject.baseobject.textsource.setstyle(),
                                ),
                                2,
                            ),
                        ],
                        [
                            "选取OCR范围后立即进行一次识别",
                            D_getsimpleswitch(globalconfig, "ocrafterrangeselect"),
                        ],
                        [
                            "选取OCR范围后显示范围框",
                            D_getsimpleswitch(
                                globalconfig, "showrangeafterrangeselect"
                            ),
                        ],
                        [
                            "选取OCR范围后自动绑定窗口",
                            D_getsimpleswitch(globalconfig, "ocrautobindhwnd"),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    return grids
