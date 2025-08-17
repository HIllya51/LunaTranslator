from qtsymbols import *
import functools, os
import gobject, uuid, shutil, copy
from myutils.config import globalconfig, translatorsetting, _TR
from myutils.utils import (
    selectdebugfile,
    splittranslatortypes,
    dynamiclink,
    translate_exits,
    dynamicapiname,
    autosql,
    getannotatedapiname,
)
import json
from traceback import print_exc
from gui.usefulwidget import SuperCombo
from collections import Counter
from myutils.wrapper import tryprint
from gui.inputdialog import autoinitdialog, autoinitdialog_items
from gui.usefulwidget import (
    D_getspinbox,
    getIconButton,
    D_getcolorbutton,
    getcolorbutton,
    check_grid_append,
    getsimpleswitch,
    D_getIconButton,
    D_getsimpleswitch,
    request_delete_ok,
    createfoldgrid,
    makesubtab_lazy,
    getspinbox,
    ClickableLabel,
    automakegrid,
    FocusFontCombo,
    getsmalllabel,
    NQGroupBox,
    makescrollgrid,
    IconButton,
    PopupWidget,
)
from gui.setting.display_text import GetFormForLineHeight
from gui.dynalang import LPushButton, LAction, LFormLayout, LDialog
from gui.setting.about import offlinelinks


def getallllms(l):
    _ = []
    for fanyi in l:
        is_gpt_like = globalconfig["fanyi"][fanyi].get("is_gpt_like", False)
        if is_gpt_like:
            _.append(fanyi)
    return _


def splitapillm(l):
    not_is_gpt_like = []
    is_gpt_likes = []
    for fanyi in l:
        is_gpt_like = globalconfig["fanyi"][fanyi].get("is_gpt_like", False)
        if is_gpt_like:
            is_gpt_likes.append(fanyi)
        else:
            not_is_gpt_like.append(fanyi)
    return is_gpt_likes, not_is_gpt_like


def loadvisinternal(copy):
    __vis = []
    __uid = []
    for _ in getallllms(globalconfig["fanyi"]):
        if copy:
            which = translate_exits(_, which=True)
            if which != 1:
                continue
        else:
            if not translate_exits(_):
                continue
        __vis.append(dynamicapiname(_))
        __uid.append(_)
    return __vis, __uid


def getalistname(parent, copy, callback):
    __d = {"k": 0, "n": ""}
    __vis, __uid = loadvisinternal(copy)
    if not __vis:
        return

    def __wrap(callback, __d, __uid):
        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        callback(uid, __d["n"])

    __ = []
    __.append(
        {
            "type": "combo",
            "name": "复制自" if not copy else "删除",
            "k": "k",
            "list": __vis,
        }
    )
    if not copy:
        __.append(
            {
                "name": "命名为",
                "type": "lineedit",
                "k": "n",
            }
        )

    __.append(
        {
            "type": "okcancel",
            "callback": functools.partial(__wrap, callback, __d, __uid),
        }
    )
    autoinitdialog(
        parent, __d, ("删除" if copy else "复制") + "接口", 600, __, exec_=True
    )


class SpecialFont(PopupWidget):
    def __init__(self, apiuid, p):
        super().__init__(p)
        self.apiuid = apiuid
        box = QGridLayout(self)
        grid = []
        grid.append(
            [
                "",
                "跟随默认",
            ]
        )
        if "privatefont" not in globalconfig["fanyi"][apiuid]:
            globalconfig["fanyi"][apiuid]["privatefont"] = {}
        dd = globalconfig["fanyi"][apiuid]["privatefont"]
        for i in range(4):
            if i == 0:
                t = "字体"
                k = "fontfamily"
                w = QPushButton()

                def _f(dd, key, x):
                    dd[key] = x
                    self.resetfont()

                w = FocusFontCombo()
                w.setCurrentFont(QFont(dd.get(k, globalconfig["fonttype2"])))
                w.currentTextChanged.connect(functools.partial(_f, dd, k))
            elif i == 1:
                t = "大小"
                k = "fontsize"
                w = getspinbox(
                    1,
                    100,
                    dd,
                    k,
                    double=True,
                    step=0.1,
                    default=globalconfig[k],
                    callback=self.resetfont,
                )
            elif i == 2:
                t = "加粗"
                k = "showbold"
                w = getsimpleswitch(
                    dd, k, default=globalconfig[k], callback=self.resetfont
                )
            elif i == 3:
                t = "间距"
                k = "lineheight"
                w = QWidget()
                GetFormForLineHeight(w, dd, self.resetfont)

            w.setEnabled(not dd.get(k + "_df", True))
            switch = D_getsimpleswitch(
                dd,
                k + "_df",
                callback=functools.partial(self.disableclear, w),
                default=True,
            )
            grid.append([getsmalllabel(t), switch, w])
        automakegrid(box, grid)

    def disableclear(self, w: QWidget, _):
        w.setEnabled(not _)
        self.resetfont()

    def resetfont(self, _=None):
        gobject.base.translation_ui.translate_text.setfontextra(self.apiuid)


