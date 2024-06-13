from qtsymbols import *
import functools, os, json
import windows, gobject
from myutils.utils import makehtml, getfilemd5
from myutils.config import (
    globalconfig,
    _TR,
    _TRL,
    savehook_new_data,
    savehook_new_list,
    static_data,
)
from gui.pretransfile import sqlite2json2
from gui.codeacceptdialog import codeacceptdialog
from gui.setting_textinput_ocr import getocrgrid
from gui.dialog_savedgame import dialog_savedgame_integrated
from gui.inputdialog import regexedit
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getspinbox,
    D_getcolorbutton,
    makegrid,
    yuitsu_switch,
    getvboxwidget,
    D_getsimpleswitch,
    makesubtab_lazy,
    makescrollgrid,
    FocusCombo
)


def gethookgrid(self):

    grids = [
        [
            ("获取最新提取器核心&错误反馈&游戏支持", 8),
            (makehtml("https://github.com/HIllya51/LunaHook"), 8, "link"),
        ],
        [],
        [
            ("选择游戏", 5),
            D_getcolorbutton(
                globalconfig,
                "",
                gobject.baseobject.createattachprocess,
                name="selectbutton",
                parent=self,
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
            ("", 5),
        ],
        [
            ("选择文本", 5),
            D_getcolorbutton(
                globalconfig,
                "",
                lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
                name="selecthookbutton",
                parent=self,
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        ],
        [],
        [
            ("检测到游戏时自动开始", 5),
            (D_getsimpleswitch(globalconfig, "autostarthook"), 1),
        ],
        [
            ("已保存游戏", 5),
            (
                D_getcolorbutton(
                    globalconfig,
                    "",
                    lambda: dialog_savedgame_integrated(self),
                    icon="fa.gamepad",
                    constcolor="#FF69B4",
                ),
                1,
            ),
        ],
        [],
        [
            ("代码页", 5),
            (
                D_getsimplecombobox(
                    _TRL(static_data["codepage_display"]),
                    globalconfig,
                    "codepage_index",
                    lambda x: gobject.baseobject.textsource.setsettings(),
                ),
                8,
            ),
        ],
        [
            ("移除非选定hook", 5),
            (D_getsimpleswitch(globalconfig, "removeuseless"), 1),
        ],
        [
            ("过滤反复刷新的句子", 5),
            (D_getsimpleswitch(globalconfig, "direct_filterrepeat"), 1),
        ],
        [
            ("刷新延迟(ms)", 5),
            (
                D_getspinbox(
                    0,
                    10000,
                    globalconfig,
                    "textthreaddelay",
                    callback=lambda x: gobject.baseobject.textsource.setsettings(),
                ),
                3,
            ),
        ],
        [
            ("最大缓冲区长度", 5),
            (
                D_getspinbox(
                    0,
                    1000000,
                    globalconfig,
                    "maxBufferSize",
                    callback=lambda x: gobject.baseobject.textsource.setsettings(),
                ),
                3,
            ),
        ],
        [
            ("最大缓存文本长度", 5),
            (
                D_getspinbox(
                    0,
                    1000000000,
                    globalconfig,
                    "maxHistorySize",
                    callback=lambda x: gobject.baseobject.textsource.setsettings(),
                ),
                3,
            ),
        ],
        [
            ("过滤包含乱码的文本行", 5),
            (D_getsimpleswitch(globalconfig, "filter_chaos_code"), 1),
            (
                D_getcolorbutton(
                    globalconfig,
                    "",
                    icon="fa.gear",
                    constcolor="#FF69B4",
                    callback=lambda: codeacceptdialog(self),
                ),
                1,
            ),
        ],
        [("区分人名和文本", 5), D_getsimpleswitch(globalconfig, "allow_set_text_name")],
        [("使用YAPI注入", 5), D_getsimpleswitch(globalconfig, "use_yapi")],
    ]

    return grids


def doexportchspatch(exe, realgame):

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
        "target_exe2": os.path.basename(realgame),
        "startup_argument": None,
        "inject_timeout": 1000,
        "embedhook": savehook_new_data[realgame]["embedablehook"],
        "embedsettings": {
            "font": (
                globalconfig["embedded"]["changefont_font"]
                if globalconfig["embedded"]["changefont"]
                else ""
            ),
            "insertspace_policy": globalconfig["embedded"]["insertspace_policy"],
            "keeprawtext": globalconfig["embedded"]["keeprawtext"],
        },
    }
    with open(
        os.path.join(os.path.dirname(exe), "LunaPatch.json"), "w", encoding="utf8"
    ) as ff:
        ff.write(json.dumps(embedconfig, ensure_ascii=False, indent=4))


def getunknowgameexe(self):

    dialog = QDialog(self, Qt.WindowType.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR("选择游戏"))
    dialog.resize(QSize(800, 10))
    formLayout = QFormLayout(dialog)
    dialog.setLayout(formLayout)

    combo = FocusCombo()
    combo.addItems([savehook_new_data[_]["title"] for _ in savehook_new_list])

    formLayout.addRow(_TR("选择游戏"), combo)

    button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)
    button.accepted.connect(dialog.accept)
    button.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
    button.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
    if dialog.exec():
        return savehook_new_list[combo.currentIndex()]


