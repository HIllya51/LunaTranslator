from qtsymbols import *
import functools, os
import gobject, qtawesome, uuid, shutil
from myutils.config import globalconfig, translatorsetting, static_data
from myutils.utils import (
    selectdebugfile,
    splittranslatortypes,
    dynamiclink,
    translate_exits,
    dynamicapiname,
)
from gui.pretransfile import sqlite2json
from gui.inputdialog import autoinitdialog, autoinitdialog_items, autoinitdialogx
from gui.usefulwidget import (
    D_getspinbox,
    getIconButton,
    D_getcolorbutton,
    Prompt_dialog,
    getcolorbutton,
    getsimpleswitch,
    D_getIconButton,
    D_getsimpleswitch,
    selectcolor,
    makegrid,
    makesubtab_lazy,
    makescrollgrid,
)
from gui.dynalang import LPushButton, LLabel, LAction
from gui.setting_about import offlinelinks


def deepcopydict(d):
    if isinstance(d, dict):
        nd = {}
        for k in d:
            nd[k] = deepcopydict(d[k])
        return nd
    elif isinstance(d, list):
        nd = []
        for k in d:
            nd.append(deepcopydict(k))
        return nd
    else:
        return d


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
        parent,
        __d,
        ("删除" if copy else "复制") + "接口",
        600,
        __,
    )


def renameapi(qlabel: QLabel, apiuid, _):
    menu = QMenu(qlabel)
    editname = LAction("重命名")
    menu.addAction(editname)
    action = menu.exec(qlabel.mapToGlobal(_))
    if action == editname:
        before = dynamicapiname(apiuid)
        _dia = Prompt_dialog(
            qlabel,
            "重命名",
            "",
            [
                [
                    "名称",
                    before,
                ],
            ],
        )

        if _dia.exec():
            title = _dia.text[0].text()
            if title not in ("", before):
                globalconfig["fanyi"][apiuid]["name_self_set"] = title
                qlabel.setText(title)


def getrenameablellabel(uid):
    name = LLabel(dynamicapiname(uid))
    name.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    name.customContextMenuRequested.connect(functools.partial(renameapi, name, uid))
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
    return autoinitdialogx(
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

    globalconfig["fanyi"][uid] = deepcopydict(globalconfig["fanyi"][fanyi])
    globalconfig["fanyi"][uid]["use"] = False

    if not name:
        name = globalconfig["fanyi"][fanyi]["name"] + "_copy"
    globalconfig["fanyi"][uid]["name"] = name
    globalconfig["fanyi"][uid]["type"] = btnplus
    if fanyi in translatorsetting:
        translatorsetting[uid] = deepcopydict(translatorsetting[fanyi])

    layout: QGridLayout = getattr(self, "damoxinggridinternal" + btnplus)

    last = getIconButton(
        callback=functools.partial(loadbutton, self, uid),
        icon="fa.gear",
    )

    name = getrenameablellabel(uid)
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


def createbtn(self, countnum, btnplus):
    btn = QPushButton(self)
    btn.setIcon(qtawesome.icon("fa.plus"))
    btn.clicked.connect(functools.partial(btnpluscallback, self, countnum, btnplus))
    setattr(self, "btnadd" + btnplus, btn)
    return btn


class Shit(QWidget):
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
    hbox = QHBoxLayout()
    hbox.setContentsMargins(0, 0, 0, 0)
    w = Shit()
    w.setLayout(hbox)

    btn = QPushButton(self)
    btn.setIcon(qtawesome.icon("fa.plus"))
    btn.clicked.connect(functools.partial(btnpluscallback, self, countnum, btnplus))

    hbox.addWidget(btn)

    btn = QPushButton(self)
    btn.setIcon(qtawesome.icon("fa.minus"))
    btn.clicked.connect(functools.partial(btndeccallback, self, countnum, btnplus))

    hbox.addWidget(btn)

    btn = QPushButton(self)
    btn.setIcon(qtawesome.icon("fa.question"))
    if btnplus == "offline":
        btn.clicked.connect(
            lambda: gobject.baseobject.openlink(
                dynamiclink("{docs_server}/#/zh/offlinellm")
            )
        )
    elif btnplus == "api":
        btn.clicked.connect(
            lambda: gobject.baseobject.openlink(
                dynamiclink("{docs_server}/#/zh/guochandamoxing")
            )
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
            last = D_getIconButton(
                callback=functools.partial(loadbutton, self, fanyi),
                icon="fa.gear",
            )
        elif fanyi == "selfbuild":
            last = D_getIconButton(
                callback=lambda: selectdebugfile("./userconfig/selfbuild.py"),
                icon="fa.gear",
            )
        else:
            last = ""
        line += [
            functools.partial(getrenameablellabel, fanyi),
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
                callback=lambda x: gobject.baseobject.translation_ui.translate_text.textbrowser.showhidetranslatorname(
                    x
                ),
            ),
            "",
            "使用翻译缓存",
            D_getsimpleswitch(globalconfig, "uselongtermcache"),
        ],
        [
            "最短翻译字数",
            D_getspinbox(0, 9999, globalconfig, "minlength"),
            "",
            "最长翻译字数",
            D_getspinbox(0, 9999, globalconfig, "maxlength"),
            "",
            "翻译请求间隔_(s)",
            D_getspinbox(
                0, 9999, globalconfig, "requestinterval", step=0.1, double=True
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

    do()
    dotab()