def renameapi(qlabel: QLabel, apiuid, self, countnum, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    specialfont = LAction("字体设置", menu)
    delete = LAction("删除", menu)
    copy = LAction("复制", menu)
    astoppest = LAction("设为首选", menu)
    astoppest.setCheckable(True)
    usecache = LAction("使用翻译缓存", menu)
    usecache.setCheckable(True)
    useproxy = LAction("使用代理", menu)
    useproxy.setCheckable(True)
    astoppest.setChecked(globalconfig["toppest_translator"] == apiuid)
    menu.addAction(editname)
    menu.addAction(specialfont)
    menu.addAction(astoppest)
    which = translate_exits(apiuid, which=True)
    is_gpt_like = globalconfig["fanyi"][apiuid].get("is_gpt_like", False)
    if is_gpt_like:
        menu.addSeparator()
        menu.addAction(usecache)
        usecache.setChecked(globalconfig["fanyi"][apiuid].get("use_trans_cache", True))
        menu.addAction(copy)

    if which == 1 or "chatgpt-offline" == apiuid:
        menu.addAction(delete)
    if globalconfig["useproxy"] and globalconfig["fanyi"][apiuid].get("type") not in (
        "offline",
        "other",
        "pre",
    ):
        menu.addSeparator()
        menu.addAction(useproxy)
        useproxy.setChecked(globalconfig["fanyi"][apiuid].get("useproxy", True))
    pos = QCursor.pos()
    action = menu.exec(pos)
    if action == delete:
        if request_delete_ok(self, "99e3f96f-8659-457f-9e0b-52643f552889"):
            selectllmcallback_2(self, countnum, apiuid, None)
    elif action == useproxy:
        globalconfig["fanyi"][apiuid]["useproxy"] = useproxy.isChecked()
    elif action == astoppest:
        globalconfig["toppest_translator"] = apiuid if action.isChecked() else None
        if action.isChecked():
            try:
                # 若已开启，则立即置顶
                globalconfig["fix_translate_rank_rank"].remove(apiuid)
                globalconfig["fix_translate_rank_rank"].insert(0, apiuid)
            except:
                pass

    elif action == usecache:
        globalconfig["fanyi"][apiuid]["use_trans_cache"] = usecache.isChecked()
    elif action == editname:
        before = dynamicapiname(apiuid)
        __d = {"k": before}

        def cb(__d):
            title = __d["k"]
            if title not in ("", before):
                globalconfig["fanyi"][apiuid]["name_self_set"] = title
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
    elif action == specialfont:
        SpecialFont(apiuid, self).display(pos)
    elif action == copy:
        selectllmcallback(self, countnum, apiuid)


def getrenameablellabel(uid, self, countnum):
    name = ClickableLabel(dynamicapiname(uid))
    fn = functools.partial(renameapi, name, uid, self, countnum)
    name.clicked.connect(fn)
    return name


def loadbutton(self, fanyi):
    which = translate_exits(fanyi, which=True)
    copyfrom = getcopyfrom(fanyi)
    if (copyfrom != fanyi) and (copyfrom in translatorsetting):
        if "args" in translatorsetting[copyfrom]:
            for k in translatorsetting[copyfrom]["args"]:
                if k not in translatorsetting[fanyi]["args"]:
                    translatorsetting[fanyi]["args"][k] = translatorsetting[copyfrom][
                        "args"
                    ][k]

            for k in list(translatorsetting[fanyi]["args"].keys()):
                if k not in translatorsetting[copyfrom]["args"]:
                    translatorsetting[fanyi]["args"].pop(k)
        if "argstype" in translatorsetting[copyfrom]:
            translatorsetting[fanyi]["argstype"] = translatorsetting[copyfrom][
                "argstype"
            ]
    items = autoinitdialog_items(translatorsetting[fanyi])
    if which == 0:
        aclass = "translator." + fanyi
    elif which == 1:
        aclass = "copyed." + fanyi
    else:
        return
    return autoinitdialog(
        self,
        translatorsetting[fanyi]["args"],
        dynamicapiname(fanyi),
        800,
        items,
        aclass,
        fanyi,
    )


def getcopyfrom(uid):
    xx = uid
    while True:
        cp = globalconfig["fanyi"][xx].get("copyfrom")
        if not cp:
            return xx
        xx = cp


def selectllmcallback(self, countnum: list, fanyi, newname=None):
    uid = str(uuid.uuid4())
    _f11 = "Lunatranslator/translator/{}.py".format(fanyi)
    _f12 = gobject.getconfig("copyed/{}.py".format(fanyi))
    _f2 = gobject.getconfig("copyed/{}.py".format(uid))
    try:
        shutil.copy(_f11, _f2)
    except:
        shutil.copy(_f12, _f2)
    copyfrom = getcopyfrom(fanyi)
    globalconfig["fanyi"][uid] = copy.deepcopy(globalconfig["fanyi"][fanyi])
    globalconfig["fanyi"][uid]["copyfrom"] = copyfrom
    globalconfig["fanyi"][uid]["use"] = False
    globalconfig["fanyi"][uid]["name"] = (
        newname if newname else (dynamicapiname(fanyi) + "_copy")
    )
    if "name_self_set" in globalconfig["fanyi"][uid]:
        globalconfig["fanyi"][uid].pop("name_self_set")
    globalconfig["fanyi"][uid]["type"] = globalconfig["fanyi"][fanyi]["type"]
    if fanyi in translatorsetting:
        translatorsetting[uid] = copy.deepcopy(translatorsetting[fanyi])

    layout: QGridLayout = getattr(self, "damoxinggridinternal")

    last = getIconButton(callback=functools.partial(loadbutton, self, uid))

    name = getrenameablellabel(uid, self, countnum)
    swc = getsimpleswitch(
        globalconfig["fanyi"][uid],
        "use",
        callback=functools.partial(gobject.base.prepare, uid),
    )
    color = getcolorbutton(
        self,
        globalconfig["fanyi"][uid],
        "color",
        callback=gobject.base.translation_ui.translate_text.setcolorstyle,
    )

    offset = 5 * (len(countnum) % 3)
    layout.addWidget(name, layout.rowCount() - 1 + (len(countnum) % 3 == 0), offset + 0)
    layout.addWidget(swc, layout.rowCount() - 1, offset + 1)
    layout.addWidget(color, layout.rowCount() - 1, offset + 2)
    layout.addWidget(last, layout.rowCount() - 1, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), layout.rowCount() - 1, offset + 4)
    countnum.append(uid)
    self.__del_btn.show()


