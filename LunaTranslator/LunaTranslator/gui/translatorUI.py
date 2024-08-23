from qtsymbols import *
import time, functools, threading, os, importlib, shutil, uuid
from traceback import print_exc
import windows, qtawesome, gobject, winsharedutils
from myutils.wrapper import threader, trypass, tryprint
from myutils.config import (
    globalconfig,
    saveallconfig,
    _TR,
    static_data,
)
from gui.dialog_savedgame import dialog_setting_game
from myutils.utils import getlanguse, dynamiclink
from myutils.subproc import endsubprocs
from myutils.ocrutil import ocr_run, imageCut
from myutils.utils import (
    loadpostsettingwindowmethod,
    str2rgba,
    makehtml,
    loadpostsettingwindowmethod_maybe,
)
from myutils.hwnd import (
    mouseselectwindow,
    grabwindow,
    getExeIcon,
    getcurrexe,
)
from gui.setting_about import doupdate
from gui.dialog_memory import dialog_memory
from gui.textbrowser import Textbrowser
from gui.rangeselect import rangeselct_function
from gui.usefulwidget import (
    resizableframeless,
    getQMessageBox,
    LIconLabel,
    pixmapviewer,
)
from gui.edittext import edittrans
from gui.dialog_savedgame import dialog_savedgame_integrated
from gui.dialog_savedgame_setting import browserdialog
from gui.dynalang import LDialog


class ButtonX(QWidget):

    def __init__(self, *argc):
        super().__init__(*argc)
        self.reflayout = None
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def showinlayout(self, layout):

        layout.addWidget(self)
        self.show()
        self.reflayout = layout

    def hideinlayout(self):
        if self.reflayout is None:
            return
        _ = self.reflayout
        self.reflayout = None
        _.removeWidget(self)
        self.hide()

    def resizeEvent(self, e):
        h = int(e.size().height() / 1.5)
        self.setFixedWidth(int(self.height() * 2 / 1.5))
        self.setIconSize(QSize(h, h))


class IconLabelX(LIconLabel, ButtonX):
    clicked = pyqtSignal()

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if QObject.receivers(self, self.clicked) == 0:
            return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        if self.rect().contains(ev.pos()):
            self.clicked.emit()
        return super().mouseReleaseEvent(ev)


class ButtonBar(QFrame):
    def __init__(self, *argc):
        super().__init__(*argc)

        def __(p=None):
            _ = QHBoxLayout()
            _.setContentsMargins(0, 0, 0, 0)
            _.setSpacing(0)
            if p is not None:
                p.addLayout(_)
            return _

        self.threelayout = __()
        self._left = __(self.threelayout)
        self.threelayout.addStretch()
        self._center = __(self.threelayout)
        self.threelayout.addStretch()
        self._right = __(self.threelayout)
        self.setLayout(self.threelayout)
        self.cntbtn = 0
        self.buttons = {}
        self.stylebuttons = {}
        self.iconstate = {}
        self.colorstate = {}

    def refreshtoolicon(self):
        for name in self.buttons:
            if name in self.colorstate:
                color = (
                    globalconfig["buttoncolor_1"]
                    if self.colorstate[name]()
                    else globalconfig["buttoncolor"]
                )
            else:
                color = globalconfig["buttoncolor"]
            if name in self.iconstate:
                icon = (
                    globalconfig["toolbutton"]["buttons"][name]["icon"]
                    if self.iconstate[name]()
                    else globalconfig["toolbutton"]["buttons"][name]["icon2"]
                )
            else:
                icon = globalconfig["toolbutton"]["buttons"][name]["icon"]
            self.buttons[name].setIcon(qtawesome.icon(icon, color=color))

    def setstyle(self, bottomr, bottomr3):

        self.setStyleSheet(
            "#titlebar{border-width: 0;%s;background-color: %s}"
            % (
                bottomr,
                str2rgba(
                    globalconfig["backcolor_tool"], globalconfig["transparent_tool"]
                ),
            )
        )
        for _type in self.stylebuttons:
            style = """
            IconLabelX{
                background-color: rgba(255, 255, 255, 0);
                color: black;%s;
                border: 0px;
                font: 100 10pt;
            }
            IconLabelX:hover{
                background-color: %s;
                border: 0px;%s;
                font: 100 10pt;
            }
            IconLabelX:focus {outline: 0px;}
            """ % (
                bottomr3,
                (
                    globalconfig["button_color_normal"],
                    globalconfig["button_color_close"],
                )[_type - 1],
                bottomr3,
            )

            for btn in self.stylebuttons[_type]:
                btn.setStyleSheet(style)

    def takusanbuttons(
        self, _type, clickfunc, tips, name, belong=None, iconstate=None, colorstate=None
    ):
        button = IconLabelX()
        if clickfunc:

            def callwrap(call):
                try:
                    call()
                except:
                    print_exc()

            button.clicked.connect(functools.partial(callwrap, clickfunc))

        if tips:
            button.setToolTip(tips)
        if _type not in self.stylebuttons:
            self.stylebuttons[_type] = []
        self.stylebuttons[_type].append(button)
        button.reflayout = None
        button.belong = belong
        self.buttons[name] = button
        if iconstate:
            self.iconstate[name] = iconstate
        if colorstate:
            self.colorstate[name] = colorstate

    def adjustbuttons(self):
        __ = [self._left, self._right, self._center]
        cnt = 0
        for name in globalconfig["toolbutton"]["rank2"]:
            button = self.buttons[name]
            if button.belong:
                hide = True
                for k in button.belong:
                    if (
                        k in globalconfig["sourcestatus2"]
                        and globalconfig["sourcestatus2"][k]["use"]
                    ):
                        hide = False
                        break
                if hide:
                    button.hideinlayout()
                    continue
            if (
                name in globalconfig["toolbutton"]["buttons"]
                and globalconfig["toolbutton"]["buttons"][name]["use"] == False
            ):
                button.hideinlayout()
                continue
            layout: QHBoxLayout = __[
                globalconfig["toolbutton"]["buttons"][name]["align"]
            ]
            button.showinlayout(layout)
            cnt += 1
        self.cntbtn = cnt
        self.adjustminwidth()

    def adjustminwidth(self):
        w = self.cntbtn * self.height() * 2 / 1.5
        self.parent().setMinimumWidth(int(w))


