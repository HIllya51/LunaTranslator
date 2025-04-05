from qtsymbols import *
import functools, time
import gobject, windows, winsharedutils
from myutils.config import globalconfig, _TR
from myutils.hwnd import grabwindow
from myutils.utils import parsekeystringtomodvkcode, unsupportkey
from gui.usefulwidget import (
    D_getsimpleswitch,
    D_getsimplekeyseq,
    makescrollgrid,
    getsmalllabel,
    makesubtab_lazy,
    getboxlayout,
)
from gui.dynalang import LLabel
from myutils.magpie_builtin import MagpieBuiltin


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

    t = winsharedutils.GetSelectedText()
    if (t is None) and (globalconfig["getWordFallbackClipboard"]):
        t = winsharedutils.clipboard_get()
    if 0:
        QToolTip.showText(
            QCursor.pos(), _TR("取词失败"), gobject.baseobject.commonstylebase
        )
        t = ""
    return t


def registrhotkeys(self):
    self.referlabels = {}
    self.referlabels_data = {}
    self.registok = {}
    self.bindfunctions = {
        "_1": gobject.baseobject.translation_ui.startTranslater,
        "_2": gobject.baseobject.translation_ui.changeTranslateMode,
        "_3": self.showsignal.emit,
        "_4": lambda: winsharedutils.clipboard_set(gobject.baseobject.currenttext),
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
        "_25": MagpieBuiltin.overlay,
        "41": lambda: gobject.baseobject.translation_ui.fullsgame_signal.emit(False),
        "42": lambda: gobject.baseobject.translation_ui.fullsgame_signal.emit(True),
        "_26": gobject.baseobject.translation_ui.ocr_once_signal.emit,
        "_26_1": lambda: gobject.baseobject.translation_ui.ocr_do_function(
            gobject.baseobject.translation_ui.ocr_once_follow_rect
        ),
        "_27": gobject.baseobject.translation_ui.simulate_key_enter,
        "_28": lambda: winsharedutils.clipboard_set(
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
            winsharedutils.clipboard_get(), False
        ),
        "37": lambda: gobject.baseobject.searchwordW.search_word.emit(safeGet(), False),
        "39": lambda: gobject.baseobject.searchwordW.ocr_once_signal.emit(),
        "38": lambda: gobject.baseobject.textgetmethod(safeGet(), False),
        "40": lambda: gobject.baseobject.searchwordW.search_word_in_new_window.emit(
            safeGet()
        ),
    }
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
    ["游戏", ["_15", "_21", "_22", "41", "42", "_25", "_27"]],
    ["查词", ["37", "40", "39", "_29", "_30", "_35", "_33"]],
]


def setTab_quick(self, l: QVBoxLayout):
    l.addWidget(
        getboxlayout(
            [
                getsmalllabel("是否使用快捷键"),
                D_getsimpleswitch(
                    globalconfig["quick_setting"],
                    "use",
                    callback=functools.partial(__enable, self),
                ),
                "",
            ],
            makewidget=True,
        )
    )
    __ = []
    __vis = []

    def ___x(ls, l):
        makescrollgrid(setTab_quick_lazy(self, ls), l)

    for _ in hotkeys:
        __vis.append(_[0])
        __.append(functools.partial(___x, _[1]))
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
                    callback=functools.partial(fanyiselect, self, name),
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


def fanyiselect(self, who, checked):
    regist_or_not_key(self, who)


def regist_or_not_key(self, name):
    maybesetreferlabels(self, name, "")

    if name in self.registok:
        winsharedutils.unregisthotkey(self.registok[name])

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
    uid = winsharedutils.registhotkey((mode, vkcode), self.bindfunctions[name])

    if not uid:
        maybesetreferlabels(self, name, ("快捷键冲突"))
    else:
        self.registok[name] = uid
