import functools, os
import gobject
from myutils.utils import splitocrtypes
from myutils.config import globalconfig, _TR, get_platform
from gui.inputdialog import (
    multicolorset,
    autoinitdialog_items,
    autoinitdialog,
)
from gui.usefulwidget import (
    yuitsu_switch,
    makescrollgrid,
    D_getsimpleswitch,
    getsimplecombobox,
    listediter,
    D_getIconButton,
    auto_select_webview,
    selectcolor,
    D_getspinbox,
    D_getcolorbutton,
    D_getsimplecombobox,
)
from gui.setting_about import offlinelinks


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
                    globalconfig["hirasetting"][name]["args"],
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


def _checkmaybefailed(self, _):
    auto_select_webview.switchtype()
    self.seletengeinecombo_1.setCurrentIndex(globalconfig["usewebview"])


def _createseletengeinecombo_1(self):

    webviews = ["MSHTML", "WebView2"]

    if get_platform() == "xp":
        webviews = ["MSHTML"]
    self.seletengeinecombo_1 = getsimplecombobox(
        webviews,
        globalconfig,
        "usewebview",
        callback=functools.partial(_checkmaybefailed, self),
        static=True,
    )
    return self.seletengeinecombo_1


def vistranslate_rank(self):
    listediter(
        self,
        "显示顺序",
        globalconfig["cishuvisrank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(globalconfig["cishu"][k]["name"]),
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
                        globalconfig["cishu"][cishu]["args"],
                        globalconfig["cishu"][cishu]["name"],
                        800,
                        items,
                        "cishu." + cishu,
                        cishu,
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
    cishugrid[-1] += [""] * (4 + 4 + 3 - len(cishugrid[-1]))
    return cishugrid


def setTabcishu_l(self):

    grids_1 = [
        (
            dict(title="分词器", type="grid", grid=gethiragrid(self)),
            0,
            "group",
        )
    ]
    offline, online = splitocrtypes(globalconfig["cishu"])
    grids2 = [
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
    ]
    grids = [
        [(functools.partial(offlinelinks, "dict"), 0)],
        grids_1,
        grids2,
        [],
        [
            (
                dict(
                    title="分词_&&_注音",
                    type="grid",
                    parent=self,
                    name="fenyinsettings",
                    enable=globalconfig["isshowrawtext"],
                    grid=(
                        [
                            "显示注音",
                            D_getsimpleswitch(
                                globalconfig,
                                "isshowhira",
                                callback=gobject.baseobject.translation_ui.translate_text.showhidert,
                            ),
                            "",
                            "颜色",
                            D_getcolorbutton(
                                globalconfig,
                                "jiamingcolor",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "jiamingcolor",
                                    self.jiamingcolor_b,
                                    callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                                ),
                                name="jiamingcolor_b",
                                parent=self,
                            ),
                            "",
                            "字体缩放",
                            D_getspinbox(
                                0.1,
                                1,
                                globalconfig,
                                "kanarate",
                                double=True,
                                step=0.05,
                                callback=gobject.baseobject.translation_ui.translate_text.setfontstyle,
                            ),
                        ],
                        [
                            "日语注音方案",
                            D_getsimplecombobox(
                                [
                                    "平假名",
                                    "片假名",
                                    "罗马音",
                                ],
                                globalconfig,
                                "hira_vis_type",
                                callback=lambda _: gobject.baseobject.translation_ui.translate_text.refreshcontent(),
                            ),
                            "",
                            "语法加亮",
                            D_getsimpleswitch(
                                globalconfig,
                                "show_fenci",
                                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                            ),
                            "",
                            "词性颜色",
                            D_getIconButton(
                                callback=lambda: multicolorset(self),
                                icon="fa.gear",
                            ),
                        ],
                    ),
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
                            "",
                            "辞书显示顺序",
                            D_getIconButton(
                                functools.partial(vistranslate_rank, self),
                                "fa.gear",
                            ),
                            "",
                        ],
                        [
                            "点击单词查词",
                            (
                                D_getsimpleswitch(
                                    globalconfig,
                                    "usesearchword",
                                    callback=gobject.baseobject.translation_ui.translate_text.showhideclick,
                                ),
                                1,
                            ),
                            "",
                            "",
                            "点击单词复制",
                            (
                                D_getsimpleswitch(
                                    globalconfig,
                                    "usecopyword",
                                    callback=gobject.baseobject.translation_ui.translate_text.showhideclick,
                                ),
                                1,
                            ),
                            "",
                            "",
                            "使用原型查询",
                            (
                                D_getsimpleswitch(globalconfig, "usewordorigin"),
                                1,
                            ),
                        ],
                        [
                            "显示引擎",
                            (
                                functools.partial(_createseletengeinecombo_1, self),
                                0,
                            ),
                        ],
                    ],
                ),
                0,
                "group",
            )
        ],
    ]
    return grids
