from qtsymbols import *
import functools, os
from myutils.config import globalconfig, ocrsetting, ocrerrorfix, static_data
from myutils.utils import splitocrtypes, dynamiclink
from gui.inputdialog import autoinitdialogx, postconfigdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    getIconButton,
    yuitsu_switch,
    D_getcolorbutton,
    D_getsimpleswitch,
    clearlayout,
    getboxlayout,
    selectcolor,
    TableViewW,
    saveposwindow,
    pixmapviewer,
    LStandardItemModel,
    LFocusCombo,
    threebuttons,
)
import gobject, qtawesome
from gui.dynalang import LFormLayout, LDialog, LAction
from myutils.ocrutil import ocr_end, ocr_init, ocr_run
from myutils.wrapper import threader, Singleton_close


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


@Singleton_close
class triggereditor(LDialog):
    def showmenu(self, p: QPoint):
        curr = self.hctable.currentIndex()
        r = curr.row()
        if r < 0:
            return
        menu = QMenu(self.hctable)
        remove = LAction("删除")
        menu.addAction(remove)
        action = menu.exec(self.hctable.cursor().pos())

        if action == remove:
            self.hctable.removeselectedrows()

    def moverank(self, dy):
        src, tgt = self.hctable.moverank(dy)
        self.internalrealname.insert(tgt, self.internalrealname.pop(src))

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.list = globalconfig["ocr_trigger_events"]

        self.setWindowTitle("触发事件")
        model = LStandardItemModel()
        model.setHorizontalHeaderLabels(["按键", "事件"])
        self.hcmodel = model
        table = TableViewW()
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        table.setModel(model)

        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.showmenu)
        self.hctable = table
        self.internalrealname = []
        formLayout = QVBoxLayout()
        self.setLayout(formLayout)
        formLayout.addWidget(self.hctable)
        self.vkeys = list(static_data["vkcode_map"].keys())
        for row, k in enumerate(self.list):  # 2
            self.hcmodel.insertRow(row, [QStandardItem(), QStandardItem()])
            combo = LFocusCombo()
            combo.addItems(self.vkeys)
            combo.setCurrentIndex(self.vkeys.index(k["vkey"]))
            self.hctable.setIndexWidget(self.hcmodel.index(row, 0), combo)
            combo = LFocusCombo()
            combo.addItems(["按下", "松开"])
            combo.setCurrentIndex(k["event"])
            self.hctable.setIndexWidget(self.hcmodel.index(row, 1), combo)
        self.buttons = threebuttons(texts=["添加行", "删除行"])
        self.buttons.btn1clicked.connect(self.click1)
        self.buttons.btn2clicked.connect(self.hctable.removeselectedrows)

        formLayout.addWidget(self.buttons)
        self.resize(600, self.sizeHint().height())
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        rows = self.hcmodel.rowCount()
        self.list.clear()
        for row in range(rows):
            i0 = self.hctable.indexWidgetX(row, 0).currentIndex()
            i1 = self.hctable.indexWidgetX(row, 1).currentIndex()
            self.list.append({"vkey": self.vkeys[i0], "event": i1})

    def click1(self):
        self.hcmodel.insertRow(0, [QStandardItem(), QStandardItem()])
        combo = LFocusCombo()
        combo.addItems(self.vkeys)
        self.hctable.setIndexWidget(self.hcmodel.index(0, 0), combo)
        combo = LFocusCombo()
        combo.addItems(["按下", "松开"])
        self.hctable.setIndexWidget(self.hcmodel.index(0, 1), combo)


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
                    autoinitdialogx,
                    self,
                    ocrsetting[name]["args"],
                    globalconfig["ocr"][name]["name"],
                    800,
                    items,
                    "ocrengines." + name,
                    name,
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
            "触发事件",
            getboxlayout(
                [
                    D_getIconButton(
                        functools.partial(triggereditor, self),
                        "fa.gear",
                    ),
                ]
            ),
        )
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


@Singleton_close
class showocrimage(saveposwindow):
    setimage = pyqtSignal(QImage)

    def closeEvent(self, e):
        gobject.baseobject.showocrimage = None
        super().closeEvent(e)

    def openff(self):
        f = QFileDialog.getOpenFileName(
            filter="image ("
            + " ".join(
                ["*" + _.data().decode() for _ in QImageWriter.supportedImageFormats()]
            )
            + ")"
        )
        res = f[0]
        if not res:
            return
        img = QImage(res)
        if img.isNull():
            return
        self.originimage = img
        self.setimagefunction(img)
        text, infotype = ocr_run(img)
        if infotype:
            gobject.baseobject.displayinfomessage(text, infotype)
        else:
            gobject.baseobject.textgetmethod(text, False)

    def __init__(self, parent, cached):
        self.img1 = None
        self.originimage = None
        super().__init__(parent, poslist=globalconfig["showocrgeo"])
        self.setWindowIcon(qtawesome.icon("fa.picture-o"))
        self.setWindowTitle("截图")
        self.originlabel = pixmapviewer()
        qw = QWidget()
        self.layout1 = QVBoxLayout()
        self.setCentralWidget(qw)
        qw.setLayout(self.layout1)
        icon = getIconButton(callback=self.openff, icon="fa.folder-open")
        button = getIconButton(callback=self.retest, icon="fa.rotate-right")
        hb = QHBoxLayout()
        hb.addWidget(icon)
        hb.addWidget(button)
        self.layout1.addLayout(hb)
        self.layout1.addWidget(self.originlabel)
        self.setimage.connect(self.setimagefunction)
        if cached:
            self.setimagefunction(cached)

    def retest(self):
        if self.originimage is None:
            return

        text, infotype = ocr_run(self.originimage)
        if infotype:
            gobject.baseobject.displayinfomessage(text, infotype)
        else:
            gobject.baseobject.textgetmethod(text, False)

    def setimagefunction(self, originimage):
        self.originimage = originimage
        self.img1 = QPixmap.fromImage(originimage)
        self.originlabel.showpixmap(self.img1)


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
                            "",
                            D_getIconButton(
                                gobject.baseobject.createshowocrimage,
                                icon="fa.picture-o",
                            ),
                            "",
                            "",
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
