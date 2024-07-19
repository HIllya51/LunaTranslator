from qtsymbols import *
import functools, os, time, hashlib
import requests, gobject, qtawesome, uuid, shutil
from myutils.wrapper import threader
from myutils.config import globalconfig, translatorsetting
from myutils.subproc import subproc_w
from myutils.utils import (
    selectdebugfile,
    splittranslatortypes,
    checkportavailable,
    dynamiclink,
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
from gui.dynalang import LPushButton, LLabel


def hashtext(a):
    return hashlib.md5(a.encode("utf8")).hexdigest()


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


def loadvisinternal(skipid=False, skipidid=None):
    __vis = []
    __uid = []
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()
    is_gpt_likes, not_is_gpt_like = splitapillm(shoufei)
    for _ in is_gpt_likes:
        _f = "./Lunatranslator/translator/{}.py".format(_)
        if not os.path.exists(_f):
            continue
        __vis.append(globalconfig["fanyi"][_]["name"])
        __uid.append(_)
    return __vis, __uid


def getalistname(parent, callback, skipid=False, skipidid=None):
    __d = {"k": 0, "n": ""}
    __vis, __uid = loadvisinternal(skipid, skipidid)

    def __wrap(callback, __d, __uid):
        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        callback(uid, __d["n"])

    autoinitdialog(
        parent,
        "复制",
        600,
        [
            {
                "type": "combo",
                "name": "目标",
                "d": __d,
                "k": "k",
                "list": __vis,
            },
            {
                "name": "名称",
                "type": "lineedit",
                "d": __d,
                "k": "n",
            },
            {
                "type": "okcancel",
                "callback": functools.partial(__wrap, callback, __d, __uid),
            },
        ],
    )


def selectllmcallback(self, countnum, btn, fanyi, name):
    uid = str(uuid.uuid4())
    _f1 = "./Lunatranslator/translator/{}.py".format(fanyi)
    _f2 = "./Lunatranslator/translator/{}.py".format(uid)
    shutil.copy(_f1, _f2)
    globalconfig["fanyi"][uid] = deepcopydict(globalconfig["fanyi"][fanyi])
    globalconfig["fanyi"][uid]["use"] = False

    if not name:
        name = globalconfig["fanyi"][fanyi]["name"] + "_copy"
    globalconfig["fanyi"][uid]["name"] = name
    if fanyi in translatorsetting:
        translatorsetting[uid] = deepcopydict(translatorsetting[fanyi])

    layout: QGridLayout = self.damoxinggridinternal

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
        layout.addWidget(btn, layout.rowCount(), 5 * 2, 1, 2)
        layout.addWidget(self.btnquestion, layout.rowCount() - 1, 5 * 2 + 2, 1, 2)
    offset = 5 * (len(countnum) % 3)
    layout.addWidget(name, layout.rowCount() - 2, offset + 0)
    layout.addWidget(swc, layout.rowCount() - 2, offset + 1)
    layout.addWidget(color, layout.rowCount() - 2, offset + 2)
    layout.addWidget(last, layout.rowCount() - 2, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), layout.rowCount() - 2, offset + 4)

    countnum.append(0)


def btnpluscallback(self, countnum, btn):
    getalistname(self, functools.partial(selectllmcallback, self, countnum, btn))


def createbtn(self, countnum):
    btn = QPushButton(self)
    btn.setIcon(qtawesome.icon("fa.plus"))
    btn.clicked.connect(functools.partial(btnpluscallback, self, countnum, btn))
    return btn


def createbtnquest(self):
    btn = QPushButton(self)
    btn.setIcon(qtawesome.icon("fa.question"))
    btn.clicked.connect(
        lambda: os.startfile(dynamiclink("{docs_server}/#/zh/guochandamoxing"))
    )
    self.btnquestion = btn
    return btn


def initsome11(self, l, label=None, btnplus=False):
    grids = []
    if label:
        grids.append([(label, 8)])
    i = 0
    line = []
    countnum = []
    for fanyi in l:

        _f = "./Lunatranslator/translator/{}.py".format(fanyi)
        if not os.path.exists(_f):
            continue
        i += 1
        countnum.append(0)
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
                (functools.partial(createbtn, self, countnum), 2),
                (functools.partial(createbtnquest, self), 2),
            ]
        )

    return grids


def initsome2(self, l, label=None):
    is_gpt_likes, not_is_gpt_like = splitapillm(l)
    not_is_gpt_like = initsome11(self, not_is_gpt_like, label)
    is_gpt_likes = initsome11(self, is_gpt_likes, label, btnplus=True)
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
                    internallayoutname="damoxinggridinternal",
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


@threader
def checkconnected(self):
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()
    while True:
        port = globalconfig["debugport"]
        _path = None
        for syspath in [
            globalconfig["chromepath"],
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]:
            if os.path.exists(syspath) and os.path.isfile(syspath):
                _path = syspath
                break
        needstart = False
        for dev in develop:
            if not globalconfig["fanyi"][dev]["use"]:
                continue

            if not os.path.exists("./LunaTranslator/translator/" + dev + ".py"):
                continue
            needstart = True
            break
        try:

            if needstart:
                requests.get("http://127.0.0.1:{}/json/list".format(port)).json()
                statuslabelsettext(self, "连接成功")
        except:
            if checkportavailable(port):
                statuslabelsettext(self, "连接失败")
                if needstart:
                    call = (
                        '"%s" --disable-extensions --remote-allow-origins=* --disable-gpu --no-first-run --remote-debugging-port=%d --user-data-dir="%s"'
                        % (
                            _path,
                            port,
                            os.path.abspath("./chrome_cache/" + hashtext(_path)),
                        )
                    )
                    print(call)
                    self.engine = subproc_w(call)
            else:
                statuslabelsettext(self, "端口冲突")
        time.sleep(1)


def createbtnexport(self):

    bt = LPushButton("导出翻译记录为json文件")
    bt.clicked.connect(lambda x: sqlite2json(self))
    return bt


def setTabTwo_lazy(self, basel):
    # 均衡负载  loadbalance
    # 单次负载个数 loadbalance_oncenum
    # 过时的，不再在ui中展示
    grids = [
        [
            "最短翻译字数",
            D_getspinbox(0, 9999, globalconfig, "minlength"),
            "",
            "最长翻译字数",
            D_getspinbox(0, 9999, globalconfig, "maxlength"),
            "",
            "",
            "",
            "",
        ],
        [
            "使用翻译缓存",
            D_getsimpleswitch(globalconfig, "uselongtermcache"),
            "",
            "翻译请求间隔(s)",
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
                    ),
                ),
                0,
                "group",
            )
        ],
        [(functools.partial(createstatuslabel, self), 16)],
        [],
    ]
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()

    offlinegrid = initsome11(self, lixians)
    onlinegrid = initsome11(self, mianfei)
    developgrid += initsome11(self, develop)
    online_reg_grid += initsome2(self, shoufei)
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
