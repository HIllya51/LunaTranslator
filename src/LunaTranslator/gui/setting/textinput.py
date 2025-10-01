from qtsymbols import *
import functools, NativeUtils
import gobject, os, re
from myutils.config import globalconfig, static_data
from myutils.utils import all_langs
from traceback import print_exc
from language import Languages
from gui.setting.textinput_ocr import getocrgrid_table
from gui.gamemanager.dialog import dialog_savedgame_integrated
from gui.dynalang import LLabel, LStandardItemModel
from myutils.wrapper import Singleton
from textio.textsource.mssr import findallmodel, mssr
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    D_getdoclink,
    SuperCombo,
    VisLFormLayout,
    LDialog,
    TableViewW,
    createfoldgrid,
    getIconButton,
    manybuttonlayout,
    LinkLabel,
    makegrid,
    listediter,
    getsimplecombobox,
    yuitsu_switch,
    D_getsimpleswitch,
    getboxwidget,
    makesubtab_lazy,
    makescrollgrid,
    FocusFontCombo,
    getboxlayout,
    getsmalllabel,
)


def __create():
    selectbutton = getIconButton(
        gobject.base.createattachprocess,
        icon=globalconfig["toolbutton"]["buttons"]["selectgame"]["icon"],
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    gobject.base.selecthookbuttonstatus.connect(selectbutton.setEnabled)
    return selectbutton


def __create2():
    selecthookbutton = getIconButton(
        lambda: gobject.base.hookselectdialog.showsignal.emit(),
        icon=globalconfig["toolbutton"]["buttons"]["selecttext"]["icon"],
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    gobject.base.selecthookbuttonstatus.connect(selecthookbutton.setEnabled)
    return selecthookbutton


def gethookgrid_em(self):
    grids = [
        [D_getdoclink("embedtranslate.html")],
        [
            "清除游戏内显示的文字",
            D_getsimpleswitch(
                globalconfig["embedded"],
                "clearText",
                callback=lambda _: gobject.base.textsource.flashembedsettings(),
            ),
            "",
            "",
            "",
        ],
        [
            "显示模式",
            "",
            D_getsimplecombobox(
                ["翻译", "原文_翻译", "翻译_原文"],
                globalconfig["embedded"],
                "displaymode",
                callback=lambda _: gobject.base.textsource.flashembedsettings(),
            ),
        ],
        [
            "翻译等待时间_(s)",
            "",
            D_getspinbox(
                0,
                30,
                globalconfig["embedded"],
                "timeout_translate",
                double=True,
                step=0.1,
                callback=lambda x: gobject.base.textsource.flashembedsettings(),
            ),
        ],
        [
            "将汉字转换成繁体/日式汉字",
            D_getsimpleswitch(globalconfig["embedded"], "trans_kanji"),
        ],
        [
            "限制每行字数",
            D_getsimpleswitch(globalconfig["embedded"], "limittextlength_use"),
            D_getspinbox(
                0,
                1000,
                globalconfig["embedded"],
                "limittextlength_length",
            ),
        ],
        [
            "修改游戏字体",
            D_getsimpleswitch(
                globalconfig["embedded"],
                "changefont",
                callback=lambda _: gobject.base.textsource.flashembedsettings(),
            ),
            creategamefont_comboBox,
        ],
        [
            "内嵌安全性检查",
            D_getsimpleswitch(globalconfig["embedded"], "safecheck_use"),
            D_getIconButton(
                callback=lambda: listediter(
                    self,
                    "正则匹配",
                    globalconfig["embedded"]["safecheckregexs"],
                )
            ),
        ],
    ]

    return grids


def gethookgrid():
    grids = [
        [D_getdoclink("hooksettings.html")],
        [
            "代码页",
            (
                D_getsimplecombobox(
                    static_data["codepage_display"],
                    globalconfig,
                    "codepage_value",
                    lambda x: gobject.base.textsource.setsettings(),
                    internal=static_data["codepage_real"],
                ),
                2,
            ),
            "",
            "",
        ],
        [
            "刷新延迟_(ms)",
            (
                D_getspinbox(
                    0,
                    10000,
                    globalconfig,
                    "textthreaddelay",
                    callback=lambda x: gobject.base.textsource.setsettings(),
                ),
                2,
            ),
        ],
        [
            "最大缓冲区长度",
            (
                D_getspinbox(
                    0,
                    1000000,
                    globalconfig,
                    "maxBufferSize",
                    callback=lambda x: gobject.base.textsource.setsettings(),
                ),
                2,
            ),
        ],
        [
            "最大缓存文本长度",
            (
                D_getspinbox(
                    0,
                    1000000000,
                    globalconfig,
                    "maxHistorySize",
                    callback=lambda x: gobject.base.textsource.setsettings(),
                ),
                2,
            ),
        ],
        [
            "最大允许输出文本长度",
            (
                D_getspinbox(
                    0,
                    1000000000,
                    globalconfig,
                    "maxOutputSize",
                    default=10000,
                ),
                2,
            ),
        ],
    ]

    return grids


def creategamefont_comboBox():

    gamefont_comboBox = FocusFontCombo()

    def callback(x):
        globalconfig["embedded"].__setitem__("changefont_font", x)
        try:
            gobject.base.textsource.flashembedsettings()
        except:
            pass

    gamefont_comboBox.currentTextChanged.connect(callback)
    gamefont_comboBox.setCurrentFont(QFont(globalconfig["embedded"]["changefont_font"]))
    return gamefont_comboBox


def getTabclip():

    grids = [
        [
            dict(
                title="输入",
                grid=(
                    [
                        "排除复制自翻译器的文本",
                        D_getsimpleswitch(globalconfig, "excule_from_self"),
                    ],
                ),
            ),
        ],
        [],
        [
            dict(
                title="输出",
                grid=(
                    [
                        "自动输出文本",
                        D_getsimpleswitch(
                            globalconfig["textoutputer"]["clipboard"], "use"
                        ),
                    ],
                    [
                        dict(
                            type="grid",
                            title="内容",
                            grid=(
                                [
                                    "原文",
                                    D_getsimpleswitch(
                                        globalconfig["textoutputer"]["clipboard"],
                                        "origin",
                                    ),
                                    "",
                                    "翻译",
                                    D_getsimpleswitch(
                                        globalconfig["textoutputer"]["clipboard"],
                                        "trans",
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ],
    ]
    return grids


def selectfile(self):
    f = QFileDialog.getOpenFileNames(
        options=QFileDialog.Option.DontResolveSymlinks,
        filter="text file (*.json *.txt *.lrc *.srt *.vtt)",
    )

    res = f[0]
    if not res:
        return
    callback = functools.partial(
        yuitsu_switch,
        self,
        globalconfig["sourcestatus2"],
        "sourceswitchs",
        "filetrans",
        gobject.base.starttextsource,
    )

    try:
        callback(True)
        gobject.base.starttranslatefiles.emit(res)
    except:
        print_exc()


def createdownloadprogress(self):

    downloadprogress = QProgressBar()

    downloadprogress.setRange(0, 10000)

    downloadprogress.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )

    def __set(_d: QProgressBar, text, i):
        _d.setValue(i)
        _d.setFormat(text)

    gobject.base.connectsignal(
        gobject.base.progresssignal2, functools.partial(__set, downloadprogress)
    )
    gobject.base.connectsignal(
        gobject.base.progresssignal3, lambda x: downloadprogress.setRange(0, x)
    )
    return downloadprogress


def loadmssrsource(mssrsource: SuperCombo):
    curr = globalconfig["sourcestatus2"]["mssr"]["source"]
    sources = ["loopback"]
    vis = ["环回录制"]
    if 1:
        sources.append("i")
        vis.append("麦克风")
    else:
        sources.append("i")
        vis.append("DefaultMicrophoneInput")
        for _, _id in NativeUtils.ListEndpoints(True):
            sources.append(_id)
            vis.append("[[" + _ + "]]")
        sources.append("o")
        vis.append("DefaultSpeakerOutput")
        for _, _id in NativeUtils.ListEndpoints(False):
            sources.append(_id)
            vis.append("[[" + _ + "]]")
    mssrsource.blockSignals(True)
    mssrsource.clear()
    mssrsource.addItems(vis, internals=sources)
    mssrsource.setCurrentData(curr)
    mssrsource.blockSignals(False)


def hhfordirect(__vis, paths):

    mssrsource = D_getsimplecombobox(
        [""],
        globalconfig["sourcestatus2"]["mssr"],
        "source",
        internal=[0],
        callback=lambda _: gobject.base.textsource.init(),
    )()
    loadmssrsource(mssrsource)
    return getboxwidget(
        [
            getsmalllabel("语言"),
            D_getsimplecombobox(
                __vis,
                globalconfig["sourcestatus2"]["mssr"],
                "path",
                internal=paths,
                callback=lambda _: gobject.base.textsource.init(),
            ),
            "",
            getsmalllabel("刷新间隔"),
            D_getspinbox(
                0,
                10,
                globalconfig["sourcestatus2"]["mssr"],
                "refreshinterval",
                True,
                0.1,
            ),
            "",
            getsmalllabel("音源"),
            mssrsource,
        ]
    )


def hhforindirect():

    return getboxwidget(
        [
            getsmalllabel("刷新间隔"),
            D_getspinbox(
                0.1,
                10,
                globalconfig["sourcestatus2"]["mssr"],
                "refreshinterval2",
                True,
                0.1,
            ),
            "",
            getsmalllabel("隐藏窗口"),
            D_getsimpleswitch(
                globalconfig["sourcestatus2"]["mssr"],
                "hidewindow",
                callback=functools.partial(
                    lambda _: (gobject.base.textsource.engine.show(not _)),
                ),
            ),
            "",
            getsmalllabel("自动结束进程"),
            D_getsimpleswitch(
                globalconfig["sourcestatus2"]["mssr"],
                "autokill",
                callback=functools.partial(
                    lambda _: (gobject.base.textsource.engine.setkill(_)),
                ),
            ),
        ]
    )


def modesW(__vis, paths):
    w = QWidget()
    layout = VisLFormLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    setvisrow = lambda _: (
        layout.setRowVisible(1, _ == "direct"),
        layout.setRowVisible(2, _ == "indirect"),
    )
    layout.addRow(
        "模式",
        getsimplecombobox(
            ["直接调用", "间接读取"],
            globalconfig["sourcestatus2"]["mssr"],
            "mode",
            internal=["direct", "indirect"],
            callback=lambda _: (gobject.base.textsource.init(), setvisrow(_)),
        ),
    )
    layout.addRow(hhfordirect(__vis, paths))
    layout.addRow(hhforindirect())
    setvisrow(globalconfig["sourcestatus2"]["mssr"]["mode"])
    return w


def getsrgrid(self):
    __vis, paths = findallmodel()
    if not paths and not gobject.sys_ge_win_10:
        return [["系统不支持"]]

    if os.path.exists(mssr.lcexe):
        __w = modesW(__vis, paths)
    else:
        __w = hhfordirect(__vis, paths)
    __w.setEnabled(globalconfig["sourcestatus2"]["mssr"]["use"])

    return [
        [
            getsmalllabel("使用"),
            D_getsimpleswitch(
                globalconfig["sourcestatus2"]["mssr"],
                "use",
                name="mssr",
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["sourcestatus2"],
                    "sourceswitchs",
                    "mssr",
                    lambda _, _2: (
                        gobject.base.starttextsource(_, _2),
                        __w.setEnabled(_2),
                    ),
                ),
                pair="sourceswitchs",
            ),
            __w,
        ],
    ]


class MDLabel2(LinkLabel):
    def __init__(self, md):
        super().__init__()
        self.setText(md)
        self.setOpenExternalLinks(False)
        self.setWordWrap(True)
        self.linkActivated.connect(self._linkActivated)

    def _linkActivated(self, url: str):
        link = "http://127.0.0.1:{}{}".format(globalconfig["networktcpport"], url)
        os.startfile(link)


def getftsgrid(self):
    gobject.base.starttranslatefiles.connect(
        lambda res: gobject.base.textsource.starttranslatefiles(res)
    )
    return [
        [
            "文件",
            D_getIconButton(
                functools.partial(selectfile, self),
                icon="fa.folder-open",
            ),
            "",
            functools.partial(createdownloadprogress, self),
        ],
    ]


def getnetgrid(self):
    fuckyou = lambda _: '<a href="{}">{}</a>'.format(_, _)
    return [
        [
            "开启",
            getboxlayout(
                [
                    D_getsimpleswitch(
                        globalconfig,
                        "networktcpenable",
                        callback=lambda _: gobject.base.serviceinit(),
                    ),
                    0,
                ]
            ),
        ],
        [
            "端口号",
            getboxlayout(
                [
                    D_getspinbox(
                        0,
                        65535,
                        globalconfig,
                        "networktcpport",
                        callback=lambda _: gobject.base.serviceinit(),
                    ),
                    __portconflict,
                ]
            ),
        ],
        [
            (
                functools.partial(
                    MDLabel2,
                    ("&nbsp;" * 4).join(
                        fuckyou(_)
                        for _ in (
                            "/",
                            "/page/mainui",
                            "/page/transhist",
                            "/page/dictionary",
                            "/page/translate",
                            "/page/ocr",
                            "/page/tts",
                        )
                    ),
                ),
                0,
            )
        ],
    ]


def validator(createproxyedit_check: QLabel, text):
    regExp = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$")
    mch = regExp.match(text)
    for _ in (1,):

        if not mch:
            break
        _1, _2, _3, _4, _p = [int(_) for _ in mch.groups()]
        if _p > 65535:
            break
        if any([_ > 255 for _ in [_1, _2, _3, _4]]):
            break
        globalconfig["proxy"] = text
        createproxyedit_check.hide()
        return
    if not createproxyedit_check.isVisible():
        createproxyedit_check.show()
    createproxyedit_check.setText("Invalid")


def proxyusage():
    hbox = QHBoxLayout()
    hbox.setContentsMargins(0, 0, 0, 0)
    w2 = QWidget()
    w2.setEnabled(globalconfig["useproxy"])
    switch1 = D_getsimpleswitch(globalconfig, "useproxy", callback=w2.setEnabled)()
    hbox.addWidget(switch1)
    hbox.addWidget(QLabel())
    hbox.addWidget(w2)
    hbox.setAlignment(Qt.AlignmentFlag.AlignTop)
    vbox = VisLFormLayout(w2)
    vbox.setContentsMargins(0, 0, 0, 0)

    def __(x):
        vbox.setRowVisible(1, not x)

    vbox.addRow(
        getboxlayout(
            [
                "使用系统代理",
                D_getsimpleswitch(globalconfig, "usesysproxy", callback=__)(),
                0,
            ]
        ),
    )
    check = QLabel()
    proxy = QLineEdit(globalconfig["proxy"])
    vbox.addRow(getboxlayout(["手动设置代理", proxy, check]))
    __(globalconfig["usesysproxy"])
    validator(check, globalconfig["proxy"])
    proxy.textChanged.connect(functools.partial(validator, check))
    return hbox


def filetranslate(self):
    grids = [
        [
            functools.partial(
                createfoldgrid,
                functools.partial(getsrgrid, self),
                "语音识别",
                globalconfig["foldstatus"]["others"],
                "sr",
                leftwidget=D_getdoclink("sr.html"),
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                functools.partial(getftsgrid, self),
                "文件翻译",
                globalconfig["foldstatus"]["others"],
                "fts",
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                functools.partial(getnetgrid, self),
                "网络服务",
                globalconfig["foldstatus"]["others"],
                "netservice",
                leftwidget=D_getdoclink("apiservice.html"),
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                [["使用代理", proxyusage]],
                "代理设置",
                globalconfig["foldstatus"]["others"],
                "proxy",
            )
        ],
    ]
    return grids


def __portconflict():
    _ = LLabel()
    gobject.base.connectsignal(gobject.base.portconflict, _.setText)
    return _


@Singleton
class extralangs(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("其他语言")
        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(["语言名称", "语言代码"])
        table = TableViewW(self)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table = table

        table.insertplainrow = lambda row: self.newline(row, {"name": "", "code": ""})
        self.table = table
        for row, item in enumerate(globalconfig["extraLangs"]):
            self.newline(row, item)
        table.startObserveInserted()
        button = manybuttonlayout(
            [
                ("添加行", functools.partial(table.insertplainrow, 0)),
                ("删除行", self.table.removeselectedrows),
            ]
        )

        formLayout = QVBoxLayout(self)
        formLayout.addWidget(table)
        formLayout.addLayout(button)

        self.resize(QSize(600, 400))
        self.exec()

    def newline(self, row, item: dict):
        self.model.insertRow(
            row,
            [
                QStandardItem(item["name"]),
                QStandardItem(item["code"]),
            ],
        )

    def apply(self):
        self.table.dedumpmodel(0)
        self.table.dedumpmodel(1)
        globalconfig["extraLangs"].clear()
        for row in range(self.model.rowCount()):
            switch = self.table.getdata(row, 0)
            es = self.table.getdata(row, 1)
            if Languages.fromcode(es):
                continue
            globalconfig["extraLangs"].append(
                {
                    "name": switch,
                    "code": es,
                }
            )

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.setFocus()
        self.apply()
        srclangw: SuperCombo = self.parent().srclangw
        tgtlangw: SuperCombo = self.parent().tgtlangw
        srclangw.blockSignals(True)
        tgtlangw.blockSignals(True)
        srclangw.clear()
        tgtlangw.clear()
        srclangw.addItems(all_langs()[0], internals=all_langs()[1])
        tgtlangw.addItems(all_langs(False)[0], internals=all_langs(False)[1])
        srclangw.blockSignals(False)
        tgtlangw.blockSignals(False)
        srclangw.setCurrentData(globalconfig["srclang4"])
        tgtlangw.setCurrentData(globalconfig["tgtlang4"])


def __srclangw(self):
    self.srclangw = getsimplecombobox(
        all_langs()[0],
        globalconfig,
        "srclang4",
        internal=all_langs()[1],
    )
    return self.srclangw


def __tgtlangw(self):
    self.tgtlangw = getsimplecombobox(
        all_langs(False)[0],
        globalconfig,
        "tgtlang4",
        internal=all_langs(False)[1],
    )
    return self.tgtlangw


def setTablanglz(self):
    return [
        [
            "源语言",
            (functools.partial(__srclangw, self), 5),
            "",
            "目标语言",
            (functools.partial(__tgtlangw, self), 5),
            D_getIconButton(
                lambda: extralangs(self),
            ),
        ]
    ]


def setTabOne_lazy_h(self, basel: QVBoxLayout):
    grids = [
        [
            "选择游戏",
            __create,
            "",
            "选择文本",
            __create2,
            "",
            "游戏管理",
            D_getIconButton(
                lambda: dialog_savedgame_integrated(self),
                icon=globalconfig["toolbutton"]["buttons"]["gamepad_new"]["icon"],
            ),
            "",
        ],
        [
            (
                lambda: makesubtab_lazy(
                    ["默认设置", "内嵌翻译"],
                    [
                        lambda l: makescrollgrid(gethookgrid(), l),
                        lambda l: makescrollgrid(gethookgrid_em(self), l),
                    ],
                    delay=True,
                ),
                0,
            )
        ],
    ]
    gridlayoutwidget, do = makegrid(grids, delay=True)
    basel.addWidget(gridlayoutwidget)
    do()


def setTabOne_lazy(self, basel: QVBoxLayout):
    _rank = [
        ("texthook", "HOOK"),
        ("ocr", "OCR"),
        ("copy", "剪贴板"),
    ]
    __ = []
    for key, name in _rank:
        __.append(getsmalllabel(name))
        __.append(
            D_getsimpleswitch(
                globalconfig["sourcestatus2"][key],
                "use",
                name=key,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["sourcestatus2"],
                    "sourceswitchs",
                    key,
                    gobject.base.starttextsource,
                ),
                pair="sourceswitchs",
            )
        )
        __.append("")
    tab1grids = [
        [dict(title="语言设置", type="grid", grid=setTablanglz(self))],
        [dict(title="文本输入", type="grid", grid=[__])],
    ]
    gridlayoutwidget, do = makegrid(tab1grids, delay=True)
    basel.addWidget(gridlayoutwidget)
    titles = ["HOOK设置", "OCR设置", "剪贴板", "其他"]
    funcs = [
        lambda l: setTabOne_lazy_h(self, l),
        lambda l: getocrgrid_table(self, l),
        lambda l: makescrollgrid(getTabclip(), l),
        lambda l: makescrollgrid(filetranslate(self), l),
    ]

    tab, dotab = makesubtab_lazy(
        titles,
        funcs,
        delay=True,
    )
    basel.addWidget(tab)
    basel.setSpacing(0)
    do()
    dotab()

    def ___(k, x):
        btn: QPushButton = self.sourceswitchs.get(k)
        if not btn:
            return
        btn.setChecked(x)

    gobject.base.sourceswitchs.connect(___)
