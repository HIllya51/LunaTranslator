from qtsymbols import *
import functools
import gobject, os
from myutils.config import globalconfig, static_data
from myutils.utils import dynamiclink
from traceback import print_exc
from language import TransLanguages
from gui.setting.textinput_ocr import getocrgrid_table
from gui.gamemanager.dialog import dialog_savedgame_integrated
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
    FocusFontCombo,
    getsmalllabel,
)


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
    grids = [
        [
            "清除游戏内显示的文字",
            D_getsimpleswitch(
                globalconfig["embedded"],
                "clearText",
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
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
                )
            ),
        ],
    ]

    return grids


def gethookgrid(self):
    grids = [
        [
            "代码页",
            (
                D_getsimplecombobox(
                    static_data["codepage_display"],
                    globalconfig,
                    "codepage_value",
                    lambda x: gobject.baseobject.textsource.setsettings(),
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
    grids = [
        [
            dict(
                title="文件翻译",
                grid=[
                    [
                        "文件",
                        D_getIconButton(
                            functools.partial(selectfile, self),
                            icon="fa.folder-open",
                        ),
                    ],
                    [functools.partial(createdownloadprogress, self)],
                ],
            ),
        ],
    ]
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


def open___(url):
    link = "http://127.0.0.1:{}{}".format(globalconfig["networktcpport"], url)
    os.startfile(link)


def createlabellink(url):
    l = QLabel('<a href="{}">{}</a>'.format(url, url))
    l.linkActivated.connect(open___)
    return l


def outputgrid():

    grids = [
        [
            D_getIconButton(
                lambda: os.startfile(dynamiclink("/apiservice.html", docs=True)),
                "fa.question",
            ),
        ],
        [
            "开启",
            D_getsimpleswitch(
                globalconfig,
                "networktcpenable",
                callback=lambda _: gobject.baseobject.serviceinit(),
            ),
            "",
            "",
            "",
        ],
        [
            "端口号",
            D_getspinbox(
                0,
                65535,
                globalconfig,
                "networktcpport",
                callback=lambda _: gobject.baseobject.serviceinit(),
            ),
        ],
        [],
        [(functools.partial(createlabellink, "/"), -1)],
        [(functools.partial(createlabellink, "/page/mainui"), -1)],
        [(functools.partial(createlabellink, "/page/transhist"), -1)],
        [(functools.partial(createlabellink, "/page/dictionary"), -1)],
        [(functools.partial(createlabellink, "/page/translate"), -1)],
        [(functools.partial(createlabellink, "/page/ocr"), -1)],
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
        [dict(title="语言设置", type="grid", grid=setTablanglz())],
        [dict(title="文本输入", type="grid", grid=[__])],
    ]
    gridlayoutwidget, do = makegrid(tab1grids, delay=True)
    basel.addWidget(gridlayoutwidget)
    titles = ["HOOK设置", "OCR设置", "剪贴板", "其他", "网络服务"]
    funcs = [
        lambda l: setTabOne_lazy_h(self, l),
        lambda l: getocrgrid_table(self, l),
        lambda l: makescrollgrid(getTabclip(), l),
        lambda l: makescrollgrid(filetranslate(self), l),
        lambda l: makescrollgrid(outputgrid(), l),
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
