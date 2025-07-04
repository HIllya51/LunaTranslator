from qtsymbols import *
import functools, NativeUtils
import gobject, os
from myutils.config import globalconfig, static_data
from traceback import print_exc
from language import TransLanguages
from gui.setting.textinput_ocr import getocrgrid_table
from gui.gamemanager.dialog import dialog_savedgame_integrated
from gui.dynalang import LLabel
from textio.textsource.mssr import findallmodel
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    D_getdoclink,
    SuperCombo,
    VisLFormLayout,
    getIconButton,
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


def __create(self):
    selectbutton = getIconButton(
        gobject.base.createattachprocess,
        icon=globalconfig["toolbutton"]["buttons"]["selectgame"]["icon"],
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    gobject.base.selecthookbuttonstatus.connect(selectbutton.setEnabled)
    return selectbutton


def __create2(self):
    selecthookbutton = getIconButton(
        lambda: gobject.base.hookselectdialog.showsignal.emit(),
        icon=globalconfig["toolbutton"]["buttons"]["selecttext"]["icon"],
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    gobject.base.selecthookbuttonstatus.connect(selecthookbutton.setEnabled)
    return selecthookbutton


def gethookgrid_em(self):
    grids = [
        [D_getdoclink("/embedtranslate.html")],
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


def gethookgrid(self):
    grids = [
        [D_getdoclink("/hooksettings.html")],
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
    f = QFileDialog.getOpenFileName(
        options=QFileDialog.Option.DontResolveSymlinks,
        filter="text file (*.json *.txt *.lrc *.srt *.vtt)",
    )

    res = f[0]
    if res == "":
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
        gobject.base.textsource.starttranslatefile(res)
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


def __srcofig(grids: list, self):
    __vis, paths = findallmodel()
    if not paths and not gobject.sys_ge_win_10:
        return

    if os.path.exists(r"C:\Windows\System32\LiveCaptions.exe"):
        __w = modesW(__vis, paths)
    else:
        __w = hhfordirect(__vis, paths)
    __w.setEnabled(globalconfig["sourcestatus2"]["mssr"]["use"])

    __ = dict(
        type="grid",
        title="语音识别",
        button=D_getdoclink("/sr.html"),
        grid=[
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
        ],
    )
    grids.insert(0, [__])


class MDLabel2(QLabel):
    def __init__(self, md):
        super().__init__()
        self.setText(md)
        self.setOpenExternalLinks(False)
        self.setWordWrap(True)
        self.linkActivated.connect(self._linkActivated)

    def _linkActivated(self, url: str):
        link = "http://127.0.0.1:{}{}".format(globalconfig["networktcpport"], url)
        os.startfile(link)


def filetranslate(self):
    fuckyou = lambda _: '<a href="{}">{}</a>'.format(_, _)
    grids = [
        [
            dict(
                type="grid",
                title="文件翻译",
                grid=[
                    [
                        "文件",
                        D_getIconButton(
                            functools.partial(selectfile, self),
                            icon="fa.folder-open",
                        ),
                        "",
                        functools.partial(createdownloadprogress, self),
                    ],
                ],
            ),
        ],
        [],
        [
            dict(
                title="网络服务",
                button=D_getdoclink("/apiservice.html"),
                grid=[
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
                                functools.partial(__portconflict, self),
                            ]
                        ),
                    ],
                    [],
                    [
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
                        )
                    ],
                ],
            ),
        ],
    ]
    __srcofig(grids, self)
    return grids


def getpath():
    for syspath in [
        globalconfig["chromepath"],
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]:
        if os.path.exists(syspath) and os.path.isfile(syspath):
            return syspath
    return None


def __portconflict(self):
    _ = LLabel()
    gobject.base.connectsignal(gobject.base.portconflict, _.setText)
    return _


def setTablanglz():
    return [
        [
            "源语言",
            (
                D_getsimplecombobox(
                    ["自动"] + [_.zhsname for _ in TransLanguages],
                    globalconfig,
                    "srclang4",
                    internal=["auto"] + [_.code for _ in TransLanguages],
                ),
                5,
            ),
            "",
            "目标语言",
            (
                D_getsimplecombobox(
                    [_.zhsname for _ in TransLanguages],
                    globalconfig,
                    "tgtlang4",
                    internal=[_.code for _ in TransLanguages],
                ),
                5,
            ),
        ]
    ]


def setTabOne_lazy_h(self, basel: QVBoxLayout):
    grids = [
        [
            "选择游戏",
            functools.partial(__create, self),
            "",
            "选择文本",
            functools.partial(__create2, self),
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
                        lambda l: makescrollgrid(gethookgrid(self), l),
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
        [dict(title="语言设置", type="grid", grid=setTablanglz())],
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

    def __(k, x):
        btn: QPushButton = self.sourceswitchs.get(k)
        if not btn:
            return
        btn.setChecked(x)

    gobject.base.sourceswitchs.connect(__)
