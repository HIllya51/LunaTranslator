from qtsymbols import *
import functools, os
import gobject, uuid, shutil, copy
from myutils.config import globalconfig, translatorsetting
from myutils.utils import (
    selectdebugfile,
    splittranslatortypes,
    dynamiclink,
    translate_exits,
    _TR,
    getannotatedapiname,
    dynamicapiname,
)
from gui.pretransfile import sqlite2json
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getspinbox,
    getIconButton,
    D_getcolorbutton,
    getcolorbutton,
    getsimpleswitch,
    D_getIconButton,
    D_getsimpleswitch,
    listediter,
    selectcolor,
    makegrid,
    makesubtab_lazy,
    getspinbox,
    ClickableLabel,
    automakegrid,
    FocusFontCombo,
    getsmalllabel,
    makescrollgrid,
    IconButton,
    PopupWidget,
)
from gui.setting_display_text import GetFormForLineHeight
from gui.dynalang import LPushButton, LAction
from gui.setting_about import offlinelinks


def splitapillm(l):
    not_is_gpt_like = []
    is_gpt_likes = []
    for fanyi in l:
        is_gpt_like = globalconfig["fanyi"][fanyi].get("is_gpt_like", False)
        if is_gpt_like:
            is_gpt_likes.append(fanyi)
        else:
            not_is_gpt_like.append(fanyi)
    return is_gpt_likes, not_is_gpt_like


def loadvisinternal(btnplus, copy):
    __vis = []
    __uid = []
    lixians, pre, mianfei, shoufei = splittranslatortypes()
    if btnplus == "api":
        is_gpt_likes, not_is_gpt_like = splitapillm(shoufei)
    elif btnplus == "offline":
        is_gpt_likes, not_is_gpt_like = splitapillm(lixians)

    for _ in is_gpt_likes:
        if copy:
            which = translate_exits(_, which=True)
            if which != 1:
                continue
        else:
            if not translate_exits(_):
                continue
        __vis.append(dynamicapiname(_))
        __uid.append(_)
    return __vis, __uid


def getalistname(parent, copy, btnplus, callback):
    __d = {"k": 0, "n": ""}
    __vis, __uid = loadvisinternal(btnplus, copy)

    def __wrap(callback, __d, __uid):
        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        callback(uid, __d["n"])

    __ = []
    __.append(
        {
            "type": "combo",
            "name": "复制自" if not copy else "删除",
            "k": "k",
            "list": __vis,
        }
    )
    if not copy:
        __.append(
            {
                "name": "命名为",
                "type": "lineedit",
                "k": "n",
            }
        )

    __.append(
        {
            "type": "okcancel",
            "callback": functools.partial(__wrap, callback, __d, __uid),
        }
    )
    autoinitdialog(
        parent, __d, ("删除" if copy else "复制") + "接口", 600, __, exec_=True
    )


class SpecialFont(PopupWidget):
    def __init__(self, apiuid, p):
        super().__init__(p)
        self.apiuid = apiuid
        box = QGridLayout(self)
        grid = []
        grid.append(
            [
                "",
                "跟随默认",
            ]
        )
        if "privatefont" not in globalconfig["fanyi"][apiuid]:
            globalconfig["fanyi"][apiuid]["privatefont"] = {}
        dd = globalconfig["fanyi"][apiuid]["privatefont"]
        for i in range(4):
            if i == 0:
                t = "字体"
                k = "fontfamily"
                w = QPushButton()

                def _f(dd, key, x):
                    dd[key] = x
                    self.resetfont()

                w = FocusFontCombo()
                w.setCurrentFont(QFont(dd.get(k, globalconfig["fonttype2"])))
                w.currentTextChanged.connect(functools.partial(_f, dd, k))
            elif i == 1:
                t = "字体大小"
                k = "fontsize"
                w = getspinbox(
                    1,
                    100,
                    dd,
                    k,
                    double=True,
                    step=0.1,
                    default=globalconfig[k],
                    callback=self.resetfont,
                )
            elif i == 2:
                t = "加粗"
                k = "showbold"
                w = getsimpleswitch(
                    dd, k, default=globalconfig[k], callback=self.resetfont
                )
            elif i == 3:
                t = "间距"
                k = "lineheight"
                w = QWidget()
                GetFormForLineHeight(w, dd, self.resetfont)

            w.setEnabled(not dd.get(k + "_df", True))
            switch = D_getsimpleswitch(
                dd,
                k + "_df",
                callback=functools.partial(self.disableclear, w),
                default=True,
            )
            grid.append([getsmalllabel(t), switch, w])
        automakegrid(box, grid)

    def disableclear(self, w: QWidget, _):
        w.setEnabled(not _)
        self.resetfont()

    def resetfont(self, _=None):
        gobject.baseobject.translation_ui.translate_text.setfontextra(self.apiuid)


