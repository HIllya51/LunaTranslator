import functools, os
import gobject
from myutils.utils import splitocrtypes
from myutils.config import globalconfig
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    yuitsu_switch,
    makescrollgrid,
    D_getsimpleswitch,
    getsimplecombobox,
    listediter,
    D_getIconButton,
    auto_select_webview,
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
    auto_select_webview.switchtype()


def _createseletengeinecombo_1(self):

    webviews = ["MSHTML", "WebView2", "QWebEngine"]
    self.seletengeinecombo_1 = getsimplecombobox(
        webviews,
        globalconfig,
        "usewebview",
        callback=functools.partial(_checkmaybefailed, self),
        static=True,
    )
    self.seletengeinecombo_1.lastindex = self.seletengeinecombo_1.currentIndex()
    return self.seletengeinecombo_1


def vistranslate_rank(self):
    listediter(
        self,
        "显示顺序",
        "显示顺序",
        globalconfig["cishuvisrank"],
        isrankeditor=True,
        namemapfunction=lambda k: globalconfig["cishu"][k]["name"],
    )


def initinternal(self, names):
    cishugrid = []
    line = []
    i = 0
    for cishu in names:
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
    return cishugrid


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
    offline, online = splitocrtypes(globalconfig["cishu"])
    grids += [
        [
            (
                dict(
                    title="辞书",
                    type="grid",
                    grid=[
                        [
                            (
                                dict(
                                    title="离线",
                                    type="grid",
                                    grid=initinternal(self, offline),
                                ),
                                0,
                                "group",
                            )
                        ],
                        [
                            (
                                dict(
                                    title="在线",
                                    type="grid",
                                    grid=initinternal(self, online),
                                ),
                                0,
                                "group",
                            )
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
                    title="查词",
                    type="grid",
                    grid=[
                        [
                            "查词",
                            D_getIconButton(
                                lambda: gobject.baseobject.searchwordW.showsignal.emit(),
                                "fa.search",
                            ),
                            "",
                            "辞书显示顺序",
                            D_getIconButton(
                                functools.partial(vistranslate_rank, self),
                                "fa.gear",
                            ),
                            "",
                        ],
                        [
                            ("点击单词查词"),
                            (
                                D_getsimpleswitch(globalconfig, "usesearchword"),
                                1,
                            ),
                            "",
                            ("点击单词复制"),
                            (
                                D_getsimpleswitch(globalconfig, "usecopyword"),
                                1,
                            ),
                            "",
                            ("使用原型查询"),
                            (
                                D_getsimpleswitch(globalconfig, "usewordorigin"),
                                1,
                            ),
                        ],
                        [
                            "显示引擎",
                            (functools.partial(_createseletengeinecombo_1, self), 0),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    return grids