def btnpluscallback(self, countnum):
    getalistname(
        self,
        False,
        functools.partial(selectllmcallback, self, countnum),
    )


def selectllmcallback_2(self, countnum: list, fanyi, name):
    _f2 = gobject.getconfig("copyed/{}.py".format(fanyi))
    try:
        os.remove(_f2)
    except:
        pass
    globalconfig["fanyi"][fanyi]["use"] = False
    try:
        gobject.base.translators.pop(fanyi)
    except:
        pass
    layout: QGridLayout = getattr(self, "damoxinggridinternal")
    if not layout:
        return
    idx = countnum.index(fanyi)
    line = idx // 3
    off = line * 14 + (idx % 3) * 5
    do = 0
    i = 0
    while do < 4:

        w = layout.itemAt(off + i).widget()
        i += 1
        if isinstance(w, NQGroupBox):
            continue
        elif isinstance(w, QLabel) and w.text() == "":
            continue
        elif not w.isEnabled():
            continue
        w.setEnabled(False)
        do += 1

    if not loadvisinternal(True)[0]:
        self.__del_btn.hide()


def btndeccallback(self, countnum):
    getalistname(
        self,
        True,
        functools.partial(selectllmcallback_2, self, countnum),
    )


def initsome11(self, l, save=False):
    grids: "list[list]" = []
    i = 0
    line = []
    countnum = []
    if save:
        self.__countnum = countnum
    for fanyi in l:
        which = translate_exits(fanyi, which=True)
        if which is None:
            continue
        i += 1
        countnum.append(fanyi)
        if translatorsetting.get(fanyi):
            last = D_getIconButton(callback=functools.partial(loadbutton, self, fanyi))
        elif fanyi == "selfbuild":
            last = D_getIconButton(
                callback=lambda: selectdebugfile("selfbuild.py"),
                icon="fa.edit",
            )
        else:
            last = ""
        line += [
            functools.partial(getrenameablellabel, fanyi, self, countnum),
            D_getsimpleswitch(
                globalconfig["fanyi"][fanyi],
                "use",
                callback=functools.partial(gobject.base.prepare, fanyi),
            ),
            D_getcolorbutton(
                self,
                globalconfig["fanyi"][fanyi],
                "color",
                callback=gobject.base.translation_ui.translate_text.setcolorstyle,
            ),
            last,
        ]

        if i % 3 == 0:
            grids.append(line)
            line = []
        else:
            line += [""]
    if len(line):
        grids.append(line)
    check_grid_append(grids)
    if len(grids) == 1:
        if i % 3 != 0:
            grids[-1].append(("", 5 * (3 - i % 3)))
    return grids


