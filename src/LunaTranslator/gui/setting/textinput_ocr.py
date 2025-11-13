from qtsymbols import *
import functools, os
from myutils.config import globalconfig, ocrsetting, ocrerrorfix
from myutils.utils import splitocrtypes, getimagefilefilter, selectdebugfile
from gui.inputdialog import postconfigdialog, autoinitdialog_items, autoinitdialog
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    getIconButton,
    yuitsu_switch,
    D_getcolorbutton,
    D_getsimpleswitch,
    clearlayout,
    D_getdoclink,
    ClickableLabel,
    getboxlayout,
    createfoldgrid,
    TableViewW,
    saveposwindow,
    check_grid_append,
    pixmapviewer,
    LStandardItemModel,
    SuperCombo,
    NQGroupBox,
    getsmalllabel,
    manybuttonlayout,
    makesubtab_lazy,
    makescrollgrid,
)
from traceback import print_exc
from myutils.keycode import vkcode_map
import gobject, qtawesome, importlib
from gui.dynalang import LFormLayout, LDialog, LAction, LLabel
from myutils.ocrutil import ocr_end, ocr_init, ocr_run
from myutils.wrapper import threader, Singleton
from gui.setting.about import offlinelinks
from ocrengines.baseocrclass import OCRResultParsed


def __label1(self):
    threshold1label = QLabel()
    gobject.base.connectsignal(gobject.base.thresholdsett1, threshold1label.setText)
    return threshold1label


def __label2(self):
    threshold2label = QLabel()
    gobject.base.connectsignal(gobject.base.thresholdsett2, threshold2label.setText)
    return threshold2label


@threader
def __directinitend(_, _ok):
    if _ok:
        ocr_init()
    else:
        ocr_end()


@Singleton
class triggereditor(LDialog):
    def showmenu(self, p: QPoint):
        curr = self.hctable.currentIndex()
        r = curr.row()
        if r < 0:
            return
        menu = QMenu(self.hctable)
        remove = LAction("删除", menu)
        menu.addAction(remove)
        action = menu.exec(self.hctable.cursor().pos())

        if action == remove:
            self.hctable.removeselectedrows()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.list: "list[dict]" = globalconfig["ocr_trigger_events"]

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
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setWordWrap(False)
        table.setModel(model)
        table.getindexdata = self.__getindexwidgetdata
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.showmenu)
        self.hctable = table
        self.internalrealname = []
        formLayout = QVBoxLayout(self)
        formLayout.addWidget(self.hctable)
        self.vkeys = list(vkcode_map.keys())
        for row, k in enumerate(self.list):  # 2
            self.hcmodel.insertRow(row, [QStandardItem(), QStandardItem()])
            combo = SuperCombo()
            combo.addItems(self.vkeys, internals=self.vkeys)
            combo.setCurrentData(k.get("vkey"))
            self.hctable.setIndexWidget(self.hcmodel.index(row, 0), combo)
            combo = SuperCombo()
            combo.addItems(["按下", "松开"])
            combo.setCurrentIndex(k.get("event", 0))
            self.hctable.setIndexWidget(self.hcmodel.index(row, 1), combo)
        buttons = manybuttonlayout(
            (("添加行", self.click1), ("删除行", self.hctable.removeselectedrows))
        )
        formLayout.addLayout(buttons)
        self.resize(600, self.sizeHint().height())
        self.show()

    def __getindexwidgetdata(self, index: QModelIndex):
        return self.hctable.indexWidgetX(index).currentIndex()

    def closeEvent(self, a0: QCloseEvent) -> None:
        rows = self.hcmodel.rowCount()
        self.list.clear()
        for row in range(rows):
            i0 = self.hctable.getdata(row, 0)
            i1 = self.hctable.getdata(row, 1)
            self.list.append({"vkey": self.vkeys[i0], "event": i1})

    def click1(self):
        self.hcmodel.insertRow(0, [QStandardItem(), QStandardItem()])
        combo = SuperCombo()
        combo.addItems(self.vkeys)
        self.hctable.setIndexWidget(self.hcmodel.index(0, 0), combo)
        combo = SuperCombo()
        combo.addItems(["按下", "松开"])
        self.hctable.setIndexWidget(self.hcmodel.index(0, 1), combo)


def safeloadfunction(p, args, file, func, name):
    try:
        func = getattr(importlib.import_module(file), func)
        func(p, args, name)
    except:
        print_exc()


def checkclickable(name: ClickableLabel):
    name.setClickable(globalconfig["useproxy"])


def renameapi(qlabel: QLabel, apiuid):
    menu = QMenu(qlabel)
    useproxy = LAction("使用代理", menu)
    useproxy.setCheckable(True)

    menu.addAction(useproxy)
    useproxy.setChecked(globalconfig["ocr"][apiuid].get("useproxy", True))
    pos = QCursor.pos()
    action = menu.exec(pos)

    if action == useproxy:
        globalconfig["ocr"][apiuid]["useproxy"] = useproxy.isChecked()


