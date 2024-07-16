from qtsymbols import *
import functools, os
import gobject
from myutils.config import globalconfig, ocrsetting, _TRL, ocrerrorfix, _TR
from myutils.utils import splitocrtypes, dynamiclink
from gui.inputdialog import autoinitdialog, postconfigdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    yuitsu_switch,
    D_getcolorbutton,
    D_getsimpleswitch,
    selectcolor,
)


def __label1(self):
    self.threshold1label = QLabel()
    return self.threshold1label


def __label2(self):
    self.threshold2label = QLabel()
    return self.threshold2label


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
                    None,
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


def getocrgrid(self):

    grids = []

    offline, online = splitocrtypes()
    self.ocrswitchs = {}

    def vissolvebtn(text):
        _ = QPushButton()
        _.setText(text)
        _.clicked.connect(gobject.baseobject.createshowocrimage)
        return _

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
                            "竖向识别",
                            D_getsimpleswitch(globalconfig, "verticalocr"),
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
                    title="预处理",
                    type="grid",
                    grid=[
                        [
                            "预处理方法",
                            D_getsimplecombobox(
                                _TRL(["不处理", "灰度化", "阈值二值化", "OTSU二值化"]),
                                globalconfig,
                                "ocr_presolve_method",
                            ),
                            functools.partial(vissolvebtn, _TR("查看处理效果")),
                        ],
                        [
                            "二值化阈值",
                            D_getspinbox(0, 255, globalconfig, "binary_thresh"),
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
                            ("自动化执行方法", 7),
                            D_getIconButton(
                                callback=lambda: os.startfile(
                                    dynamiclink("{docs_server}/#/zh/ocrparam")
                                ),
                                icon="fa.question",
                            ),
                            (
                                D_getsimplecombobox(
                                    _TRL(
                                        [
                                            "分析图像更新",
                                            "周期执行",
                                            "分析图像更新+周期执行",
                                        ]
                                    ),
                                    globalconfig,
                                    "ocr_auto_method",
                                ),
                                12,
                            ),
                        ],
                        [
                            (("执行周期(s)"), 8),
                            (
                                D_getspinbox(
                                    0.1,
                                    100,
                                    globalconfig,
                                    "ocr_interval",
                                    double=True,
                                    step=0.1,
                                ),
                                4,
                            ),
                        ],
                        [
                            (("图像稳定性阈值"), 8),
                            (
                                D_getspinbox(
                                    0,
                                    1,
                                    globalconfig,
                                    "ocr_stable_sim",
                                    double=True,
                                    step=0.01,
                                    dec=3,
                                ),
                                4,
                            ),
                            (functools.partial(__label1, self), 0),
                        ],
                        [
                            (("图像一致性阈值"), 8),
                            (
                                D_getspinbox(
                                    0,
                                    1,
                                    globalconfig,
                                    "ocr_diff_sim",
                                    double=True,
                                    step=0.01,
                                    dec=3,
                                ),
                                4,
                            ),
                            (functools.partial(__label2, self), 0),
                        ],
                        [
                            (("文本相似度阈值"), 8),
                            (D_getspinbox(0, 100000, globalconfig, "ocr_text_diff"), 4),
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
                    title="其他",
                    type="grid",
                    grid=[
                        [
                            "多重区域模式",
                            D_getsimpleswitch(globalconfig, "multiregion"),
                        ],
                        [
                            "记忆选定区域",
                            D_getsimpleswitch(globalconfig, "rememberocrregions"),
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
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    return grids
