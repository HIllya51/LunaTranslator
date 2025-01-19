from qtsymbols import *
import functools, os, json
import windows, gobject
from myutils.utils import translate_exits, getannotatedapiname
from myutils.config import (
    globalconfig,
    _TR,
    savehook_new_data,
    get_launchpath,
    savehook_new_list,
    get_platform,
)
from textsource.texthook import codepage_display
from traceback import print_exc
from gui.pretransfile import sqlite2json2
from language import TransLanguages
from gui.setting_textinput_ocr import getocrgrid_table
from gui.dialog_savedgame import dialog_savedgame_integrated
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getIconButton,
    getIconButton,
    makegrid,
    listediter,
    yuitsu_switch,
    D_getsimpleswitch,
    makesubtab_lazy,
    makescrollgrid,
    FocusCombo,
    FocusFontCombo,
    getsmalllabel,
)
from gui.dynalang import LDialog, LFormLayout


def __create(self):
    self.selectbutton = getIconButton(
        gobject.baseobject.createattachprocess,
        icon=globalconfig["toolbutton"]["buttons"]["selectgame"]["icon"],
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    return self.selectbutton


def __create2(self):
    self.selecthookbutton = getIconButton(
        lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
        icon=globalconfig["toolbutton"]["buttons"]["selecttext"]["icon"],
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    return self.selecthookbutton


def gethookgrid_em(self):
    alltrans, alltransvis = loadvalidtss()
    grids = [
        [
            "显示模式",
            "",
            D_getsimplecombobox(
                ["翻译", "原文_翻译", "翻译_原文"],
                globalconfig["embedded"],
                "displaymode",
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
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
                callback=lambda x: gobject.baseobject.textsource.flashembedsettings(),
            ),
        ],
        [
            "使用指定翻译器",
            D_getsimpleswitch(globalconfig["embedded"], "use_appointed_translate"),
            D_getsimplecombobox(
                alltransvis,
                globalconfig["embedded"],
                "translator_2",
                internal=alltrans,
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
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
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
                ),
                icon="fa.gear",
            ),
        ],
        [
            "导出翻译补丁",
            D_getIconButton(
                callback=lambda: exportchspatch(self),
                icon="fa.gear",
            ),
            "",
            "",
        ],
    ]

    return grids


def gethookgrid(self):
    grids = [
        [
            "代码页",
            (
                D_getsimplecombobox(
                    codepage_display,
                    globalconfig,
                    "codepage_index",
                    lambda x: gobject.baseobject.textsource.setsettings(),
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
                    callback=lambda x: gobject.baseobject.textsource.setsettings(),
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
                    callback=lambda x: gobject.baseobject.textsource.setsettings(),
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
                    callback=lambda x: gobject.baseobject.textsource.setsettings(),
                ),
                2,
            ),
        ],
    ]

    return grids


def doexportchspatch(exe, gameuid):

    b = windows.GetBinaryType(exe)
    is64 = b == 6
    arch = ["32", "64"][is64]

    dllhook = os.path.abspath("./files/plugins/LunaHook/LunaHook{}.dll".format(arch))
    dllhost = os.path.abspath(
        "./files/plugins/LunaHook/LunaHost{}.dll".format(arch, arch)
    )
    runner = os.path.abspath("./files/plugins/shareddllproxy{}.exe".format(arch))

    windows.CopyFile(
        dllhook, os.path.join(os.path.dirname(exe), os.path.basename(dllhook)), False
    )
    windows.CopyFile(
        dllhost, os.path.join(os.path.dirname(exe), os.path.basename(dllhost)), False
    )
    windows.CopyFile(runner, os.path.join(os.path.dirname(exe), "LunaPatch.exe"), False)

    embedconfig = {
        "translation_file": "translation.json",
        "target_exe": os.path.basename(exe),
        "target_exe2": os.path.basename(exe),
        "startup_argument": None,
        "inject_timeout": 1000,
        "embedhook": savehook_new_data[gameuid]["embedablehook"],
        "embedsettings": globalconfig["embedded"],
    }
    try:
        with open(
            os.path.join(os.path.dirname(exe), "LunaPatch.json"), "w", encoding="utf8"
        ) as ff:
            ff.write(json.dumps(embedconfig, ensure_ascii=False, indent=4))
    except:
        pass


def selectgameuid(self):

    dialog = LDialog(self, Qt.WindowType.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle("选择游戏")
    dialog.resize(QSize(800, 10))
    formLayout = LFormLayout(dialog)
    _internal = []
    _vis = []
    for gameuid in savehook_new_list:
        if not savehook_new_data[gameuid]["embedablehook"]:
            continue
        exe = get_launchpath(gameuid)
        if not exe.lower().endswith(".exe"):
            continue
        if not os.path.exists(exe):
            continue
        _vis.append(savehook_new_data[gameuid]["title"])
        _internal.append(gameuid)

    combo = FocusCombo()
    combo.addItems(_vis)

    formLayout.addRow("选择游戏", combo)

    button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)
    button.accepted.connect(dialog.accept)
    button.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
    button.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
    if dialog.exec():
        if not _internal:
            return None
        return _internal[combo.currentIndex()]


def exportchspatch(self):
    gameuid = selectgameuid(self)
    if gameuid is None:
        return
    exe = get_launchpath(gameuid)
    doexportchspatch(exe, gameuid)

    f = QFileDialog.getOpenFileName(
        self,
        caption=_TR("选择预翻译文件"),
        directory="translation_record",
        filter="*.sqlite",
    )
    sqlfname_all = f[0]
    if not sqlfname_all:
        return
    sqlite2json2(
        self,
        sqlfname_all,
        os.path.join(os.path.dirname(exe), "translation.json"),
        existsmerge=True,
        isforembed=True,
    )


def creategamefont_comboBox():

    gamefont_comboBox = FocusFontCombo()

    def callback(x):
        globalconfig["embedded"].__setitem__("changefont_font", x)
        try:
            gobject.baseobject.textsource.flashembedsettings()
        except:
            pass

    gamefont_comboBox.currentTextChanged.connect(callback)
    gamefont_comboBox.setCurrentFont(QFont(globalconfig["embedded"]["changefont_font"]))
    return gamefont_comboBox


def sortAwithB(l1, l2):
    sorted_pairs = sorted(zip(l1, l2))
    return [x[1] for x in sorted_pairs], [x[0] for x in sorted_pairs]


def loadvalidtss():

    alltransvis = []
    alltrans = []
    for x in globalconfig["fanyi"]:
        if x == "premt":
            continue
        if not translate_exits(x):
            continue
        alltransvis.append(getannotatedapiname(x))
        alltrans.append(x)
    return sortAwithB(alltransvis, alltrans)


def getTabclip(self):

    grids = [
        [
            "排除复制自翻译器的文本",
            D_getsimpleswitch(globalconfig, "excule_from_self"),
            "",
            "",
        ]
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
        gobject.baseobject.starttextsource,
    )

    try:
        callback(True)
        gobject.baseobject.textsource.starttranslatefile(res)
    except:
        print_exc()


def createdownloadprogress(self):

    downloadprogress = QProgressBar()

    downloadprogress.setRange(0, 10000)

    downloadprogress.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )

    def __set(_d, text, i):
        _d.setValue(i)
        _d.setFormat(text)

    self.progresssignal2.connect(functools.partial(__set, downloadprogress))
    self.progresssignal3.connect(lambda x: downloadprogress.setRange(0, x))
    return downloadprogress


