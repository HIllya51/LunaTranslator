from qtsymbols import *
import functools, os
import gobject
from myutils.utils import splitocrtypes, dynamiccishuname
from myutils.config import globalconfig, _TR
from myutils.wrapper import Singleton
from gui.inputdialog import autoinitdialog_items, autoinitdialog
from gui.usefulwidget import (
    yuitsu_switch,
    makescrollgrid,
    D_getsimpleswitch,
    listediter,
    D_getIconButton,
    D_getspinbox,
    getsmalllabel,
    getcenterX,
    D_getcolorbutton,
    getboxlayout,
    getsimpleswitch,
    D_getsimplecombobox,
    getspinbox,
    ClickableLabel,
    getcolorbutton,
    KeySequenceEdit,
    check_grid_append,
)
import qtawesome
from gui.dynalang import LFormLayout, LLabel, LAction, LDialog
from gui.setting.about import offlinelinks
from gui.rendertext.tooltipswidget import tooltipssetting
from gui.showword import cishusX


@Singleton
class multicolorset(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("颜色设置")
        self.setWindowIcon(qtawesome.icon("fa.paint-brush"))
        self.resize(QSize(300, 10))
        formLayout = LFormLayout(self)  # 配置layout
        _hori = QHBoxLayout()
        l = LLabel("不透明度")
        _hori.addWidget(l)
        _s = getspinbox(
            1,
            100,
            d=globalconfig,
            key="showcixing_touming",
            callback=gobject.base.translation_ui.translate_text.setcolorstyle,
        )
        _hori.addWidget(_s)
        formLayout.addRow(_hori)
        _s.valueChanged.connect(
            lambda x: globalconfig.__setitem__("showcixing_touming", x)
        )
        hori = QHBoxLayout()
        hori.addWidget(LLabel("词性"))
        hori.addWidget(LLabel("是否显示"))
        hori.addWidget(LLabel("颜色"))
        for k in globalconfig["cixingcolor"]:
            hori = QHBoxLayout()

            l = LLabel(k)

            hori.addWidget(l)

            b = getsimpleswitch(
                d=globalconfig["cixingcolorshow"],
                key=k,
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )

            p = getcolorbutton(
                self,
                globalconfig["cixingcolor"],
                k,
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            )
            hori.addWidget(b)
            hori.addWidget(p)

            formLayout.addRow(hori)
        self.show()


def setTabcishu(self, basel):
    makescrollgrid(setTabcishu_l(self), basel)
    gobject.base.fenyinsettings.connect(self.fenyinsettings.setEnabled)


def gethiragrid(self):

    grids = []
    i = 0
    self.hiraswitchs = {}
    line = []
    for name in ("mecab",):
        if "args" in globalconfig["hirasetting"][name]:
            items = autoinitdialog_items(globalconfig["hirasetting"][name])
            items[-1]["callback"] = gobject.base.startmecab
            _3 = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["hirasetting"][name]["args"],
                    globalconfig["hirasetting"][name]["name"],
                    800,
                    items,
                ),
            )

        else:
            _3 = ""

        line += [
            globalconfig["hirasetting"][name]["name"],
            D_getsimpleswitch(
                globalconfig["hirasetting"][name],
                "use",
                name=name,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["hirasetting"],
                    "hiraswitchs",
                    name,
                    gobject.base.startmecab,
                ),
                pair="hiraswitchs",
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
    grids[-1] += [""] * (4 + 4 + 3 - len(grids[-1]))
    return grids


def vistranslate_rank(self):
    listediter(
        self,
        "显示顺序",
        globalconfig["cishuvisrank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(dynamiccishuname(k)),
        exec=True,
    )


def renameapi(qlabel: QLabel, apiuid, self, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    menu.addAction(editname)
    useproxy = LAction("使用代理", menu)
    useproxy.setCheckable(True)
    if globalconfig["useproxy"] and globalconfig["cishu"][apiuid].get("type") not in ("offline",):
        menu.addSeparator()
        menu.addAction(useproxy)
        useproxy.setChecked(globalconfig["cishu"][apiuid].get("useproxy", True))
    action = menu.exec(QCursor.pos())

    if action == editname:
        before = dynamiccishuname(apiuid)
        __d = {"k": before}

        def cb(__d):
            title = __d["k"]
            if title not in ("", before):
                globalconfig["cishu"][apiuid]["name_self_set"] = title
                qlabel.setText(title)

        autoinitdialog(
            self,
            __d,
            "重命名",
            600,
            [
                {
                    "type": "lineedit",
                    "name": "名称",
                    "k": "k",
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(cb, __d),
                },
            ],
            exec_=True,
        )

    elif action == useproxy:
        globalconfig["cishu"][apiuid]["useproxy"] = useproxy.isChecked()


def getrenameablellabel(uid, self):
    name = ClickableLabel(dynamiccishuname(uid))
    fn = functools.partial(renameapi, name, uid, self)
    name.clicked.connect(fn)
    return name


def initinternal(self, names):
    cishugrid = []
    line = []
    i = 0
    for cishu in names:
        _f = "LunaTranslator/cishu/{}.py".format(cishu)
        if os.path.exists(_f) == False:
            continue

        line += [
            functools.partial(getrenameablellabel, cishu, self),
            D_getsimpleswitch(
                globalconfig["cishu"][cishu],
                "use",
                callback=functools.partial(gobject.base.startxiaoxueguan, cishu),
            ),
        ]
        if "args" in globalconfig["cishu"][cishu]:

            items = autoinitdialog_items(globalconfig["cishu"][cishu])
            items[-1]["callback"] = functools.partial(
                gobject.base.startxiaoxueguan, cishu
            )

            def __(cishu):
                autoinitdialog(
                    self,
                    globalconfig["cishu"][cishu]["args"],
                    dynamiccishuname(cishu),
                    800,
                    items,
                    "cishu." + cishu,
                    cishu,
                )

            line += [
                D_getIconButton(callback=functools.partial(__, cishu)),
            ]
        else:
            line += [""]
        if i % 3 == 2:
            cishugrid.append(line)
            line = []
        else:
            line += [""]
        i += 1
    if len(line):
        cishugrid.append(line)
    cishugrid[-1] += [""] * (4 + 4 + 3 - len(cishugrid[-1]))
    check_grid_append(cishugrid)
    return cishugrid


def setTabcishu_l(self):

    grids_1 = [dict(title="分词器", type="grid", grid=gethiragrid(self))]
    offline, online = splitocrtypes(globalconfig["cishu"])
    grids2 = [
        dict(
            title="辞书",
            type="grid",
            grid=[
                [
                    getsmalllabel("查词"),
                    D_getIconButton(
                        lambda: gobject.base.searchwordW.showsignal.emit(),
                        icon="fa.search",
                        tips="查词",
                    ),
                    getsmalllabel(""),
                    getsmalllabel("辞书显示顺序"),
                    D_getIconButton(functools.partial(vistranslate_rank, self)),
                    "",
                ],
                [
                    dict(
                        title="离线",
                        type="grid",
                        grid=initinternal(self, offline),
                    )
                ],
                [
                    dict(
                        title="在线",
                        type="grid",
                        grid=initinternal(self, online),
                    )
                ],
            ],
        )
    ]

    def _getkeys(key):
        dia = QDialog(self)
        dia.setWindowIcon(qtawesome.icon("fa.keyboard-o"))
        dia.setWindowFlags(
            dia.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        l = QVBoxLayout(dia)
        edit = KeySequenceEdit(callonlymod=True)
        edit.setString(globalconfig["wordclickkbtrigger"].get(key, ""))
        l.addWidget(edit)
        dia.setWindowTitle(_TR("需要的键"))
        button = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button.accepted.connect(dia.accept)
        button.rejected.connect(dia.reject)
        l.addWidget(button)
        dia.resize(800, 10)
        ok = dia.exec()
        if ok:
            globalconfig["wordclickkbtrigger"][key] = edit.string()

    def _getlink():
        listediter(
            self,
            "外部链接",
            globalconfig["useopenlinklink1"],
            exec=True,
            icon="fa.link",
        )

    grids = [
        [(functools.partial(offlinelinks, "dict"), 0)],
        grids_1,
        grids2,
        [],
        [
            dict(
                title="分词_&&_注音",
                type="grid",
                parent=self,
                name="fenyinsettings",
                enable=globalconfig["isshowrawtext"],
                grid=(
                    [
                        "显示注音",
                        D_getsimpleswitch(
                            globalconfig,
                            "isshowhira",
                            callback=gobject.base.translation_ui.translate_text.showhidert,
                        ),
                        D_getcolorbutton(
                            self,
                            globalconfig,
                            "jiamingcolor",
                            callback=gobject.base.translation_ui.translate_text.setcolorstyle,
                            tips="注音颜色",
                        ),
                        "",
                        "字体缩放",
                        D_getspinbox(
                            0.1,
                            1,
                            globalconfig,
                            "kanarate",
                            double=True,
                            step=0.05,
                            callback=gobject.base.translation_ui.translate_text.setfontstyle,
                        ),
                        "",
                        "日语注音方案",
                        D_getsimplecombobox(
                            [
                                "平假名",
                                "片假名",
                                "罗马音",
                            ],
                            globalconfig,
                            "hira_vis_type",
                            callback=lambda _: gobject.base.translation_ui.translate_text.refreshcontent(),
                        ),
                    ],
                    [
                        "语法加亮",
                        D_getsimpleswitch(
                            globalconfig,
                            "show_fenci",
                            callback=lambda _: (
                                gobject.base.translation_ui.translate_text.setcolorstyle(),
                                gobject.base.translation_ui.translate_text.showhideclick(
                                    _
                                ),
                            ),
                        ),
                        D_getIconButton(
                            icon="fa.paint-brush",
                            callback=lambda: multicolorset(self),
                            tips="语法加亮_颜色设置",
                        ),
                    ],
                    [
                        dict(
                            title="鼠标悬停时",
                            type="grid",
                            button=D_getcolorbutton(
                                self,
                                globalconfig,
                                "hovercolor",
                                callback=gobject.base.translation_ui.translate_text.sethovercolor,
                                alpha=True,
                            ),
                            grid=[
                                [
                                    "显示详细信息",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "word_hover_show_word_info",
                                        callback=lambda _: (
                                            gobject.base.translation_ui.translate_text.set_word_hover_show_word_info(
                                                _
                                            ),
                                            gobject.base.translation_ui.translate_text.showhideclick(
                                                _
                                            ),
                                        ),
                                    ),
                                    D_getIconButton(
                                        callback=lambda: tooltipssetting(self),
                                        tips="样式",
                                    ),
                                ],
                                [
                                    "查词_在小窗口中",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "usesearchword_S_hover",
                                        callback=gobject.base.translation_ui.translate_text.showhideclick,
                                    ),
                                    D_getIconButton(
                                        callback=functools.partial(
                                            listediter,
                                            self,
                                            "不使用的辞书",
                                            globalconfig["ignoredict_S_hover"],
                                            candidates=cishusX(),
                                            namemapfunction=dynamiccishuname,
                                            exec=True,
                                        ),
                                        tips="不使用的辞书",
                                    ),
                                    "",
                                    "需要键盘按下",
                                    D_getsimpleswitch(
                                        globalconfig["wordclickkbtriggerneed"],
                                        "searchword_S_hover",
                                        default=False,
                                    ),
                                    D_getIconButton(
                                        icon="fa.keyboard-o",
                                        callback=functools.partial(
                                            _getkeys, "searchword_S_hover"
                                        ),
                                        tips="需要的键",
                                    ),
                                    "",
                                    "使用单词原型",
                                    D_getsimpleswitch(
                                        globalconfig["usewordoriginfor"],
                                        "searchword_S_hover",
                                        default=False,
                                    ),
                                ],
                            ],
                        )
                    ],
                    [
                        dict(
                            title="点击单词时",
                            type="grid",
                            grid=[
                                [
                                    "",
                                    "",
                                    "",
                                    "",
                                    getcenterX("需要键盘按下"),
                                    "",
                                    getcenterX("使用单词原型"),
                                ],
                                [
                                    "查词",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "usesearchword",
                                        callback=gobject.base.translation_ui.translate_text.showhideclick,
                                    ),
                                    "",
                                    "",
                                    getboxlayout(
                                        [
                                            D_getsimpleswitch(
                                                globalconfig["wordclickkbtriggerneed"],
                                                "searchword",
                                                default=False,
                                            ),
                                            D_getIconButton(
                                                icon="fa.keyboard-o",
                                                callback=functools.partial(
                                                    _getkeys, "searchword"
                                                ),
                                                tips="需要的键",
                                            ),
                                        ]
                                    ),
                                    "",
                                    getcenterX(
                                        D_getsimpleswitch(
                                            globalconfig["usewordoriginfor"],
                                            "searchword",
                                            default=False,
                                        )
                                    ),
                                ],
                                [
                                    "查词_在小窗口中",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "usesearchword_S",
                                        callback=gobject.base.translation_ui.translate_text.showhideclick,
                                    ),
                                    D_getIconButton(
                                        callback=functools.partial(
                                            listediter,
                                            self,
                                            "不使用的辞书",
                                            globalconfig["ignoredict_S_click"],
                                            candidates=cishusX(),
                                            namemapfunction=dynamiccishuname,
                                            exec=True,
                                        ),
                                        tips="不使用的辞书",
                                    ),
                                    "",
                                    getboxlayout(
                                        [
                                            D_getsimpleswitch(
                                                globalconfig["wordclickkbtriggerneed"],
                                                "searchword_S",
                                                default=False,
                                            ),
                                            D_getIconButton(
                                                icon="fa.keyboard-o",
                                                callback=functools.partial(
                                                    _getkeys, "searchword_S"
                                                ),
                                                tips="需要的键",
                                            ),
                                        ]
                                    ),
                                    "",
                                    getcenterX(
                                        D_getsimpleswitch(
                                            globalconfig["usewordoriginfor"],
                                            "searchword_S",
                                            default=False,
                                        )
                                    ),
                                ],
                                [
                                    "复制到剪贴板",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "usecopyword",
                                        callback=gobject.base.translation_ui.translate_text.showhideclick,
                                    ),
                                    "",
                                    "",
                                    getboxlayout(
                                        [
                                            D_getsimpleswitch(
                                                globalconfig["wordclickkbtriggerneed"],
                                                "copyword",
                                                default=False,
                                            ),
                                            D_getIconButton(
                                                icon="fa.keyboard-o",
                                                callback=functools.partial(
                                                    _getkeys, "copyword"
                                                ),
                                                tips="需要的键",
                                            ),
                                        ]
                                    ),
                                    "",
                                    getcenterX(
                                        D_getsimpleswitch(
                                            globalconfig["usewordoriginfor"],
                                            "copyword",
                                            default=False,
                                        )
                                    ),
                                ],
                                [
                                    "打开外部链接",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "useopenlink",
                                        callback=gobject.base.translation_ui.translate_text.showhideclick,
                                    ),
                                    D_getIconButton(
                                        icon="fa.link",
                                        callback=_getlink,
                                        tips="外部链接",
                                    ),
                                    "",
                                    getboxlayout(
                                        [
                                            D_getsimpleswitch(
                                                globalconfig["wordclickkbtriggerneed"],
                                                "openlink",
                                                default=False,
                                            ),
                                            D_getIconButton(
                                                icon="fa.keyboard-o",
                                                callback=functools.partial(
                                                    _getkeys, "openlink"
                                                ),
                                                tips="需要的键",
                                            ),
                                        ]
                                    ),
                                    "",
                                    getcenterX(
                                        D_getsimpleswitch(
                                            globalconfig["usewordoriginfor"],
                                            "openlink",
                                            default=False,
                                        )
                                    ),
                                ],
                            ],
                        )
                    ],
                ),
            ),
        ],
    ]
    return grids
