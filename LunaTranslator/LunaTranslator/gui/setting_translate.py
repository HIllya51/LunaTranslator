from qtsymbols import *
import functools, os, time, hashlib
import requests, gobject
from myutils.wrapper import threader
from myutils.config import globalconfig, translatorsetting
from myutils.subproc import subproc_w
from myutils.config import globalconfig, _TR, _TRL
from myutils.utils import selectdebugfile, splittranslatortypes, checkportavailable
from gui.pretransfile import sqlite2json
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getspinbox,
    getspinbox,
    D_getcolorbutton,
    D_getsimpleswitch,
    selectcolor,
    makegrid,
    makesubtab_lazy,
    makescrollgrid,
    getvboxwidget,
)


def hashtext(a):
    return hashlib.md5(a.encode("utf8")).hexdigest()


def initsome11(self, l, label=None):
    grids = []
    if label:
        grids.append([(label, 8)])
    i = 0
    line = []
    for fanyi in globalconfig["fanyi"]:

        if fanyi not in l:
            continue

        _f = "./Lunatranslator/translator/{}.py".format(fanyi)
        if fanyi != "selfbuild" and os.path.exists(_f) == False:
            continue
        i += 1

        if fanyi in translatorsetting:

            items = autoinitdialog_items(translatorsetting[fanyi])
            last = D_getcolorbutton(
                globalconfig,
                "",
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    (globalconfig["fanyi"][fanyi]["name"]),
                    800,
                    items,
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            )
        elif fanyi == "selfbuild":
            last = D_getcolorbutton(
                globalconfig,
                "",
                callback=lambda: selectdebugfile("./userconfig/selfbuild.py"),
                icon="fa.gear",
                constcolor="#FF69B4",
            )
        else:
            last = ""
        line += [
            (globalconfig["fanyi"][fanyi]["name"], 6),
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

    self.statuslabel = QLabel()
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
            if dev == "selfbuild":
                if not os.path.exists("./userconfig/selfbuild.py"):
                    continue
            else:
                if not os.path.exists("./LunaTranslator/translator/" + dev + ".py"):
                    continue
            needstart = True
            break
        try:

            if needstart:
                requests.get("http://127.0.0.1:{}/json/list".format(port)).json()
                statuslabelsettext(self, _TR("连接成功"))
        except:
            if checkportavailable(port):
                statuslabelsettext(self, _TR("连接失败"))
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
                statuslabelsettext(self, _TR("端口冲突"))
        time.sleep(1)


def createbtnexport(self):

    bt = QPushButton(_TR("导出翻译记录为json文件"))
    bt.clicked.connect(lambda x: sqlite2json(self))
    return bt


def createfuzspin(self):

    _fuzainum = getspinbox(1, 99999, globalconfig, "loadbalance_oncenum", step=1)
    _fuzainum.setEnabled(globalconfig["loadbalance"])
    self._fuzainum = _fuzainum
    return _fuzainum


def setTabTwo_lazy(self, basel):

    grids = [
        [
            ("最短翻译字数", 7),
            (D_getspinbox(0, 9999, globalconfig, "minlength"), 3),
            "",
            ("最长翻译字数", 7),
            (D_getspinbox(0, 9999, globalconfig, "maxlength"), 3),
            "",
        ],
        [
            ("使用翻译缓存", 8),
            (D_getsimpleswitch(globalconfig, "uselongtermcache")),
            "",
            "",
            ("显示错误信息", 8),
            (D_getsimpleswitch(globalconfig, "showtranexception"), 1),
            "",
            "",
            ("翻译请求间隔(s)", 7),
            (
                D_getspinbox(
                    0, 9999, globalconfig, "requestinterval", step=0.1, double=True
                ),
                3,
            ),
        ],
        [
            ("均衡负载", 8),
            (
                D_getsimpleswitch(
                    globalconfig,
                    "loadbalance",
                    callback=lambda x: self._fuzainum.setEnabled(x),
                )
            ),
            "",
            "",
            ("单次负载个数", 7),
            (functools.partial(createfuzspin, self), 3),
        ],
    ]
    online_reg_grid = [[("若有多个api key，用|将每个key连接后填入，即可轮流使用", -1)]]
    pretransgrid = [
        [
            ("预翻译采用模糊匹配", 6),
            (D_getsimpleswitch(globalconfig, "premtsimiuse"), 1),
            "",
            "",
            "",
            ("模糊匹配_相似度_%", 6),
            (D_getspinbox(0, 100, globalconfig, "premtsimi2"), 4),
        ],
        [
            (functools.partial(createbtnexport, self), 12),
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
            ("Chromium_路径", 8),
            (
                D_getcolorbutton(
                    globalconfig,
                    "",
                    callback=functools.partial(
                        autoinitdialog, self, "Chromium_路径", 800, _items
                    ),
                    icon="fa.gear",
                    constcolor="#FF69B4",
                )
            ),
        ],
        [
            ("端口号", 8),
            (D_getspinbox(0, 65535, globalconfig, "debugport"), 4),
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
        _TRL(["在线翻译", "注册在线翻译", "离线翻译", "调试浏览器", "预翻译"]),
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
