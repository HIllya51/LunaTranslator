import functools, os
from myutils.config import globalconfig, _TRL
from gui.inputdialog import getsomepath1, autoinitdialog
from gui.usefulwidget import (
    getcolorbutton,
    yuitsu_switch,
    getsimpleswitch,
    getsimplecombobox,
)
import gobject


def setTabcishu(self):
    self.tabadd_lazy(self.tab_widget, ("辞书设置"), lambda: setTabcishu_l(self))


def gethiragrid(self):

    grids = []
    i = 0
    self.ocrswitchs = {}
    line = []
    for name in globalconfig["hirasetting"]:

        _f = "./LunaTranslator/hiraparse/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue

        line += [
            ((globalconfig["hirasetting"][name]["name"]), 5),
            getsimpleswitch(
                globalconfig["hirasetting"][name],
                "use",
                parent=self,
                name=name,
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
        ]
        items = []
        for key in globalconfig["hirasetting"][name]:
            if key == "path":
                items.append(
                    {
                        "t": "file",
                        "l": globalconfig["hirasetting"][name]["name"],
                        "d": globalconfig["hirasetting"][name],
                        "k": "path",
                        "dir": True,
                    }
                )
            elif key == "token":
                items.append(
                    {
                        "t": "lineedit",
                        "l": globalconfig["hirasetting"][name]["token_name"],
                        "d": globalconfig["hirasetting"][name],
                        "k": "token",
                    }
                )
            elif key == "codec":
                items.append(
                    {
                        "t": "combo",
                        "l": "codec",
                        "d": globalconfig["hirasetting"][name],
                        "k": "codec",
                        "list": ["utf8", "shiftjis"],
                    }
                )
        if len(items):
            items.append({"t": "okcancel", "callback": gobject.baseobject.starthira})
            line += [
                getcolorbutton(
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
            ]

        else:
            line += [""]
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
            [("分词&假名分析器", 10)],
            [
                ("日语注音方案", 5),
                (
                    getsimplecombobox(
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
                ("点击单词查词", 5),
                (getsimpleswitch(globalconfig, "usesearchword"), 1),
                getcolorbutton(
                    globalconfig,
                    "",
                    callback=lambda: gobject.baseobject.searchwordW.showsignal.emit(),
                    icon="fa.search",
                    constcolor="#FF69B4",
                ),
                "",
                ("点击单词复制", 5),
                (getsimpleswitch(globalconfig, "usecopyword"), 1),
            ],
            [
                ("使用原型查询", 5),
                (getsimpleswitch(globalconfig, "usewordorigin"), 1),
            ],
            [],
            [("辞书", 10)],
        ]
    )

    line = []
    i = 0
    for cishu in globalconfig["cishu"]:
        _f = "./LunaTranslator/cishu/{}.py".format(cishu)
        if os.path.exists(_f) == False:
            continue
        line += [
            (globalconfig["cishu"][cishu]["name"], 5),
            getsimpleswitch(
                globalconfig["cishu"][cishu],
                "use",
                callback=functools.partial(gobject.baseobject.startxiaoxueguan, cishu),
            ),
            (
                getcolorbutton(
                    globalconfig,
                    "",
                    callback=functools.partial(
                        getsomepath1,
                        self,
                        globalconfig["cishu"][cishu]["name"],
                        globalconfig["cishu"][cishu],
                        "path",
                        globalconfig["cishu"][cishu]["name"],
                        functools.partial(gobject.baseobject.startxiaoxueguan, cishu),
                        globalconfig["cishu"][cishu]["isdir"],
                        globalconfig["cishu"][cishu]["filter"],
                    ),
                    icon="fa.gear",
                    constcolor="#FF69B4",
                )
                if "path" in globalconfig["cishu"][cishu]
                else ""
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

    gridlayoutwidget = self.makegrid(grids)
    gridlayoutwidget = self.makescroll(gridlayoutwidget)

    return gridlayoutwidget
