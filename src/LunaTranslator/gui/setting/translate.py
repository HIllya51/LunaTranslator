from qtsymbols import *
import functools, os
import gobject, uuid, shutil, copy, importlib
from myutils.config import globalconfig, translatorsetting, _TR, defaultglobalconfig
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


def loadvisinternal(btnplus, copy):
    __vis = []
    __uid = []
    res = splittranslatortypes()
    if btnplus == "api":
        is_gpt_likes, not_is_gpt_like = splitapillm(res.api)
    elif btnplus == "offline":
        is_gpt_likes, not_is_gpt_like = splitapillm(res.offline)

    for _ in is_gpt_likes:
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


def getalistname(parent, copy, btnplus, callback):
    __d = {"k": 0, "n": ""}
    __vis, __uid = loadvisinternal(btnplus, copy)

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
        gobject.baseobject.translation_ui.translate_text.setfontextra(self.apiuid)


def renameapi(qlabel: QLabel, apiuid, self, countnum, btnplus, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    specialfont = LAction("字体设置", menu)
    delete = LAction("删除", menu)
    copy = LAction("复制", menu)
    astoppest = LAction("设为首选", menu)
    astoppest.setCheckable(True)
    usecache = LAction("使用翻译缓存", menu)
    usecache.setCheckable(True)
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
    if which == 1:
        menu.addAction(delete)
    pos = QCursor.pos()
    action = menu.exec(pos)
    if action == delete:
        selectllmcallback_2(self, countnum, btnplus, apiuid, None)
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
        selectllmcallback(self, countnum, btnplus, apiuid, None)


def getrenameablellabel(uid, self, countnum, btnplus):
    name = ClickableLabel(dynamicapiname(uid))
    isdeprecated = uid not in defaultglobalconfig["fanyi"] and (
        0 == translate_exits(uid, which=True)
    )
    if isdeprecated:
        name.setStyleSheet("QLabel{background:red}")
    fn = functools.partial(renameapi, name, uid, self, countnum, btnplus)
    name.clicked.connect(fn)
    return name


def loadbutton(self, fanyi):
    which = translate_exits(fanyi, which=True)
    items = autoinitdialog_items(translatorsetting[fanyi])
    if which == 0:
        aclass = "translator." + fanyi
    elif which == 1:
        aclass = "userconfig.copyed." + fanyi
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


def selectllmcallback(self, countnum: list, btnplus, fanyi, name):
    uid = str(uuid.uuid4())
    _f11 = "Lunatranslator/translator/{}.py".format(fanyi)
    _f12 = "userconfig/copyed/{}.py".format(fanyi)
    _f2 = "userconfig/copyed/{}.py".format(uid)
    os.makedirs("userconfig/copyed", exist_ok=True)
    try:
        shutil.copy(_f11, _f2)
    except:
        shutil.copy(_f12, _f2)

    globalconfig["fanyi"][uid] = copy.deepcopy(globalconfig["fanyi"][fanyi])
    globalconfig["fanyi"][uid]["use"] = False

    if not name:
        name = globalconfig["fanyi"][fanyi]["name"] + "_copy"
    globalconfig["fanyi"][uid]["name"] = name
    globalconfig["fanyi"][uid]["type"] = btnplus
    if fanyi in translatorsetting:
        translatorsetting[uid] = copy.deepcopy(translatorsetting[fanyi])

    layout: QGridLayout = getattr(self, "damoxinggridinternal" + btnplus)

    last = getIconButton(callback=functools.partial(loadbutton, self, uid))

    name = getrenameablellabel(uid, self, countnum, btnplus)
    swc = getsimpleswitch(
        globalconfig["fanyi"][uid],
        "use",
        callback=functools.partial(gobject.baseobject.prepare, uid),
    )
    color = getcolorbutton(
        self,
        globalconfig["fanyi"][uid],
        "color",
        callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
    )

    offset = 5 * (len(countnum) % 3)
    layout.addWidget(name, layout.rowCount() - 1, offset + 0)
    layout.addWidget(swc, layout.rowCount() - 1, offset + 1)
    layout.addWidget(color, layout.rowCount() - 1, offset + 2)
    layout.addWidget(last, layout.rowCount() - 1, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), layout.rowCount() - 1, offset + 4)

    else:
        layout.addWidget(
            getattr(self, "btnmany" + btnplus), layout.rowCount(), 5 * 2, 1, 4
        )
    countnum.append(uid)


def btnpluscallback(self, countnum, btnplus):
    getalistname(
        self,
        False,
        btnplus,
        functools.partial(selectllmcallback, self, countnum, btnplus),
    )


