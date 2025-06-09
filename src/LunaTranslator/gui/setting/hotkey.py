from qtsymbols import *
import functools
import gobject, NativeUtils, uuid, os, shutil
from myutils.config import globalconfig, _TR
from myutils.hwnd import grabwindow
from traceback import print_exc
from myutils.utils import (
    parsekeystringtomodvkcode,
    unsupportkey,
    selectdebugfile,
    checkmd5reloadmodule,
)
from gui.usefulwidget import (
    D_getsimpleswitch,
    D_getsimplekeyseq,
    makescrollgrid,
    D_getIconButton,
    makesubtab_lazy,
    makegrid,
    getboxlayout,
    VisLFormLayout,
    IconButton,
    makescroll,
    SClickableLabel,
)
from gui.inputdialog import autoinitdialog
from gui.dynalang import LLabel, LAction


def delaycreatereferlabels(self, name):
    referlabel = LLabel()
    self.referlabels[name] = referlabel
    try:
        referlabel.setText(self.referlabels_data[name])
    except:
        pass
    return referlabel


def maybesetreferlabels(self, name, text):
    try:
        self.referlabels[name].setText(text)
    except:
        self.referlabels_data[name] = text


def autoreadswitch(self):
    try:
        self.autoread.clicksignal.emit()
    except:
        globalconfig["autoread"] = not globalconfig["autoread"]


def safeGet():

    t = NativeUtils.GetSelectedText()
    if (t is None) and (globalconfig["getWordFallbackClipboard"]):
        t = NativeUtils.ClipBoard.text
    if 0:
        QToolTip.showText(
            QCursor.pos(), _TR("取词失败"), gobject.baseobject.commonstylebase
        )
        t = ""
    return t


def createreloadablewrapper(self, name):
    _, module = checkmd5reloadmodule(
        "userconfig/myhotkeys/{}.py".format(name), "myhotkeys." + name
    )
    try:
        gobject.signals.safeinvokefunction.emit(module.OnHotKeyClicked)
    except:
        print_exc()


def registrhotkeys(self):
    self.referlabels = {}
    self.referlabels_data = {}
    self.registok = {}
    self.bindfunctions = {
        "_1": gobject.baseobject.translation_ui.startTranslater,
        "_2": gobject.baseobject.translation_ui.changeTranslateMode,
        "_3": self.showsignal.emit,
        "_4": lambda: NativeUtils.ClipBoard.setText(gobject.baseobject.currenttext),
        "_5": gobject.baseobject.translation_ui.changeshowhiderawsig.emit,
        "_51": gobject.baseobject.translation_ui.changeshowhidetranssig.emit,
        "_6": lambda: gobject.baseobject.transhis.showsignal.emit(),
        "_7": lambda: gobject.baseobject.readcurrent(force=True),
        "_7_1": lambda: gobject.baseobject.audioplayer.stop(),
        "_8": lambda: gobject.baseobject.translation_ui.changemousetransparentstate(0),
        "_9": gobject.baseobject.translation_ui.changetoolslockstate,
        "_10": gobject.baseobject.translation_ui.showsavegame_signal.emit,
        "_11": gobject.baseobject.translation_ui.hotkeyuse_selectprocsignal.emit,
        "_12": lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
        "_13": lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(),
        "_14": gobject.baseobject.translation_ui.showhide_signal.emit,
        "_14_1": gobject.baseobject.translation_ui.clear_signal_1.emit,
        "_15": gobject.baseobject.translation_ui.bindcropwindow_signal.emit,
        "_16": gobject.baseobject.translation_ui.showhideuisignal.emit,
        "_17": gobject.baseobject.translation_ui.quitf_signal.emit,
        "_21": grabwindow,
        "_22": gobject.baseobject.translation_ui.muteprocessignal.emit,
        "41": lambda: gobject.baseobject.translation_ui.fullsgame_signal.emit(False),
        "42": lambda: gobject.baseobject.translation_ui.fullsgame_signal.emit(True),
        "_26": gobject.baseobject.translation_ui.ocr_once_signal.emit,
        "_26_1": lambda: gobject.baseobject.translation_ui.ocr_do_function(
            gobject.baseobject.translation_ui.ocr_once_follow_rect
        ),
        "_28": lambda: NativeUtils.ClipBoard.setText(
            gobject.baseobject.currenttranslate
        ),
        "_29": lambda: gobject.baseobject.searchwordW.ankiwindow.recordbtn1.click(),
        "_30": lambda: gobject.baseobject.searchwordW.ankiwindow.recordbtn2.click(),
        "_32": functools.partial(autoreadswitch, self),
        "_33": lambda: gobject.baseobject.searchwordW.soundbutton.click(),
        "_35": lambda: gobject.baseobject.searchwordW.ankiconnect.customContextMenuRequested.emit(
            QPoint()
        ),
        "36": lambda: gobject.baseobject.textgetmethod(
            NativeUtils.ClipBoard.text, False
        ),
        "37": lambda: gobject.baseobject.searchwordW.search_word.emit(
            safeGet(), None, False
        ),
        "39": lambda: gobject.baseobject.searchwordW.ocr_once_signal.emit(),
        "38": lambda: gobject.baseobject.textgetmethod(safeGet(), False),
        "40": lambda: gobject.baseobject.searchwordW.search_word_in_new_window.emit(
            safeGet()
        ),
    }

    for name in globalconfig["myquickkeys"]:
        self.bindfunctions[name] = functools.partial(
            createreloadablewrapper, self, name
        )
    for name in self.bindfunctions:
        regist_or_not_key(self, name)