class TranslatorWindow(resizableframeless):
    displayglobaltooltip = pyqtSignal(str)
    displaylink = pyqtSignal(str)
    displaymessagebox = pyqtSignal(str, str)
    displayres = pyqtSignal(dict)
    displayraw1 = pyqtSignal(dict)
    displaystatus = pyqtSignal(str, str, bool, bool)
    showhideuisignal = pyqtSignal()
    toolbarhidedelaysignal = pyqtSignal()
    showsavegame_signal = pyqtSignal()
    clickRange_signal = pyqtSignal(bool)
    showhide_signal = pyqtSignal()
    bindcropwindow_signal = pyqtSignal()
    fullsgame_signal = pyqtSignal()
    quitf_signal = pyqtSignal()
    refreshtooliconsignal = pyqtSignal()
    hidesignal = pyqtSignal()
    muteprocessignal = pyqtSignal()
    ocr_once_signal = pyqtSignal()
    resizesignal = pyqtSignal(QSize)
    move_signal = pyqtSignal(QPoint)
    closesignal = pyqtSignal()

    @threader
    def tracewindowposthread(self):
        lastpos = None
        tracepos = None
        tracehwnd = None

        def _castqp(rect):
            return QPoint(
                int(rect[0] / self.devicePixelRatioF()),
                int(rect[1] / self.devicePixelRatioF()),
            )

        while True:
            time.sleep(0.01)
            if self._move_drag:
                lastpos = None
                continue
            if not globalconfig["movefollow"]:
                lastpos = None
                continue
            if self.isdoingsomething():
                lastpos = None
                continue

            hwnd = gobject.baseobject.hwnd
            if not hwnd:
                continue
            if hwnd != tracehwnd:
                tracehwnd = hwnd
                lastpos = None
                continue
            rect = windows.GetWindowRect(hwnd)
            if not rect:
                lastpos = None
                continue
            rect = _castqp(rect)
            if not lastpos:
                lastpos = rect
                tracepos = self.pos()
                try:
                    gobject.baseobject.textsource.starttrace(rect)
                except:
                    pass
                continue

            if rect == QPoint(0, 0):
                continue
            try:
                gobject.baseobject.textsource.traceoffset(rect)
            except:
                pass
            self.move_signal.emit(tracepos - lastpos + rect)

    def showres(self, kwargs):  # name,color,res,onlytrans,iter_context):
        try:
            name = kwargs.get("name", "")
            color = kwargs.get("color")
            res = kwargs.get("res")
            onlytrans = kwargs.get("onlytrans", False)  # 仅翻译，不显示
            iter_context = kwargs.get("iter_context", (0, None))
            clear = kwargs.get("clear", False)

            iter_res_status, iter_context_class = iter_context
            if iter_res_status in (0, 2):  # iter结束
                gobject.baseobject.transhis.getnewtranssignal.emit(name, res)
                if iter_res_status == 2:
                    return

            if onlytrans:
                return
            if len(res) > globalconfig["maxoriginlength"]:
                _res = res[: globalconfig["maxoriginlength"]] + "……"
            else:
                _res = res

            if globalconfig["showfanyisource"]:
                _showtext = name + "  " + _res
            else:
                _showtext = _res
            self.showline(
                clear=clear,
                text=_showtext,
                color=color,
                origin=False,
                iter_context=iter_context,
            )

        except:
            print_exc()

    def showraw(self, kwargs):  # res,color,onlytrans):
        text = kwargs.get("text")
        color = kwargs.get("color")
        onlytrans = kwargs.get("onlytrans")

        clear = True
        if onlytrans:
            return
        if len(text) > globalconfig["maxoriginlength"]:
            _res = text[: globalconfig["maxoriginlength"]] + "……"
        else:
            _res = text
        if globalconfig["isshowrawtext"]:
            self.showline(clear=clear, text=_res, isshowrawtext=True, color=color)
        else:
            self.showline(clear=clear)

    def showstatus(self, res, color, clear, origin):
        self.showline(clear=clear, text=res, color=color, origin=origin)

    def cleartext(self, text):
        text = text.replace("\t", " ")
        text = text.replace("\r", "\n")
        lines = text.split("\n")
        newlines = []
        for line in lines:
            if len(line.strip()):
                newlines.append(line)
        return "\n".join(newlines)

    def showline(self, **kwargs):  # clear,res,color ,type_=1,origin=True):
        clear = kwargs.get("clear", True)
        origin = kwargs.get("origin", True)
        text = kwargs.get("text", None)
        color = kwargs.get("color", "black")
        isshowrawtext = kwargs.get("isshowrawtext", False)
        iter_context = kwargs.get("iter_context", None)

        if clear:
            self.translate_text.clear()
        if text is None:
            return
        text = self.cleartext(text)

        atcenter = globalconfig["showatcenter"]

        if iter_context:
            _, iter_context_class = iter_context
            self.translate_text.iter_append(
                iter_context_class, origin, atcenter, text, color
            )
        else:
            hira = []
            isshowhira = isshow_fenci = isfenciclick = False
            if isshowrawtext:
                isshowhira = globalconfig["isshowhira"]
                isshow_fenci = globalconfig["show_fenci"]
                isfenciclick = (
                    globalconfig["usesearchword"] or globalconfig["usecopyword"]
                )
                needhira = isshow_fenci or isshowhira or isfenciclick
                if needhira:
                    hira = gobject.baseobject.parsehira(text)

            self.translate_text.append(
                origin,
                atcenter,
                text,
                hira,
                (isshowhira, isshow_fenci, isfenciclick),
                color,
            )
        if globalconfig["autodisappear"]:
            flag = (globalconfig["showintab"] and self.isMinimized()) or (
                not globalconfig["showintab"] and self.isHidden()
            )

            if flag:
                self.show_()
            self.lastrefreshtime = time.time()
            self.autohidestart = True

    @threader
    def autohidedelaythread(self):
        while True:
            if globalconfig["autodisappear"] and self.autohidestart:
                tnow = time.time()
                if tnow - self.lastrefreshtime >= globalconfig["disappear_delay"]:
                    self.hidesignal.emit()
                    self.autohidestart = False
                    self.lastrefreshtime = tnow

            time.sleep(0.5)

    def showhideui(self):
        if self._move_drag:
            return

        flag = (globalconfig["showintab"] and self.isMinimized()) or (
            not globalconfig["showintab"] and self.isHidden()
        )

        if flag:
            self.show_()
        else:
            self.hide_()

    def refreshtoolicon(self):
        self.titlebar.setFixedHeight(int(globalconfig["buttonsize"] * 1.5))
        self.titlebar.adjustminwidth()
        self.titlebar.refreshtoolicon()
        self.setMinimumHeight(self.titlebar.height() * 2)
        self.set_color_transparency()
        self.seteffect()
        self.changeextendstated()

    @threader
    def ocr_do_function(self, rect):
        if not rect:
            return
        img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
        text, infotype = ocr_run(img)
        if infotype:
            gobject.baseobject.displayinfomessage(text, infotype)
        else:
            gobject.baseobject.textgetmethod(text, False)

    def ocr_once_function(self):
        def ocroncefunction(rect):
            self.ocr_once_follow_rect = rect
            self.ocr_do_function(rect)

        rangeselct_function(ocroncefunction, False, False)

    @threader
    def simulate_key_enter(self):
        windows.SetForegroundWindow(gobject.baseobject.hwnd)
        time.sleep(0.1)
        while windows.GetForegroundWindow() == gobject.baseobject.hwnd:
            time.sleep(0.001)
            windows.keybd_event(13, 0, 0, 0)
        windows.keybd_event(13, 0, windows.KEYEVENTF_KEYUP, 0)

    def btnsetontopfunction(self):
        try:

            gobject.baseobject.settin_ui.keepontopbutton.clicksignal.emit()
        except:
            globalconfig["keepontop"] = not globalconfig["keepontop"]

            self.refreshtoolicon()
            self.setontopthread()

    def addbuttons(self):
        def simulate_key_ctrl():
            windows.SetForegroundWindow(gobject.baseobject.hwnd)
            time.sleep(0.1)
            windows.keybd_event(17, 0, 0, 0)
            while windows.GetForegroundWindow() == gobject.baseobject.hwnd:
                time.sleep(0.001)
            windows.keybd_event(17, 0, windows.KEYEVENTF_KEYUP, 0)

        functions = (
            ("move", None),
            ("retrans", self.startTranslater),
            (
                "automodebutton",
                self.changeTranslateMode,
                lambda: globalconfig["autorun"],
                lambda: globalconfig["autorun"],
            ),
            ("setting", lambda: gobject.baseobject.settin_ui.showsignal.emit()),
            (
                "copy",
                lambda: winsharedutils.clipboard_set(gobject.baseobject.currenttext),
            ),
            ("edit", gobject.baseobject.createedittextui),
            ("edittrans", lambda: edittrans(gobject.baseobject.commonstylebase)),
            (
                "showraw",
                self.changeshowhideraw,
                lambda: globalconfig["isshowrawtext"],
                lambda: globalconfig["isshowrawtext"],
            ),
            (
                "showtrans",
                self.changeshowhidetrans,
                lambda: globalconfig["showfanyi"],
                lambda: globalconfig["showfanyi"],
            ),
            ("history", lambda: gobject.baseobject.transhis.showsignal.emit()),
            (
                "noundict",
                lambda: loadpostsettingwindowmethod("noundict")(
                    gobject.baseobject.commonstylebase
                ),
            ),
            (
                "noundict_2",
                lambda: loadpostsettingwindowmethod_maybe(
                    "noundict", gobject.baseobject.commonstylebase
                ),
            ),
            (
                "noundict_direct",
                lambda: loadpostsettingwindowmethod_maybe(
                    "vndbnamemap", gobject.baseobject.commonstylebase
                ),
            ),
            (
                "noundict_sakura",
                lambda: loadpostsettingwindowmethod_maybe(
                    "gptpromptdict", gobject.baseobject.commonstylebase
                ),
            ),
            (
                "fix",
                lambda: loadpostsettingwindowmethod("transerrorfix")(
                    gobject.baseobject.commonstylebase
                ),
            ),
            (
                "fix_2",
                lambda: loadpostsettingwindowmethod_maybe(
                    "transerrorfix", gobject.baseobject.commonstylebase
                ),
            ),
            ("langdu", lambda: gobject.baseobject.readcurrent(force=True)),
            (
                "mousetransbutton",
                lambda: self.changemousetransparentstate(0),
                None,
                lambda: globalconfig["mousetransparent"],
            ),
            (
                "backtransbutton",
                lambda: self.changemousetransparentstate(1),
                None,
                lambda: globalconfig["backtransparent"],
            ),
            (
                "locktoolsbutton",
                self.changetoolslockstate,
                lambda: globalconfig["locktools"],
                lambda: globalconfig["locktools"],
            ),
            (
                "gamepad_new",
                lambda: dialog_savedgame_integrated(gobject.baseobject.commonstylebase),
            ),
            (
                "selectgame",
                lambda: gobject.baseobject.createattachprocess(),
            ),
            (
                "selecttext",
                lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
            ),
            ("selectocrrange", lambda: self.clickRange(False)),
            ("hideocrrange", self.showhideocrrange, None, lambda: self.showhidestate),
            (
                "bindwindow",
                self.bindcropwindow_signal.emit,
                None,
                lambda: self.isbindedwindow,
            ),
            ("searchwordW", lambda: gobject.baseobject.searchwordW.showsignal.emit()),
            ("fullscreen", self._fullsgame, lambda: self.isletgamefullscreened, None),
            ("grabwindow", grabwindow),
            (
                "muteprocess",
                self.muteprocessfuntion,
                lambda: self.processismuteed,
                None,
            ),
            (
                "memory",
                lambda: dialog_memory(gobject.baseobject.commonstylebase),
            ),
            (
                "keepontop",
                self.btnsetontopfunction,
                None,
                lambda: globalconfig["keepontop"],
            ),
            (
                "simulate_key_ctrl",
                lambda: threading.Thread(target=simulate_key_ctrl).start(),
            ),
            (
                "simulate_key_enter",
                self.simulate_key_enter,
            ),
            (
                "copy_once",
                lambda: gobject.baseobject.textgetmethod(
                    winsharedutils.clipboard_get(), False
                ),
            ),
            (
                "open_relative_link",
                lambda: browserdialog(
                    gobject.baseobject.commonstylebase,
                    trypass(lambda: gobject.baseobject.gameuid)(),
                ),
            ),
            (
                "open_game_setting",
                lambda: dialog_setting_game(
                    gobject.baseobject.commonstylebase, gobject.baseobject.gameuid, 1
                ),
            ),
            ("ocr_once", self.ocr_once_signal.emit),
            (
                "ocr_once_follow",
                lambda: self.ocr_do_function(self.ocr_once_follow_rect),
            ),
            ("minmize", self.hide_),
            ("quit", self.close),
            (
                "selectable",
                self.setselectable,
                None,
                lambda: globalconfig["selectable"],
            ),
        )

        _type = {"quit": 2}

        for __ in functions:
            if len(__) == 2:
                btn, func = __
                iconstate = colorstate = None
            elif len(__) == 4:
                btn, func, iconstate, colorstate = __
            else:
                raise
            belong = (
                globalconfig["toolbutton"]["buttons"][btn]["belong"]
                if "belong" in globalconfig["toolbutton"]["buttons"][btn]
                else None
            )
            tp = _type[btn] if btn in _type else 1
            self.titlebar.takusanbuttons(
                tp,
                func,
                globalconfig["toolbutton"]["buttons"][btn]["tip"],
                btn,
                belong,
                iconstate,
                colorstate,
            )

    @property
    def winid(self):
        return int(self.winId())

    def changeextendstated(self):
        dh = self.dynamicextraheight()
        self.translate_text.move(0, dh)
        height = self.height() - dh
        self.translate_text.resize(self.width(), int(height))

    def hide_(self):
        if globalconfig["showintab"]:
            windows.ShowWindow(self.winid, windows.SW_SHOWMINIMIZED)
        else:
            self.hide()

    def show_(self):
        if globalconfig["showintab"]:
            windows.ShowWindow(self.winid, windows.SW_SHOWNOACTIVATE)
        else:
            self.show()
            windows.SetForegroundWindow(self.winid)
        gobject.baseobject.commonstylebase.hide()

    def aftershowdosomething(self):

        windows.SetForegroundWindow(self.winid)
        self.refreshtoolicon()
        self.setontopthread()

    def canceltop(self):
        if self.istopmost():
            windows.SetWindowPos(
                self.winid,
                windows.HWND_NOTOPMOST,
                0,
                0,
                0,
                0,
                windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
            )

    def istopmost(self):
        return bool(
            windows.GetWindowLong(self.winid, windows.GWL_EXSTYLE)
            & windows.WS_EX_TOPMOST
        )

    def settop(self):
        windows.SetWindowPos(
            self.winid,
            windows.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
        )

    @threader
    def setontopthread(self):

        with self.setontopthread_lock:
            if not globalconfig["keepontop"]:
                return self.canceltop()
            self.settop()
            while globalconfig["keepontop"]:

                try:
                    hwnd = windows.GetForegroundWindow()
                    pid = windows.GetWindowThreadProcessId(hwnd)
                    if pid == os.getpid():
                        pass
                    elif globalconfig["focusnotop"] and self.thistimenotsetop:
                        pass
                    else:
                        self.settop()
                except:
                    print_exc()
                time.sleep(0.5)

    def seteffect(self):
        if globalconfig["WindowEffect"] == 0:
            winsharedutils.clearEffect(self.winid)
        elif globalconfig["WindowEffect"] == 1:
            winsharedutils.setAcrylicEffect(
                self.winid, globalconfig["WindowEffect_shadow"]
            )
        elif globalconfig["WindowEffect"] == 2:
            winsharedutils.setAeroEffect(
                self.winid, globalconfig["WindowEffect_shadow"]
            )

    def initvalues(self):
        self.enter_sig = 0
        self.fullscreenmanager_busy = False
        self.isletgamefullscreened = False
        self.fullscreenmanager = None
        self.fullscreenmethod = None
        self.showhidestate = False
        self.autohidestart = False
        self.processismuteed = False
        self.thistimenotsetop = False
        self.isbindedwindow = False
        self.setontopthread_lock = threading.Lock()
        self.ocr_once_follow_rect = None

    def displayglobaltooltip_f(self, string):
        QToolTip.showText(QCursor.pos(), string, self)

    def displaymessagebox_f(self, string1, string2):
        getQMessageBox(self, string1, string2)

    def displaylink_f(self, link):
        class linkviewer(LDialog):
            def __init__(_self, _link) -> None:
                super().__init__(self)
                _self.setWindowTitle("打开链接")
                l = QLabel(makehtml(_link, show=_link))
                l.setOpenExternalLinks(True)
                la = QHBoxLayout()
                _self.setLayout(la)
                la.addWidget(l)
                _self.exec()

        linkviewer(link)

    def initsignals(self):
        self.hidesignal.connect(self.hide_)
        self.displaylink.connect(self.displaylink_f)
        self.displayglobaltooltip.connect(self.displayglobaltooltip_f)
        self.displaymessagebox.connect(self.displaymessagebox_f)
        self.ocr_once_signal.connect(self.ocr_once_function)
        self.displaystatus.connect(self.showstatus)
        self.showhideuisignal.connect(self.showhideui)
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)
        self.refreshtooliconsignal.connect(self.refreshtoolicon)
        self.showsavegame_signal.connect(
            lambda: dialog_savedgame_integrated(gobject.baseobject.commonstylebase)
        )
        self.clickRange_signal.connect(self.clickRange)
        self.showhide_signal.connect(self.showhideocrrange)
        self.bindcropwindow_signal.connect(
            functools.partial(mouseselectwindow, self.bindcropwindowcallback)
        )
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame)

        self.muteprocessignal.connect(self.muteprocessfuntion)
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        self.resizesignal.connect(self.resize)
        self.move_signal.connect(self.move)
        self.closesignal.connect(self.close)

    def __init__(self):

        super(TranslatorWindow, self).__init__(
            None,
            flags=Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinimizeButtonHint,
            poslist=globalconfig["transuigeo"],
        )  # 设置为顶级窗口，无边框
        icon = getExeIcon(getcurrexe())  #'./LunaTranslator.exe')# QIcon()
        # icon.addPixmap(QPixmap('./files/luna.png'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.firstshow = True
        if globalconfig["keepontop"]:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowTitle("LunaTranslator")
        self.initvalues()
        self.initsignals()
        self.titlebar = ButtonBar(self)
        self.titlebar.setFixedHeight(int(globalconfig["buttonsize"] * 1.5))
        self.titlebar.setObjectName("titlebar")
        self.titlebar.setMouseTracking(True)
        self.addbuttons()
        self.translate_text = Textbrowser(self)
        self.translate_text.contentsChanged.connect(self.textAreaChanged)
        self.translate_text.textbrowser.setselectable(globalconfig["selectable"])
        self.titlebar.raise_()
        t = QTimer(self)
        t.setInterval(33)
        self._isentered = False
        t.timeout.connect(self.__betterenterevent)
        t.start()
        self.adjustbuttons = self.titlebar.adjustbuttons

    def showEvent(self, e):
        if not self.firstshow:
            self.enterfunction()
            return
        self.firstshow = False
        self.mousetransparent_check()
        self.adjustbuttons()
        # 有个莫名其妙的加载时间
        self.enterfunction(2 + globalconfig["disappear_delay_tool"])
        self.autohidedelaythread()
        self.tracewindowposthread()
        today = time.strftime("%Y-%m-%d", time.localtime())
        if globalconfig.get("lastvisday", None) != today:
            globalconfig["lastvisday"] = today
            self.__showlinks()

    def __showsupport(self, _):
        dia = QDialog(self, Qt.WindowType.WindowCloseButtonHint)
        dia.setWindowTitle("支持作者")
        vbox = QVBoxLayout()
        dia.setLayout(vbox)
        vbox.addWidget(QLabel("如果你感觉该软件对你有帮助，欢迎微信扫码赞助，谢谢~"))
        _view = pixmapviewer(self)
        _view.showpixmap(QPixmap.fromImage(QImage("./files/zan.jpg")))
        _view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        dia.resize(400, 400)
        vbox.addWidget(_view)
        dia.exec()

    def __showlinks(self):
        __text = (
            _TR("欢迎使用")
            + " LunaTranslator\nGithub "
            + _TR("官方网站")
            + " "
            + _TR("使用说明")
            + "\n"
        )
        __tags = [
            {
                "orig": _TR("欢迎使用") + " LunaTranslator",
                "hira": "",
            },
            {"orig": "\n", "hira": "\n"},
            {
                "orig": "Github",
                "hira": "1",
                "clickfunction": lambda s: gobject.baseobject.openlink(
                    "https://github.com/HIllya51/LunaTranslator"
                ),
            },
            {"orig": " ", "hira": ""},
            {
                "orig": _TR("官方网站"),
                "hira": "1",
                "clickfunction": lambda s: gobject.baseobject.openlink(
                    dynamiclink("{main_server}/")
                ),
            },
            {"orig": " ", "hira": ""},
            {
                "orig": _TR("使用说明"),
                "hira": "1",
                "clickfunction": lambda s: gobject.baseobject.openlink(
                    dynamiclink("{docs_server}/")
                ),
            },
            {"orig": "\n", "hira": ""},
        ]
        if getlanguse() == "zh":
            __text += "支持作者 QQ群 Bilibili"
            __tags += [
                {
                    "orig": "支持作者",
                    "hira": "1",
                    "clickfunction": self.__showsupport,
                },
                {"orig": " ", "hira": ""},
                {
                    "orig": "QQ群",
                    "hira": "1",
                    "clickfunction": lambda s: gobject.baseobject.openlink(
                        dynamiclink("{main_server}/Resource/QQGroup")
                    ),
                },
                {"orig": " ", "hira": ""},
                {
                    "orig": "Bilibili",
                    "hira": "1",
                    "clickfunction": lambda s: gobject.baseobject.openlink(
                        dynamiclink("{main_server}/Resource/Bilibili")
                    ),
                },
            ]
        else:
            __text += "Discord Patreon"
            __tags += [
                {
                    "orig": "Discord",
                    "hira": "1",
                    "clickfunction": lambda s: gobject.baseobject.openlink(
                        dynamiclink("{main_server}/Resource/DiscordGroup")
                    ),
                },
                {"orig": " ", "hira": ""},
                {
                    "orig": "Patreon",
                    "hira": "1",
                    "clickfunction": lambda s: gobject.baseobject.openlink(
                        "https://www.patreon.com/hillya51"
                    ),
                },
            ]
        self.translate_text.append(
            True,
            globalconfig["showatcenter"],
            __text,
            __tags,
            (False, True, True),
            "black",
        )

    def setselectable(self):

        try:
            gobject.baseobject.settin_ui.selectable_btn.clicksignal.emit()
        except:
            globalconfig["selectable"] = not globalconfig["selectable"]
            self.translate_text.textbrowser.setselectable(globalconfig["selectable"])
            self.refreshtoolicon()

    def createborderradiusstring(self, r, merge, top=False):
        if merge:
            if top:
                return """
                border-top-left-radius: %spx;
                border-top-right-radius: %spx;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
                """ % (
                    r,
                    r,
                )
            else:
                return """
                border-bottom-left-radius: %spx;
                border-bottom-right-radius: %spx;
                border-top-left-radius: 0;
                border-top-right-radius: 0;
                """ % (
                    r,
                    r,
                )
        else:
            return "border-radius:%spx" % r

    def set_color_transparency(self):
        rate = int(globalconfig["WindowEffect"] == 0)
        use_r1 = min(
            self.translate_text.height() // 2,
            self.translate_text.width() // 2,
            globalconfig["yuanjiao_r"],
        )
        use_r2 = min(
            self.titlebar.height() // 2,
            self.titlebar.width() // 2,
            globalconfig["yuanjiao_r"],
        )
        topr = self.createborderradiusstring(
            rate * use_r1,
            (globalconfig["WindowEffect"] == 0 or globalconfig["locktools"])
            and self.titlebar.isVisible(),
            False,
        )
        bottomr3 = self.createborderradiusstring(use_r2, False)
        bottomr = self.createborderradiusstring(rate * use_r2, True, True)

        self.translate_text.setStyleSheet(
            "Textbrowser{border-width: 0;%s;background-color: %s}"
            % (
                topr,
                str2rgba(
                    globalconfig["backcolor"],
                    max(100 / 255, globalconfig["transparent"])
                    * (not globalconfig["backtransparent"]),
                ),
            )
        )
        self.titlebar.setstyle(bottomr, bottomr3)

    def muteprocessfuntion(self):
        pid = windows.GetWindowThreadProcessId(gobject.baseobject.hwnd)
        if not pid:
            return
        self.processismuteed = not self.processismuteed
        self.refreshtoolicon()
        winsharedutils.SetProcessMute(pid, self.processismuteed)

    def _externalfsend(self, current):
        self.isletgamefullscreened = current
        self.refreshtooliconsignal.emit()

    @threader
    def _fullsgame(self):
        if self.fullscreenmanager_busy:
            return
        self.fullscreenmanager_busy = True
        try:
            if gobject.baseobject.hwnd:
                _hwnd = gobject.baseobject.hwnd
            else:
                _hwnd = windows.GetForegroundWindow()
                _pid = windows.GetWindowThreadProcessId(_hwnd)
                if _pid == os.getpid():
                    return
            # self.isletgamefullscreened = not self.isletgamefullscreened
            # self.refreshtoolicon()
            skip = False
            if (self.fullscreenmanager is None) or (
                self.fullscreenmethod != globalconfig["fullscreenmethod_4"]
            ):

                self.fullscreenmethod = globalconfig["fullscreenmethod_4"]

                if self.fullscreenmanager:
                    skip = self.fullscreenmanager.endX()
                self.fullscreenmanager = importlib.import_module(
                    "scalemethod."
                    + static_data["scalemethods"][globalconfig["fullscreenmethod_4"]]
                ).Method(self._externalfsend)
            if skip:
                return
            self.fullscreenmanager.callstatuschange(
                _hwnd
            )  # , self.isletgamefullscreened)
        except:
            print_exc()
        self.fullscreenmanager_busy = False

    @property
    def mousetranscheckrect(self):
        btn: QWidget = self.titlebar.buttons["mousetransbutton"]
        usegeo = btn.geometry()
        usegeo = QRect(
            usegeo.x() - usegeo.width(),
            usegeo.y(),
            usegeo.width() * 3,
            usegeo.height(),
        )
        usegeo = usegeo.intersected(self.rect())
        return usegeo

    @threader
    def mousetransparent_check(self):
        hwnd = int(self.winid)
        while globalconfig["mousetransparent"]:
            cursor_pos = self.mapFromGlobal(QCursor.pos())
            usegeo = self.titlebar.geometry()
            btn: QWidget = self.titlebar.buttons["mousetransbutton"]
            if (not btn.isVisible()) and (btn.reflayout is not None):
                usegeo = self.mousetranscheckrect
            if usegeo.contains(cursor_pos):

                windows.SetWindowLong(
                    hwnd,
                    windows.GWL_EXSTYLE,
                    windows.GetWindowLong(hwnd, windows.GWL_EXSTYLE)
                    & ~windows.WS_EX_TRANSPARENT,
                )
            else:
                windows.SetWindowLong(
                    hwnd,
                    windows.GWL_EXSTYLE,
                    windows.GetWindowLong(hwnd, windows.GWL_EXSTYLE)
                    | windows.WS_EX_TRANSPARENT,
                )
            time.sleep(0.1)
        # 结束时取消穿透(可能以快捷键终止)
        windows.SetWindowLong(
            hwnd,
            windows.GWL_EXSTYLE,
            windows.GetWindowLong(hwnd, windows.GWL_EXSTYLE)
            & ~windows.WS_EX_TRANSPARENT,
        )

    def changemousetransparentstate(self, idx):
        if idx == 0:

            try:
                gobject.baseobject.settin_ui.mousetransbutton.clicksignal.emit()
            except:
                globalconfig["mousetransparent"] = not globalconfig["mousetransparent"]
                self.mousetransparent_check()
        elif idx == 1:
            globalconfig["backtransparent"] = not globalconfig["backtransparent"]
            self.set_color_transparency()
        self.refreshtoolicon()

    def showhideocrrange(self):
        try:
            self.showhidestate = not self.showhidestate
            self.refreshtoolicon()
            gobject.baseobject.textsource.showhiderangeui(self.showhidestate)
        except:
            pass

    def bindcropwindowcallback(self, pid, hwnd):
        _pid = os.getpid()
        gobject.baseobject.hwnd = hwnd if pid != _pid else None

    def changeshowhideraw(self):
        try:
            gobject.baseobject.settin_ui.show_original_switch.clicksignal.emit()
        except:
            globalconfig["isshowrawtext"] = not globalconfig["isshowrawtext"]
            self.refreshtoolicon()

    def changeshowhidetrans(self):
        try:
            gobject.baseobject.settin_ui.show_fany_switch.clicksignal.emit()
        except:
            globalconfig["showfanyi"] = not globalconfig["showfanyi"]
            self.refreshtoolicon()

    def changeTranslateMode(self):
        globalconfig["autorun"] = not globalconfig["autorun"]
        self.refreshtoolicon()

    def changetoolslockstate(self):
        try:
            gobject.baseobject.settin_ui.locktoolsbutton.clicksignal.emit()
        except:
            globalconfig["locktools"] = not globalconfig["locktools"]
            self.refreshtoolicon()

    def dynamicextraheight(self):
        if globalconfig["WindowEffect"] == 0:

            return self.titlebar.height()
        if globalconfig["locktools"]:
            return self.titlebar.height()

        return 0

    def textAreaChanged(self, size: QSize):

        if self.translate_text.cleared:
            return
        if not globalconfig["adaptive_height"]:
            return
        limit = min(size.height(), self.screen().geometry().height())
        newHeight = limit + self.dynamicextraheight()
        size = QSize(self.width(), newHeight)
        self.autoresizesig = uuid.uuid4()
        if newHeight > self.height():
            self.resize(size)
        else:
            self.delaymaybeshrink(size, self.autoresizesig)

    @threader
    def delaymaybeshrink(self, size: QSize, sig):

        time.sleep(0.1)
        if sig != self.autoresizesig:
            return
        self.resizesignal.emit(size)

    def clickRange(self, auto):
        if globalconfig["sourcestatus2"]["ocr"]["use"] == False:
            return
        self.showhidestate = False

        rangeselct_function(self.afterrange, auto, auto)

    @tryprint
    def afterrange(self, rect):
        gobject.baseobject.textsource.newrangeadjustor()
        gobject.baseobject.textsource.setrect(rect)
        self.showhideocrrange()
        if globalconfig["showrangeafterrangeselect"] == False:
            self.showhideocrrange()
        if globalconfig["ocrafterrangeselect"]:
            self.startTranslater()

    def startTranslater(self):
        if gobject.baseobject.textsource:
            threading.Thread(target=gobject.baseobject.textsource.runonce).start()

    def toolbarhidedelay(self):

        self.titlebar.hide()
        self.set_color_transparency()

    def checkisentered(self):
        hwnd = windows.GetForegroundWindow()
        hwndpid = windows.GetWindowThreadProcessId(hwnd)
        ismyprocbutnotmainuiforeground = hwndpid == os.getpid() and hwnd != self.winid
        onlychecktitle = (
            globalconfig["mousetransparent"] or ismyprocbutnotmainuiforeground
        )
        if onlychecktitle:
            usegeo = self.titlebar.geometry()
            btn: QWidget = self.titlebar.buttons["mousetransbutton"]
            if (
                globalconfig["mousetransparent"]
                and (not btn.isVisible())
                and (btn.reflayout is not None)
            ):
                usegeo = self.mousetranscheckrect
            return usegeo.contains(self.mapFromGlobal(QCursor.pos()))
        else:
            return self.geometry().contains(QCursor.pos())

    def __betterenterevent(self):
        if self._isentered:
            return
        if not self.checkisentered():
            return
        self._isentered = True
        self.enterfunction()

    @threader
    def dodelayhide(self, delay):
        enter_sig = uuid.uuid4()
        self.enter_sig = enter_sig
        while self.checkisentered():
            time.sleep(0.1)
        self._isentered = False

        if delay is None:
            delay = globalconfig["disappear_delay_tool"]
        time.sleep(delay)
        if self.enter_sig != enter_sig:
            return
        if globalconfig["locktools"]:
            return
        self.toolbarhidedelaysignal.emit()

    def enterfunction(self, delay=None):
        self.titlebar.show()
        self.set_color_transparency()

        self.dodelayhide(delay)

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        wh = self.dynamicextraheight()
        height = self.height() - wh

        self.translate_text.resize(self.width(), int(height))
        if e.oldSize().width() != e.size().width():
            self.titlebar.setFixedWidth(self.width())

    def tryremoveuseless(self):
        try:
            allisremoved = True
            tmpbase = gobject.gettempdir_1()
            for f in os.listdir(tmpbase):
                try:
                    pid = int(f)
                except:
                    continue
                if (pid != os.getpid()) and (winsharedutils.pid_running(pid)):
                    allisremoved = False
                    continue

                try:
                    shutil.rmtree(os.path.join(tmpbase, f))
                except:
                    pass
            if allisremoved:
                try:
                    shutil.rmtree(tmpbase)
                except:
                    pass
            try:
                os.remove("./cache/Updater.exe")
            except:
                pass
        except:
            pass

    def closeEvent(self, a0) -> None:
        try:
            if self.fullscreenmanager:
                self.fullscreenmanager.endX()
            gobject.baseobject.isrunning = False
            self.hide()

            gobject.baseobject.textsource = None
            endsubprocs()
            gobject.baseobject.destroytray()
            handle = windows.CreateMutex(False, "LUNASAVECONFIGUPDATE")
            if windows.GetLastError() != windows.ERROR_ALREADY_EXISTS:
                saveallconfig()
                self.tryremoveuseless()
                doupdate()
                windows.CloseHandle(handle)
            os._exit(0)

        except:
            print_exc()
