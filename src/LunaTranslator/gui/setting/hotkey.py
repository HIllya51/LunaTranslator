from qtsymbols import *
import functools, gobject, NativeUtils, uuid, windows, shutil, time, math
from myutils.config import globalconfig, _TR
from myutils.hwnd import grabwindow
from traceback import print_exc
from myutils.wrapper import threader, tryprint
from myutils.keycode import vkcode_map
from myutils.utils import (
    parsekeystringtomodvkcode,
    unsupportkey,
    selectdebugfile,
    checkmd5reloadmodule,
)
from gui.usefulwidget import (
    D_getsimpleswitch,
    D_getsimplekeyseq,
    D_getdoclink,
    makescrollgrid,
    D_getIconButton,
    makesubtab_lazy,
    getspinbox,
    request_delete_ok,
    makegrid,
    getboxlayout,
    VisLFormLayout,
    IconButton,
    makescroll,
    SClickableLabel,
    getsimplecombobox,
)
from gui.inputdialog import autoinitdialog
from gui.dynalang import LLabel, LAction, LDialog, LFormLayout


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
        QToolTip.showText(QCursor.pos(), _TR("取词失败"), gobject.base.commonstylebase)
        t = ""
    return t


def createreloadablewrapper(self, name):
    module = checkmd5reloadmodule(
        gobject.getconfig("myhotkeys/{}.py").format(name), "myhotkeys." + name
    )
    try:
        gobject.base.safeinvokefunction.emit(module.OnHotKeyClicked)
    except:
        print_exc()


liandianqi_stoped = True


def invoke_liandianqi_or_stop():
    global liandianqi_stoped
    key = globalconfig.get("liandianqi_vkey")
    if not key:
        return
    interval = globalconfig.get("liandianqi_interval", 1)
    if liandianqi_stoped:
        liandianqi_stoped = False

        @threader
        def __():
            d = globalconfig["quick_setting"]["all"]["44"]
            while d["use"] and not liandianqi_stoped:
                if key in (1, 2, 4):
                    flags = {
                        1: (windows.MOUSEEVENTF_LEFTDOWN, windows.MOUSEEVENTF_LEFTUP),
                        2: (windows.MOUSEEVENTF_RIGHTDOWN, windows.MOUSEEVENTF_RIGHTUP),
                        4: (
                            windows.MOUSEEVENTF_MIDDLEDOWN,
                            windows.MOUSEEVENTF_MIDDLEUP,
                        ),
                    }
                    windows.mouse_event(flags[key][0], 0, 0, 0)
                    time.sleep(0.1)
                    windows.mouse_event(flags[key][1], 0, 0, 0)
                else:
                    windows.keybd_event(key, 0, 0, 0)
                    time.sleep(0.1)
                    windows.keybd_event(key, 0, windows.KEYEVENTF_KEYUP, 0)
                time.sleep(interval)

        __()
    else:
        liandianqi_stoped = True


@tryprint
def _ocr_focus_switch(to):
    curr = 0
    for i, r in enumerate(gobject.base.textsource.ranges):
        if r.range_ui.isfocus:
            curr = i
            break
    __l = len(gobject.base.textsource.ranges)
    for i in range(__l):
        curri = (__l + curr + i + to) % __l
        r = gobject.base.textsource.ranges[curri]
        if r.range_ui.getrect():
            r.range_ui.isfocus = True
            gobject.base.translation_ui.startTranslater()
            break


def _calc_dis_and_centerdis(rect, point):

    (x1, y1), (x2, y2) = rect
    px, py = point.x, point.y

    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])

    if x1 <= px <= x2 and y1 <= py <= y2:
        edge_dist = 0
    else:
        dx = max(x1 - px, 0, px - x2)
        dy = max(y1 - py, 0, py - y2)
        edge_dist = math.hypot(dx, dy)

    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    center_dist = math.hypot(px - cx, py - cy)

    return edge_dist, center_dist


@tryprint
def _ocr_focus_No():
    for r in gobject.base.textsource.ranges:
        if r.range_ui.isfocus:
            r.range_ui.isfocus = False


@tryprint
def _ocr_focus_switch_near():
    nearestr = None
    dist = math.inf, math.inf
    curr = windows.GetCursorPos()
    for rr in gobject.base.textsource.ranges:
        r = rr.range_ui.getrect()
        if not r:
            continue
        d, cd = _calc_dis_and_centerdis(r, curr)
        if d < dist[0]:
            nearestr = rr
            dist = d, cd
        elif d == dist[0] and cd < dist[1]:
            nearestr = rr
            dist = d, cd
    if not nearestr:
        return
    nearestr.range_ui.isfocus = True
    gobject.base.translation_ui.startTranslater()


