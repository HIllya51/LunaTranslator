from qtsymbols import *
import os, functools, re
from myutils.config import globalconfig
from gui.setting.translate import splitapillm
from myutils.utils import (
    splittranslatortypes,
    translate_exits,
    dynamiccishuname,
    dynamicapiname,
)
from gui.usefulwidget import (
    D_getsimpleswitch,
    makegrid,
    createfoldgrid,
    makesubtab_lazy,
    makescrollgrid,
    D_getsimplecombobox,
)


def getall(l, item="fanyi", name=None, getname=None):
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
            getname(fanyi) if getname else globalconfig[item][fanyi].get("name", fanyi),
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


def makegridW(grid, lay):
    wid, do = makegrid(grid, delay=True)
    lay.addWidget(wid)
    do()
    return wid


def makeproxytab():

    res = splittranslatortypes()
    is_gpt_likes, not_is_gpt_like = splitapillm(res.api)
    mianfei = getall(
        l=res.free, item="fanyi", name=translate_exits, getname=dynamicapiname
    )
    is_gpt_likes = getall(
        l=is_gpt_likes, item="fanyi", name=translate_exits, getname=dynamicapiname
    )
    not_is_gpt_like = getall(
        l=not_is_gpt_like, item="fanyi", name=translate_exits, getname=dynamicapiname
    )

    tsgrids = [
        [
            functools.partial(
                createfoldgrid,
                is_gpt_likes,
                "大模型",
                globalconfig["foldstatus"]["proxy"],
                "gpt",
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                mianfei,
                "传统",
                globalconfig["foldstatus"]["proxy"],
                "free",
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                not_is_gpt_like,
                "传统_API",
                globalconfig["foldstatus"]["proxy"],
                "api",
            )
        ],
    ]
    if res.external:
        external = getall(
            l=res.external, item="fanyi", name=translate_exits, getname=dynamicapiname
        )
        if external:
            tsgrids += [
                [
                    functools.partial(
                        createfoldgrid,
                        external,
                        "其他",
                        globalconfig["foldstatus"]["proxy"],
                        "external",
                    )
                ]
            ]
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
        getname=dynamiccishuname,
    )
    titles = [
        "在线翻译",
        "OCR",
        "语音合成",
        "辞书",
        "元数据",
    ]
    funcs = [
        functools.partial(makegridW, tsgrids),
        functools.partial(makegridW, ocrs),
        functools.partial(makegridW, readers),
        functools.partial(makegridW, cishus),
        functools.partial(makegridW, meta),
    ]
    tab, dotab = makesubtab_lazy(
        titles,
        funcs,
        delay=True,
    )
    dotab()
    return tab


def setTab_proxy(self, l):
    grids1 = [
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
    ]
    grids = [
        grids1,
        [
            dict(
                title="代理设置",
                type="grid",
                grid=[
                    [
                        "使用代理",
                        D_getsimpleswitch(globalconfig, "useproxy"),
                    ],
                    [
                        "自动获取系统代理",
                        D_getsimpleswitch(
                            globalconfig,
                            "usesysproxy",
                            callback=lambda x: _ifusesysproxy(self, x),
                        ),
                        "",
                        "手动设置代理_(ip:port)",
                        functools.partial(createproxyedit, self),
                        functools.partial(createproxyedit_check, self),
                    ],
                ],
            ),
        ],
        [dict(title="使用代理的项目", grid=[[makeproxytab]])],
    ]
    makescrollgrid(grids, l)
