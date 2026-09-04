from qtsymbols import *
import functools, os
import gobject
from myutils.utils import splitocrtypes, dynamiccishuname, selectdebugfile, cishuexits
from myutils.config import globalconfig, _TR
from myutils.wrapper import Singleton
from gui.inputdialog import autoinitdialog_items, autoinitdialog
from gui.rcdownload import resourcewidget, resourcewidget2
from gui.usefulwidget import (
    LGroupBox,
    VisLFormLayout,
    makescrollgrid,
    D_getsimpleswitch,
    listediter,
    D_getIconButton,
    LPushButton,
    NQGroupBox,
    getsmalllabel,
    D_getdoclink,
    D_getcolorbutton,
    MyInputDialog,
    getboxlayout,
    getsimpleswitch,
    D_getsimplecombobox,
    getspinbox,
    ClickableLabel,
    ColorButton,
    KeySequenceEdit,
    check_grid_append,
    automakegrid,
    request_delete_ok,
    DarkLightAutoResetIconHelper,
    FocusFontCombo,
    getIconSwitch,
    clearlayout,
)
import qtawesome
from gui.dynalang import LFormLayout, LLabel, LAction, LDialog
from gui.rendertext.tooltipswidget import tooltipssetting
from gui.showword import cishusX
from gui.setting.cishucommunity import CommunityCishuDialog


