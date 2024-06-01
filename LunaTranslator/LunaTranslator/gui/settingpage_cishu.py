import functools, os
from myutils.config import globalconfig, _TRL
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getcolorbutton,
    yuitsu_switch,
    makescrollgrid,
    D_getsimpleswitch,
    D_getsimplecombobox,
)
import gobject


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
            _3 = D_getcolorbutton(
                globalconfig,
                "",
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["hirasetting"][name]["name"],
                    800,
                    items,
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            )

        else:
            _3 = ""

        line += [
            ((globalconfig["hirasetting"][name]["name"]), 6),
            (
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
                1,
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


def setTabcishu_l(self):

    grids = (
        [
            [("分词&假名分析器", -1)],
            [
                ("日语注音方案", 6),
                (
                    D_getsimplecombobox(
                        _TRL(["平假名", "片假名", "罗马音"]),
                        globalconfig,
                        "hira_vis_type",
                    ),
                    5,
                ),
            ],
        ]
        + gethiragrid(self)
        + [
            [],
            [],
            [
                ("点击单词查词", 6),
                (D_getsimpleswitch(globalconfig, "usesearchword"), 1),
                D_getcolorbutton(
                    globalconfig,
                    "",
                    callback=lambda: gobject.baseobject.searchwordW.showsignal.emit(),
                    icon="fa.search",
                    constcolor="#FF69B4",
                ),
                "",
                ("点击单词复制", 6),
                (D_getsimpleswitch(globalconfig, "usecopyword"), 1),
            ],
            [
                ("使用原型查询", 6),
                (D_getsimpleswitch(globalconfig, "usewordorigin"), 1),
            ],
            [],
            [("辞书", -1)],
        ]
    )

    line = []
    i = 0
    for cishu in globalconfig["cishu"]:
        _f = "./LunaTranslator/cishu/{}.py".format(cishu)
        if os.path.exists(_f) == False:
            continue

        items = autoinitdialog_items(globalconfig["cishu"][cishu])
        items[-1]["callback"] = functools.partial(
            gobject.baseobject.startxiaoxueguan, cishu
        )
        line += [
            (globalconfig["cishu"][cishu]["name"], 6),
            D_getsimpleswitch(
                globalconfig["cishu"][cishu],
                "use",
                callback=functools.partial(gobject.baseobject.startxiaoxueguan, cishu),
            ),
            D_getcolorbutton(
                globalconfig,
                "",
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["cishu"][cishu]["name"],
                    800,
                    items,
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
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
