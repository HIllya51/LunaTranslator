from qtsymbols import *
import functools, os, time, hashlib
import requests, gobject
from myutils.wrapper import threader
from myutils.config import globalconfig, translatorsetting
from myutils.subproc import subproc_w
from myutils.config import globalconfig
from myutils.utils import selectdebugfile, splittranslatortypes, checkportavailable
from gui.pretransfile import sqlite2json
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getspinbox,
    getspinbox,
    D_getcolorbutton,
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


def initsome11(self, l, label=None):
    grids = []
    if label:
        grids.append([(label, 8)])
    i = 0
    line = []
    for fanyi in l:

        _f = "./Lunatranslator/translator/{}.py".format(fanyi)
        if not os.path.exists(_f):
            continue
        i += 1

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
    online_reg_grid += initsome11(self, shoufei)
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