def selectllmcallback_2(self, countnum, btnplus, fanyi, name):
    _f2 = "userconfig/copyed/{}.py".format(fanyi)
    try:
        os.remove(_f2)
    except:
        pass
    globalconfig["fanyi"][fanyi]["use"] = False
    try:
        gobject.baseobject.translators.pop(fanyi)
    except:
        pass
    layout: QGridLayout = getattr(self, "damoxinggridinternal" + btnplus)
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


def btndeccallback(self, countnum, btnplus):
    getalistname(
        self,
        True,
        btnplus,
        functools.partial(selectllmcallback_2, self, countnum, btnplus),
    )


def createmanybtn(self, countnum, btnplus):
    w = NQGroupBox()
    hbox = QHBoxLayout(w)
    hbox.setContentsMargins(0, 0, 0, 0)
    if btnplus == "api1":
        btn = IconButton("fa.question", fix=False, tips="使用说明")
        hbox.addWidget(btn)
        btn.clicked.connect(
            lambda: os.startfile(dynamiclink("/useapis/tsapi.html", docs=True))
        )
        return w

    btn = IconButton("fa.plus", fix=False, tips="复制")
    btn.clicked.connect(functools.partial(btnpluscallback, self, countnum, btnplus))

    hbox.addWidget(btn)

    btn = IconButton("fa.minus", fix=False, tips="删除")
    btn.clicked.connect(functools.partial(btndeccallback, self, countnum, btnplus))

    hbox.addWidget(btn)

    btn = IconButton(
        "fa.question",
        fix=False,
        tips="使用说明",
    )
    if btnplus == "offline":
        btn.clicked.connect(
            lambda: os.startfile(dynamiclink("/offlinellm.html", docs=True))
        )
    elif btnplus == "api":
        btn.clicked.connect(
            lambda: os.startfile(dynamiclink("/guochandamoxing.html", docs=True))
        )
    hbox.addWidget(btn)
    setattr(self, "btnmany" + btnplus, w)
    return w