def registrhotkeys(self):
    self.referlabels = {}
    self.referlabels_data = {}
    self.registok = {}
    self.bindfunctions = {
        "_1": gobject.base.translation_ui.startTranslater,
        "_2": gobject.base.translation_ui.changeTranslateMode,
        "_3": gobject.base.settin_ui_showsignal.emit,
        "_4": lambda: NativeUtils.ClipBoard.setText(gobject.base.currenttext),
        "_5": gobject.base.translation_ui.changeshowhiderawsig.emit,
        "_51": gobject.base.translation_ui.changeshowhidetranssig.emit,
        "_6": lambda: gobject.base.transhis.showsignal.emit(),
        "_7": lambda: gobject.base.readcurrent(force=True),
        "_7_1": lambda: gobject.base.audioplayer.stop(),
        "_8": lambda: gobject.base.translation_ui.changemousetransparentstate(0),
        "_9": gobject.base.translation_ui.changetoolslockstate,
        "_10": gobject.base.translation_ui.showsavegame_signal.emit,
        "_11": gobject.base.translation_ui.hotkeyuse_selectprocsignal.emit,
        "_12": lambda: gobject.base.hookselectdialog.showsignal.emit(),
        "_13": lambda: gobject.base.translation_ui.clickRange_signal.emit(),
        "_14": gobject.base.translation_ui.showhide_signal.emit,
        "_14_1": gobject.base.translation_ui.clear_signal_1.emit,
        "_15": gobject.base.translation_ui.bindcropwindow_signal.emit,
        "_16": gobject.base.translation_ui.showhideuisignal.emit,
        "_17": gobject.base.translation_ui.quitf_signal.emit,
        "_21": grabwindow,
        "_22": gobject.base.translation_ui.muteprocessignal.emit,
        "41": lambda: gobject.base.translation_ui.fullsgame_signal.emit(False),
        "42": lambda: gobject.base.translation_ui.fullsgame_signal.emit(True),
        "_26": gobject.base.translation_ui.ocr_once_signal.emit,
        "_26_1": lambda: gobject.base.translation_ui.ocr_do_function(
            gobject.base.translation_ui.ocr_once_follow_rect
        ),
        "_28": lambda: NativeUtils.ClipBoard.setText(gobject.base.currenttranslate),
        "_29": lambda: gobject.base.searchwordW.ankiwindow.recordbtn1.click(),
        "_30": lambda: gobject.base.searchwordW.ankiwindow.recordbtn2.click(),
        "_32": functools.partial(autoreadswitch, self),
        "_33": lambda: gobject.base.searchwordW.soundbutton.click(),
        "_35": lambda: gobject.base.searchwordW.ankiconnect.customContextMenuRequested.emit(
            QPoint()
        ),
        "36": lambda: gobject.base.textgetmethod(NativeUtils.ClipBoard.text, False),
        "37": lambda: gobject.base.searchwordW.search_word.emit(safeGet(), None, False),
        "39": lambda: gobject.base.searchwordW.ocr_once_signal.emit(),
        "38": lambda: gobject.base.textgetmethod(safeGet(), False),
        "40": lambda: gobject.base.searchwordW.search_word_in_new_window.emit(
            safeGet()
        ),
        "43": lambda: NativeUtils.SuspendResumeProcess(
            windows.GetWindowThreadProcessId(gobject.base.hwnd)
        ),
        "44": invoke_liandianqi_or_stop,
        "45": gobject.base.prepare,
        "46": lambda: _ocr_focus_switch(-1),
        "47": lambda: _ocr_focus_switch(1),
        "48": lambda: _ocr_focus_switch_near(),
        "49": lambda: _ocr_focus_No(),
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
        [
            "_1",
            "_2",
            "_3",
            "_5",
            "_51",
            "_6",
            "_8",
            "_9",
            "38",
            "_16",
            "_17",
            "44",
            "45",
        ],
    ],
    ["HOOK", ["_11", "_12"]],
    ["OCR", ["_13", "_14", "_14_1", "_26", "_26_1", "46", "47", "48", "49"]],
    ["剪贴板", ["36", "_4", "_28"]],
    ["TTS", ["_32", "_7", "_7_1"]],
    ["游戏", ["_10", "_15", "_21", "_22", "43", "41", "42"]],
    ["查词", ["37", "40", "39", "_29", "_30", "_35", "_33"]],
]


class liandianqi(LDialog):
    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("设置")
        formLayout = LFormLayout(self)
        formLayout.addRow(
            "点击间隔_(s)",
            getspinbox(
                0.1, 10000, globalconfig, "liandianqi_interval", True, 0.1, default=1
            ),
        )
        combo = getsimplecombobox(
            list(vkcode_map.keys()),
            globalconfig,
            "liandianqi_vkey",
            default=1,
            internal=list(vkcode_map.values()),
        )
        formLayout.addRow("按键", combo)
        self.exec()


hotkeysettings = {"44": liandianqi}


def renameapi(qlabel: QLabel, name, self, form: VisLFormLayout, cnt, _=None):
    menu = QMenu(self)
    editname = LAction("重命名", menu)
    delete = LAction("删除", menu)
    menu.addAction(editname)
    menu.addAction(delete)
    action = menu.exec(QCursor.pos())
    if action == delete:
        if request_delete_ok(self, "1ac8bc89-7049-4e1c-9d36-b30698ad104a"):
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
                        "myhotkeys/{}.py".format(name), ishotkey=True
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
    shutil.copy(
        "LunaTranslator/myutils/template/hotkey.py",
        gobject.getconfig("myhotkeys/{}.py".format(name)),
    )
    createmykeyline(self, form, name)


def selfdefkeys(self, lay: QLayout):
    wid = QWidget()
    wid.setObjectName("FUCKYOU")
    wid.setStyleSheet("QWidget#FUCKYOU{background:transparent}")
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
                                0,
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
        d = globalconfig["quick_setting"]["all"][name]
        l = [
            D_getdoclink("fastkeys.html#anchor-" + name),
            (d["name"], 2),
            D_getsimpleswitch(
                d,
                "use",
                callback=functools.partial(regist_or_not_key, self, name),
            ),
            D_getsimplekeyseq(
                d,
                "keystring",
                functools.partial(regist_or_not_key, self, name),
            ),
            (functools.partial(delaycreatereferlabels, self, name), -1),
        ]
        if name in hotkeysettings:
            l[1] = (l[1][0], 1)
            l.insert(
                2,
                D_getIconButton(
                    callback=functools.partial(hotkeysettings[name], self),
                    tips="设置",
                ),
            )
        grids.append(l)
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
    __ = globalconfig["quick_setting"]["all"].get(name)
    if not __:
        return
    keystring = __["keystring"]
    if keystring == "" or (not (__["use"] and globalconfig["quick_setting"]["use"])):
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
