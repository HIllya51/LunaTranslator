import functools, os
from myutils.config import globalconfig, ocrsetting, _TRL, ocrerrorfix
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getcolorbutton,
    yuitsu_switch,
    D_getsimpleswitch,
    selectcolor,
)
from qtsymbols import *
from gui.inputdialog import autoinitdialog, postconfigdialog, autoinitdialog_items
import gobject


def __label1(self):
    self.threshold1label = QLabel()
    return self.threshold1label


def __label2(self):
    self.threshold2label = QLabel()
    return self.threshold2label


def getocrgrid(self):

    grids = []
    i = 0

    self.ocrswitchs = {}
    line = []
    for name in globalconfig["ocr"]:

        _f = "./Lunatranslator/ocrengines/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue
        if name in ocrsetting:
            items = autoinitdialog_items(ocrsetting[name])
            _3 = D_getcolorbutton(
                globalconfig,
                "",
                callback=functools.partial(
                    autoinitdialog, self, globalconfig["ocr"][name]["name"], 800, items
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            )

        else:
            _3 = ""

        line += [
            ((globalconfig["ocr"][name]["name"]), 6),
            (
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
                1,
            ),
            _3,
        ]
        if i % 3 == 2:
            grids.append(line)
            line = []
        else:
            line += [""]
        i += 1
    if len(line):
        grids.append(line)

    grids += [
        [],
        [(("竖向OCR识别"), 12), D_getsimpleswitch(globalconfig, "verticalocr")],
        [(("合并多行识别结果"), 12), D_getsimpleswitch(globalconfig, "ocrmergelines")],
        [],
        [
            ("OCR预处理方法", 8),
            (
                D_getsimplecombobox(
                    _TRL(["不处理", "灰度化", "阈值二值化", "OTSU二值化"]),
                    globalconfig,
                    "ocr_presolve_method",
                ),
                12,
            ),
            "",
        ],
        [
            ("查看处理效果", 6),
            D_getcolorbutton(
                globalconfig,
                "",
                gobject.baseobject.createshowocrimage,
                icon="fa.picture-o",
                constcolor="#FF69B4",
            ),
            "",
            (("二值化阈值"), 8),
            (D_getspinbox(0, 255, globalconfig, "binary_thresh"), 4),
        ],
        [],
        [
            ("OCR自动化方法", 8),
            (
                D_getsimplecombobox(
                    _TRL(["分析图像更新", "周期执行", "分析图像更新+周期执行"]),
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
                    0.1, 100, globalconfig, "ocr_interval", double=True, step=0.1
                ),
                4,
            ),
        ],
        [
            (("图像稳定性阈值"), 8),
            (
                D_getspinbox(
                    0, 1, globalconfig, "ocr_stable_sim", double=True, step=0.01, dec=3
                ),
                4,
            ),
            (functools.partial(__label1, self), 0),
        ],
        [
            (("图像一致性阈值"), 8),
            (
                D_getspinbox(
                    0, 1, globalconfig, "ocr_diff_sim", double=True, step=0.01, dec=3
                ),
                4,
            ),
            (functools.partial(__label2, self), 0),
        ],
        [
            (("文本相似度阈值"), 8),
            (D_getspinbox(0, 100000, globalconfig, "ocr_text_diff"), 4),
        ],
        [],
        [(("多重区域模式"), 12), D_getsimpleswitch(globalconfig, "multiregion")],
        [(("记忆选定区域"), 12), D_getsimpleswitch(globalconfig, "rememberocrregions")],
        [],
        [
            (("OCR范围框颜色"), 12),
            (
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
                1,
            ),
        ],
        [
            (("OCR范围框宽度"), 12),
            (
                D_getspinbox(
                    1,
                    100,
                    globalconfig,
                    "ocrrangewidth",
                    callback=lambda x: gobject.baseobject.textsource.setstyle(),
                ),
                4,
            ),
        ],
        [
            (("选取OCR范围后立即进行一次识别"), 12),
            D_getsimpleswitch(globalconfig, "ocrafterrangeselect"),
        ],
        [
            (("选取OCR范围后显示范围框"), 12),
            D_getsimpleswitch(globalconfig, "showrangeafterrangeselect"),
        ],
        [
            (("OCR识别易错内容修正"), 12),
            D_getsimpleswitch(ocrerrorfix, "use"),
            D_getcolorbutton(
                globalconfig,
                "",
                callback=functools.partial(
                    postconfigdialog, self, ocrerrorfix["args"], "OCR识别易错内容修正"
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        ],
    ]
    return grids