def initsome21(self, not_is_gpt_like):
    not_is_gpt_like = initsome11(self, not_is_gpt_like)
    grids = [
        [
            functools.partial(
                createfoldgrid,
                not_is_gpt_like,
                "过时的",
                globalconfig["foldstatus"]["ts"],
                "outdate",
            )
        ],
    ]
    return grids


def leftwidget(self):

    btn = IconButton("fa.plus", fix=False, tips="复制")
    btn.clicked.connect(functools.partial(btnpluscallback, self, self.__countnum))

    btn2 = IconButton("fa.minus", fix=False, tips="删除")
    btn2.clicked.connect(functools.partial(btndeccallback, self, self.__countnum))
    self.__del_btn = btn2
    if not loadvisinternal(True)[0]:
        btn2.hide()

    btn3 = IconButton(
        "fa.question",
        fix=False,
        tips="使用说明",
    )
    btn3.clicked.connect(
        lambda: os.startfile(dynamiclink("guochandamoxing.html", docs=True))
    )

    return [btn3, btn, btn2]


def initsome2(self, mianfei, api):

    onlinegrid = initsome11(self, mianfei)
    api = initsome11(self, api)
    is_gpt_likes = initsome11(self, getallllms(globalconfig["fanyi"]), save=True)
    grids = [
        [
            functools.partial(
                createfoldgrid,
                is_gpt_likes,
                "大模型",
                globalconfig["foldstatus"]["ts"],
                "gpt",
                "damoxinggridinternal",
                self,
                leftwidget=functools.partial(leftwidget, self),
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                onlinegrid,
                "传统",
                globalconfig["foldstatus"]["ts"],
                "free",
            )
        ],
        [
            functools.partial(
                createfoldgrid,
                api,
                "传统_API",
                globalconfig["foldstatus"]["ts"],
                "api",
                leftwidget=D_getIconButton(
                    fix=False,
                    icon="fa.question",
                    callback=lambda: os.startfile(
                        dynamiclink("useapis/tsapi.html", docs=True)
                    ),
                    tips="使用说明",
                ),
            )
        ],
    ]
    return grids


