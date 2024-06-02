from qtsymbols import *
import functools
import gobject, windows, winsharedutils
from myutils.config import globalconfig, _TR
from myutils.winsyshotkey import SystemHotkey, registerException
from myutils.hwnd import grabwindow
from myutils.utils import getimageformat, parsekeystringtomodvkcode, unsupportkey
from gui.usefulwidget import (
    D_getsimpleswitch,
    D_getsimplekeyseq,
    makescrollgrid,
)


def delaycreatereferlabels(self, name):
    referlabel = QLabel()
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
        "_5": gobject.baseobject.translation_ui.changeshowhideraw,
        "_6": lambda: gobject.baseobject.transhis.showsignal.emit(),
        "_7": gobject.baseobject.translation_ui.langdu,
        "_8": lambda: gobject.baseobject.translation_ui.changemousetransparentstate(0),
        "_9": gobject.baseobject.translation_ui.changetoolslockstate,
        "_10": lambda: gobject.baseobject.translation_ui.showsavegame_signal.emit(),
        "_11": gobject.baseobject.createattachprocess,
        "_12": lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
        "_13": lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(False),
        "_14": gobject.baseobject.translation_ui.showhide_signal.emit,
        "_15": gobject.baseobject.translation_ui.bindcropwindow_signal.emit,
        "_16": gobject.baseobject.translation_ui.showhideuisignal.emit,
        "_17": gobject.baseobject.translation_ui.quitf_signal.emit,
        "_18": lambda: gobject.baseobject.settin_ui.fontbigsmallsignal.emit(1),
        "_19": lambda: gobject.baseobject.settin_ui.fontbigsmallsignal.emit(-1),
        "_20": gobject.baseobject.translation_ui.fullsgame_signal.emit,
        "_21": lambda: grabwindow(getimageformat()),
        "_22": gobject.baseobject.translation_ui.muteprocessignal.emit,
        "_23": lambda: gobject.baseobject.translation_ui.clickRange_signal.emit(True),
        "_25": lambda: windows.SendMessage(
            windows.FindWindow("WNDCLS_Magpie_Core_CLI_Message", None),
            windows.RegisterWindowMessage("Magpie_Core_CLI_Message_ToggleOverlay"),
        ),
        "_26": gobject.baseobject.translation_ui.ocr_once_signal.emit,
        "_27": gobject.baseobject.translation_ui.simulate_key_enter,
        "_28": lambda: winsharedutils.clipboard_set(
            gobject.baseobject.currenttranslate
        ),
    }
    for name in globalconfig["quick_setting"]["all"]:
        if name not in self.bindfunctions:
            continue
        regist_or_not_key(self, name)


def setTab_quick(self, l):

    makescrollgrid(setTab_quick_lazy(self), l)


def setTab_quick_lazy(self):

    grids = [
        [
            (("是否使用快捷键"), 4),
            D_getsimpleswitch(
                globalconfig["quick_setting"],
                "use",
                callback=functools.partial(__enable, self),
            ),
            ((""), 8),
        ]
    ]
    for name in globalconfig["quick_setting"]["all"]:
        if name not in self.bindfunctions:
            continue

        grids.append(
            [
                ((globalconfig["quick_setting"]["all"][name]["name"]), 4),
                D_getsimpleswitch(
                    globalconfig["quick_setting"]["all"][name],
                    "use",
                    callback=functools.partial(fanyiselect, self, name),
                ),
                (
                    D_getsimplekeyseq(
                        globalconfig["quick_setting"]["all"][name],
                        "keystring",
                        functools.partial(regist_or_not_key, self, name),
                    ),
                    2,
                ),
                (functools.partial(delaycreatereferlabels, self, name), 4),
            ]
        )
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
        maybesetreferlabels(self, name, _TR("不支持的键位") + ",".join(e.args[0]))
        return

    try:
        self.hotkeymanager.register((mode, vkcode), callback=self.bindfunctions[name])
        self.registok[name] = (mode, vkcode)
    except registerException:
        maybesetreferlabels(self, name, _TR("快捷键冲突"))
