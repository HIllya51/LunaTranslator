from qtsymbols import *
import time, functools, threading, os, shutil, uuid
from traceback import print_exc
import windows, qtawesome, gobject, NativeUtils
from myutils.wrapper import threader, tryprint
from myutils.config import (
    globalconfig,
    saveallconfig,
    _TR,
    mayberelpath,
    savehook_new_data,
    savehook_new_list,
    translatorsetting,
)
from myutils.magpie_builtin import MagpieBuiltin, AdapterService
from gui.gamemanager.dialog import dialog_setting_game
from myutils.ocrutil import ocr_run, imageCut
from myutils.utils import (
    stringfyerror,
    loadpostsettingwindowmethod,
    makehtml,
    getlangsrc,
    loadpostsettingwindowmethod_maybe,
    find_or_create_uid,
)
from myutils.hwnd import mouseselectwindow, grabwindow, getExeIcon, getcurrexe
from gui.setting.about import doupdate
from gui.dialog_memory import dialog_memory
from gui.rendertext.texttype import TextType, SpecialColor
from gui.textbrowser import Textbrowser
from gui.rangeselect import rangeselct_function
from gui.usefulwidget import resizableframeless, findnearestscreen
from gui.edittext import edittrans
from gui.gamemanager.dialog import dialog_savedgame_integrated
from gui.gamemanager.setting import favorites, calculate_centered_rect
from gui.gamemanager.common import startgame
from gui.dynalang import LDialog, LLabel


class IconLabelX(LLabel):
    clicked = pyqtSignal()
    rightclick = pyqtSignal()
    middleclick = pyqtSignal()

    @staticmethod
    def w():
        return (
            globalconfig["buttonsize"]
            * gobject.Consts.toolwdivh
            * gobject.Consts.toolscale
        )

    @staticmethod
    def h():
        return globalconfig["buttonsize"] * gobject.Consts.toolscale

    def setSize(self):
        sz = (QSizeF(IconLabelX.w(), IconLabelX.h())).toSize()
        self.setFixedSize(sz)

    def __init__(self, *argc):
        super().__init__(*argc)
        self.reflayout = None
        self.belong = None
        self._icon = QIcon()
        self._size = QSize()
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    def showinlayout(self, layout: QBoxLayout):

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
        h = int(e.size().height() / gobject.Consts.toolscale)
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
            elif ev.button() == Qt.MouseButton.MiddleButton:
                self.middleclick.emit()
        return super().mouseReleaseEvent(ev)


def str2rgba(string, alpha100):
    c = QColor(string)
    c.setAlphaF(alpha100 / 100)
    return c.name(QColor.NameFormat.HexArgb)


class buttonfunctions:
    def __init__(
        self,
        clicked=None,
        rightclick=None,
        middleclick=None,
        iconstate=None,
        colorstate=None,
    ):
        (
            self.clicked,
            self.rightclick,
            self.middleclick,
            self.iconstate,
            self.colorstate,
        ) = (clicked, rightclick, middleclick, iconstate, colorstate)


