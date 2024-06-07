from qtsymbols import *
import os, functools
from myutils.config import _TR, _TRL, globalconfig
from myutils.utils import splittranslatortypes
from gui.usefulwidget import (
    D_getsimpleswitch,
    makegrid,
    makesubtab_lazy,
    getvboxwidget,
    makescrollgrid,
)


def getall(l, item="fanyi", name=None):
    grids = []
    i = 0
    line = []
    for fanyi in globalconfig[item]:

        if fanyi not in l:
            continue
        if name:
            _f = name % fanyi
            if fanyi != "selfbuild" and os.path.exists(_f) == False:
                continue
        i += 1

        line += [
            (globalconfig[item][fanyi].get("name", fanyi), 6),
            D_getsimpleswitch(globalconfig[item][fanyi], "useproxy", default=True),
            "",
        ]
        if i % 3 == 0:
            grids.append(line)
            line = []
        else:
            line += []
    if len(line):
        grids.append(line)
    return grids


def createcheckbtn(self):

    btn = QPushButton(_TR("确定"))

    btn.clicked.connect(
        lambda x: globalconfig.__setitem__("proxy", self.__proxyedit.text())
    )
    self.__checkproxybtn = btn
    _ifusesysproxy(self, globalconfig["usesysproxy"])
    return btn


def createproxyedit(self):
    proxy = QLineEdit(globalconfig["proxy"])
    self.__proxyedit = proxy
    return proxy


def _ifusesysproxy(self, x):
    self.__proxyedit.setEnabled(not x)
    self.__checkproxybtn.setEnabled(not x)


def getnotofflines(key):
    __ = []
    for k in globalconfig[key]:
        if globalconfig[key][k].get("type", None) != "offline":
            __.append(k)
    return __


def setTab_proxy_lazy(self, basel):

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
            (functools.partial(createcheckbtn, self), 2),
        ],
        [],
        [("使用代理的项目", -1)],
    ]
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()

    mianfei = getall(l=mianfei, item="fanyi", name="./Lunatranslator/translator/%s.py")
    shoufei = getall(l=shoufei, item="fanyi", name="./Lunatranslator/translator/%s.py")
    ocrs = getall(
        l=getnotofflines("ocr"),
        item="ocr",
        name="./Lunatranslator/ocrengines/%s.py",
    )
    meta = getall(
        l=list(globalconfig["metadata"].keys()),
        item="metadata",
        name="./LunaTranslator/myutils/metadata/%s.py",
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
    hira = getall(
        l=getnotofflines("hirasetting"),
        item="hirasetting",
        name="./LunaTranslator/hiraparse/%s.py",
    )
    github = getall(
        l=list(globalconfig["github"].keys()),
        item="github",
    )
    vw, vl = getvboxwidget()
    basel.addWidget(vw)
    gridlayoutwidget, do = makegrid(grid1, delay=True)
    vl.addWidget(gridlayoutwidget)
    tab, dotab = makesubtab_lazy(
        _TRL(
            [
                "在线翻译",
                "注册在线翻译",
                "OCR",
                "语音合成",
                "辞书",
                "元数据",
                "分词",
                "github",
            ]
        ),
        [
            functools.partial(makescrollgrid, mianfei),
            functools.partial(makescrollgrid, shoufei),
            functools.partial(makescrollgrid, ocrs),
            functools.partial(makescrollgrid, readers),
            functools.partial(makescrollgrid, cishus),
            functools.partial(makescrollgrid, meta),
            functools.partial(makescrollgrid, hira),
            functools.partial(makescrollgrid, github),
        ],
        delay=True,
    )
    vl.addWidget(tab)
    do()
    dotab()


def setTab_proxy(self, l):
    setTab_proxy_lazy(self, l)