@Singleton
class multicolorset(LDialog, DarkLightAutoResetIconHelper):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("语法加亮_颜色设置")
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
            default=30,
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

            p = ColorButton(
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
    gobject.base.fencisettings.connect(self.fencisettings.setEnabled)


def vistranslate_rank(self):
    listediter(
        self,
        "显示顺序",
        globalconfig["cishuvisrank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(dynamiccishuname(k)),
        exec=True,
    )


def rebuildcishugrid(self):
    layout = getattr(self, "cishugridinternal", None)
    if layout is None:
        return
    clearlayout(layout)
    _, online = splitocrtypes(globalconfig["cishu"])
    automakegrid(layout, initinternal(self, online))


def deletecishu(self, apiuid):
    if not request_delete_ok(self, "99e3f96f-8659-457f-9e0b-52643f552889"):
        return
    _f = gobject.getconfig("copyed/{}.py".format(apiuid))
    try:
        os.remove(_f)
    except:
        pass
    try:
        globalconfig["cishu"][apiuid]["use"] = False
    except:
        pass
    try:
        gobject.base.cishus.pop(apiuid)
    except:
        pass
    globalconfig["cishu"].pop(apiuid, None)
    rebuildcishugrid(self)


def renameapi(qlabel: QLabel, apiuid, self, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    menu.addAction(editname)
    useproxy = LAction("使用代理", menu)
    useproxy.setCheckable(True)
    if globalconfig.get("useproxy", True) and globalconfig["cishu"][apiuid].get(
        "type"
    ) not in ("offline",):
        menu.addSeparator()
        menu.addAction(useproxy)
        useproxy.setChecked(globalconfig["cishu"][apiuid].get("useproxy", True))
    delete = LAction("删除", menu)
    if cishuexits(apiuid, only_copy=True):
        menu.addSeparator()
        menu.addAction(delete)
    action = menu.exec(QCursor.pos())

    if action == editname:
        before = dynamiccishuname(apiuid)
        title = MyInputDialog(self, "重命名", "名称", before)
        if not title:
            return
        if title == before:
            return
        globalconfig["cishu"][apiuid]["name_self_set"] = title
        qlabel.setText(title)

    elif action == useproxy:
        globalconfig["cishu"][apiuid]["useproxy"] = useproxy.isChecked()

    elif action == delete:
        deletecishu(self, apiuid)


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
        which = cishuexits(cishu)
        if not which:
            continue
        reloadcb = functools.partial(gobject.base.startxiaoxueguan, cishu)
        line += [
            functools.partial(getrenameablellabel, cishu, self),
            D_getsimpleswitch(globalconfig["cishu"][cishu], "use", callback=reloadcb),
        ]
        if "args" in globalconfig["cishu"][cishu]:

            items = autoinitdialog_items(globalconfig["cishu"][cishu])
            items[-1]["callback"] = reloadcb

            def __(cishu, _which=which):
                autoinitdialog(
                    self,
                    globalconfig["cishu"][cishu]["args"],
                    dynamiccishuname(cishu),
                    800,
                    items,
                    _which,
                    cishu,
                )

            line += [
                D_getIconButton(callback=functools.partial(__, cishu)),
            ]
        elif cishu == "selfbuild":
            line += [
                D_getIconButton(
                    callback=lambda: selectdebugfile("selfbuild_cishu.py"),
                    icon="fa.edit",
                )
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
    if cishugrid:
        cishugrid[-1] += [""] * (4 + 4 + 3 - len(cishugrid[-1]))
    check_grid_append(cishugrid)
    return cishugrid


def clickcallback2(l: list, lay: VisLFormLayout, checked):
    if not l:
        l.append(0)
        lay.addRow(resourcewidget2())
        return

    lay.setRowVisible(1, checked)


def clickcallback(l: list, lay: VisLFormLayout, checked):
    if not l:
        l.append(0)
        lay.addRow(resourcewidget())
        return

    lay.setRowVisible(1, checked)


def fenciqisettings(self):
    box = LGroupBox(self)
    box.setTitle("分词器")
    lay = VisLFormLayout(box)
    l1 = QHBoxLayout()

    lay.addRow(l1)
    l1.addWidget(QLabel("Mecab"))
    items = autoinitdialog_items(globalconfig["hirasetting"]["mecab"])
    items[-1]["callback"] = gobject.base.startmecab
    _3 = D_getIconButton(
        callback=functools.partial(
            autoinitdialog,
            self,
            globalconfig["hirasetting"]["mecab"]["args"],
            "Mecab",
            800,
            items,
        ),
    )
    l1.addWidget(_3())
    l1.addStretch(1)
    btn = LPushButton("资源下载")
    btn.setCheckable(True)
    reflist = []
    btn.clicked.connect(functools.partial(clickcallback, reflist, lay))
    l1.addWidget(btn)
    l1.addStretch(8)
    return box


def mdictsettings(self):
    box = LGroupBox(self)
    box.setTitle("离线")
    lay = VisLFormLayout(box)
    l1 = QHBoxLayout()

    lay.addRow(l1)
    l1.addWidget(getrenameablellabel("mdict", self))
    reloadcb = functools.partial(gobject.base.startxiaoxueguan, "mdict")
    l1.addWidget(
        getsimpleswitch(globalconfig["cishu"]["mdict"], "use", callback=reloadcb)
    )
    items = autoinitdialog_items(globalconfig["cishu"]["mdict"])
    items[-1]["callback"] = reloadcb
    _3 = D_getIconButton(
        callback=functools.partial(
            autoinitdialog,
            self,
            globalconfig["cishu"]["mdict"]["args"],
            dynamiccishuname("mdict"),
            800,
            items,
        ),
    )
    l1.addWidget(_3())
    l1.addStretch(1)
    btn = LPushButton("资源下载")
    btn.setCheckable(True)
    reflist = []
    btn.clicked.connect(functools.partial(clickcallback2, reflist, lay))
    l1.addWidget(btn)
    l1.addStretch(8)
    return box


class fontsettings(NQGroupBox):

    def createtextfontcom(self, key, df):
        def _f(key, x):
            globalconfig[key] = x
            gobject.base.translation_ui.translate_text.setfontstyle()

        font_comboBox = FocusFontCombo(sizeX=True)
        font_comboBox.setCurrentFont(QFont(globalconfig.get(key, df)))
        font_comboBox.currentTextChanged.connect(functools.partial(_f, key))
        return font_comboBox

    def __init__(self, parent):
        super().__init__(parent)
        form = LFormLayout(self)
        form.addRow(
            "相对大小",
            getspinbox(
                0.1,
                1,
                globalconfig,
                "kanarate",
                double=True,
                step=0.05,
                callback=gobject.base.translation_ui.translate_text.setfontstyle,
                default=0.5,
            ),
        )
        form2 = VisLFormLayout()
        form.addRow("字体", form2)
        form2.addRow(
            getboxlayout(
                [
                    getsmalllabel("跟随默认"),
                    getsimpleswitch(
                        globalconfig,
                        "kanafontfollowdefault",
                        default=True,
                        callback=lambda x: (
                            form2.setRowVisible(1, not x),
                            gobject.base.translation_ui.translate_text.setfontstyle(),
                        ),
                    ),
                    "",
                ]
            )
        )
        form2.addRow(
            getboxlayout(
                [
                    self.createtextfontcom(
                        "kanafont",
                        globalconfig.get(
                            "fonttype", gobject.tempconfig.get("fonttype", "")
                        ),
                    ),
                    getIconSwitch(
                        globalconfig,
                        "kanabold",
                        callback=gobject.base.translation_ui.translate_text.setfontstyle,
                        tips="加粗",
                        default=globalconfig.get("showbold", False),
                        icon="fa.bold",
                    ),
                    getIconSwitch(
                        globalconfig,
                        "kanaitalic",
                        callback=gobject.base.translation_ui.translate_text.setfontstyle,
                        tips="倾斜",
                        default=globalconfig.get("showitalic", False),
                        icon="fa.italic",
                    ),
                ]
            ),
        )
        form2.setRowVisible(1, not globalconfig.get("kanafontfollowdefault", True))


def _opencommunitycishu(self):
    dlg = getattr(self, "_communitycishudlg", None)
    if dlg is not None and dlg.isVisible():
        dlg.raise_()
        dlg.activateWindow()
        return
    self._communitycishudlg = CommunityCishuDialog(
        self, oninstalled=functools.partial(rebuildcishugrid, self)
    )


def _headercishubuttons(self):
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    btns = [
        D_getdoclink("internaldict.html")(),
        D_getIconButton(
            callback=functools.partial(_opencommunitycishu, self),
            icon="fa.download",
            tips="社区辞书",
        )(),
    ]
    for b in btns:
        lay.addWidget(b)

    def _refit(*_):
        w.setFixedSize(lay.sizeHint())

    for b in btns:
        b.sizeChanged.connect(_refit)
    _refit()
    return w


def setTabcishu_l(self):

    grids_1 = [functools.partial(fenciqisettings, self)]
    _, online = splitocrtypes(globalconfig["cishu"])
    cishu = dict(
        title="辞书",
        widget=functools.partial(_headercishubuttons, self),
        type="grid",
        grid=[
            [(functools.partial(mdictsettings, self), 0)],
            [
                dict(
                    title="在线",
                    type="grid",
                    parent=self,
                    internallayoutname="cishugridinternal",
                    grid=initinternal(self, online),
                )
            ],
        ],
    )

    def _getkeys(key):
        edit = KeySequenceEdit(callonlymod=True)
        edit.setString(globalconfig["wordclickkbtrigger"].get(key, ""))
        edit.changeedvent.connect(
            functools.partial(globalconfig["wordclickkbtrigger"].__setitem__, key)
        )
        return edit

    zhuyin = dict(
        title="注音",
        type="grid",
        parent=self,
        name="fenyinsettings",
        enable=globalconfig.get("isshowrawtext", True),
        hiderows=[1],
        widget=D_getdoclink("qa1.html"),
        grid=(
            [
                getsmalllabel("显示"),
                D_getsimpleswitch(
                    globalconfig,
                    "isshowhira",
                    callback=gobject.base.translation_ui.translate_text.showhidert,
                    default=True,
                ),
                D_getcolorbutton(
                    self,
                    globalconfig,
                    "jiamingcolor",
                    callback=gobject.base.translation_ui.translate_text.setcolorstyle,
                    tips="注音颜色",
                    default="black",
                ),
                "",
                getsmalllabel("日语注音方案"),
                D_getsimplecombobox(
                    [
                        "平假名",
                        "片假名",
                        "罗马音",
                    ],
                    globalconfig,
                    "hira_vis_type",
                    callback=lambda _: gobject.base.translation_ui.translate_text.refreshcontent(),
                    default=0,
                ),
                "",
                getsmalllabel("字体"),
                getIconSwitch(
                    icon="fa.gear",
                    checkablechangecolor=False,
                    callback=lambda x: self.fenyinsettings.layout().setRowVisible(1, x),
                ),
            ],
            [(functools.partial(fontsettings, self), 0)],
        ),
    )

    def showhidebutton(idx):
        return getIconSwitch(
            icon="fa.gear",
            checkablechangecolor=False,
            callback=lambda x: self.triggerfuncs.layout().setRowVisible(idx, x),
        )

    def manysettings(title, k, k2, extra=None, canhover=True):
        grid = [
            [
                "触发方式",
                D_getsimplecombobox(
                    ["左键点击", "右键点击", "中键点击", "鼠标悬停"][
                        : (4 if canhover else 3)
                    ],
                    globalconfig,
                    k=k,
                    internal=["left", "right", "mid", "hover"][
                        : (4 if canhover else 3)
                    ],
                    default="left",
                    callback=gobject.base.translation_ui.translate_text.showhideclick,
                ),
                "",
                getsmalllabel("需要键盘按下"),
                D_getsimpleswitch(
                    globalconfig["wordclickkbtriggerneed"],
                    k2,
                    default=False,
                ),
                functools.partial(_getkeys, k2),
            ],
            [
                "使用单词原型",
                D_getsimpleswitch(
                    globalconfig["usewordoriginfor"],
                    k2,
                    default=False,
                ),
            ],
        ]
        if extra:
            grid[-1] += [getsmalllabel("")] + extra
        grid[-1] += [""]
        return dict(title=title, type="form", grid=grid)

    triggerfuncs = [
        [
            "显示详细信息",
            D_getsimpleswitch(
                globalconfig,
                "word_hover_show_word_info",
                callback=lambda _: (
                    gobject.base.translation_ui.translate_text.set_word_hover_show_word_info(
                        _
                    ),
                    gobject.base.translation_ui.translate_text.showhideclick(_),
                ),
                default=False,
            ),
            functools.partial(showhidebutton, 2),
            "",
            "",
            "复制到剪贴板",
            D_getsimpleswitch(
                globalconfig,
                "usecopyword",
                callback=gobject.base.translation_ui.translate_text.showhideclick,
                default=False,
            ),
            functools.partial(showhidebutton, 3),
            "",
            "",
            "",
        ],
        [
            "查词",
            D_getsimpleswitch(
                globalconfig,
                "usesearchword",
                callback=gobject.base.translation_ui.translate_text.showhideclick,
                default=True,
            ),
            functools.partial(showhidebutton, 4),
            D_getIconButton(
                lambda: gobject.base.searchwordW.showsignal.emit(),
                icon="fa.search",
                tips="查词",
            ),
            "",
            "查词_在小窗口中",
            D_getsimpleswitch(
                globalconfig,
                "usesearchword_S",
                callback=gobject.base.translation_ui.translate_text.showhideclick,
                default=False,
            ),
            functools.partial(showhidebutton, 5),
        ],
        [
            dict(
                title="显示详细信息",
                type="form",
                grid=[
                    ["触发方式", "鼠标悬停"],
                    [
                        dict(
                            title="样式",
                            type="form",
                            grid=tooltipssetting(self),
                        )
                    ],
                ],
            )
        ],
        [
            manysettings(
                "复制到剪贴板", "copyword_mousetrigger", "copyword", canhover=False
            )
        ],
        [
            manysettings(
                "查词",
                "searchword_mousetrigger",
                "searchword",
                [
                    getsmalllabel("辞书显示顺序"),
                    D_getIconButton(functools.partial(vistranslate_rank, self)),
                ],
                canhover=False,
            )
        ],
        [
            manysettings(
                "查词_在小窗口中",
                "searchword_S_mousetrigger",
                "searchword_S",
                [
                    getsmalllabel("辞书显示顺序"),
                    D_getIconButton(functools.partial(vistranslate_rank, self)),
                    getsmalllabel(""),
                    getsmalllabel("不使用的辞书"),
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
                ],
                canhover=True,
            )
        ],
    ]

    fenci = dict(
        title="分词",
        type="grid",
        parent=self,
        name="fencisettings",
        enable=globalconfig.get("isshowrawtext", True),
        grid=(
            [
                getsmalllabel("语法加亮"),
                D_getsimpleswitch(
                    globalconfig,
                    "show_fenci",
                    callback=lambda _: (
                        gobject.base.translation_ui.translate_text.setcolorstyle(),
                        gobject.base.translation_ui.translate_text.showhideclick(_),
                    ),
                    default=True,
                ),
                D_getIconButton(
                    icon="fa.paint-brush",
                    callback=lambda: multicolorset(self),
                    tips="语法加亮_颜色设置",
                ),
                D_getcolorbutton(
                    self,
                    globalconfig,
                    "hovercolor",
                    callback=gobject.base.translation_ui.translate_text.sethovercolor,
                    alpha=True,
                    default="#80000000",
                    tips="鼠标悬停_颜色设置",
                ),
                "",
            ],
            [
                dict(
                    title="触发功能",
                    type="grid",
                    parent=self,
                    name="triggerfuncs",
                    hiderows=[2, 3, 4, 5],
                    grid=triggerfuncs,
                )
            ],
        ),
    )

    grids = [
        grids_1,
        [cishu],
        [],
        [zhuyin],
        [fenci],
    ]
    return grids