def renameapi(qlabel: QLabel, apiuid, self, countnum, btnplus, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    specialfont = LAction("字体设置", menu)
    delete = LAction("删除", menu)
    copy = LAction("复制", menu)
    menu.addAction(editname)
    menu.addAction(specialfont)
    which = translate_exits(apiuid, which=True)
    is_gpt_like = globalconfig["fanyi"][apiuid].get("is_gpt_like", False)
    if is_gpt_like:
        menu.addSeparator()
        menu.addAction(copy)
    if which == 1:
        menu.addAction(delete)
    pos = QCursor.pos()
    action = menu.exec(pos)
    if action == delete:
        selectllmcallback_2(self, countnum, btnplus, apiuid, None)
    elif action == editname:
        before = dynamicapiname(apiuid)
        __d = {"k": before}

        def cb(__d):
            title = __d["k"]
            if title not in ("", before):
                globalconfig["fanyi"][apiuid]["name_self_set"] = title
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
    elif action == specialfont:
        SpecialFont(apiuid, self).display(pos)
    elif action == copy:
        selectllmcallback(self, countnum, btnplus, apiuid, None)


def getrenameablellabel(uid, self, countnum, btnplus):
    name = ClickableLabel(dynamicapiname(uid))
    fn = functools.partial(renameapi, name, uid, self, countnum, btnplus)
    name.clicked.connect(fn)
    return name


def loadbutton(self, fanyi):
    which = translate_exits(fanyi, which=True)
    items = autoinitdialog_items(translatorsetting[fanyi])
    if which == 0:
        aclass = "translator." + fanyi
    elif which == 1:
        aclass = "userconfig.copyed." + fanyi
    else:
        return
    return autoinitdialog(
        self,
        translatorsetting[fanyi]["args"],
        dynamicapiname(fanyi),
        800,
        items,
        aclass,
        fanyi,
    )


def selectllmcallback(self, countnum, btnplus, fanyi, name):
    uid = str(uuid.uuid4())
    _f11 = "./Lunatranslator/translator/{}.py".format(fanyi)
    _f12 = "./userconfig/copyed/{}.py".format(fanyi)
    _f2 = "./userconfig/copyed/{}.py".format(uid)
    os.makedirs("./userconfig/copyed", exist_ok=True)
    try:
        shutil.copy(_f11, _f2)
    except:
        shutil.copy(_f12, _f2)

    globalconfig["fanyi"][uid] = copy.deepcopy(globalconfig["fanyi"][fanyi])
    globalconfig["fanyi"][uid]["use"] = False

    if not name:
        name = globalconfig["fanyi"][fanyi]["name"] + "_copy"
    globalconfig["fanyi"][uid]["name"] = name
    globalconfig["fanyi"][uid]["type"] = btnplus
    if fanyi in translatorsetting:
        translatorsetting[uid] = copy.deepcopy(translatorsetting[fanyi])

    layout: QGridLayout = getattr(self, "damoxinggridinternal" + btnplus)

    last = getIconButton(callback=functools.partial(loadbutton, self, uid))

    name = getrenameablellabel(uid, self, countnum, btnplus)
    swc = getsimpleswitch(
        globalconfig["fanyi"][uid],
        "use",
        callback=functools.partial(gobject.baseobject.prepare, uid),
    )
    color = getcolorbutton(
        globalconfig["fanyi"][uid],
        "color",
        parent=self,
        name="fanyicolor_" + uid,
        callback=functools.partial(
            selectcolor,
            self,
            globalconfig["fanyi"][uid],
            "color",
            None,
            self,
            "fanyicolor_" + uid,
        ),
    )

    offset = 5 * (len(countnum) % 3)
    layout.addWidget(name, layout.rowCount() - 1, offset + 0)
    layout.addWidget(swc, layout.rowCount() - 1, offset + 1)
    layout.addWidget(color, layout.rowCount() - 1, offset + 2)
    layout.addWidget(last, layout.rowCount() - 1, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), layout.rowCount() - 1, offset + 4)

    else:
        layout.addWidget(
            getattr(self, "btnmany" + btnplus), layout.rowCount(), 5 * 2, 1, 4
        )
    countnum.append(uid)


