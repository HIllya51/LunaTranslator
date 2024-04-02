from PyQt5.QtWidgets import QLineEdit, QPushButton
from myutils.config import _TR
from myutils.config import globalconfig
from myutils.utils import splittranslatortypes
from gui.usefulwidget import getsimpleswitch
import os


def getall(self, l, item="fanyi", name=""):
    grids = []
    i = 0
    line = []
    for fanyi in globalconfig[item]:

        if fanyi not in l:
            continue
        _f = name % fanyi
        if fanyi != "selfbuild" and os.path.exists(_f) == False:
            continue
        i += 1

        line += [
            (globalconfig[item][fanyi]["name"], 6),
            getsimpleswitch(globalconfig[item][fanyi], "useproxy", default=True),
        ]
        if i % 3 == 0:
            grids.append(line)
            line = []
        else:
            line += []
    if len(line):
        grids.append(line)
    return grids


def setTab_proxy_lazy(self):

    proxy = QLineEdit(globalconfig["proxy"])
    btn = QPushButton(_TR("确定"))

    btn.clicked.connect(lambda x: globalconfig.__setitem__("proxy", proxy.text()))

    def _ifusesysproxy(x):
        proxy.setEnabled(not x)
        btn.setEnabled(not x)

    _ifusesysproxy(globalconfig["usesysproxy"])
    grid1 = [
        [("使用代理", 5), (getsimpleswitch(globalconfig, "useproxy"), 1), ("", 10)],
        [
            ("自动获取系统代理", 5),
            (
                getsimpleswitch(
                    globalconfig, "usesysproxy", callback=lambda x: _ifusesysproxy(x)
                )
            ),
        ],
        [
            ("手动设置代理(ip:port)", 5),
            (proxy, 5),
            (btn, 2),
        ],
        [],
        [("使用代理的项目", 5)],
    ]
    lixians, pre, mianfei, develop, shoufei = splittranslatortypes()

    mianfei = getall(
        self, l=mianfei, item="fanyi", name="./Lunatranslator/translator/%s.py"
    )
    shoufei = getall(
        self, l=shoufei, item="fanyi", name="./Lunatranslator/translator/%s.py"
    )
    ocrs = getall(
        self,
        l=set(globalconfig["ocr"].keys()) - set(["local", "windowsocr"]),
        item="ocr",
        name="./Lunatranslator/ocrengines/%s.py",
    )
    tab = self.makesubtab_lazy(
        ["在线翻译", "注册在线翻译", "在线OCR"],
        [
            lambda: self.makescroll(self.makegrid(mianfei)),
            lambda: self.makescroll(self.makegrid(shoufei)),
            lambda: self.makescroll(self.makegrid(ocrs)),
        ],
    )

    gridlayoutwidget = self.makegrid(grid1)
    return self.makevbox([gridlayoutwidget, tab])


def setTab_proxy(self):
    self.tabadd_lazy(self.tab_widget, ("代理设置"), lambda: setTab_proxy_lazy(self))