hotkeys = [
    [
        "通用",
        ["_1", "_2", "_3", "_5", "_51", "_6", "_8", "_9", "_10", "38", "_16", "_17"],
    ],
    ["HOOK", ["_11", "_12"]],
    ["OCR", ["_13", "_14", "_14_1", "_26", "_26_1"]],
    ["剪贴板", ["36", "_4", "_28"]],
    ["TTS", ["_32", "_7", "_7_1"]],
    ["游戏", ["_15", "_21", "_22", "41", "42"]],
    ["查词", ["37", "40", "39", "_29", "_30", "_35", "_33"]],
]


def renameapi(qlabel: QLabel, name, self, form: VisLFormLayout, cnt, _=None):
    menu = QMenu(qlabel)
    editname = LAction("重命名", menu)
    delete = LAction("删除", menu)
    menu.addAction(editname)
    menu.addAction(delete)
    action = menu.exec(QCursor.pos())
    if action == delete:
        form.setRowVisible(cnt, False)
        globalconfig["myquickkeys"].remove(name)
        globalconfig["quick_setting"]["all"][name]["use"] = False
        regist_or_not_key(self, name)
    elif action == editname:
        before = globalconfig["quick_setting"]["all"][name]["name"]
        __d = {"k": before}

        def cb(__d):
            title = __d["k"]
            if title not in ("", before):
                globalconfig["quick_setting"]["all"][name]["name"] = title
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


def getrenameablellabel(form: VisLFormLayout, cnt: int, uid: str, self):
    bl = SClickableLabel(globalconfig["quick_setting"]["all"][uid]["name"])
    fn = functools.partial(renameapi, bl, uid, self, form, cnt)
    bl.clicked.connect(fn)
    return bl


def createmykeyline(self, form: QFormLayout, name):
    cnt = form.rowCount()
    form.addRow(
        getrenameablellabel(form, cnt, name, self),
        getboxlayout(
            [
                D_getsimpleswitch(
                    globalconfig["quick_setting"]["all"][name],
                    "use",
                    callback=functools.partial(regist_or_not_key, self, name),
                ),
                D_getIconButton(
                    callback=lambda: selectdebugfile(
                        "userconfig/myhotkeys/{}.py".format(name), ishotkey=True
                    ),
                    icon="fa.edit",
                ),
                D_getsimplekeyseq(
                    globalconfig["quick_setting"]["all"][name],
                    "keystring",
                    functools.partial(regist_or_not_key, self, name),
                ),
                functools.partial(delaycreatereferlabels, self, name),
            ]
        ),
    )