def btnpluscallback(self, countnum, btnplus):
    getalistname(
        self,
        False,
        btnplus,
        functools.partial(selectllmcallback, self, countnum, btnplus),
    )


class Shit(QGroupBox):
    pass


def selectllmcallback_2(self, countnum, btnplus, fanyi, name):
    _f2 = "./userconfig/copyed/{}.py".format(fanyi)
    try:
        os.remove(_f2)
    except:
        pass
    globalconfig["fanyi"][fanyi]["use"] = False
    try:
        gobject.baseobject.translators.pop(fanyi)
    except:
        pass
    layout: QGridLayout = getattr(self, "damoxinggridinternal" + btnplus)
    idx = countnum.index(fanyi)
    line = idx // 3
    off = line * 14 + (idx % 3) * 5
    do = 0
    i = 0
    while do < 4:

        w = layout.itemAt(off + i).widget()
        i += 1
        if isinstance(w, Shit):
            continue
        elif isinstance(w, QLabel) and w.text() == "":
            continue
        elif not w.isEnabled():
            continue
        w.setEnabled(False)
        do += 1


def btndeccallback(self, countnum, btnplus):
    getalistname(
        self,
        True,
        btnplus,
        functools.partial(selectllmcallback_2, self, countnum, btnplus),
    )


def createmanybtn(self, countnum, btnplus):
    w = Shit()
    hbox = QHBoxLayout(w)
    hbox.setContentsMargins(0, 0, 0, 0)

    btn = IconButton("fa.plus")
    btn.clicked.connect(functools.partial(btnpluscallback, self, countnum, btnplus))

    hbox.addWidget(btn)

    btn = IconButton("fa.minus")
    btn.clicked.connect(functools.partial(btndeccallback, self, countnum, btnplus))

    hbox.addWidget(btn)

    btn = IconButton("fa.question")
    if btnplus == "offline":
        btn.clicked.connect(
            lambda: os.startfile(dynamiclink("{docs_server}/offlinellm.html"))
        )
    elif btnplus == "api":
        btn.clicked.connect(
            lambda: os.startfile(dynamiclink("{docs_server}/guochandamoxing.html"))
        )
    hbox.addWidget(btn)
    setattr(self, "btnmany" + btnplus, w)
    return w


def initsome11(self, l, label=None, btnplus=False):
    grids = []
    if label:
        grids.append([(label, 8)])
    i = 0
    line = []
    countnum = []
    for fanyi in l:
        which = translate_exits(fanyi, which=True)
        if which is None:
            continue
        i += 1
        countnum.append(fanyi)
        if fanyi in translatorsetting:
            last = D_getIconButton(callback=functools.partial(loadbutton, self, fanyi))
        elif fanyi == "selfbuild":
            last = D_getIconButton(
                callback=lambda: selectdebugfile("./userconfig/selfbuild.py"),
                icon="fa.edit",
            )
        else:
            last = ""
        line += [
            functools.partial(getrenameablellabel, fanyi, self, countnum, btnplus),
            D_getsimpleswitch(
                globalconfig["fanyi"][fanyi],
                "use",
                callback=functools.partial(gobject.baseobject.prepare, fanyi),
            ),
            D_getcolorbutton(
                globalconfig["fanyi"][fanyi],
                "color",
                parent=self,
                name="fanyicolor_" + fanyi,
                callback=functools.partial(
                    selectcolor,
                    self,
                    globalconfig["fanyi"][fanyi],
                    "color",
                    None,
                    self,
                    "fanyicolor_" + fanyi,
                    callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                ),
            ),
            last,
        ]

        if i % 3 == 0:
            grids.append(line)
            line = []
        else:
            line += [""]
    if len(line):
        grids.append(line)
    if btnplus:

        if i % 3 == 0:
            grids.append([])
        if i % 3 != 2:
            grids[-1].append(("", 5 * (2 - i % 3)))
        grids[-1].append((functools.partial(createmanybtn, self, countnum, btnplus), 4))

    return grids