@tryprint
def sqlite2json2(self, sqlitefile, targetjson=None, existsmerge=False):
    try:
        sql = autosql(sqlitefile, check_same_thread=False)
        ret = sql.execute("SELECT * FROM artificialtrans  ").fetchall()
        js_format2: "dict[str, dict|str]" = {}
        collect = []
        for _aret in ret:
            if len(_aret) == 4:
                _id, source, mt, source_origin = _aret
                if targetjson:
                    source = source_origin
                js_format2[source] = mt
            elif len(_aret) == 3:
                _id, source, mt = _aret
                js_format2[source] = mt
            try:
                mtjs = json.loads(mt)
            except:
                mtjs = mt
            js_format2[source] = mtjs
            if isinstance(mtjs, dict):
                collect.extend(list(mtjs.keys()))
    except:
        print_exc()
        QMessageBox.critical(self, _TR("错误"), _TR("所选文件格式错误！"))
        return
    _collect = []
    for _, __ in Counter(collect).most_common():
        if _ in globalconfig["fanyi"]:
            _collect.append(_)
    dialog = LDialog(self, Qt.WindowType.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle("导出翻译记录为json文件")
    dialog.resize(QSize(800, 10))
    formLayout = LFormLayout(dialog)  # 配置layout

    combo = SuperCombo()
    combo.addItems([getannotatedapiname(_) for _ in _collect], _collect)

    formLayout.addRow("首选翻译", combo)
    e = QLineEdit(sqlitefile[: -(len(".sqlite"))])

    bu = LPushButton("选择路径")

    def __selectsavepath():
        ff = QFileDialog.getSaveFileName(
            dialog, directory=sqlitefile[: -(len(".sqlite"))]
        )
        if ff[0] == "":
            return
        e.setText(ff[0])

    bu.clicked.connect(__selectsavepath)
    hori = QHBoxLayout()
    hori.addWidget(e)
    hori.addWidget(bu)

    if targetjson is None:
        formLayout.addRow("保存路径", hori)

    button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)

    def __savefunction(target, existsmerge):
        transkirokuuse = combo.getIndexData(combo.currentIndex())
        for k in js_format2:
            if isinstance(js_format2[k], dict):
                js_format2[k] = js_format2[k].get(transkirokuuse, "")

        if target is None:
            target = e.text() + ".json"
        if existsmerge and os.path.exists(target):
            try:
                with open(target, "r", encoding="utf8") as ff:
                    existsjs = json.load(ff)
            except:
                existsjs = {}
            for k in existsjs:
                if k not in js_format2 or js_format2[k] == "":
                    js_format2[k] = existsjs[k]
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf8") as ff:
            ff.write(
                json.dumps(js_format2, ensure_ascii=False, sort_keys=False, indent=4)
            )
        dialog.close()

    button.accepted.connect(functools.partial(__savefunction, targetjson, existsmerge))
    button.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
    button.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
    dialog.show()


def sqlite2json(self):
    f = QFileDialog.getOpenFileName(directory="translation_record", filter="*.sqlite")
    if f[0] == "":
        return

    sqlite2json2(self, f[0])


def createbtnexport(self):

    bt = LPushButton("导出翻译记录为json文件")
    bt.clicked.connect(lambda x: sqlite2json(self))
    return bt


def setTabTwo_lazy(self, basel: QVBoxLayout):

    res = splittranslatortypes()

    _, not_is_gpt_like = splitapillm(res.offline)
    offlinegrid = initsome21(self, not_is_gpt_like)
    offlinegrid += [[functools.partial(offlinelinks, "translate")]]
    _, not_is_gpt_like = splitapillm(res.api)
    online_reg_grid = initsome2(self, res.free, not_is_gpt_like)
    pretransgrid = [
        [
            dict(
                type="grid",
                title="其他设置",
                grid=[
                    [
                        "最短翻译字数",
                        D_getspinbox(0, 9999, globalconfig, "minlength"),
                        "",
                        "最长翻译字数",
                        D_getspinbox(0, 9999, globalconfig, "maxlength"),
                        "",
                        "翻译请求间隔_(s)",
                        D_getspinbox(
                            0,
                            9999,
                            globalconfig,
                            "requestinterval",
                            step=0.1,
                            double=True,
                        ),
                    ],
                ],
            ),
        ],
        [],
        [
            dict(
                title="预翻译",
                grid=[
                    [
                        dict(
                            type="grid",
                            grid=[
                                [
                                    "模糊匹配_相似度_%",
                                    D_getspinbox(0, 100, globalconfig, "premtsimi2"),
                                    "",
                                    functools.partial(createbtnexport, self),
                                ],
                            ],
                        ),
                    ],
                    [dict(type="grid", grid=initsome11(self, res.pre))],
                ],
            ),
        ],
        [dict(type="grid", title="其他", grid=initsome11(self, res.other))],
    ]
    pretransgrid += offlinegrid
    savelay = []
    tab, dotab = makesubtab_lazy(
        ["翻译接口", "其他"],
        [
            functools.partial(makescrollgrid, online_reg_grid, savelay=savelay),
            functools.partial(makescrollgrid, pretransgrid),
        ],
        delay=True,
    )
    basel.addWidget(tab)
    dotab()