def exportchspatch(self):
    realgame = getunknowgameexe(self)
    if realgame is None:
        return
    exe = realgame
    if exe.lower().endswith(".exe") == False:
        f = QFileDialog.getOpenFileName(
            self, caption=_TR("选择EXE文件"), filter="*.exe"
        )
        exe = f[0]
        if exe == "":
            return
        exe = os.path.normpath(exe)
    doexportchspatch(exe, realgame)
    md5 = getfilemd5(exe)
    name = os.path.basename(exe).replace("." + os.path.basename(exe).split(".")[-1], "")
    os.makedirs("./translation_record", exist_ok=True)
    sqlfname_all = "./translation_record/" + name + "_" + md5 + ".sqlite"
    if os.path.exists(sqlfname_all) == False:
        f = QFileDialog.getOpenFileName(
            self,
            caption=_TR("选择预翻译文件"),
            directory="./translation_record/",
            filter="*.sqlite",
        )
        sqlfname_all = f[0]
    if os.path.exists(sqlfname_all):
        sqlite2json2(
            self,
            sqlfname_all,
            os.path.join(os.path.dirname(exe), "translation.json"),
            existsmerge=True,
        )
    else:
        with open(os.path.join(os.path.dirname(exe), "translation.json"), "w") as ff:
            ff.write("{}")


def creategamefont_comboBox():

    gamefont_comboBox = QFontComboBox()

    def callback(x):
        globalconfig["embedded"].__setitem__("changefont_font", x)
        try:
            gobject.baseobject.textsource.flashembedsettings()
        except:
            pass

    gamefont_comboBox.currentTextChanged.connect(callback)
    gamefont_comboBox.setCurrentFont(QFont(globalconfig["embedded"]["changefont_font"]))
    return gamefont_comboBox


