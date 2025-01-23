from qtsymbols import *
import time, functools, threading, os, importlib, shutil, uuid
from traceback import print_exc
import windows, qtawesome, gobject, winsharedutils
from myutils.wrapper import threader, tryprint
from myutils.config import (
    globalconfig,
    saveallconfig,
    static_data,
    savehook_new_data,
    savehook_new_list,
)
from gui.dialog_savedgame import dialog_setting_game
from myutils.ocrutil import ocr_run, imageCut
from myutils.utils import (
    loadpostsettingwindowmethod,
    makehtml,
    getlangsrc,
    loadpostsettingwindowmethod_maybe,
    find_or_create_uid,
)
from myutils.hwnd import (
    mouseselectwindow,
    grabwindow,
    getExeIcon,
    getcurrexe,
)
from gui.setting_about import doupdate
from gui.dialog_memory import dialog_memory
from gui.textbrowser import Textbrowser, TextType, SpecialColor, TranslateColor
from gui.rangeselect import rangeselct_function
from gui.usefulwidget import resizableframeless, getQMessageBox, findnearestscreen
from gui.edittext import edittrans
from gui.dialog_savedgame import dialog_savedgame_integrated
from gui.dialog_savedgame_setting import favorites, calculate_centered_rect
from gui.dialog_savedgame_common import startgame
from gui.dynalang import LDialog, LLabel


class IconLabelX(LLabel):
    clicked = pyqtSignal()
    rightclick = pyqtSignal()

    def __init__(self, *argc):
        super().__init__(*argc)
        self.reflayout = None
        self._icon = QIcon()
        self._size = QSize()
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    def showinlayout(self, layout: QHBoxLayout):

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

    def resizeEvent(self, e: QResizeEvent):
        h = int(e.size().height() / 1.5)
        self.setFixedWidth(int(self.height() * 2 / 1.5))
        self.setIconSize(QSize(h, h))

    def setIcon(self, icon: QIcon):
        self._icon = icon
        self.update()

    def setIconSize(self, size: QSize):
        self._size = size
        self.update()

    def paintEvent(self, a0: QPaintEvent) -> None:

        painter = QPainter(self)
        if self._size.isEmpty():
            return
        rect = QRect(
            (self.width() - self._size.width()) // 2,
            (self.height() - self._size.height()) // 2,
            self._size.width(),
            self._size.height(),
        )
        self._icon.paint(
            painter,
            rect,
            Qt.AlignmentFlag.AlignCenter,
            QIcon.Mode.Normal,
            QIcon.State.On,
        )

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if QObject.receivers(self, self.clicked) == 0:
            return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        if self.rect().contains(ev.pos()):
            if ev.button() == Qt.MouseButton.RightButton:
                self.rightclick.emit()
            elif ev.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()
        return super().mouseReleaseEvent(ev)


def str2rgba(string, alpha100):
    c = QColor(string)
    c.setAlphaF(alpha100 / 100)
    return c.name(QColor.NameFormat.HexArgb)


