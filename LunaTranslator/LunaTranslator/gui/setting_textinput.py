from qtsymbols import *
import functools, os, json
import windows, gobject
from myutils.utils import getfilemd5, dynamiclink
from myutils.config import (
    globalconfig,
    _TR,
    savehook_new_data,
    uid2gamepath,
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
    D_getIconButton,
    getIconButton,
    makegrid,
    yuitsu_switch,
    getvboxwidget,
    D_getsimpleswitch,
    makesubtab_lazy,
    makescrollgrid,
    FocusCombo,
    FocusFontCombo,
)
from gui.dynalang import LPushButton, LDialog, LFormLayout


def __create(self):
    self.selectbutton = getIconButton(
        gobject.baseobject.createattachprocess,
        icon="fa.gear",
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    return self.selectbutton


def __create2(self):
    self.selecthookbutton = getIconButton(
        lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
        icon="fa.gear",
        enable=globalconfig["sourcestatus2"]["texthook"]["use"],
    )
    return self.selecthookbutton


def gethookgrid(self):

    grids = [
        [
            "选择游戏",
            functools.partial(__create, self),
            ("", 5),
        ],
        [
            "选择文本",
            functools.partial(__create2, self),
        ],
        [],
        [
            "检测到游戏时自动开始",
            (D_getsimpleswitch(globalconfig, "autostarthook"), 1),
        ],
        [
            "已保存游戏",
            (
                D_getIconButton(
                    lambda: dialog_savedgame_integrated(self),
                    icon="fa.gamepad",
                ),
                1,
            ),
        ],
        [],
        [
            (
                dict(
                    title="默认设置",
                    type="grid",
                    grid=(
                        [
                            "代码页",
                            (
                                D_getsimplecombobox(
                                    static_data["codepage_display"],
                                    globalconfig,
                                    "codepage_index",
                                    lambda x: gobject.baseobject.textsource.setsettings(),
                                ),
                                4,
                            ),
                        ],
                        [
                            "移除非选定hook",
                            D_getsimpleswitch(globalconfig, "removeuseless"),
                        ],
                        [
                            "过滤反复刷新的句子",
                            D_getsimpleswitch(globalconfig, "direct_filterrepeat"),
                        ],
                        [
                            "刷新延迟(ms)",
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
                        [
                            "过滤包含乱码的文本行",
                            D_getsimpleswitch(globalconfig, "filter_chaos_code"),
                            D_getIconButton(
                                icon="fa.gear",
                                callback=lambda: codeacceptdialog(self),
                            ),
                        ],
                        [
                            "使用YAPI注入",
                            D_getsimpleswitch(globalconfig, "use_yapi"),
                        ],
                    ),
                ),
                0,
                "group",
            )
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
    with open(
        os.path.join(os.path.dirname(exe), "LunaPatch.json"), "w", encoding="utf8"
    ) as ff:
        ff.write(json.dumps(embedconfig, ensure_ascii=False, indent=4))


def selectgameuid(self):

    dialog = LDialog(self, Qt.WindowType.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle("选择游戏")
    dialog.resize(QSize(800, 10))
    formLayout = LFormLayout(dialog)
    dialog.setLayout(formLayout)

    combo = FocusCombo()
    combo.addItems([savehook_new_data[_]["title"] for _ in savehook_new_list])

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
        return savehook_new_list[combo.currentIndex()]


def exportchspatch(self):
    gameuid = selectgameuid(self)
    if gameuid is None:
        return
    exe = uid2gamepath[gameuid]
    if exe.lower().endswith(".exe") == False:
        f = QFileDialog.getOpenFileName(
            self, caption=_TR("选择EXE文件"), filter="*.exe"
        )
        exe = f[0]
        if exe == "":
            return
        exe = os.path.normpath(exe)
    doexportchspatch(exe, gameuid)
    md5 = getfilemd5(exe)
    name = os.path.basename(exe).replace("." + os.path.basename(exe).split(".")[-1], "")
    sqlfname_all = gobject.gettranslationrecorddir(name + "_" + md5 + ".sqlite")
    if os.path.exists(sqlfname_all) == False:
        f = QFileDialog.getOpenFileName(
            self,
            caption=_TR("选择预翻译文件"),
            directory="translation_record",
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


def gethookembedgrid(self):
    grids = [
        [
            "导出翻译补丁",
            D_getIconButton(
                callback=lambda: exportchspatch(self),
                icon="fa.gear",
            ),
            "",
            "",
        ],
        [],
        [
            "保留原文",
            D_getsimpleswitch(
                globalconfig["embedded"],
                "keeprawtext",
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
            ),
        ],
        [
            "翻译等待时间(s)",
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
            "使用最快翻译而非指定翻译器",
            D_getsimpleswitch(globalconfig["embedded"], "as_fast_as_posible"),
        ],
        [
            "内嵌的翻译器",
            "",
            D_getsimplecombobox(
                [globalconfig["fanyi"][x]["name"] for x in globalconfig["fanyi"]],
                globalconfig["embedded"],
                "translator_2",
                internallist=list(globalconfig["fanyi"]),
            ),
        ],
        [
            "将汉字转换成繁体/日式汉字",
            D_getsimpleswitch(globalconfig["embedded"], "trans_kanji"),
        ],
        [
            "在重叠显示的字间插入空格",
            "",
            D_getsimplecombobox(
                ["不插入空格", "每个字后插入空格", "仅在无法编码的字后插入"],
                globalconfig["embedded"],
                "insertspace_policy",
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
            ),
        ],
        [
            "限制每行字数",
            D_getsimpleswitch(
                globalconfig["embedded"],
                "limittextlength_use",
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
            ),
            D_getspinbox(
                0,
                1000,
                globalconfig["embedded"],
                "limittextlength_length",
                callback=lambda x: gobject.baseobject.textsource.flashembedsettings(),
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
        [],
        [
            "内嵌安全性检查",
            D_getsimpleswitch(globalconfig["embedded"], "safecheck_use"),
            D_getIconButton(
                callback=lambda: regexedit(
                    self, globalconfig["embedded"]["safecheckregexs"]
                ),
                icon="fa.gear",
            ),
        ],
    ]

    return grids


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


def outputgrid(self):

    grids = [
        ["自动输出提取的文本"],
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
        [],
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


def setTabOne_lazy(self, basel):
    tab1grids = [
        [("选择文本输入源", -1)],
        [
            "HOOK",
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
            "",
            "OCR",
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
            "",
            "剪贴板",
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
            "",
        ],
    ]

    vw, vl = getvboxwidget()
    basel.addWidget(vw)
    gridlayoutwidget, do = makegrid(tab1grids, delay=True)
    vl.addWidget(gridlayoutwidget)
    tab, dotab = makesubtab_lazy(
        ["HOOK设置", "OCR设置", "剪贴板", "内嵌翻译", "文本输出"],
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
