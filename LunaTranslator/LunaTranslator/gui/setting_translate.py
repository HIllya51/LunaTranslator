from qtsymbols import *
import functools, os
import gobject, qtawesome, uuid, shutil
from myutils.config import globalconfig, translatorsetting
from myutils.utils import (
    selectdebugfile,
    splittranslatortypes,
    dynamiclink,
    translate_exits,
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
    selectcolor,
    makegrid,
    makesubtab_lazy,
    makescrollgrid,
    getvboxwidget,
)
from traceback import print_exc
from gui.dynalang import LPushButton, LLabel


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
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()
    if btnplus == "api":
        is_gpt_likes, not_is_gpt_like = splitapillm(shoufei)
    elif btnplus == "offline":
        is_gpt_likes, not_is_gpt_like = splitapillm(lixians)
    elif btnplus == "develop":
        is_gpt_likes, not_is_gpt_like = splitapillm(develop)

    for _ in is_gpt_likes:
        if copy:
            which = translate_exits(_, which=True)
            if which != 1:
                continue
        else:
            if not translate_exits(_):
                continue
        __vis.append(globalconfig["fanyi"][_]["name"])
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
            "d": __d,
            "k": "k",
            "list": __vis,
        }
    )
    if not copy:
        __.append(
            {
                "name": "命名为",
                "type": "lineedit",
                "d": __d,
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
        ("删除" if copy else "复制") + "接口",
        600,
        __,
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

    items = autoinitdialog_items(translatorsetting[uid])
    last = getIconButton(
        callback=functools.partial(
            autoinitdialog,
            self,
            (globalconfig["fanyi"][uid]["name"]),
            800,
            items,
        ),
        icon="fa.gear",
    )

    name = LLabel(globalconfig["fanyi"][uid]["name"])
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

    if len(countnum) % 3 == 0:
        layout.addWidget(
            getattr(self, "btnmany" + btnplus), layout.rowCount(), 5 * 2, 1, 4
        )
    offset = 5 * (len(countnum) % 3)
    layout.addWidget(name, layout.rowCount() - 2, offset + 0)
    layout.addWidget(swc, layout.rowCount() - 2, offset + 1)
    layout.addWidget(color, layout.rowCount() - 2, offset + 2)
    layout.addWidget(last, layout.rowCount() - 2, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), layout.rowCount() - 2, offset + 4)

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
    elif btnplus == "develop":
        btn.clicked.connect(
            lambda: gobject.baseobject.openlink(
                dynamiclink("{docs_server}/#/zh/tiaoshiliulanqi")
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

        if not translate_exits(fanyi):
            continue
        i += 1
        countnum.append(fanyi)
        if fanyi in translatorsetting:

            items = autoinitdialog_items(translatorsetting[fanyi])
            last = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    (globalconfig["fanyi"][fanyi]["name"]),
                    800,
                    items,
                ),
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
            globalconfig["fanyi"][fanyi]["name"],
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
        grids.append(
            [
                ("", 10),
                (functools.partial(createmanybtn, self, countnum, btnplus), 4),
            ]
        )

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


def statuslabelsettext(self, text):
    try:
        self.statuslabel.setText(text)
    except:
        pass


def createstatuslabel(self):

    self.statuslabel = LLabel()
    return self.statuslabel


def createbtnexport(self):

    bt = LPushButton("导出翻译记录为json文件")
    bt.clicked.connect(lambda x: sqlite2json(self))
    return bt


def __changeuibuttonstate2(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()


def setTabTwo_lazy(self, basel):
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
            D_getsimpleswitch(globalconfig, "showfanyisource"),
            "",
            "翻译请求间隔(s)",
            D_getspinbox(
                0, 9999, globalconfig, "requestinterval", step=0.1, double=True
            ),
        ],
        [
            "使用翻译缓存",
            D_getsimpleswitch(globalconfig, "uselongtermcache"),
            "",
            "最短翻译字数",
            D_getspinbox(0, 9999, globalconfig, "minlength"),
            "",
            "最长翻译字数",
            D_getspinbox(0, 9999, globalconfig, "maxlength"),
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
                            "预翻译采用模糊匹配",
                            D_getsimpleswitch(globalconfig, "premtsimiuse"),
                            "",
                            "模糊匹配_相似度_%",
                            D_getspinbox(0, 100, globalconfig, "premtsimi2"),
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
    _items = [
        {
            "type": "file",
            "dir": False,
            "filter": "*.exe",
            "name": "Chromium_路径",
            "d": globalconfig,
            "k": "chromepath",
        },
        {"type": "okcancel"},
    ]

    developgrid = [
        [
            (
                dict(
                    title="Chromium_设置",
                    type="grid",
                    grid=(
                        [
                            "路径",
                            D_getIconButton(
                                callback=functools.partial(
                                    autoinitdialog,
                                    self,
                                    "Chromium_路径",
                                    800,
                                    _items,
                                ),
                                icon="fa.gear",
                            ),
                            "",
                            "端口号",
                            D_getspinbox(0, 65535, globalconfig, "debugport"),
                            "",
                        ],
                        [(functools.partial(createstatuslabel, self), 0)],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()

    offlinegrid = initsome2(self, lixians, btnplus="offline")
    onlinegrid = initsome11(self, mianfei)
    developgrid += initsome2(self, develop, btnplus="develop")
    online_reg_grid += initsome2(self, shoufei, btnplus="api")
    pretransgrid += initsome11(self, pre)
    vw, vl = getvboxwidget()
    basel.addWidget(vw)

    gridlayoutwidget, do = makegrid(grids, delay=True)
    vl.addWidget(gridlayoutwidget)
    tab, dotab = makesubtab_lazy(
        ["在线翻译", "注册在线翻译", "离线翻译", "调试浏览器", "预翻译"],
        [
            functools.partial(makescrollgrid, onlinegrid),
            functools.partial(makescrollgrid, online_reg_grid),
            functools.partial(makescrollgrid, offlinegrid),
            functools.partial(makescrollgrid, developgrid),
            functools.partial(makescrollgrid, pretransgrid),
        ],
        delay=True,
    )
    vl.addWidget(tab)

    do()
    dotab()