def getrenameablellabel(uid):
    if globalconfig["ocr"][uid].get("type") in ("offline",):
        return LLabel(globalconfig["ocr"][uid]["name"])
    name = ClickableLabel(globalconfig["ocr"][uid]["name"])
    fn = functools.partial(renameapi, name, uid)
    name.clicked.connect(fn)
    name.beforeEnter.connect(functools.partial(checkclickable, name))
    return name


def initgridsources(self, names):
    line = []
    i = 0
    grids_source = []
    for name in names:
        _f = "Lunatranslator/ocrengines/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue
        if globalconfig["ocr"][name].get("argstype", None):
            _3 = D_getIconButton(
                callback=functools.partial(
                    safeloadfunction,
                    self,
                    ocrsetting[name]["args"],
                    "ocrengines." + name,
                    globalconfig["ocr"][name].get("argstype", None),
                    globalconfig["ocr"][name]["name"],
                )
            )
        elif name == "selfbuild":
            _3 = D_getIconButton(
                callback=lambda: selectdebugfile("selfbuild_ocr.py"),
                icon="fa.edit",
            )
        elif name in ocrsetting:
            items = autoinitdialog_items(ocrsetting[name])
            _3 = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    ocrsetting[name]["args"],
                    globalconfig["ocr"][name]["name"],
                    800,
                    items,
                    "ocrengines." + name,
                    name,
                )
            )
        else:
            _3 = ""

        line += [
            functools.partial(getrenameablellabel, name),
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
    check_grid_append(grids_source)

    return grids_source


def _ocrparam_create(self, f):
    clearlayout(self._ocrparaml)
    if f == "period":
        self._ocrparaml.addRow(
            "执行周期_(s)",
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
    if f == "trigger":
        self._ocrparaml.addRow(
            "触发事件",
            getboxlayout([D_getIconButton(functools.partial(triggereditor, self))]),
        )
        self._ocrparaml.addRow(
            "延迟_(s)",
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
    if f in ["analysis", "trigger"]:
        self._ocrparaml.addRow(
            "图像稳定性阈值",
            getboxlayout(
                [
                    D_getspinbox(
                        0,
                        1,
                        globalconfig,
                        ("ocr_stable_sim_v2", "ocr_stable_sim2_v2")[f == "trigger"],
                        double=True,
                        step=0.001,
                    ),
                    functools.partial(__label1, self),
                ]
            ),
        )
    if f == "analysis":
        self._ocrparaml.addRow(
            "图像一致性阈值",
            getboxlayout(
                [
                    D_getspinbox(
                        0,
                        1,
                        globalconfig,
                        "ocr_diff_sim_v2",
                        double=True,
                        step=0.001,
                    ),
                    functools.partial(__label2, self),
                ]
            ),
        )
    self._ocrparaml.addRow(
        "文本相似度阈值",
        getboxlayout([D_getspinbox(0, 100000, globalconfig, "ocr_text_diff"), QLabel]),
    )


def _ocrparam(self):
    self._ocrparam = NQGroupBox()
    self._ocrparaml = LFormLayout(self._ocrparam)
    _ocrparam_create(self, globalconfig["ocr_auto_method_v2"])
    return self._ocrparam


@Singleton
class showocrimage(saveposwindow):
    def closeEvent(self, e):
        super().closeEvent(e)
        self.deleteLater()

    def openff(self):
        f = QFileDialog.getOpenFileName(filter=getimagefilefilter())
        res = f[0]
        if not res:
            return
        self.ocrfile(res)

    def ocrfile(self, res):
        img = QImage(res)
        if img.isNull():
            return
        self.originimage = img
        self.setimagefunction(img)
        result = ocr_run(img)
        result = result.maybeerror()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if len(files):
            self.ocrfile(files[0])

    def __init__(self, parent):
        self.originimage = None
        super().__init__(parent, poslist=globalconfig["showocrgeo"])
        self.setWindowIcon(qtawesome.icon("fa.picture-o"))
        self.setWindowTitle("查看")
        self.originlabel = pixmapviewer()
        qw = QWidget()
        self.layout1 = QVBoxLayout(qw)
        self.setAcceptDrops(True)
        self.setCentralWidget(qw)
        icon = getIconButton(callback=self.openff, icon="fa.file-image-o")
        button = getIconButton(callback=self.retest, icon="fa.rotate-right")
        button2 = getIconButton(callback=self.retest2, icon="fa.rotate-right")
        hb = QHBoxLayout()
        hb.addWidget(icon)
        hb.addWidget(button)
        hb.addWidget(button2)
        self.dial = QSpinBox(self)
        self.dial.setRange(0, 359)
        self.dial.setWrapping(True)
        self.dial.valueChanged.connect(self.onValueChanged)
        self.dial.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        hb.addWidget(self.dial)
        self.layout1.addLayout(hb)
        self.timecost = QLabel()
        self.timecost.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.layout1.addWidget(self.timecost)
        self.layout1.addWidget(self.originlabel)
        gobject.base.connectsignal(gobject.base.setimage, self.setimagefunction)
        gobject.base.connectsignal(gobject.base.setresult, self.setocr)
        self.show()

    def onValueChanged(self, value):
        if not self.originimage:
            return
        transform = QTransform()
        transform.rotate(value)
        rotated_image = self.originimage.transformed(transform)
        self.originlabel.showpixmap(QPixmap.fromImage(rotated_image))

    def retest2(self):
        gobject.base.textgetmethod(self.retest(), is_auto_run=False)

    def retest(self):
        if self.originimage is None:
            return
        transform = QTransform()
        transform.rotate(self.dial.value())
        result = ocr_run(self.originimage.transformed(transform))
        return result.maybeerror()

    def setimagefunction(self, originimage):
        self.originimage = originimage
        self.originlabel.showpixmap(QPixmap.fromImage(originimage))

    def setocr(self, result: OCRResultParsed):
        self.timecost.setText("time: {}".format(result.timecost))
        self.originlabel.showboxtext(result.result)


def internal(self):
    offline, online, other = splitocrtypes(globalconfig["ocr"], other=True)
    offgrids = initgridsources(self, offline)
    offgrids += [
        [(functools.partial(offlinelinks, "ocr"), 0)],
    ]
    engines = [
        [
            dict(
                title="离线",
                type="grid",
                grid=offgrids,
                button=D_getdoclink("useapis/ocrapi.html#anchor-offline"),
            )
        ],
        [
            dict(
                title="在线",
                type="grid",
                grid=initgridsources(self, online),
                button=D_getdoclink("useapis/ocrapi.html#anchor-online"),
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                initgridsources(self, other),
                "其他",
                d=globalconfig["foldstatus"]["ocr"],
                k="other",
            )
        ],
        [
            D_getIconButton(
                callback=lambda: showocrimage(self), icon="fa.picture-o", tips="查看"
            ),
            "",
        ],
    ]
    autorun = [
        [
            "自动化执行方法",
            getboxlayout(
                [
                    D_getsimplecombobox(
                        [
                            "分析图像更新",
                            "周期执行",
                            "鼠标键盘触发+等待稳定",
                        ],
                        globalconfig,
                        "ocr_auto_method_v2",
                        internal=["analysis", "period", "trigger"],
                        callback=functools.partial(_ocrparam_create, self),
                    ),
                ]
            ),
        ],
        [functools.partial(_ocrparam, self)],
    ]
    reco = [
        [
            "识别方向",
            D_getsimplecombobox(
                ["横向", "竖向", "自适应"], globalconfig, "verticalocr"
            ),
            "",
            "合并临近行",
            D_getsimpleswitch(globalconfig, "ocrmergelines"),
            getsmalllabel("距离"),
            D_getspinbox(
                0, 3, globalconfig, "ocrmergelines_distance", double=True, step=0.01
            ),
            getsmalllabel("x"),
            "",
            "",
            "",
        ],
        [
            "多重区域模式",
            D_getsimpleswitch(
                globalconfig,
                "multiregion",
                callback=lambda _: gobject.base.textsource.leaveone(),
            ),
            "",
            "易错内容修正",
            D_getsimpleswitch(ocrerrorfix, "use"),
            D_getIconButton(
                callback=functools.partial(
                    postconfigdialog,
                    self,
                    ocrerrorfix["args"]["替换内容"],
                    "易错内容修正",
                    ["原文内容", "替换为"],
                )
            ),
        ],
    ]

    others = [
        [
            "范围框颜色",
            D_getcolorbutton(
                self,
                globalconfig,
                "ocrrangecolor",
                callback=lambda _: gobject.base.textsource.setstyle(),
            ),
            "",
            "范围框宽度",
            D_getspinbox(
                1,
                100,
                globalconfig,
                "ocrrangewidth",
                callback=lambda _: gobject.base.textsource.setstyle(),
            ),
            "",
            "",
            "",
        ],
        [
            "选取OCR范围后显示范围框",
            D_getsimpleswitch(globalconfig, "showrangeafterrangeselect"),
        ],
    ]
    allothers = [
        [dict(title="识别设置", type="grid", grid=reco)],
        [dict(title="自动化执行", grid=autorun, button=D_getdoclink("ocrparam.html"))],
        [dict(title="其他设置", type="grid", grid=others)],
    ]

    return makesubtab_lazy(
        ["OCR引擎", "其他设置"],
        [
            lambda l: makescrollgrid(engines, l),
            lambda l: makescrollgrid(allothers, l),
        ],
        delay=True,
    )


def getocrgrid_table(self, basel: QVBoxLayout):

    self.ocrswitchs = {}

    gridlayoutwidget, do = internal(self)
    basel.addWidget(gridlayoutwidget)
    do()