def initsome2(self, l, label=None, btnplus=None):
    is_gpt_likes, not_is_gpt_like = splitapillm(l)
    not_is_gpt_like = initsome11(self, not_is_gpt_like, label)
    is_gpt_likes = initsome11(self, is_gpt_likes, label, btnplus=btnplus)
    grids = [
        [
            (
                dict(type="grid", title="传统", grid=not_is_gpt_like),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    type="grid",
                    title="大模型",
                    grid=is_gpt_likes,
                    internallayoutname=(
                        ("damoxinggridinternal" + btnplus) if btnplus else None
                    ),
                    parent=self,
                ),
                0,
                "group",
            )
        ],
    ]
    return grids


def createbtnexport(self):

    bt = LPushButton("导出翻译记录为json文件")
    bt.clicked.connect(lambda x: sqlite2json(self))
    return bt


def __changeuibuttonstate2(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.maybeneedtranslateshowhidetranslate()


def vistranslate_rank(self):
    _not = []
    for i, k in enumerate(globalconfig["fix_translate_rank_rank"]):
        if not translate_exits(k):
            _not.append(i)
    for _ in reversed(_not):
        globalconfig["fix_translate_rank_rank"].pop(_)
    listediter(
        self,
        "显示顺序",
        globalconfig["fix_translate_rank_rank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(getannotatedapiname(k)),
        exec=True,
    )


def setTabTwo_lazy(self, basel: QVBoxLayout):
    # 均衡负载  loadbalance
    # 单次负载个数 loadbalance_oncenum
    # 过时的，不再在ui中展示
    grids = [
        [
            "使用翻译",
            D_getsimpleswitch(
                globalconfig,
                "showfanyi",
                callback=lambda x: __changeuibuttonstate2(self, x),
                name="show_fany_switch",
                parent=self,
            ),
            "",
            "显示翻译器名称",
            D_getsimpleswitch(
                globalconfig,
                "showfanyisource",
                callback=gobject.baseobject.translation_ui.translate_text.showhidename,
            ),
            "",
            "固定翻译显示顺序",
            D_getsimpleswitch(globalconfig, "fix_translate_rank"),
            D_getIconButton(functools.partial(vistranslate_rank, self)),
        ],
        [
            "最短翻译字数",
            D_getspinbox(0, 9999, globalconfig, "minlength"),
            "",
            "最长翻译字数",
            D_getspinbox(0, 9999, globalconfig, "maxlength"),
            "",
            "翻译请求间隔_(s)",
            (
                D_getspinbox(
                    0, 9999, globalconfig, "requestinterval", step=0.1, double=True
                ),
                0,
            ),
        ],
    ]
    online_reg_grid = [[("若有多个api key，用|将每个key连接后填入，即可轮流使用", -1)]]
    pretransgrid = [
        [
            (
                dict(
                    type="grid",
                    grid=(
                        [
                            "模糊匹配_相似度_%",
                            D_getspinbox(0, 100, globalconfig, "premtsimi2"),
                            "",
                            "",
                            "",
                        ],
                        [
                            (functools.partial(createbtnexport, self), 0),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [],
    ]

    lixians, pre, mianfei, shoufei = splittranslatortypes()

    offlinegrid = initsome2(self, lixians, btnplus="offline")
    offlinegrid += [[functools.partial(offlinelinks, "translate")]]
    onlinegrid = initsome11(self, mianfei)
    online_reg_grid += initsome2(self, shoufei, btnplus="api")
    pretransgrid += initsome11(self, pre)

    gridlayoutwidget, do = makegrid(grids, delay=True)
    basel.addWidget(gridlayoutwidget)
    tab, dotab = makesubtab_lazy(
        ["在线翻译", "注册在线翻译", "离线翻译", "预翻译"],
        [
            functools.partial(makescrollgrid, onlinegrid),
            functools.partial(makescrollgrid, online_reg_grid),
            functools.partial(makescrollgrid, offlinegrid),
            functools.partial(makescrollgrid, pretransgrid),
        ],
        delay=True,
    )
    basel.addWidget(tab)

    basel.setSpacing(0)
    do()
    dotab()
