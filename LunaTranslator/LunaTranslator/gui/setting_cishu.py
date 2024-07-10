import functools, os
import gobject
from myutils.config import globalconfig, _TR
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    yuitsu_switch,
    makescrollgrid,
    D_getsimpleswitch,
    getsimplecombobox,
    listediter,
    D_getIconButton,
)
from gui.setting_display_text import on_not_find_qweb


def setTabcishu(self, basel):
    makescrollgrid(setTabcishu_l(self), basel)


def gethiragrid(self):

    grids = []
    i = 0
    self.hiraswitchs = {}
    line = []
    for name in globalconfig["hirasetting"]:

        _f = "./LunaTranslator/hiraparse/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue
        if "args" in globalconfig["hirasetting"][name]:
            items = autoinitdialog_items(globalconfig["hirasetting"][name])
            items[-1]["callback"] = gobject.baseobject.starthira
            _3 = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["hirasetting"][name]["name"],
                    800,
                    items,
                ),
                icon="fa.gear",
            )

        else:
            _3 = ""

        line += [
            globalconfig["hirasetting"][name]["name"],
            D_getsimpleswitch(
                globalconfig["hirasetting"][name],
                "use",
                name=name,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["hirasetting"],
                    "hiraswitchs",
                    name,
                    gobject.baseobject.starthira,
                ),
                pair="hiraswitchs",
            ),
            _3,
        ]
        if i % 3 == 2:
            grids.append(line)
            line = []
        else:
            line += [""]
        i += 1
    if len(line):
        grids.append(line)
    return grids


def _checkmaybefailed(self, idx):
    if idx == 2 and not gobject.testuseqwebengine():
        self.seletengeinecombo_1.setCurrentIndex(self.seletengeinecombo_1.lastindex)
        on_not_find_qweb(self)
        return
    self.seletengeinecombo_1.lastindex = self.seletengeinecombo_1.currentIndex()


def _createseletengeinecombo_1(self):

    webviews = ["MSHTML", "WebView2", "QWebEngine"]
    self.seletengeinecombo_1 = getsimplecombobox(
        webviews,
        globalconfig,
        "usewebview",
        callback=functools.partial(_checkmaybefailed, self),
    )
    self.seletengeinecombo_1.lastindex = self.seletengeinecombo_1.currentIndex()
    return self.seletengeinecombo_1


def vistranslate_rank(self):
    listediter(
        self,
        _TR("显示顺序"),
        _TR("显示顺序"),
        globalconfig["cishuvisrank"],
        isrankeditor=True,
        namemapfunction=lambda k: globalconfig["cishu"][k]["name"],
    )


def setTabcishu_l(self):

    grids = [
        [
            (
                dict(title="分词器", type="grid", grid=gethiragrid(self)),
                0,
                "group",
            )
        ],
    ]
    cishugrid = []
    line = []
    i = 0
    for cishu in globalconfig["cishu"]:
        _f = "./LunaTranslator/cishu/{}.py".format(cishu)
        if os.path.exists(_f) == False:
            continue

        line += [
            globalconfig["cishu"][cishu]["name"],
            D_getsimpleswitch(
                globalconfig["cishu"][cishu],
                "use",
                callback=functools.partial(gobject.baseobject.startxiaoxueguan, cishu),
            ),
        ]
        if "args" in globalconfig["cishu"][cishu]:

            items = autoinitdialog_items(globalconfig["cishu"][cishu])
            items[-1]["callback"] = functools.partial(
                gobject.baseobject.startxiaoxueguan, cishu
            )
            line += [
                D_getIconButton(
                    callback=functools.partial(
                        autoinitdialog,
                        self,
                        globalconfig["cishu"][cishu]["name"],
                        800,
                        items,
                    ),
                    icon="fa.gear",
                ),
            ]
        else:
            line += [""]
        if i % 3 == 2:
            cishugrid.append(line)
            line = []
        else:
            line += [""]
        i += 1
    if len(line):
        cishugrid.append(line)
    grids += [
        [
            (
                dict(title="辞书", type="grid", grid=cishugrid),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="显示",
                    grid=[
                        [
                            "显示顺序",
                            D_getIconButton(
                                functools.partial(vistranslate_rank, self), "fa.gear"
                            ),
                        ],
                        [
                            "网页显示",
                            functools.partial(_createseletengeinecombo_1, self),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    return grids