def initsome11(self, l, label=None, btnplus=False, savecountnum=False):
    grids = []
    if label:
        grids.append([(label, 8)])
    i = 0
    line = []
    countnum = []
    for fanyi in l:
        which = translate_exits(fanyi, which=True)
        if which is None:
            continue
        i += 1
        countnum.append(fanyi)
        if fanyi in translatorsetting:
            last = D_getIconButton(callback=functools.partial(loadbutton, self, fanyi))
        elif fanyi == "selfbuild":
            last = D_getIconButton(
                callback=lambda: selectdebugfile("userconfig/selfbuild.py"),
                icon="fa.edit",
            )
        else:
            last = ""
        line += [
            functools.partial(getrenameablellabel, fanyi, self, countnum, btnplus),
            D_getsimpleswitch(
                globalconfig["fanyi"][fanyi],
                "use",
                callback=functools.partial(gobject.baseobject.prepare, fanyi),
            ),
            D_getcolorbutton(
                self,
                globalconfig["fanyi"][fanyi],
                "color",
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
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
    if btnplus and btnplus != "fuckyou":

        if i % 3 == 0:
            grids.append([])
        if i % 3 != 2:
            grids[-1].append(("", 5 * (2 - i % 3)))
        grids[-1].append((functools.partial(createmanybtn, self, countnum, btnplus), 4))
    elif len(grids) == 1:
        if i % 3 != 0:
            grids[-1].append(("", 5 * (3 - i % 3)))
    if savecountnum:
        return grids, countnum
    return grids


def initsome21(self, l, label=None, btnplus=None):
    is_gpt_likes, not_is_gpt_like = splitapillm(l)
    not_is_gpt_like = initsome11(self, not_is_gpt_like, label)
    is_gpt_likes = initsome11(self, is_gpt_likes, label, btnplus=btnplus)
    grids = [
        [
            functools.partial(
                createfoldgrid,
                is_gpt_likes,
                "大模型",
                globalconfig["foldstatus"]["ts"],
                "gptoffline",
                ("damoxinggridinternal" + btnplus) if btnplus else None,
                self,
            )
        ],
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


def initsome2(self, mianfei, l, external: list, label=None, btnplus=None):

    onlinegrid = initsome11(self, mianfei)
    is_gpt_likes, not_is_gpt_like = splitapillm(l)
    not_is_gpt_like = initsome11(self, not_is_gpt_like, label, btnplus="api1")
    is_gpt_likes = initsome11(self, is_gpt_likes, label, btnplus=btnplus)
    grids = [
        [
            functools.partial(
                createfoldgrid,
                is_gpt_likes,
                "大模型",
                globalconfig["foldstatus"]["ts"],
                "gpt",
                "damoxinggridinternal" + btnplus,
                self,
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
                not_is_gpt_like,
                "传统_API",
                globalconfig["foldstatus"]["ts"],
                "api",
            )
        ],
    ]
    if external:
        external, self.countnumexternal = initsome11(
            self, external, label, savecountnum=True, btnplus="fuckyou"
        )
        if external:
            grids += [
                [
                    functools.partial(
                        createfoldgrid,
                        external,
                        "其他",
                        globalconfig["foldstatus"]["ts"],
                        "external",
                        internallayoutname="damoxinggridinternalfuckyou",
                        parent=self,
                    )
                ],
            ]
    return grids


@tryprint
def sqlite2json2(self, sqlitefile, targetjson=None, existsmerge=False):
    try:
        sql = autosql(sqlitefile, check_same_thread=False)
        ret = sql.execute("SELECT * FROM artificialtrans  ").fetchall()
        js_format2 = {}
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
        if len(_collect) > 0:
            transkirokuuse = combo.getIndexData(combo.currentIndex())
            for k in js_format2:
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

    offlinegrid = initsome21(self, res.offline, btnplus="offline")
    offlinegrid += [[functools.partial(offlinelinks, "translate")]]
    online_reg_grid = initsome2(self, res.free, res.api, res.external, btnplus="api")
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
    savelay = []
    tab, dotab = makesubtab_lazy(
        ["在线翻译", "离线翻译", "其他"],
        [
            functools.partial(makescrollgrid, online_reg_grid, savelay=savelay),
            functools.partial(makescrollgrid, offlinegrid),
            functools.partial(makescrollgrid, pretransgrid),
        ],
        delay=True,
    )
    tab.setAcceptDrops(True)
    tab.dragEnterEvent = __dragEnterEvent
    tab.dropEvent = functools.partial(__dropEvent, self, savelay)
    basel.addWidget(tab)
    dotab()


def __dragEnterEvent(event: QDragEnterEvent):
    if event.mimeData().hasUrls():
        event.accept()
    else:
        event.ignore()


def ___appendex(self, ll: QGridLayout):
    if ll.count() > 3:
        return
    fold = createfoldgrid(
        [],
        "其他",
        globalconfig["foldstatus"]["ts"],
        "external",
        internallayoutname="damoxinggridinternalfuckyou",
        parent=self,
    )
    ll.addWidget(fold)
    self.countnumexternal = []


def __additem(self, layout: QGridLayout, uid):
    countnum: list = self.countnumexternal
    last = getIconButton(callback=functools.partial(loadbutton, self, uid))

    name = getrenameablellabel(uid, self, countnum, "fuckyou")
    swc = getsimpleswitch(
        globalconfig["fanyi"][uid],
        "use",
        callback=functools.partial(gobject.baseobject.prepare, uid),
    )
    color = getcolorbutton(
        self,
        globalconfig["fanyi"][uid],
        "color",
        callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
    )
    offset = 5 * (len(countnum) % 3)
    rx = len(countnum) % 3 == 0
    r = layout.rowCount() - 1 + rx
    layout.addWidget(name, r, offset + 0)
    layout.addWidget(swc, r, offset + 1)
    layout.addWidget(color, r, offset + 2)
    layout.addWidget(last, r, offset + 3)
    if len(countnum) % 3 != 2:
        layout.addWidget(QLabel(), r, offset + 4)

    countnum.append(uid)


@tryprint
def __importnew(self, savelay, f):

    from translator.basetranslator import basetrans

    fanyi = str(uuid.uuid4())
    os.makedirs("userconfig/copyed", exist_ok=True)
    shutil.copy(f, "userconfig/copyed/{}.py".format(fanyi))
    module = importlib.import_module("userconfig.copyed." + fanyi)
    TS = module.TS
    if not issubclass(TS, basetrans):
        raise Exception()
    default = {
        "type": "external",
        "color": "blue",
        "name": os.path.basename(os.path.splitext(f)[0]),
    }
    try:
        basic_config = module.basic_config
    except:
        basic_config = {}
    try:
        translator_config = module.translator_config
    except:
        translator_config = {}
    default.update(basic_config)
    default["use"] = False
    globalconfig["fanyi"][fanyi] = default
    if translator_config:
        translatorsetting[fanyi] = translator_config
    ll: QGridLayout = savelay[0]
    ___appendex(self, ll)
    __additem(self, self.damoxinggridinternalfuckyou, fanyi)


def __dropEvent(self, savelay: list, event: QDropEvent):
    files = [u.toLocalFile() for u in event.mimeData().urls()]
    for f in files:
        if os.path.splitext(f)[1].lower() != ".py":
            continue
        __importnew(self, savelay, f)