def plusclicked(self, form):
    name = str(uuid.uuid4())
    self.bindfunctions[name] = functools.partial(createreloadablewrapper, self, name)
    globalconfig["myquickkeys"].append(name)
    globalconfig["quick_setting"]["all"][name] = {
        "use": False,
        "name": name,
        "keystring": "",
    }
    os.makedirs("userconfig/myhotkeys", exist_ok=True)
    shutil.copy(
        "LunaTranslator/myutils/template/hotkey.py",
        "userconfig/myhotkeys/{}.py".format(name),
    )
    createmykeyline(self, form, name)


def selfdefkeys(self, lay: QLayout):
    wid = QWidget()
    wid.setStyleSheet("background:transparent")
    form = VisLFormLayout(wid)
    swid = makescroll()
    lay.addWidget(swid)
    swid.setWidget(wid)
    plus = IconButton(icon="fa.plus")
    plus.clicked.connect(functools.partial(plusclicked, self, form))
    form.addRow(plus)
    for name in globalconfig["myquickkeys"]:
        createmykeyline(self, form, name)
    return wid


def setTab_quick(self, l: QVBoxLayout):

    tab1grids = [
        [
            dict(
                grid=[
                    [
                        "使用快捷键",
                        getboxlayout(
                            [
                                D_getsimpleswitch(
                                    globalconfig["quick_setting"],
                                    "use",
                                    callback=functools.partial(__enable, self),
                                ),
                                "",
                            ],
                        ),
                    ]
                ]
            )
        ],
    ]
    gridlayoutwidget, do = makegrid(tab1grids, delay=True)
    l.addWidget(gridlayoutwidget)
    do()
    __ = []
    __vis = []

    def ___x(ls, l):
        makescrollgrid(setTab_quick_lazy(self, ls), l)

    for _ in hotkeys:
        __vis.append(_[0])
        __.append(functools.partial(___x, _[1]))
    __vis.append("自定义")
    __.append(functools.partial(selfdefkeys, self))
    tab, do = makesubtab_lazy(__vis, __, delay=True)

    l.addWidget(tab)
    l.setSpacing(0)
    do()


def setTab_quick_lazy(self, ls):
    grids = []
    for name in ls:

        grids.append(
            [
                globalconfig["quick_setting"]["all"][name]["name"],
                D_getsimpleswitch(
                    globalconfig["quick_setting"]["all"][name],
                    "use",
                    callback=functools.partial(regist_or_not_key, self, name),
                ),
                D_getsimplekeyseq(
                    globalconfig["quick_setting"]["all"][name],
                    "keystring",
                    functools.partial(regist_or_not_key, self, name),
                ),
                (functools.partial(delaycreatereferlabels, self, name), -1),
            ]
        )
    grids.append([("", 40)])
    return grids


def __enable(self, x):
    for quick in globalconfig["quick_setting"]["all"]:
        if quick not in self.bindfunctions:
            continue
        regist_or_not_key(self, quick)


def regist_or_not_key(self, name, _=None):
    maybesetreferlabels(self, name, "")

    if name in self.registok:
        NativeUtils.UnRegisterHotKey(self.registok[name])

    keystring = globalconfig["quick_setting"]["all"][name]["keystring"]
    if keystring == "" or (
        not (
            globalconfig["quick_setting"]["all"][name]["use"]
            and globalconfig["quick_setting"]["use"]
        )
    ):
        return

    try:
        mode, vkcode = parsekeystringtomodvkcode(keystring)
    except unsupportkey as e:
        maybesetreferlabels(self, name, ("不支持的键位_") + ",".join(e.args[0]))
        return
    uid = NativeUtils.RegisterHotKey((mode, vkcode), self.bindfunctions[name])

    if not uid:
        maybesetreferlabels(self, name, ("快捷键冲突"))
    else:
        self.registok[name] = uid
