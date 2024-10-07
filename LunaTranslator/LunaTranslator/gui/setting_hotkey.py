from qtsymbols import *
import functools
import gobject, windows, winsharedutils
from myutils.config import globalconfig, static_data
from myutils.winsyshotkey import SystemHotkey, registerException
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


def registrhotkeys(self):
    self.hotkeymanager = SystemHotkey()
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
        "_13": lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(False),
        "_14": gobject.baseobject.translation_ui.showhide_signal.emit,
        "_15": gobject.baseobject.translation_ui.bindcropwindow_signal.emit,
        "_16": gobject.baseobject.translation_ui.showhideuisignal.emit,
        "_17": gobject.baseobject.translation_ui.quitf_signal.emit,
        "_20": gobject.baseobject.translation_ui.fullsgame_signal.emit,
        "_21": grabwindow,
        "_22": gobject.baseobject.translation_ui.muteprocessignal.emit,
        "_23": lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(True),
        "_25": lambda: windows.SendMessage(
            windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
            windows.RegisterWindowMessage("Magpie_Core_CLI_Message_ToggleOverlay"),
        ),
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
        "_31": lambda: gobject.baseobject.hualang_recordbtn.click(),
        "_32": functools.partial(autoreadswitch, self),
        "_33": lambda: gobject.baseobject.searchwordW.soundbutton.click(),
        "_35": lambda: gobject.baseobject.searchwordW.ankiconnect.customContextMenuRequested.emit(
            QPoint()
        ),
        "36": lambda: gobject.baseobject.textgetmethod(
            winsharedutils.clipboard_get(), False
        ),
    }
    for name in self.bindfunctions:
        regist_or_not_key(self, name)


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
            ],
            makewidget=True,
        )
    )
    __ = []
    __vis = []

    def ___x(ls, l):
        makescrollgrid(setTab_quick_lazy(self, ls), l)

    for _ in static_data["hotkeys"]:
        __vis.append(_[0])
        __.append(functools.partial(___x, _[1]))
    tab, do = makesubtab_lazy(__vis, __, delay=True)

    l.addWidget(tab)
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
        self.hotkeymanager.unregister(self.registok[name])

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

    try:
        self.hotkeymanager.register((mode, vkcode), callback=self.bindfunctions[name])
        self.registok[name] = (mode, vkcode)
    except registerException:
        maybesetreferlabels(self, name, ("快捷键冲突"))
