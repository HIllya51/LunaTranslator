from qtsymbols import *
import functools, os
import gobject
from myutils.utils import splitocrtypes, dynamiccishuname
from myutils.config import globalconfig, _TR
from myutils.wrapper import Singleton_close
from gui.inputdialog import autoinitdialog_items, autoinitdialog
from gui.usefulwidget import (
    yuitsu_switch,
    makescrollgrid,
    D_getsimpleswitch,
    listediter,
    D_getIconButton,
    selectcolor,
    D_getspinbox,
    D_getcolorbutton,
    getsimpleswitch,
    D_getsimplecombobox,
    getspinbox,
    ClickableLabel,
    getcolorbutton,
    check_grid_append,
)
from gui.dynalang import LFormLayout, LLabel, LAction, LDialog
from gui.setting.about import offlinelinks


@Singleton_close
class multicolorset(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("颜色设置")
        self.resize(QSize(300, 10))
        formLayout = LFormLayout(self)  # 配置layout
        _hori = QHBoxLayout()
        l = LLabel("不透明度")
        _hori.addWidget(l)
        _s = getspinbox(
            1,
            100,
            d=globalconfig,
            key="showcixing_touming",
            callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
        )
        _hori.addWidget(_s)
        formLayout.addRow(_hori)
        _s.valueChanged.connect(
            lambda x: globalconfig.__setitem__("showcixing_touming", x)
        )
        hori = QHBoxLayout()
        hori.addWidget(LLabel("词性"))
        hori.addWidget(LLabel("是否显示"))
        hori.addWidget(LLabel("颜色"))
        for k in globalconfig["cixingcolor"]:
            hori = QHBoxLayout()

            l = LLabel(k)

            hori.addWidget(l)

            b = getsimpleswitch(
                d=globalconfig["cixingcolorshow"],
                key=k,
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
            )

            p = getcolorbutton(
                globalconfig["cixingcolor"],
                k,
                name="miaobian_color_button",
                parent=self,
            )

            p.clicked.connect(
                functools.partial(
                    selectcolor,
                    self,
                    globalconfig["cixingcolor"],
                    k,
                    p,
                    callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                )
            )
            hori.addWidget(b)
            hori.addWidget(p)

            formLayout.addRow(hori)
        self.show()


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
    grids[-1] += [""] * (4 + 4 + 3 - len(grids[-1]))
    return grids


def vistranslate_rank(self):
    listediter(
        self,
        "显示顺序",
        globalconfig["cishuvisrank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(dynamiccishuname(k)),
        exec=True,
    )


def renameapi(qlabel: QLabel, apiuid, self, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    menu.addAction(editname)
    action = menu.exec(QCursor.pos())

    if action == editname:
        before = dynamiccishuname(apiuid)
        __d = {"k": before}

        def cb(__d):
            title = __d["k"]
            if title not in ("", before):
                globalconfig["cishu"][apiuid]["name_self_set"] = title
                qlabel.setText(title)

        autoinitdialog(
            self,
            __d,
            "重命名",
            600,
            [
                {
                    "type": "lineedit",
                    "name": "名称",
                    "k": "k",
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(cb, __d),
                },
            ],
            exec_=True,
        )


def getrenameablellabel(uid, self):
    name = ClickableLabel(dynamiccishuname(uid))
    fn = functools.partial(renameapi, name, uid, self)
    name.clicked.connect(fn)
    return name


def initinternal(self, names):
    cishugrid = []
    line = []
    i = 0
    for cishu in names:
        _f = "./LunaTranslator/cishu/{}.py".format(cishu)
        if os.path.exists(_f) == False:
            continue

        line += [
            functools.partial(getrenameablellabel, cishu, self),
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

            def __(cishu):
                autoinitdialog(
                    self,
                    globalconfig["cishu"][cishu]["args"],
                    dynamiccishuname(cishu),
                    800,
                    items,
                    "cishu." + cishu,
                    cishu,
                )

            line += [
                D_getIconButton(callback=functools.partial(__, cishu)),
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
    check_grid_append(cishugrid)
    return cishugrid


def setTabcishu_l(self):

    grids_1 = [dict(title="分词器", type="grid", grid=gethiragrid(self))]
    offline, online = splitocrtypes(globalconfig["cishu"])
    grids2 = [
        dict(
            title="辞书",
            type="grid",
            grid=[
                [
                    dict(
                        title="离线",
                        type="grid",
                        grid=initinternal(self, offline),
                    )
                ],
                [
                    dict(
                        title="在线",
                        type="grid",
                        grid=initinternal(self, online),
                    )
                ],
            ],
        )
    ]
    grids = [
        [(functools.partial(offlinelinks, "dict"), 0)],
        grids_1,
        grids2,
        [],
        [
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
                        D_getIconButton(callback=lambda: multicolorset(self)),
                    ],
                ),
            ),
        ],
        [
            dict(
                title="查词",
                type="grid",
                grid=[
                    [
                        "查词",
                        D_getIconButton(
                            lambda: gobject.baseobject.searchwordW.showsignal.emit(),
                            icon="fa.search",
                        ),
                        "",
                        "",
                        "辞书显示顺序",
                        D_getIconButton(functools.partial(vistranslate_rank, self)),
                        "",
                    ],
                    [
                        "点击单词查词",
                        D_getsimpleswitch(
                            globalconfig,
                            "usesearchword",
                            callback=gobject.baseobject.translation_ui.translate_text.showhideclick,
                        ),
                        getcolorbutton(
                            globalconfig,
                            "hovercolor",
                            callback=functools.partial(
                                selectcolor,
                                self,
                                globalconfig,
                                "hovercolor",
                                None,
                                self,
                                "hovercolor",
                                callback=lambda: gobject.baseobject.translation_ui.translate_text.sethovercolor(
                                    globalconfig["hovercolor"]
                                ),
                                alpha=True,
                            ),
                            name="hovercolor",
                            parent=self,
                        ),
                        "",
                        "点击单词复制",
                        D_getsimpleswitch(
                            globalconfig,
                            "usecopyword",
                            callback=gobject.baseobject.translation_ui.translate_text.showhideclick,
                        ),
                        "",
                        "",
                        "使用原型查询",
                        D_getsimpleswitch(globalconfig, "usewordorigin"),
                    ],
                ],
            ),
        ],
    ]
    return grids