class ButtonBar(QFrame):
    def setDirection(self, v):
        self.v = v
        direct = [QBoxLayout.Direction.LeftToRight, QBoxLayout.Direction.TopToBottom][v]
        self.threelayout.setDirection(direct)
        self._left.setDirection(direct)
        self._center.setDirection(direct)
        self._right.setDirection(direct)

    def __init__(self, *argc):
        super().__init__(*argc)
        self.v = False

        def __(p: QBoxLayout = None, pp=None):
            _ = QBoxLayout(QBoxLayout.Direction.LeftToRight, pp)
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

        style = """IconLabelX:focus {{outline: 0px;}}
            IconLabelX{{
                background-color: rgba(255, 255, 255, 0);
                border: 0px;{bottomr3};
            }}
            IconLabelX#IconLabelX2:hover{{
                background-color: {color0};
                border: 0px;{bottomr3};
            }}
            IconLabelX#IconLabelX1:hover{{
                background-color: {color1};
                border: 0px;{bottomr3};
            }}
            #titlebar{{border-width: 0;{bottomr};background-color: {color2}}}
        """.format(
            bottomr3=bottomr3,
            color1=globalconfig["button_color_normal"],
            color0="red",
            bottomr=bottomr,
            color2=str2rgba(
                globalconfig["backcolor_tool"], globalconfig["transparent_tool"]
            ),
        )
        self.setStyleSheet(style)

    def takusanbuttons(
        self,
        _type,
        clicked,
        rightclick,
        tips,
        name,
        belong=None,
        iconstate=None,
        colorstate=None,
        middleclick=None,
    ):
        button = IconLabelX()

        def callwrap(call):
            try:
                call()
            except:
                print_exc()

        if clicked:
            button.clicked.connect(functools.partial(callwrap, clicked))
        if rightclick:
            button.rightclick.connect(functools.partial(callwrap, rightclick))
        if middleclick:
            button.middleclick.connect(functools.partial(callwrap, middleclick))
        if tips:
            button.setToolTip(tips)
            button.setAccessibleName(tips)
        if _type not in self.stylebuttons:
            self.stylebuttons[_type] = []
        self.stylebuttons[_type].append(button)
        if clicked:
            button.setObjectName("IconLabelX{}".format(_type))
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
            button: IconLabelX = self.buttons[name]
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
            layout: QBoxLayout = __[
                globalconfig["toolbutton"]["buttons"][name]["align"]
            ]
            button.showinlayout(layout)
            cnt += 1
        self.cntbtn = cnt
        self.adjustminwidth()

    def adjustminwidth(self):
        p: QWidget = self.parent()
        if self.v:
            w = self.cntbtn * IconLabelX.h()
            p.setMinimumHeight(int(w))
            p.setMinimumWidth(self.width() * 2)
        else:
            w = self.cntbtn * IconLabelX.w()
            p.setMinimumWidth(int(w))
            p.setMinimumHeight(self.height() * 2)

    def setbuttonsize(self):

        if globalconfig["verticalhorizontal"]:
            self.setFixedWidth(int(IconLabelX.w()))
        else:
            self.setFixedHeight(int(IconLabelX.h()))
        for _ in self.buttons:
            btn: IconLabelX = self.buttons[_]
            btn.setSize()


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
    fullsgame_signal = pyqtSignal(bool)
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
    magpiecallback = pyqtSignal(bool)
    clipboardcallback = pyqtSignal(bool, str)
    internaltexthide = pyqtSignal(bool)

    def setbuttonsizeX(self):
        self.changeextendstated()
        if globalconfig["verticalhorizontal"]:
            self.titlebar.move(self.width() - self.titlebar.width(), 0)
        else:
            self.titlebar.move(0, 0)

    def verticalhorizontal(self, v):
        self.changeextendstated()
        self.titlebar.setDirection(v)
        self.translate_text.verticalhorizontal(v)
        if v:
            self.titlebar.setFixedHeight(self.height())
            self.titlebar.setFixedWidth(int(IconLabelX.w()))
            self.titlebar.move(self.width() - self.titlebar.width(), 0)
        else:
            self.titlebar.move(0, 0)
            self.titlebar.setFixedWidth(self.width())
            self.titlebar.setFixedHeight(int(IconLabelX.h()))
        self.titlebar.adjustminwidth()
        self.enterfunction()

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
            if not NativeUtils.IsWindowViewable(hwnd):
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
            klass = kwargs.get("klass", None)
            self.showline(
                name=name,
                clear=clear,
                text=res,
                color=color,
                texttype=TextType.Translate,
                iter_context=iter_context,
                klass=klass,
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

    def cleartext(self, text: str):
        text = text.replace("\t", " ")
        lines = text.splitlines()
        newlines = [line for line in lines if line.strip()]
        return "\n".join(newlines)

    def showline(self, **kwargs):  # clear,res,color ,type_=1,origin=True):
        name = kwargs.get("name", "")
        clear = kwargs.get("clear", True)
        texttype = kwargs.get("texttype", TextType.Origin)
        text = kwargs.get("text", None)
        color = kwargs.get("color", SpecialColor.DefaultColor)
        iter_context = kwargs.get("iter_context", None)
        hira = kwargs.get("hira", [])
        klass = kwargs.get("klass", None)
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
                iter_context_class, texttype, name, text, color, klass
            )
        else:
            self.translate_text.append(texttype, name, text, hira, color, klass)
        if globalconfig["autodisappear"]:
            self.lastrefreshtime = time.time()
            self.autohidestart = True
            if globalconfig["autodisappear_which"] == 0:
                flag = (globalconfig["showintab"] and self.isMinimized()) or (
                    not globalconfig["showintab"] and self.isHidden()
                )
                if flag:
                    self.show_()
            elif globalconfig["autodisappear_which"] == 1:
                if globalconfig["disappear_delay"] == 0:
                    if self.isMouseHover:
                        self.translate_text.textbrowser.setVisible(True)
                else:
                    self.translate_text.textbrowser.setVisible(True)

    @property
    def isMouseHover(self):
        # 当鼠标悬停，或前景窗口为当前进程的其他窗口时，返回真
        return self.geometry().contains(QCursor.pos()) or (
            windows.GetForegroundWindow() != self.winid
            and windows.GetWindowThreadProcessId(windows.GetForegroundWindow())
            == os.getpid()
        )

    @threader
    def autohidedelaythread(self):
        while True:
            time.sleep(0.5)
            # 当鼠标悬停，或前景窗口为当前进程的其他窗口时，禁止自动隐藏
            if self.isMouseHover:
                self.lastrefreshtime = time.time()
                continue
            if globalconfig["autodisappear"]:
                if self.autohidestart and (
                    time.time() - self.lastrefreshtime
                    >= globalconfig["disappear_delay"]
                ):
                    if globalconfig["autodisappear_which"] == 0:

                        self.hidesignal.emit()
                    elif globalconfig["autodisappear_which"] == 1:
                        self.internaltexthide.emit(False)
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
        self.titlebar.setbuttonsize()
        self.titlebar.adjustminwidth()
        self.titlebar.refreshtoolicon()
        self.set_color_transparency()
        self.seteffect()
        self.changeextendstated()

    @threader
    def ocr_do_function(self, rect, img=None):
        if not rect:
            return
        if not img:
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
        result = ocr_run(img)
        result = result.maybeerror()
        if result:
            gobject.baseobject.textgetmethod(result, False)

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
        globalconfig["keepontop"] = not globalconfig["keepontop"]

        self.refreshtoolicon()
        self.setontopthread()

    def favoritesmenu(self):
        menu = QMenu(gobject.baseobject.commonstylebase)
        gameuid = gobject.baseobject.gameuid
        maps = {}
        if gameuid:
            for name, link in savehook_new_data[gameuid].get("relationlinks", []):
                act = QAction(name, menu)
                maps[act] = link
                menu.addAction(act)
        if (
            globalconfig["relationlinks"]
            and gameuid
            and savehook_new_data[gameuid].get("relationlinks", [])
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
                buttonfunctions(
                    clicked=self.changeTranslateMode,
                    iconstate=lambda: globalconfig["autorun"],
                    colorstate=lambda: globalconfig["autorun"],
                ),
            ),
            ("setting", lambda: gobject.baseobject.settin_ui.showsignal.emit()),
            (
                "copy",
                lambda: NativeUtils.ClipBoard.setText(gobject.baseobject.currenttext),
            ),
            ("edit", gobject.baseobject.createedittextui),
            ("edittrans", lambda: edittrans(gobject.baseobject.commonstylebase)),
            (
                "showraw",
                buttonfunctions(
                    clicked=self.changeshowhideraw,
                    iconstate=lambda: globalconfig["isshowrawtext"],
                    colorstate=lambda: globalconfig["isshowrawtext"],
                ),
            ),
            (
                "showtrans",
                buttonfunctions(
                    clicked=self.changeshowhidetrans,
                    iconstate=lambda: globalconfig["showfanyi"],
                    colorstate=lambda: globalconfig["showfanyi"],
                ),
            ),
            ("history", lambda: gobject.baseobject.transhis.showsignal.emit()),
            (
                "noundict",
                buttonfunctions(
                    clicked=lambda: loadpostsettingwindowmethod_maybe(
                        "noundict", gobject.baseobject.commonstylebase
                    ),
                    rightclick=lambda: loadpostsettingwindowmethod("noundict")(
                        gobject.baseobject.commonstylebase,
                    ),
                ),
            ),
            (
                "noundict_direct",
                buttonfunctions(
                    clicked=lambda: loadpostsettingwindowmethod_maybe(
                        "vndbnamemap", gobject.baseobject.commonstylebase
                    ),
                    rightclick=lambda: loadpostsettingwindowmethod("vndbnamemap")(
                        gobject.baseobject.commonstylebase
                    ),
                ),
            ),
            (
                "fix",
                buttonfunctions(
                    clicked=lambda: loadpostsettingwindowmethod_maybe(
                        "transerrorfix", gobject.baseobject.commonstylebase
                    ),
                    rightclick=lambda: loadpostsettingwindowmethod("transerrorfix")(
                        gobject.baseobject.commonstylebase
                    ),
                ),
            ),
            (
                "langdu",
                buttonfunctions(
                    clicked=lambda: gobject.baseobject.readcurrent(force=True),
                    rightclick=lambda: gobject.baseobject.audioplayer.stop(),
                ),
            ),
            (
                "mousetransbutton",
                buttonfunctions(
                    clicked=lambda: self.changemousetransparentstate(0),
                    colorstate=lambda: globalconfig["mousetransparent"],
                ),
            ),
            (
                "backtransbutton",
                buttonfunctions(
                    clicked=lambda: self.changemousetransparentstate(1),
                    colorstate=lambda: globalconfig["backtransparent"],
                ),
            ),
            (
                "locktoolsbutton",
                buttonfunctions(
                    clicked=self.changetoolslockstate,
                    iconstate=lambda: globalconfig["locktools"],
                    colorstate=lambda: globalconfig["locktools"],
                    rightclick=self.changetoolslockstateEx,
                ),
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
                buttonfunctions(
                    clicked=self.clickRange,
                    rightclick=self.clickRangeclear,
                ),
            ),
            (
                "hideocrrange",
                buttonfunctions(
                    clicked=self.showhideocrrange,
                    colorstate=lambda: self.showhidestate,
                    rightclick=self.clear_signal_1.emit,
                ),
            ),
            (
                "bindwindow",
                buttonfunctions(
                    clicked=self.bindcropwindow_signal.emit,
                    colorstate=lambda: self.isbindedwindow,
                ),
            ),
            ("searchwordW", self.callopensearchwordwindow),
            (
                "fullscreen",
                buttonfunctions(
                    clicked=lambda: self._fullsgame(False),
                    rightclick=lambda: self._fullsgame(True),
                    iconstate=lambda: self.isletgamefullscreened,
                ),
            ),
            (
                "grabwindow",
                buttonfunctions(
                    clicked=grabwindow, rightclick=lambda: grabwindow(tocliponly=True)
                ),
            ),
            (
                "muteprocess",
                buttonfunctions(
                    clicked=self.muteprocessfuntion,
                    iconstate=lambda: self.processismuteed,
                ),
            ),
            (
                "memory",
                buttonfunctions(
                    clicked=lambda: dialog_memory(gobject.baseobject.commonstylebase),
                    rightclick=lambda: dialog_memory(
                        gobject.baseobject.commonstylebase, True
                    ),
                ),
            ),
            (
                "keepontop",
                buttonfunctions(
                    clicked=self.btnsetontopfunction,
                    colorstate=lambda: globalconfig["keepontop"],
                ),
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
                buttonfunctions(
                    clicked=lambda: gobject.baseobject.textgetmethod(
                        NativeUtils.ClipBoard.text, False
                    ),
                    rightclick=lambda: gobject.baseobject.textgetmethod(
                        gobject.baseobject.currenttext
                        + (getlangsrc().space if gobject.baseobject.currenttext else "")
                        + NativeUtils.ClipBoard.text,
                        False,
                    ),
                ),
            ),
            (
                "game_ref_favorites",
                buttonfunctions(
                    clicked=self.favoritesmenu,
                    rightclick=lambda: favorites(
                        gobject.baseobject.commonstylebase,
                        gobject.baseobject.gameuid,
                    ),
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
                buttonfunctions(
                    clicked=self.setselectable,
                    colorstate=lambda: globalconfig["selectable"],
                    rightclick=self.setselectableEx,
                ),
            ),
            (
                "editable",
                buttonfunctions(
                    clicked=self.seteditable,
                    colorstate=lambda: globalconfig["editable"],
                ),
            ),
        )

        _type = {"quit": 2}

        for __ in functions:
            btn = clicked = iconstate = colorstate = rightclick = middleclick = None
            if len(__) == 2:
                btn, funcs = __
                if isinstance(funcs, buttonfunctions):
                    clicked = funcs.clicked
                    rightclick = funcs.rightclick
                    middleclick = funcs.middleclick
                    iconstate = funcs.iconstate
                    colorstate = funcs.colorstate
                else:
                    clicked = funcs
            belong = (
                globalconfig["toolbutton"]["buttons"][btn]["belong"]
                if "belong" in globalconfig["toolbutton"]["buttons"][btn]
                else None
            )
            tp = _type[btn] if btn in _type else 1
            self.titlebar.takusanbuttons(
                tp,
                clicked,
                rightclick,
                globalconfig["toolbutton"]["buttons"][btn]["tip"],
                btn,
                belong,
                iconstate,
                colorstate,
                middleclick,
            )

    def callopensearchwordwindow(self):
        curr = self.translate_text.GetSelectedText()
        if curr:
            gobject.baseobject.searchwordW.search_word.emit(curr, False)
        else:
            gobject.baseobject.searchwordW.showsignal.emit()

    @property
    def winid(self):
        return int(self.winId())

    def changeextendstated(self):
        dh = self.dynamicextraheight()
        if globalconfig["verticalhorizontal"]:
            self.translate_text.move(0, 0)
            height = self.width() - dh
            self.translate_text.resize(int(height), self.height())
        else:
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
            NativeUtils.clearEffect(self.winid)
        elif globalconfig["WindowEffect"] == 1:
            NativeUtils.setAcrylicEffect(
                self.winid, globalconfig["WindowEffect_shadow"]
            )
        elif globalconfig["WindowEffect"] == 2:
            NativeUtils.setAeroEffect(self.winid, globalconfig["WindowEffect_shadow"])

    def initvalues(self):
        self.enter_sig = 0
        self.lastrefreshtime = time.time()
        self.fullscreenmanager_busy = threading.Lock()
        self.isletgamefullscreened = False
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
        QMessageBox.information(self, _TR(string1), _TR(string2))

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

        def __():
            self.clearstate() or gobject.baseobject.textsource.clearrange()

        self.clear_signal_1.connect(tryprint(__))
        self.bindcropwindow_signal.connect(
            functools.partial(mouseselectwindow, self.bindcropwindowcallback)
        )
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame)

        self.muteprocessignal.connect(self.muteprocessfuntion)
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)
        self.move_signal.connect(self.safemove)
        self.closesignal.connect(self.close)
        self.changeshowhiderawsig.connect(self.changeshowhideraw)
        self.changeshowhidetranssig.connect(self.changeshowhidetrans)
        self.internaltexthide.connect(
            lambda _: self.translate_text.textbrowser.setVisible(_)
        )

    def safemove(self, pos: QPoint):
        if pos.x() < -self.width() / 2:
            return
        if pos.y() < 0:
            return
        if len(QApplication.screens()) == 1:
            if (
                pos.x() + self.width() / 2
                > QApplication.primaryScreen().geometry().width()
            ):
                return
            if (
                pos.y() + self.height()
                > QApplication.primaryScreen().geometry().height()
            ):
                return

        self.move(pos)

    def __init__(self):
        flags = (
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint
        )
        if globalconfig["keepontop"]:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        super(TranslatorWindow, self).__init__(
            None, flags=flags, poslist=globalconfig["transuigeo"]
        )

        self.fullscreenmanager = None
        self.magpiecallback.connect(
            lambda _: (
                self.fullscreenmanager.setuistatus(_)
                if self.fullscreenmanager
                else None
            )
        )
        icon = getExeIcon(getcurrexe())
        self.setWindowIcon(icon)
        self.firstshow = True
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowTitle("LunaTranslator")
        self.initvalues()
        self.initsignals()
        self.titlebar = ButtonBar(self)
        self.titlebar.move(0, 0)  # 多显示屏下，谜之错位
        self.titlebar.setbuttonsize()
        self.titlebar.setObjectName("titlebar")
        self.titlebar.setMouseTracking(True)
        self.addbuttons()
        self.smooth_resizer = QVariantAnimation(self)
        self.smooth_resizer.setDuration(500)
        self.smooth_resizer.setEasingCurve(QEasingCurve.Type.InOutQuad)
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
        self.verticalhorizontal(globalconfig["verticalhorizontal"])

    def __parsedropexe(self, file):
        uid = find_or_create_uid(savehook_new_list, file)
        if uid not in savehook_new_list:
            savehook_new_list.insert(0, uid)
        startgame(uid)
        self.displaystatus.emit(
            _TR("启动游戏_ " + savehook_new_data[uid]["title"]), TextType.Info
        )

    def __parsedropmecab(self, file):
        isfile = os.path.isfile(file)
        flow = os.path.basename(file).lower()
        if isfile and flow == "dicrc":
            file = os.path.dirname(file)
        filer = mayberelpath(file)
        changed = filer != globalconfig["hirasetting"]["mecab"]["args"]["path"]
        globalconfig["hirasetting"]["mecab"]["args"]["path"] = filer
        self.displaystatus.emit(_TR("成功设置_Mecab_路径_ " + filer), TextType.Info)
        if changed:
            gobject.baseobject.startmecab()

    def __parsedropmdx(self, file: str):
        isfile = os.path.isfile(file)
        flow = os.path.basename(file).lower()
        if isfile and flow == "dicrc":
            file = os.path.dirname(file)
        filer = mayberelpath(file)
        changed = filer not in globalconfig["cishu"]["mdict"]["args"]["paths"]
        if changed:
            globalconfig["cishu"]["mdict"]["args"]["paths"].append(filer)
        self.displaystatus.emit(_TR("成功添加_MDict_ " + filer), TextType.Info)
        if changed:
            gobject.baseobject.startxiaoxueguan("mdict")

    def __parsedropjson(self, file):
        try:
            gameuid = gobject.baseobject.gameuid
            _path = savehook_new_data[gameuid].get("gamejsonfile", [])
            if isinstance(_path, str):
                _path = [_path]
            filer = mayberelpath(file)
            if filer not in _path:
                _path.append(filer)
                savehook_new_data[gameuid]["gamejsonfile"] = _path
                self.displaystatus.emit(
                    _TR("成功添加_Mecab_路径_ " + filer), TextType.Info
                )
        except:
            print_exc()

            _path: list = translatorsetting["rengong"]["args"]["jsonfile"]
            filer = mayberelpath(file)
            if filer not in _path:
                _path.append(filer)
                translatorsetting["rengong"]["args"]["jsonfile"] = _path
                self.displaystatus.emit(
                    _TR("成功添加_json翻译文件_ " + filer), TextType.Info
                )

    def dropfilecallback(self, file: str):
        isfile = os.path.isfile(file)
        flow = os.path.basename(file).lower()
        checks = [
            (
                lambda: (isfile and flow == "dicrc")
                or ((not isfile) and os.path.isfile(os.path.join(file, "dicrc"))),
                self.__parsedropmecab,
            ),
            (
                lambda: (isfile and flow.endswith(".mdx")),
                self.__parsedropmdx,
            ),
            (lambda: isfile and flow.endswith(".json"), self.__parsedropjson),
            (
                lambda: isfile and (flow.endswith(".exe") or flow.endswith(".lnk")),
                self.__parsedropexe,
            ),
        ]
        for checkf, do in checks:
            if checkf():
                try:
                    do(file)
                except:
                    print_exc()
                break

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

    def setselectableEx(self):
        globalconfig["selectableEx"] = True
        globalconfig["selectable"] = not globalconfig["selectable"]
        self.translate_text.setselectable(globalconfig["selectable"])
        self.refreshtoolicon()

    def setselectable(self):
        globalconfig["selectableEx"] = False
        globalconfig["selectable"] = not globalconfig["selectable"]
        self.translate_text.setselectable(globalconfig["selectable"])
        self.refreshtoolicon()

    def seteditable(self):
        globalconfig["editable"] = not globalconfig["editable"]
        self.translate_text.seteditable(globalconfig["editable"])
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
                str2rgba(globalconfig["backcolor"], self.transparent_value_actually),
            )
        )
        self.titlebar.setstyle(bottomr, bottomr3)
        QApplication.postEvent(
            self.translate_text.textbrowser, QEvent(QEvent.Type.User + 2)
        )

    @property
    def transparent_value_actually(self):
        return max(
            (1 - globalconfig["transparent_EX"]) * 100 / 255,
            globalconfig["transparent"] * (not globalconfig["backtransparent"]),
        )

    def muteprocessfuntion(self):
        NativeUtils.SetCurrProcessMute(not self.processismuteed)

    def _externalfsend(self, current):
        self.isletgamefullscreened = current
        self.refreshtooliconsignal.emit()

    @threader
    def _fullsgame(self, windowmode):
        with self.fullscreenmanager_busy:
            try:
                if gobject.baseobject.hwnd:
                    _hwnd = gobject.baseobject.hwnd
                else:
                    _hwnd = windows.GetForegroundWindow()
                    _pid = windows.GetWindowThreadProcessId(_hwnd)
                    if _pid == os.getpid():
                        return
                if not self.fullscreenmanager:
                    self.fullscreenmanager = MagpieBuiltin(self._externalfsend)
                self.fullscreenmanager.callstatuschange(_hwnd, windowmode)
            except:
                print_exc()

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

    @property
    def locktoolsExcheckrect(self):
        btn: QWidget = self.titlebar.buttons["locktoolsbutton"]
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

    def changetoolslockstateEx(self):
        globalconfig["locktoolsEx"] = True
        globalconfig["locktools"] = not globalconfig["locktools"]
        self.refreshtoolicon()

    def changetoolslockstate(self):
        globalconfig["locktoolsEx"] = False
        globalconfig["locktools"] = not globalconfig["locktools"]
        self.refreshtoolicon()

    def dynamicextraheight(self):

        if globalconfig["WindowEffect"] == 0:
            if globalconfig["verticalhorizontal"]:
                return int(IconLabelX.w())
            else:
                return int(IconLabelX.h())
        if globalconfig["locktools"]:
            if globalconfig["verticalhorizontal"]:
                return int(IconLabelX.w())
            else:
                return int(IconLabelX.h())

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
        if globalconfig["verticalhorizontal"]:
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
        (x1, y1), (x2, y2) = rect
        if x1 == x2 or y1 == y2:
            return
        if clear or not globalconfig["multiregion"]:
            gobject.baseobject.textsource.clearrange()
        gobject.baseobject.textsource.newrangeadjustor()
        gobject.baseobject.textsource.setrect(rect)
        self.showhideocrrange()
        if globalconfig["showrangeafterrangeselect"] == False:
            self.showhideocrrange()

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

    def checklocktoolsEx(self):
        usegeo = self.titlebar.geometry()
        btn: QWidget = self.titlebar.buttons["locktoolsbutton"]
        if (not btn.isVisible()) and (btn.reflayout is not None):
            usegeo = self.locktoolsExcheckrect
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
        if (not globalconfig["locktoolsEx"]) or self.checklocktoolsEx():
            self.titlebar.show()
        self.translate_text.textbrowser.setVisible(True)
        self.autohidestart = True
        self.lastrefreshtime = time.time()
        self.set_color_transparency()
        self.dodelayhide(delay)

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        wh = self.dynamicextraheight()

        if globalconfig["verticalhorizontal"]:
            height = self.width() - wh
            self.translate_text.resize(int(height), self.height())
            self.translate_text.move(0, 0)
            if e.oldSize().height() != e.size().height():
                self.titlebar.setFixedHeight(self.height())
            self.titlebar.move(self.width() - self.titlebar.width(), 0)
        else:
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
                if (pid != os.getpid()) and (NativeUtils.IsProcessRunning(pid)):
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
                os.remove("cache/Updater.exe")
            except:
                pass
        except:
            pass

    def closeEvent(self, a0) -> None:
        try:
            if self.fullscreenmanager:
                self.fullscreenmanager.endX()
            AdapterService.uninit()
            gobject.baseobject.isrunning = False
            self.hide()

            gobject.baseobject.textsource = None
            gobject.baseobject.destroytray()
            handle = NativeUtils.SimpleCreateMutex("LUNASAVECONFIGUPDATE")
            if windows.GetLastError() != windows.ERROR_ALREADY_EXISTS:
                errors = saveallconfig()
                if errors:
                    errors = [f + "\n\t" + stringfyerror(e) for e, f in errors]
                    QMessageBox.critical(
                        gobject.baseobject.commonstylebase,
                        _TR("错误"),
                        "\n\n".join(errors),
                    )
                self.tryremoveuseless()
                doupdate()
                windows.CloseHandle(handle)
            os._exit(0)

        except:
            print_exc()