def filetranslate(self):
    alltrans, alltransvis = loadvalidtss()
    grids = [
        [
            (
                dict(
                    title="文件翻译",
                    type="grid",
                    grid=[
                        [
                            "文件",
                            D_getIconButton(
                                functools.partial(selectfile, self),
                                icon="fa.folder-open",
                            ),
                        ],
                        [(functools.partial(createdownloadprogress, self), 0)],
                        [],
                        [
                            "使用指定翻译器",
                            D_getsimpleswitch(globalconfig, "use_appointed_translate"),
                            D_getsimplecombobox(
                                alltransvis,
                                globalconfig,
                                "translator_2",
                                internal=alltrans,
                            ),
                        ],
                    ],
                ),
                0,
                "group",
            ),
        ],
    ]
    return grids


def outputgrid(self):

    grids = [
        [
            (
                dict(
                    title="输出的内容",
                    grid=(
                        [
                            "原文",
                            D_getsimpleswitch(globalconfig, "textoutput_origin"),
                        ],
                        [
                            "翻译",
                            D_getsimpleswitch(globalconfig, "textoutput_trans"),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [],
        [
            (
                dict(
                    title="剪贴板",
                    grid=(
                        [
                            "自动输出",
                            D_getsimpleswitch(
                                globalconfig["textoutputer"]["clipboard"], "use"
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="WebSocket",
                    grid=(
                        [
                            "自动输出",
                            D_getsimpleswitch(
                                globalconfig["textoutputer"]["websocket"],
                                "use",
                                callback=lambda _: gobject.baseobject.startoutputer_re(
                                    "websocket"
                                ),
                            ),
                        ],
                        [
                            "端口号",
                            D_getspinbox(
                                0,
                                65535,
                                globalconfig["textoutputer"]["websocket"],
                                "port",
                                callback=lambda _: gobject.baseobject.startoutputer_re(
                                    "websocket"
                                ),
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    return grids


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
    if get_platform() == "xp":
        _rank.pop(1)
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
                    gobject.baseobject.starttextsource,
                ),
                pair="sourceswitchs",
            )
        )
        __.append("")
    tab1grids = [
        [
            (
                dict(title="语言设置", type="grid", grid=setTablanglz()),
                0,
                "group",
            ),
        ],
        [
            (
                dict(title="文本输入", type="grid", grid=[__]),
                0,
                "group",
            ),
        ],
    ]
    gridlayoutwidget, do = makegrid(tab1grids, delay=True)
    basel.addWidget(gridlayoutwidget)
    titles = ["HOOK设置", "OCR设置", "剪贴板", "其他", "文本输出"]
    funcs = [
        lambda l: setTabOne_lazy_h(self, l),
        lambda l: getocrgrid_table(self, l),
        lambda l: makescrollgrid(getTabclip(self), l),
        lambda l: makescrollgrid(filetranslate(self), l),
        lambda l: makescrollgrid(outputgrid(self), l),
    ]

    if get_platform() == "xp":
        titles.pop(1)
        funcs.pop(1)
    tab, dotab = makesubtab_lazy(
        titles,
        funcs,
        delay=True,
    )
    basel.addWidget(tab)
    do()
    dotab()
