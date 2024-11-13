from qtsymbols import *
import os, functools, re
from myutils.config import globalconfig
from myutils.utils import splittranslatortypes, translate_exits
from gui.usefulwidget import (
    D_getsimpleswitch,
    makegrid,
    makesubtab_lazy,
    LGroupBox,
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


def makegridW(grid, lay, save=False, savelist=None, savelay=None):
    wid, do = makegrid(grid, save, savelist, savelay, delay=True)
    lay.addWidget(wid)
    do()
    return wid


def makeproxytab():

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
            functools.partial(makegridW, mianfei),
            functools.partial(makegridW, shoufei),
            functools.partial(makegridW, ocrs),
            functools.partial(makegridW, readers),
            functools.partial(makegridW, cishus),
            functools.partial(makegridW, meta),
            functools.partial(makegridW, lixians),
            functools.partial(makegridW, github),
        ],
        delay=True,
    )
    dotab()
    return tab


def setTab_proxy(self, l):
    grids = [
        [
            (
                dict(
                    title="网络请求",
                    type="grid",
                    grid=[
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
                            "",
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
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="代理设置",
                    type="grid",
                    grid=[
                        [
                            ("使用代理", 5),
                            (D_getsimpleswitch(globalconfig, "useproxy"), 1),
                            ("", 10),
                        ],
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
                            ("手动设置代理_(ip:port)", 5),
                            (functools.partial(createproxyedit, self), 5),
                            (functools.partial(createproxyedit_check, self), 5),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="使用代理的项目",
                    type="grid",
                    grid=[
                        [(makeproxytab, -1)],
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    makescrollgrid(grids, l)
