from qtsymbols import *
import os, functools, re
from myutils.config import globalconfig
from myutils.utils import splittranslatortypes, translate_exits
from gui.usefulwidget import (
    D_getsimpleswitch,
    makegrid,
    makesubtab_lazy,
    getvboxwidget,
    makescrollgrid,
    D_getsimplecombobox,
)


def getall(l, item="fanyi", name=None):
    grids = []
    i = 0
    line = []
    for fanyi in l:
        if name:
            if isinstance(name, str):
                _f = name % fanyi
                if not os.path.exists(_f):
                    continue
            elif callable(name):
                if not name(fanyi):
                    continue
        i += 1

        line += [
            globalconfig[item][fanyi].get("name", fanyi),
            D_getsimpleswitch(globalconfig[item][fanyi], "useproxy", default=True),
        ]
        if i % 3 == 0:
            grids.append(line)
            line = []
        else:
            line += [""]
    if len(line):
        grids.append(line)
    return grids


def validator(self, text):
    regExp = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$")
    mch = regExp.match(text)
    for _ in (1,):

        if not mch:
            break
        _1, _2, _3, _4, _p = [int(_) for _ in mch.groups()]
        if _p > 65535:
            break
        if any([_ > 255 for _ in [_1, _2, _3, _4]]):
            break
        globalconfig["proxy"] = text
        self.createproxyedit_check.setText("")
        return
    self.createproxyedit_check.setText("Invalid")


def createproxyedit(self):
    proxy = QLineEdit(globalconfig["proxy"])
    self.__proxyedit = proxy
    proxy.textChanged.connect(functools.partial(validator, self))
    _ifusesysproxy(self, globalconfig["usesysproxy"])
    return proxy


def createproxyedit_check(self):
    self.createproxyedit_check = QLabel()
    return self.createproxyedit_check


def _ifusesysproxy(self, x):
    self.__proxyedit.setEnabled(not x)


def getnotofflines(key):
    __ = []
    for k in globalconfig[key]:
        if globalconfig[key][k].get("type", None) != "offline":
            __.append(k)
    return __


def checkxx(key):
    if not translate_exits(key):
        return False
    return globalconfig["fanyi"][key].get("is_gpt_like", False)


def makeproxytab(self, basel):

    grid1 = [
        [("使用代理", 5), (D_getsimpleswitch(globalconfig, "useproxy"), 1), ("", 10)],
        [
            ("自动获取系统代理", 5),
            (
                D_getsimpleswitch(
                    globalconfig,
                    "usesysproxy",
                    callback=lambda x: _ifusesysproxy(self, x),
                )
            ),
        ],
        [
            ("手动设置代理(ip:port)", 5),
            (functools.partial(createproxyedit, self), 5),
            (functools.partial(createproxyedit_check, self), 5),
        ],
        [],
        [("使用代理的项目", -1)],
    ]
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()

    mianfei = getall(l=mianfei, item="fanyi", name="./Lunatranslator/translator/%s.py")
    shoufei = getall(l=shoufei, item="fanyi", name=translate_exits)
    lixians = getall(l=lixians, item="fanyi", name=checkxx)
    ocrs = getall(
        l=getnotofflines("ocr"),
        item="ocr",
        name="./Lunatranslator/ocrengines/%s.py",
    )
    meta = getall(
        l=globalconfig["metadata"],
        item="metadata",
        name="./LunaTranslator/metadata/%s.py",
    )
    readers = getall(
        l=getnotofflines("reader"),
        item="reader",
        name="./LunaTranslator/tts/%s.py",
    )
    cishus = getall(
        l=getnotofflines("cishu"),
        item="cishu",
        name="./LunaTranslator/cishu/%s.py",
    )
    github = getall(
        l=globalconfig["update"],
        item="update",
    )

    vw, vl = getvboxwidget()
    basel.addWidget(vw)
    gridlayoutwidget, do = makegrid(grid1, delay=True)
    vl.addWidget(gridlayoutwidget)
    tab, dotab = makesubtab_lazy(
        [
            "在线翻译",
            "注册在线翻译",
            "OCR",
            "语音合成",
            "辞书",
            "元数据",
            "离线翻译",
            "自动更新",
        ],
        [
            functools.partial(makescrollgrid, mianfei),
            functools.partial(makescrollgrid, shoufei),
            functools.partial(makescrollgrid, ocrs),
            functools.partial(makescrollgrid, readers),
            functools.partial(makescrollgrid, cishus),
            functools.partial(makescrollgrid, meta),
            functools.partial(makescrollgrid, lixians),
            functools.partial(makescrollgrid, github),
        ],
        delay=True,
    )
    vl.addWidget(tab)
    do()
    dotab()


def setTab_proxy_lazy(self, basel):
    tab, dotab = makesubtab_lazy(
        [
            "代理设置",
            "网络请求",
        ],
        [
            functools.partial(makeproxytab, self),
            functools.partial(
                makescrollgrid,
                [
                    [
                        "HTTP",
                        (
                            D_getsimplecombobox(
                                ["winhttp", "libcurl"],
                                globalconfig,
                                "network",
                                static=True,
                            ),
                            5,
                        ),
                    ],
                    [
                        "WebSocket",
                        (
                            D_getsimplecombobox(
                                ["winhttp", "libcurl"],
                                globalconfig,
                                "network_websocket",
                                static=True,
                            ),
                            5,
                        ),
                    ],
                ],
            ),
        ],
        delay=True,
    )
    basel.addWidget(tab)
    dotab()


def setTab_proxy(self, l):
    setTab_proxy_lazy(self, l)