class ButtonBar(QFrame):
    def __init__(self, *argc):
        super().__init__(*argc)

        def __(p=None, pp=None):
            _ = QHBoxLayout(pp)
            _.setContentsMargins(0, 0, 0, 0)
            _.setSpacing(0)
            if p is not None:
                p.addLayout(_)
            return _

        self.threelayout = __(pp=self)
        self._left = __(self.threelayout)
        self.threelayout.addStretch()
        self._center = __(self.threelayout)
        self.threelayout.addStretch()
        self._right = __(self.threelayout)
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
        self,
        _type,
        clickfunc,
        rightclick,
        tips,
        name,
        belong=None,
        iconstate=None,
        colorstate=None,
    ):
        button = IconLabelX()

        def callwrap(call):
            try:
                call()
            except:
                print_exc()

        if clickfunc:
            button.clicked.connect(functools.partial(callwrap, clickfunc))
        if rightclick:
            button.rightclick.connect(functools.partial(callwrap, rightclick))
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
    displayraw1 = pyqtSignal(str)
    displaystatus = pyqtSignal(str, int)
    showhideuisignal = pyqtSignal()
    toolbarhidedelaysignal = pyqtSignal()
    showsavegame_signal = pyqtSignal()
    clickRange_signal = pyqtSignal()
    showhide_signal = pyqtSignal()
    clear_signal_1 = pyqtSignal()
    bindcropwindow_signal = pyqtSignal()
    fullsgame_signal = pyqtSignal()
    quitf_signal = pyqtSignal()
    refreshtooliconsignal = pyqtSignal()
    hidesignal = pyqtSignal()
    muteprocessignal = pyqtSignal()
    ocr_once_signal = pyqtSignal()
    move_signal = pyqtSignal(QPoint)
    closesignal = pyqtSignal()
    hotkeyuse_selectprocsignal = pyqtSignal()
    changeshowhiderawsig = pyqtSignal()
    changeshowhidetranssig = pyqtSignal()

    @threader
    def tracewindowposthread(self):
        lastpos = None
        tracepos = None
        tracehwnd = None

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
            if not winsharedutils.check_window_viewable(hwnd):
                lastpos = None
                continue
            rate = self.devicePixelRatioF()
            rect = QRect(
                int(rect[0] / rate),
                int(rect[1] / rate),
                int((rect[2] - rect[0]) / rate),
                int((rect[3] - rect[1]) / rate),
            )
            if not lastpos:
                lastpos = rect
                tracepos = self.pos()
                try:
                    gobject.baseobject.textsource.starttrace(rect.topLeft())
                except:
                    pass
                continue
            if (rect.topLeft() == QPoint(0, 0)) or (rect.size() != lastpos.size()):
                lastpos = rect
                continue
            try:
                gobject.baseobject.textsource.traceoffset(rect.topLeft())
            except:
                pass
            if windows.MonitorFromWindow(hwnd) != windows.MonitorFromWindow(self.winid):
                lastpos = None
                return
            if globalconfig["top_align"] == 0:
                self.move_signal.emit(tracepos - lastpos.topLeft() + rect.topLeft())

    def showres(self, kwargs):
        try:
            name = kwargs.get("name", "")
            color = kwargs.get("color")
            res = kwargs.get("res")
            iter_context = kwargs.get("iter_context", None)
            clear = kwargs.get("clear", False)

            self.showline(
                name=name,
                clear=clear,
                text=res,
                color=color,
                texttype=TextType.Translate,
                iter_context=iter_context,
            )

        except:
            print_exc()

    def showraw(self, text):
        color = SpecialColor.RawTextColor
        clear = True
        hira = []
        isshowhira = isshow_fenci = isfenciclick = False

        text = self.cleartext(text)
        isshowhira = globalconfig["isshowhira"]
        isshow_fenci = globalconfig["show_fenci"]
        isfenciclick = globalconfig["usesearchword"] or globalconfig["usecopyword"]
        needhira = isshow_fenci or isshowhira or isfenciclick
        if needhira:
            hira = gobject.baseobject.parsehira(text)

        self.showline(
            clear=clear,
            text=text,
            color=color,
            hira=hira,
        )

    def showstatus(self, res, t: TextType):
        if t == TextType.Info:
            color = SpecialColor.RawTextColor
            clear = True
        elif t == TextType.Error_origin:
            color = SpecialColor.ErrorColor
            clear = True
        elif t == TextType.Error_translator:
            color = SpecialColor.ErrorColor
            clear = False
        self.showline(clear=clear, text=res, color=color, texttype=t)

    def cleartext(self, text):
        text = text.replace("\t", " ")
        text = text.replace("\r", "\n")
        text = text.replace("\u2028", "\n")
        text = text.replace("\u2029", "\n")
        lines = text.split("\n")
        newlines = []
        for line in lines:
            if len(line.strip()):
                newlines.append(line)
        return "\n".join(newlines)

    def showline(self, **kwargs):  # clear,res,color ,type_=1,origin=True):
        name = kwargs.get("name", "")
        clear = kwargs.get("clear", True)
        texttype = kwargs.get("texttype", TextType.Origin)
        text = kwargs.get("text", None)
        color = kwargs.get("color", SpecialColor.DefaultColor)
        iter_context = kwargs.get("iter_context", None)
        hira = kwargs.get("hira", [])

        if clear:
            self.translate_text.clear()
        if text is None:
            return
        text = self.cleartext(text)
        if iter_context:
            iter_res_status, iter_context_class = iter_context
        else:
            iter_res_status = 0
        if iter_res_status:
            self.translate_text.iter_append(
                iter_context_class, texttype, name, text, color
            )
        else:
            self.translate_text.append(texttype, name, text, hira, color)
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
            time.sleep(0.5)
            # 当鼠标悬停，或前景窗口为当前进程的其他窗口时，禁止自动隐藏
            if self.geometry().contains(QCursor.pos()) or (
                windows.GetForegroundWindow() != self.winid
                and windows.GetWindowThreadProcessId(windows.GetForegroundWindow())
                == os.getpid()
            ):
                self.lastrefreshtime = time.time()
                continue
            if globalconfig["autodisappear"] and self.autohidestart:
                if (
                    time.time() - self.lastrefreshtime
                    >= globalconfig["disappear_delay"]
                ):
                    self.hidesignal.emit()
                    self.autohidestart = False

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
    def ocr_do_function(self, rect, img=None):
        if not rect:
            return
        if not img:
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
        text, infotype = ocr_run(img)
        if infotype:
            gobject.baseobject.displayinfomessage(text, infotype)
        else:
            gobject.baseobject.textgetmethod(text, False)

    def ocr_once_function(self):
        def ocroncefunction(rect, img=None):
            self.ocr_once_follow_rect = rect
            self.ocr_do_function(rect, img)

        rangeselct_function(ocroncefunction)

    @threader
    def simulate_key_enter(self):
        windows.SetForegroundWindow(gobject.baseobject.hwnd)
        time.sleep(0.1)
        while windows.GetForegroundWindow() == gobject.baseobject.hwnd:
            time.sleep(0.001)
            windows.keybd_event(windows.VK_RETURN, 0, 0, 0)
        windows.keybd_event(windows.VK_RETURN, 0, windows.KEYEVENTF_KEYUP, 0)

    def btnsetontopfunction(self):
        try:

            gobject.baseobject.settin_ui.keepontopbutton.clicksignal.emit()
        except:
            globalconfig["keepontop"] = not globalconfig["keepontop"]

            self.refreshtoolicon()
            self.setontopthread()

    def favoritesmenu(self):
        menu = QMenu(gobject.baseobject.commonstylebase)
        gameuid = gobject.baseobject.gameuid
        maps = {}
        if gameuid:
            for name, link in savehook_new_data[gameuid]["relationlinks"]:
                act = QAction(name, menu)
                maps[act] = link
                menu.addAction(act)
        if (
            globalconfig["relationlinks"]
            and gameuid
            and savehook_new_data[gameuid]["relationlinks"]
        ):
            menu.addSeparator()
        for name, link in globalconfig["relationlinks"]:
            act = QAction(name, menu)
            maps[act] = link
            menu.addAction(act)
        action = menu.exec(QCursor.pos())
        link = maps.get(action)
        if link:
            os.startfile(link)

    def addbuttons(self):
        def simulate_key_ctrl():
            windows.SetForegroundWindow(gobject.baseobject.hwnd)
            time.sleep(0.1)
            windows.keybd_event(windows.VK_CONTROL, 0, 0, 0)
            while windows.GetForegroundWindow() == gobject.baseobject.hwnd:
                time.sleep(0.001)
            windows.keybd_event(windows.VK_CONTROL, 0, windows.KEYEVENTF_KEYUP, 0)

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
            (
                "langdu",
                lambda: gobject.baseobject.readcurrent(force=True),
                None,
                None,
                lambda: gobject.baseobject.audioplayer.stop(),
            ),
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
            (
                "selectocrrange",
                self.clickRange,
                None,
                None,
                self.clickRangeclear,
            ),
            (
                "hideocrrange",
                self.showhideocrrange,
                None,
                lambda: self.showhidestate,
                self.clear_signal_1.emit,
            ),
            (
                "bindwindow",
                self.bindcropwindow_signal.emit,
                None,
                lambda: self.isbindedwindow,
            ),
            ("searchwordW", lambda: gobject.baseobject.searchwordW.showsignal.emit()),
            ("fullscreen", self._fullsgame, lambda: self.isletgamefullscreened, None),
            ("grabwindow", grabwindow, None, None, lambda: grabwindow(tocliponly=True)),
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
                None,
                None,
                lambda: gobject.baseobject.textgetmethod(
                    gobject.baseobject.currenttext
                    + (getlangsrc().space if gobject.baseobject.currenttext else "")
                    + winsharedutils.clipboard_get(),
                    False,
                ),
            ),
            (
                "game_ref_favorites",
                self.favoritesmenu,
                None,
                None,
                lambda: favorites(
                    gobject.baseobject.commonstylebase,
                    gobject.baseobject.gameuid,
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
            btn = func = iconstate = colorstate = rightclick = None
            if len(__) == 2:
                btn, func = __
            elif len(__) == 4:
                btn, func, iconstate, colorstate = __
            elif len(__) == 5:
                btn, func, iconstate, colorstate, rightclick = __
            belong = (
                globalconfig["toolbutton"]["buttons"][btn]["belong"]
                if "belong" in globalconfig["toolbutton"]["buttons"][btn]
                else None
            )
            tp = _type[btn] if btn in _type else 1
            self.titlebar.takusanbuttons(
                tp,
                func,
                rightclick,
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

        # 若窗口飞了，则将窗口拉回来
        usescreen, mindis = findnearestscreen(self.geometry())
        if mindis < 0:
            return
        self.setGeometry(calculate_centered_rect(usescreen.geometry(), self.size()))

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
                la = QHBoxLayout(_self)
                la.addWidget(l)
                _self.exec()

        linkviewer(link)

    def initsignals(self):
        self.hotkeyuse_selectprocsignal.connect(gobject.baseobject.createattachprocess)
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
        self.clear_signal_1.connect(
            lambda: self.clearstate() or gobject.baseobject.textsource.clearrange()
        )
        self.bindcropwindow_signal.connect(
            functools.partial(mouseselectwindow, self.bindcropwindowcallback)
        )
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame)

        self.muteprocessignal.connect(self.muteprocessfuntion)
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        self.move_signal.connect(self.move)
        self.closesignal.connect(self.close)
        self.changeshowhiderawsig.connect(self.changeshowhideraw)
        self.changeshowhidetranssig.connect(self.changeshowhidetrans)

    def __init__(self):
        flags = (
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint
        )
        if globalconfig["keepontop"]:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        super(TranslatorWindow, self).__init__(
            None,
            flags=flags,
            poslist=globalconfig["transuigeo"],
        )  # 设置为顶级窗口，无边框
        icon = getExeIcon(getcurrexe())  #'./LunaTranslator.exe')# QIcon()
        # icon.addPixmap(QPixmap('./files/luna.png'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.firstshow = True
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowTitle("LunaTranslator")
        self.initvalues()
        self.initsignals()
        self.titlebar = ButtonBar(self)
        self.titlebar.move(0, 0)  # 多显示屏下，谜之错位
        self.titlebar.setFixedHeight(int(globalconfig["buttonsize"] * 1.5))
        self.titlebar.setObjectName("titlebar")
        self.titlebar.setMouseTracking(True)
        self.addbuttons()
        self.smooth_resizer = QVariantAnimation(self)
        self.smooth_resizer.setDuration(500)
        self.smooth_resizer.valueChanged.connect(self.smooth_resizing)
        self.smooth_resizer2 = QVariantAnimation(self)
        self.smooth_resizer2.setDuration(500)
        self.smooth_resizer2.valueChanged.connect(self.smooth_resizing2)
        self.left_bottom_corner = self.geometry().bottomLeft()
        self.translate_text = Textbrowser(self)
        self.translate_text.move(0, 0)
        self.translate_text.dropfilecallback.connect(self.dropfilecallback)
        self.translate_text.contentsChanged.connect(self.textAreaChanged)
        self.translate_text.setselectable(globalconfig["selectable"])
        self.titlebar.raise_()
        t = QTimer(self)
        t.setInterval(25)
        self._isentered = False
        t.timeout.connect(self.__betterenterevent)
        t.start()
        self.adjustbuttons = self.titlebar.adjustbuttons

    def dropfilecallback(self, file: str):
        if not (file.lower().endswith(".exe") or file.lower().endswith(".lnk")):
            return
        uid = find_or_create_uid(savehook_new_list, file)
        if uid not in savehook_new_list:
            savehook_new_list.insert(0, uid)
        startgame(uid)

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

    def setselectable(self):

        try:
            gobject.baseobject.settin_ui.selectable_btn.clicksignal.emit()
        except:
            globalconfig["selectable"] = not globalconfig["selectable"]
            self.translate_text.setselectable(globalconfig["selectable"])
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
                    max(
                        (1 - globalconfig["transparent_EX"]) * 100 / 255,
                        globalconfig["transparent"]
                        * (not globalconfig["backtransparent"]),
                    ),
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
            try:
                gobject.baseobject.settin_ui.horizontal_slider.setEnabled(
                    not globalconfig["backtransparent"]
                )
                gobject.baseobject.settin_ui.horizontal_slider_label.setEnabled(
                    not globalconfig["backtransparent"]
                )
            except:
                pass
        self.refreshtoolicon()

    def showhideocrrange(self):
        try:
            self.showhidestate = not self.showhidestate
            self.refreshtoolicon()
            gobject.baseobject.textsource.showhiderangeui(self.showhidestate)
        except:
            pass

    def clearstate(self):
        try:
            self.showhidestate = False
            self.refreshtoolicon()
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
            self.translate_text.showhideorigin(globalconfig["isshowrawtext"])
            try:
                gobject.baseobject.settin_ui.fenyinsettings.setEnabled(
                    globalconfig["isshowrawtext"]
                )
            except:
                pass

    def changeshowhidetrans(self):
        try:
            gobject.baseobject.settin_ui.show_fany_switch.clicksignal.emit()
        except:
            globalconfig["showfanyi"] = not globalconfig["showfanyi"]
            self.refreshtoolicon()
            gobject.baseobject.maybeneedtranslateshowhidetranslate()

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

    def mouseReleaseEvent(self, e: QMouseEvent):
        super().mouseReleaseEvent(e)
        self.left_bottom_corner = self.geometry().bottomLeft()

    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        self.smooth_resizer.stop()
        self.smooth_resizer2.stop()
        self.left_bottom_corner = self.geometry().bottomLeft()

    def smooth_resizing(self, value):
        self.resize(QSize(self.width(), value))

    def smooth_resizing2(self, new_size: QSize):
        new_pos = self.left_bottom_corner - QPoint(0, new_size.height())
        self.setGeometry(new_pos.x(), new_pos.y(), new_size.width(), new_size.height())

    def textAreaChanged(self, size: QSize):

        if self.translate_text.cleared:
            return
        if not globalconfig["adaptive_height"]:
            return
        limit = min(size.height(), self.screen().geometry().height())
        newHeight = limit + self.dynamicextraheight()
        size = QSize(self.width(), newHeight)
        self.smooth_resizer.stop()
        self.smooth_resizer2.stop()
        if self.isdoingsomething():
            self.resize(size)
            return
        if globalconfig["top_align"] == 0:
            if newHeight > self.height():
                self.resize(size)
            else:
                self.smooth_resizer.setStartValue(self.height())
                self.smooth_resizer.setEndValue(newHeight)
                self.smooth_resizer.start()
        else:
            if newHeight > self.height():
                self.smooth_resizing2(size)
            else:
                self.smooth_resizer2.setStartValue(self.size())
                self.smooth_resizer2.setEndValue(size)
                self.smooth_resizer2.start()

    def clickRange(self):
        if globalconfig["sourcestatus2"]["ocr"]["use"] == False:
            return
        self.showhidestate = False

        rangeselct_function(functools.partial(self.afterrange, False), False)

    def clickRangeclear(self):
        if globalconfig["sourcestatus2"]["ocr"]["use"] == False:
            return
        self.showhidestate = False
        rangeselct_function(functools.partial(self.afterrange, True), False)

    @tryprint
    def afterrange(self, clear, rect, img=None):
        if clear or not globalconfig["multiregion"]:
            gobject.baseobject.textsource.clearrange()
        gobject.baseobject.textsource.newrangeadjustor()
        gobject.baseobject.textsource.setrect(rect)
        self.showhideocrrange()
        if globalconfig["showrangeafterrangeselect"] == False:
            self.showhideocrrange()
        if globalconfig["ocrafterrangeselect"]:
            self.startTranslater()
            if not globalconfig["keepontop"]:
                windows.SetForegroundWindow(self.winid)

    def startTranslater(self):
        if gobject.baseobject.textsource:
            threading.Thread(target=gobject.baseobject.textsource.runonce).start()

    def toolbarhidedelay(self):

        self.titlebar.hide()
        self.set_color_transparency()

    def checkisentered(self):
        usegeo = self.titlebar.geometry()
        btn: QWidget = self.titlebar.buttons["mousetransbutton"]
        if (
            globalconfig["mousetransparent"]
            and (not btn.isVisible())
            and (btn.reflayout is not None)
        ):
            usegeo = self.mousetranscheckrect
        return usegeo.contains(self.mapFromGlobal(QCursor.pos()))

    def __betterenterevent(self):
        if self._isentered:
            return
        if not self.checkisentered():
            return
        self._isentered = True
        self.enterfunction()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.dodelayhide(None)

    def enterEvent(self, e: QEvent):
        super().enterEvent(e)
        self.enterfunction(delay=-1)

    @threader
    def dodelayhide(self, delay):
        enter_sig = uuid.uuid4()
        self.enter_sig = enter_sig
        if delay == -1:
            return
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