def gethookembedgrid(self):
    grids = [
        [
            ("导出翻译补丁", 5),
            D_getcolorbutton(
                globalconfig,
                "",
                callback=lambda x: exportchspatch(self),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        ],
        [],
        [
            ("保留原文", 5),
            (
                D_getsimpleswitch(
                    globalconfig["embedded"],
                    "keeprawtext",
                    callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
                ),
                1,
            ),
        ],
        [
            ("翻译等待时间(s)", 5),
            "",
            (
                D_getspinbox(
                    0,
                    30,
                    globalconfig["embedded"],
                    "timeout_translate",
                    double=True,
                    step=0.1,
                    callback=lambda x: gobject.baseobject.textsource.flashembedsettings(),
                ),
                3,
            ),
        ],
        [
            ("使用最快翻译而非指定翻译器", 5),
            (D_getsimpleswitch(globalconfig["embedded"], "as_fast_as_posible"), 1),
        ],
        [
            ("内嵌的翻译器", 5),
            "",
            (
                D_getsimplecombobox(
                    _TRL(
                        [
                            globalconfig["fanyi"][x]["name"]
                            for x in globalconfig["fanyi"]
                        ]
                    ),
                    globalconfig["embedded"],
                    "translator_2",
                    internallist=list(globalconfig["fanyi"]),
                ),
                5,
            ),
        ],
        [
            ("将汉字转换成繁体/日式汉字", 5),
            (D_getsimpleswitch(globalconfig["embedded"], "trans_kanji"), 1),
        ],
        [
            ("在重叠显示的字间插入空格", 5),
            "",
            (
                D_getsimplecombobox(
                    _TRL(["不插入空格", "每个字后插入空格", "仅在无法编码的字后插入"]),
                    globalconfig["embedded"],
                    "insertspace_policy",
                    callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
                ),
                5,
            ),
        ],
        [
            ("修改游戏字体", 5),
            (
                D_getsimpleswitch(
                    globalconfig["embedded"],
                    "changefont",
                    callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
                ),
                1,
            ),
            (creategamefont_comboBox, 5),
        ],
        [],
        [
            ("内嵌安全性检查", 5),
            D_getsimpleswitch(globalconfig["embedded"], "safecheck_use"),
            D_getcolorbutton(
                globalconfig,
                "",
                callback=lambda x: regexedit(
                    self, globalconfig["embedded"]["safecheckregexs"]
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        ],
    ]

    return grids


def getTabclip(self):

    grids = [
        [
            ("排除复制自翻译器的文本", 3),
            D_getsimpleswitch(globalconfig, "excule_from_self"),
            ("", 3),
        ]
    ]
    return grids


def outputgrid(self):

    grids = [
        [("自动输出提取的文本", 15)],
        [],
        [("剪贴板", 0)],
        [
            "",
            ("输出到剪贴板", 5),
            (D_getsimpleswitch(globalconfig["textoutputer"]["clipboard"], "use"), 1),
        ],
        [("WebSocket", -1)],
        [
            "",
            ("输出到WebSocket", 5),
            (
                D_getsimpleswitch(
                    globalconfig["textoutputer"]["websocket"],
                    "use",
                    callback=lambda _: gobject.baseobject.startoutputer_re("websocket"),
                ),
                1,
            ),
        ],
        [
            "",
            ("端口号", 5),
            (
                D_getspinbox(
                    0,
                    65535,
                    globalconfig["textoutputer"]["websocket"],
                    "port",
                    callback=lambda _: gobject.baseobject.startoutputer_re("websocket"),
                ),
                3,
            ),
        ],
    ]
    return grids


def setTabOne_lazy(self, basel):
    tab1grids = [
        [("选择文本输入源", -1)],
        [
            ("HOOK", 3),
            (
                D_getsimpleswitch(
                    globalconfig["sourcestatus2"]["texthook"],
                    "use",
                    name="texthook",
                    parent=self,
                    callback=functools.partial(
                        yuitsu_switch,
                        self,
                        globalconfig["sourcestatus2"],
                        "sourceswitchs",
                        "texthook",
                        gobject.baseobject.starttextsource,
                    ),
                    pair="sourceswitchs",
                ),
                1,
            ),
            "",
            ("OCR", 3),
            (
                D_getsimpleswitch(
                    globalconfig["sourcestatus2"]["ocr"],
                    "use",
                    name="ocr",
                    parent=self,
                    callback=functools.partial(
                        yuitsu_switch,
                        self,
                        globalconfig["sourcestatus2"],
                        "sourceswitchs",
                        "ocr",
                        gobject.baseobject.starttextsource,
                    ),
                    pair="sourceswitchs",
                ),
                1,
            ),
            "",
            ("剪贴板", 3),
            (
                D_getsimpleswitch(
                    globalconfig["sourcestatus2"]["copy"],
                    "use",
                    name="copy",
                    parent=self,
                    callback=functools.partial(
                        yuitsu_switch,
                        self,
                        globalconfig["sourcestatus2"],
                        "sourceswitchs",
                        "copy",
                        gobject.baseobject.starttextsource,
                    ),
                    pair="sourceswitchs",
                ),
                1,
            ),
            "",
        ],
    ]

    vw, vl = getvboxwidget()
    basel.addWidget(vw)
    gridlayoutwidget, do = makegrid(tab1grids, delay=True)
    vl.addWidget(gridlayoutwidget)
    tab, dotab = makesubtab_lazy(
        _TRL(["HOOK设置", "OCR设置", "剪贴板", "内嵌翻译", "文本输出"]),
        [
            lambda l: makescrollgrid(gethookgrid(self), l),
            lambda l: makescrollgrid(getocrgrid(self), l),
            lambda l: makescrollgrid(getTabclip(self), l),
            lambda l: makescrollgrid(gethookembedgrid(self), l),
            lambda l: makescrollgrid(outputgrid(self), l),
        ],
        delay=True,
    )
    vl.addWidget(tab)
    do()
    dotab()
