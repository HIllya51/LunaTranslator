from qtsymbols import *
import os, functools
import gobject
from myutils.utils import splitocrtypes
from myutils.config import globalconfig
from gui.inputdialog import (
    autoinitdialog_items,
    noundictconfigdialog1,
    autoinitdialog,
    yuyinzhidingsetting,
)
from gui.dynalang import LAction, LLabel
from tts.basettsclass import TTSbase
from gui.setting.about import offlinelinks
from gui.usefulwidget import (
    D_getspinbox,
    makescrollgrid,
    D_getIconButton,
    yuitsu_switch,
    FocusCombo,
    D_getsimpleswitch,
    getboxlayout,
    getboxwidget,
    ClickableLabel,
    check_grid_append,
)


def showvoicelist(self, obj: TTSbase):

    if obj is None:
        self.voicecombo.clear()
        self.pitch____.setEnabled(False)
        self.rate____.setEnabled(False)
        return
    vl = obj.voiceshowlist
    idx = obj.voicelist.index(obj.voice)
    self.pitch____.setEnabled(obj.arg_support_pitch)
    self.rate____.setEnabled(obj.arg_support_speed)

    self.voicecombo.clear()
    self.voicecombo.addItems(vl)
    self.voicecombo.setCurrentIndex(idx)


def changevoice(self, _):
    if gobject.baseobject.reader is None:
        return
    gobject.baseobject.reader.voice = gobject.baseobject.reader.voicelist[
        self.voicecombo.currentIndex()
    ]


def createrate(self):
    self.rate____ = getboxwidget(
        [
            "语速_(-10~10)",
            D_getspinbox(
                -10,
                10,
                globalconfig["ttscommon"],
                "rate",
                step=0.5,
                double=True,
            ),
        ],
    )
    return self.rate____


def createpitch(self):
    self.pitch____ = getboxwidget(
        [
            "音高_(-10~10)",
            D_getspinbox(
                -10,
                10,
                globalconfig["ttscommon"],
                "pitch",
                step=0.5,
                double=True,
            ),
        ],
    )
    return self.pitch____


def createvoicecombo(self):

    self.voicecombo = FocusCombo(sizeX=True)
    self.voicecombo.currentTextChanged.connect(lambda x: changevoice(self, x))

    return self.voicecombo


def setTab5(self, l):
    makescrollgrid(setTab5lz(self), l)

    gobject.signals.connectsignal(
        gobject.signals.voicelistsignal, functools.partial(showvoicelist, self)
    )


def renameapi(qlabel: QLabel, apiuid):
    menu = QMenu(qlabel)
    useproxy = LAction("使用代理", menu)
    useproxy.setCheckable(True)

    menu.addAction(useproxy)
    useproxy.setChecked(globalconfig["reader"][apiuid].get("useproxy", True))
    pos = QCursor.pos()
    action = menu.exec(pos)

    if action == useproxy:
        globalconfig["reader"][apiuid]["useproxy"] = useproxy.isChecked()


def checkclickable(name: ClickableLabel):
    name.setClickable(globalconfig["useproxy"])


def getrenameablellabel(uid):
    if globalconfig["reader"][uid].get("type") in ("offline",):
        return LLabel(globalconfig["reader"][uid]["name"])
    name = ClickableLabel(globalconfig["reader"][uid]["name"])
    fn = functools.partial(renameapi, name, uid)
    name.beforeEnter.connect(functools.partial(checkclickable, name))
    name.clicked.connect(fn)
    return name


def getttsgrid(self, names):

    grids = []
    i = 0
    self.ttswitchs = {}
    line = []
    for name in names:

        _f = "LunaTranslator/tts/{}.py".format(name)
        if os.path.exists(_f) == False:
            continue
        if "args" in globalconfig["reader"][name]:
            items = autoinitdialog_items(globalconfig["reader"][name])
            items[-1]["callback"] = functools.partial(
                gobject.baseobject.startreader, name, True, True
            )
            _3 = D_getIconButton(
                callback=functools.partial(
                    autoinitdialog,
                    self,
                    globalconfig["reader"][name]["args"],
                    globalconfig["reader"][name]["name"],
                    800,
                    items,
                    "tts." + name,
                    name,
                )
            )

        else:
            _3 = ""

        line += [
            functools.partial(getrenameablellabel, name),
            D_getsimpleswitch(
                globalconfig["reader"][name],
                "use",
                name=name,
                parent=self,
                callback=functools.partial(
                    yuitsu_switch,
                    self,
                    globalconfig["reader"],
                    "ttswitchs",
                    name,
                    gobject.baseobject.startreader,
                ),
                pair="ttswitchs",
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
    check_grid_append(grids)
    return grids


def setTab5lz(self):
    grids = []
    offline, online = splitocrtypes(globalconfig["reader"])
    offilesgrid = getttsgrid(self, offline)
    offilesgrid += [
        [(functools.partial(offlinelinks, "tts"), 0)],
    ]
    grids += [
        [
            dict(
                title="引擎",
                grid=[
                    [dict(title="离线", type="grid", grid=offilesgrid)],
                    [dict(title="在线", type="grid", grid=getttsgrid(self, online))],
                ],
            ),
        ],
        [
            dict(
                title="声音",
                grid=[
                    [
                        "选择声音",
                        functools.partial(createvoicecombo, self),
                    ],
                    [
                        getboxlayout(
                            [
                                getboxlayout(
                                    [
                                        "音量_(0~100)",
                                        D_getspinbox(
                                            0,
                                            100,
                                            globalconfig["ttscommon"],
                                            "volume",
                                        ),
                                    ],
                                ),
                                "",
                                functools.partial(createrate, self),
                                "",
                                functools.partial(createpitch, self),
                            ],
                        ),
                    ],
                ],
            ),
        ],
        [
            dict(
                title="行为",
                grid=[
                    [
                        dict(
                            type="grid",
                            grid=[
                                [
                                    "自动朗读",
                                    D_getsimpleswitch(
                                        globalconfig,
                                        "autoread",
                                        name="autoread",
                                        parent=self,
                                    ),
                                    "",
                                    "不被打断",
                                    D_getsimpleswitch(globalconfig, "ttsnointerrupt"),
                                    "",
                                    "自动前进",
                                    D_getsimpleswitch(globalconfig, "ttsautoforward"),
                                ],
                                [
                                    "朗读原文",
                                    D_getsimpleswitch(globalconfig, "read_raw"),
                                    "",
                                    "朗读翻译",
                                    D_getsimpleswitch(globalconfig, "read_trans"),
                                ],
                            ],
                        ),
                    ],
                    [
                        dict(
                            type="grid",
                            grid=[
                                [
                                    "语音指定",
                                    D_getsimpleswitch(
                                        globalconfig["ttscommon"], "tts_skip"
                                    ),
                                    D_getIconButton(
                                        callback=lambda: yuyinzhidingsetting(
                                            self,
                                            globalconfig["ttscommon"]["tts_skip_regex"],
                                        )
                                    ),
                                    "",
                                    "语音修正",
                                    D_getsimpleswitch(
                                        globalconfig["ttscommon"], "tts_repair"
                                    ),
                                    D_getIconButton(
                                        callback=lambda: noundictconfigdialog1(
                                            self,
                                            globalconfig["ttscommon"][
                                                "tts_repair_regex"
                                            ],
                                            "语音修正",
                                            ["正则", "转义", "原文", "替换"],
                                            extraX=globalconfig["ttscommon"],
                                        )
                                    ),
                                    "",
                                    "",
                                    "",
                                ],
                            ],
                        ),
                    ],
                ],
            ),
        ],
    ]
    return grids
