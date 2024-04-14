import time
import functools
import threading
import os, sys
import winsharedutils
from PyQt5.QtCore import QT_VERSION_STR
import windows
from traceback import print_exc
from PyQt5.QtCore import Qt, pyqtSignal
import qtawesome
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QLabel, QPushButton, QSystemTrayIcon
import gobject
from myutils.wrapper import threader
import winsharedutils
from myutils.config import globalconfig, saveallconfig, _TR, static_data
from myutils.subproc import endsubprocs
from myutils.ocrutil import ocr_run, imageCut
from myutils.hwnd import mouseselectwindow, showintab, grabwindow, getExeIcon
from gui.dialog_savedgame import dialog_savedgame_new
from gui.dialog_memory import dialog_memory
from gui.textbrowser import Textbrowser
from myutils.fullscreen import fullscreen
from gui.rangeselect import moveresizegame, rangeselct_function
from gui.usefulwidget import resizableframeless
from gui.dialog_savedgame import browserdialog


class QUnFrameWindow(resizableframeless):
    displayres = pyqtSignal(dict)
    displayraw1 = pyqtSignal(dict)
    displaystatus = pyqtSignal(str, str, bool, bool)
    showhideuisignal = pyqtSignal()
    hookfollowsignal = pyqtSignal(int, tuple)
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
    entersignal = pyqtSignal()
    ocr_once_signal = pyqtSignal()

    def hookfollowsignalsolve(self, code, other):
        if self._move_drag:
            return
        if code == 3:
            self.show_()
            try:
                _h = windows.GetForegroundWindow()
                _fpid = windows.GetWindowThreadProcessId(_h)
                _hpid = windows.GetWindowThreadProcessId(other[0])
                if _fpid != _hpid:
                    windows.SetForegroundWindow(other[0])
            except:
                pass
        elif code == 4:
            self.hide_()
        elif code == 5:
            # print(self.pos())
            # self.move(self.pos() + self._endPos)z
            try:
                gobject.baseobject.textsource.moveui(other[0], other[1])
            except:
                pass
            self.move(self.pos().x() + other[0], self.pos().y() + other[1])

    def showres(self, kwargs):  # name,color,res,onlytrans,iter_context):
        try:
            name = kwargs.get("name", "")
            color = kwargs.get("color")
            res = kwargs.get("res")
            onlytrans = kwargs.get("onlytrans")
            iter_context = kwargs.get("iter_context", None)

            if iter_context:
                iter_res_status, iter_context_class = iter_context
                if iter_res_status == 2:  # iter结束
                    gobject.baseobject.transhis.getnewtranssignal.emit(name, res)
                    return
            else:
                gobject.baseobject.transhis.getnewtranssignal.emit(name, res)

            if onlytrans:
                return
            clear = name == ""
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

    def showraw(self, kwargs):  # hira,res,color,onlytrans):
        text = kwargs.get("text")
        color = kwargs.get("color")
        onlytrans = kwargs.get("onlytrans")

        clear = True
        gobject.baseobject.transhis.getnewsentencesignal.emit(text)
        if onlytrans:
            return
        if len(text) > globalconfig["maxoriginlength"]:
            _res = text[: globalconfig["maxoriginlength"]] + "……"
        else:
            _res = text
        if globalconfig["isshowhira"] and globalconfig["isshowrawtext"]:
            self.showline(clear=clear, text=_res, hira=True, color=color)
        elif globalconfig["isshowrawtext"]:
            self.showline(clear=clear, text=_res, color=color)
        else:
            self.showline(clear=clear)

        gobject.baseobject.edittextui.getnewsentencesignal.emit(text)

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

    def parsehira(self, text):
        hira = []
        try:
            if gobject.baseobject.hira_:
                hira = gobject.baseobject.hira_.fy(text)
                for _1 in range(len(hira)):
                    _ = len(hira) - 1 - _1
                    if globalconfig["hira_vis_type"] == 0:
                        hira[_]["hira"] = hira[_]["hira"].translate(self.castkata2hira)
                    elif globalconfig["hira_vis_type"] == 1:
                        hira[_]["hira"] = hira[_]["hira"].translate(self.casthira2kata)
                    elif globalconfig["hira_vis_type"] == 2:
                        __kanas = [
                            static_data["hira"] + ["っ"],
                            static_data["kata"] + ["ッ"],
                        ]
                        target = static_data["roma"] + ["-"]
                        for _ka in __kanas:
                            for __idx in range(len(_ka)):
                                _reverse_idx = len(_ka) - 1 - __idx
                                hira[_]["hira"] = hira[_]["hira"].replace(
                                    _ka[_reverse_idx], target[_reverse_idx]
                                )
        except:
            print_exc()
        return hira

    def showline(self, **kwargs):  # clear,res,color ,type_=1,origin=True):
        clear = kwargs.get("clear", True)
        origin = kwargs.get("origin", True)
        text = kwargs.get("text", None)
        color = kwargs.get("color", None)
        hira = kwargs.get("hira", False)
        iter_context = kwargs.get("iter_context", None)

        if clear:
            self.translate_text.clear()
        if text is None:
            return
        text = self.cleartext(text)
        if hira:
            hiras = [self.parsehira(_) for _ in text.split("\n")]
            hira = []
            for i, _h in enumerate(hiras):
                if i:
                    hira += [{"orig": "\n", "hira": "\n"}]
                hira += _h
        else:
            hira = []
        self.translate_text.setnextfont(origin)

        if globalconfig["showatcenter"]:
            self.translate_text.setAlignment(Qt.AlignCenter)
        else:
            self.translate_text.setAlignment(Qt.AlignLeft)

        if globalconfig["zitiyangshi"] == 2:
            self.translate_text.mergeCurrentCharFormat_out(
                globalconfig["miaobiancolor"], color, globalconfig["miaobianwidth2"]
            )
        elif globalconfig["zitiyangshi"] == 4:
            self.translate_text.mergeCurrentCharFormat_out(
                color, globalconfig["miaobiancolor"], globalconfig["miaobianwidth2"]
            )
        elif globalconfig["zitiyangshi"] == 1:
            self.translate_text.mergeCurrentCharFormat(
                color, globalconfig["miaobianwidth"]
            )
        elif globalconfig["zitiyangshi"] == 0:
            self.translate_text.simplecharformat(color)
        elif globalconfig["zitiyangshi"] == 3:
            self.translate_text.simplecharformat(color)

        if iter_context:
            iter_res_status, iter_context_class = iter_context
            if iter_res_status == 3:
                self.translate_text.append(" ", hira, origin)
                self.saveiterclasspointer[iter_context_class] = {
                    "currtext": "",
                    "curr": self.translate_text.getcurrpointer(),
                    "start": self.translate_text.getcurrpointer(),
                }
            else:
                currbefore = self.saveiterclasspointer[iter_context_class]["curr"]
                currlen = len(self.saveiterclasspointer[iter_context_class]["currtext"])
                if len(text) < currlen:
                    self.translate_text.deletebetween(
                        self.saveiterclasspointer[iter_context_class]["start"]
                        + len(text),
                        self.saveiterclasspointer[iter_context_class]["curr"],
                    )
                else:
                    newtext = text[currlen:]
                    self.translate_text.insertatpointer(
                        self.saveiterclasspointer[iter_context_class]["start"]
                        + currlen,
                        newtext,
                    )

                self.saveiterclasspointer[iter_context_class]["currtext"] = text
                currcurrent = self.translate_text.getcurrpointer()
                self.saveiterclasspointer[iter_context_class]["curr"] = currcurrent
                currchange = currcurrent - currbefore
                for klass in self.saveiterclasspointer:
                    if klass == iter_context_class:
                        continue
                    if self.saveiterclasspointer[klass]["curr"] > currbefore:
                        self.saveiterclasspointer[klass]["curr"] += currchange
                        self.saveiterclasspointer[klass]["start"] += currchange

            if globalconfig["zitiyangshi"] == 3:
                self.translate_text.showyinyingtext2(
                    color,
                    iter_context_class,
                    self.saveiterclasspointer[iter_context_class]["start"],
                    text,
                )

        else:
            self.translate_text.append(text, hira, origin)
            if globalconfig["zitiyangshi"] == 3:
                self.translate_text.showyinyingtext(color)
        if (
            globalconfig["usesearchword"]
            or globalconfig["usecopyword"]
            or globalconfig["show_fenci"]
        ) and hira:

            def callback(word):
                if globalconfig["usewordorigin"] == False:
                    word = word["orig"]
                else:
                    word = word.get("origorig", word["orig"])

                if globalconfig["usecopyword"]:
                    winsharedutils.clipboard_set(word)
                if globalconfig["usesearchword"]:
                    gobject.baseobject.searchwordW.getnewsentencesignal.emit(word)

            self.translate_text.addsearchwordmask(hira, text, callback)

        if globalconfig["autodisappear"]:
            flag = (self.showintab and self.isMinimized()) or (
                not self.showintab and self.isHidden()
            )

            if flag:
                self.show_()
            self.lastrefreshtime = time.time()
            self.autohidestart = True

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

        flag = (self.showintab and self.isMinimized()) or (
            not self.showintab and self.isHidden()
        )

        if flag:
            self.show_()
        else:
            self.hide_()

    def leftclicktray(self, reason):
        # 鼠标左键点击
        if reason == QSystemTrayIcon.Trigger:
            self.showhideui()

    def refreshtoolicon(self):

        iconstate = {
            "fullscreen": self.isletgamefullscreened,
            "muteprocess": self.processismuteed,
            "locktoolsbutton": globalconfig["locktools"],
            "showraw": globalconfig["isshowrawtext"],
            "automodebutton": globalconfig["autorun"],
        }
        colorstate = {
            "automodebutton": globalconfig["autorun"],
            "showraw": globalconfig["isshowrawtext"],
            "mousetransbutton": self.mousetransparent,
            "backtransbutton": self.backtransparent,
            "locktoolsbutton": globalconfig["locktools"],
            "hideocrrange": self.showhidestate,
            "bindwindow": self.isbindedwindow,
            "keepontop": globalconfig["keepontop"],
        }
        onstatecolor = "#FF69B4"

        self._TitleLabel.setFixedHeight(int(globalconfig["buttonsize"] * 1.5))
        for i in range(len(self.buttons)):
            name = self.buttons[i].name
            if name in colorstate:
                color = (
                    onstatecolor if colorstate[name] else globalconfig["buttoncolor"]
                )
            else:
                color = globalconfig["buttoncolor"]
            if name in iconstate:
                icon = (
                    globalconfig["toolbutton"]["buttons"][name]["icon"]
                    if iconstate[name]
                    else globalconfig["toolbutton"]["buttons"][name]["icon2"]
                )
            else:
                icon = globalconfig["toolbutton"]["buttons"][name]["icon"]
            self.buttons[i].setIcon(qtawesome.icon(icon, color=color))  # (icon[i])
            self.buttons[i].resize(
                int(globalconfig["buttonsize"] * 2),
                int(globalconfig["buttonsize"] * 1.5),
            )

            if self.buttons[i].adjast:
                self.buttons[i].adjast()
            self.buttons[i].setIconSize(
                QSize(globalconfig["buttonsize"], globalconfig["buttonsize"])
            )
        self.showhidetoolbuttons()
        self.translate_text.movep(0, globalconfig["buttonsize"] * 1.5)
        self.textAreaChanged()
        self.setMinimumHeight(int(globalconfig["buttonsize"] * 1.5 + 10))
        self.setMinimumWidth(globalconfig["buttonsize"] * 2)

    def ocr_once_function(self):
        @threader
        def ocroncefunction(rect):
            img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            fname = "./cache/ocr/once.png"
            img.save(fname)
            text = ocr_run(fname)
            gobject.baseobject.textgetmethod(text, False)

        rangeselct_function(self, ocroncefunction, False, False)

    @threader
    def simulate_key_enter(self):
        windows.SetForegroundWindow(gobject.baseobject.textsource.hwnd)
        time.sleep(0.1)
        while windows.GetForegroundWindow() == gobject.baseobject.textsource.hwnd:
            time.sleep(0.001)
            windows.keybd_event(13, 0, 0, 0)
        windows.keybd_event(13, 0, windows.KEYEVENTF_KEYUP, 0)

    def addbuttons(self):
        def simulate_key_ctrl():
            windows.SetForegroundWindow(gobject.baseobject.textsource.hwnd)
            time.sleep(0.1)
            windows.keybd_event(17, 0, 0, 0)
            while windows.GetForegroundWindow() == gobject.baseobject.textsource.hwnd:
                time.sleep(0.001)
            windows.keybd_event(17, 0, windows.KEYEVENTF_KEYUP, 0)

        functions = (
            ("move", None),
            ("retrans", self.startTranslater),
            ("automodebutton", self.changeTranslateMode),
            ("setting", lambda: gobject.baseobject.settin_ui.showsignal.emit()),
            (
                "copy",
                lambda: winsharedutils.clipboard_set(gobject.baseobject.currenttext),
            ),
            ("edit", lambda: gobject.baseobject.edittextui.showsignal.emit()),
            ("showraw", self.changeshowhideraw),
            ("history", lambda: gobject.baseobject.transhis.showsignal.emit()),
            ("noundict", lambda: gobject.baseobject.settin_ui.button_noundict.click()),
            ("fix", lambda: gobject.baseobject.settin_ui.button_fix.click()),
            ("langdu", self.langdu),
            ("mousetransbutton", lambda: self.changemousetransparentstate(0)),
            ("backtransbutton", lambda: self.changemousetransparentstate(1)),
            ("locktoolsbutton", self.changetoolslockstate),
            ("gamepad_new", lambda: dialog_savedgame_new(gobject.baseobject.settin_ui)),
            (
                "selectgame",
                lambda: gobject.baseobject.AttachProcessDialog.showsignal.emit(),
            ),
            (
                "selecttext",
                lambda: gobject.baseobject.hookselectdialog.showsignal.emit(),
            ),
            ("selectocrrange", lambda: self.clickRange(False)),
            ("hideocrrange", self.showhideocrrange),
            ("bindwindow", self.bindcropwindow_signal.emit),
            (
                "resize",
                lambda: (
                    moveresizegame(self, gobject.baseobject.textsource.hwnd)
                    if gobject.baseobject.textsource.hwnd
                    else 0
                ),
            ),
            ("fullscreen", self._fullsgame),
            ("grabwindow", lambda: grabwindow()),
            ("muteprocess", self.muteprocessfuntion),
            (
                "memory",
                lambda: dialog_memory(
                    gobject.baseobject.settin_ui, gobject.baseobject.currentmd5
                ),
            ),
            (
                "keepontop",
                lambda: globalconfig.__setitem__(
                    "keepontop", not globalconfig["keepontop"]
                )
                is None
                and self.refreshtoolicon() is None
                and self.setontopthread(),
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
                    gobject.baseobject.settin_ui, gobject.baseobject.textsource
                ),
            ),
            (
                "open_game_setting",
                lambda: gobject.baseobject.hookselectdialog.opengamesetting(),
            ),
            ("ocr_once", self.ocr_once_signal.emit),
            ("minmize", self.hide_),
            ("quit", self.close),
        )
        adjast = {"minmize": -2, "quit": -1}
        _type = {"quit": 2}

        for btn, func in functions:
            belong = (
                globalconfig["toolbutton"]["buttons"][btn]["belong"]
                if "belong" in globalconfig["toolbutton"]["buttons"][btn]
                else None
            )
            _adjast = adjast[btn] if btn in adjast else 0
            tp = _type[btn] if btn in _type else 1
            self.takusanbuttons(
                tp,
                func,
                _adjast,
                globalconfig["toolbutton"]["buttons"][btn]["tip"],
                btn,
                belong,
            )

    def hide_(self):
        if self.showintab:
            windows.ShowWindow(int(self.winId()), windows.SW_SHOWMINIMIZED)
        else:
            self.hide()

    def show_(self):
        if self.showintab:
            windows.ShowWindow(int(self.winId()), windows.SW_SHOWNOACTIVATE)
        else:
            self.show()
        windows.SetForegroundWindow(int(self.winId()))

    def showEvent(self, a0) -> None:
        if self.isfirstshow:
            self.showline(clear=True, text=_TR("欢迎使用"), origin=False)

            self.tray.activated.connect(self.leftclicktray)

            self.tray.show()
            windows.SetForegroundWindow(int(self.winId()))
            self.isfirstshow = False
            self.setontopthread()
        return super().showEvent(a0)

    def canceltop(self):
        windows.SetWindowPos(
            int(self.winId()),
            windows.HWND_NOTOPMOST,
            0,
            0,
            0,
            0,
            windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
        )
        HWNDStyleEx = windows.GetWindowLong(int(self.winId()), windows.GWL_EXSTYLE)
        windows.SetWindowLong(
            int(self.winId()), windows.GWL_EXSTYLE, HWNDStyleEx & ~windows.WS_EX_TOPMOST
        )

        windows.SetWindowPos(
            int(self.winId()),
            windows.GetForegroundWindow(),
            0,
            0,
            0,
            0,
            windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
        )

    def istopmost(self):
        return bool(
            windows.GetWindowLong(int(self.winId()), windows.GWL_EXSTYLE)
            & windows.WS_EX_TOPMOST
        )

    def settop(self):
        if not self.istopmost():
            self.canceltop()
        HWNDStyleEx = windows.GetWindowLong(int(self.winId()), windows.GWL_EXSTYLE)
        windows.SetWindowLong(
            int(self.winId()), windows.GWL_EXSTYLE, HWNDStyleEx | windows.WS_EX_TOPMOST
        )
        windows.SetWindowPos(
            int(self.winId()),
            windows.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
        )

    def setontopthread(self):
        def _():
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
            self.canceltop()

        threading.Thread(target=_).start()

    def __init__(self):

        super(QUnFrameWindow, self).__init__(
            None,
            flags=Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint,
            dic=globalconfig,
            key="transuigeo",
        )  # 设置为顶级窗口，无边框
        icon = getExeIcon(sys.argv[0])  #'./LunaTranslator.exe')# QIcon()
        # icon.addPixmap(QPixmap('./files/luna.png'), QIcon.Normal, QIcon.On)
        self.setWindowIcon(icon)
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        showintab(int(self.winId()), globalconfig["showintab"])
        self.isfirstshow = True
        if QT_VERSION_STR != "5.5.1":
            self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.showintab = globalconfig["showintab"]
        self.setWindowTitle("LunaTranslator")
        self.hidesignal.connect(self.hide_)
        self.lastrefreshtime = time.time()
        self.autohidestart = False
        threading.Thread(target=self.autohidedelaythread).start()
        self.muteprocessignal.connect(self.muteprocessfuntion)
        self.toolbarhidedelaysignal.connect(self.toolbarhidedelay)

        self.ocr_once_signal.connect(self.ocr_once_function)
        self.entersignal.connect(self.enterfunction)
        self.displaystatus.connect(self.showstatus)
        self.showhideuisignal.connect(self.showhideui)
        self.hookfollowsignal.connect(self.hookfollowsignalsolve)
        self.displayres.connect(self.showres)
        self.displayraw1.connect(self.showraw)
        self.refreshtooliconsignal.connect(self.refreshtoolicon)
        self.showsavegame_signal.connect(
            lambda: dialog_savedgame_new(gobject.baseobject.settin_ui)
        )
        self.clickRange_signal.connect(self.clickRange)
        self.showhide_signal.connect(self.showhideocrrange)
        self.bindcropwindow_signal.connect(
            functools.partial(mouseselectwindow, self.bindcropwindowcallback)
        )
        self.quitf_signal.connect(self.close)
        self.fullsgame_signal.connect(self._fullsgame)

        self.castkata2hira = str.maketrans(
            static_data["allkata"], static_data["allhira"]
        )
        self.casthira2kata = str.maketrans(
            static_data["allhira"], static_data["allkata"]
        )
        self.isletgamefullscreened = False
        self.fullscreenmanager = fullscreen(self._externalfsend)
        self._isTracking = False
        self.isontop = True
        self._TitleLabel = QLabel(self)
        self._TitleLabel.move(0, 0)
        self.showhidestate = False
        self.processismuteed = False
        self.mousetransparent = False
        self.backtransparent = False
        self.isbindedwindow = False
        self.buttons = []
        self.showbuttons = []
        self.saveiterclasspointer = {}
        self.addbuttons()

        self.translate_text = Textbrowser(self)

        # 翻译框根据内容自适应大小
        self.document = self.translate_text.document()

        self.document.contentsChanged.connect(self.textAreaChanged)
        self.set_color_transparency()
        self.refreshtoolicon()
        self.thistimenotsetop = False

    def set_color_transparency(self):
        self.translate_text.setStyleSheet(
            "border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                            \
                                           background-color: rgba(%s, %s, %s, %s)"
            % (
                int(globalconfig["backcolor"][1:3], 16),
                int(globalconfig["backcolor"][3:5], 16),
                int(globalconfig["backcolor"][5:7], 16),
                globalconfig["transparent"] * (not self.backtransparent) / 100,
            )
        )
        self._TitleLabel.setStyleSheet(
            "border-width: 0;\
                                           border-style: outset;\
                                           border-top: 0px solid #e8f3f9;\
                                           color: white;\
                                           font-weight: bold;\
                                           background-color: rgba(%s, %s, %s, %s)"
            % (
                int(globalconfig["backcolor"][1:3], 16),
                int(globalconfig["backcolor"][3:5], 16),
                int(globalconfig["backcolor"][5:7], 16),
                globalconfig["transparent"] / 200,
            )
        )

    def muteprocessfuntion(self):
        if gobject.baseobject.textsource and gobject.baseobject.textsource.pids:
            self.processismuteed = not self.processismuteed
            self.refreshtoolicon()
            for pid in gobject.baseobject.textsource.pids:
                winsharedutils.SetProcessMute(pid, self.processismuteed)

    def _externalfsend(self):
        self.isletgamefullscreened = False
        self.refreshtooliconsignal.emit()

    def _fullsgame(self):
        if gobject.baseobject.textsource and gobject.baseobject.textsource.hwnd:
            _hwnd = gobject.baseobject.textsource.hwnd
        else:
            _hwnd = windows.GetForegroundWindow()
            _pid = windows.GetWindowThreadProcessId(_hwnd)
            if _pid == os.getpid():
                return
        self.isletgamefullscreened = not self.isletgamefullscreened
        self.refreshtoolicon()
        self.fullscreenmanager(_hwnd, self.isletgamefullscreened)

    def changemousetransparentstate(self, idx):
        if idx == 0:
            self.mousetransparent = not self.mousetransparent

            def _checkplace():
                hwnd = int(int(self.winId()))
                while self.mousetransparent:
                    cursor_pos = self.mapFromGlobal(QCursor.pos())

                    if self.isinrect(
                        cursor_pos,
                        [
                            self._TitleLabel.x(),
                            self._TitleLabel.x() + self._TitleLabel.width(),
                            self._TitleLabel.y(),
                            self._TitleLabel.y() + self._TitleLabel.height(),
                        ],
                    ):

                        windows.SetWindowLong(
                            int(self.winId()),
                            windows.GWL_EXSTYLE,
                            windows.GetWindowLong(hwnd, windows.GWL_EXSTYLE)
                            & ~windows.WS_EX_TRANSPARENT,
                        )
                    else:
                        windows.SetWindowLong(
                            int(self.winId()),
                            windows.GWL_EXSTYLE,
                            windows.GetWindowLong(hwnd, windows.GWL_EXSTYLE)
                            | windows.WS_EX_TRANSPARENT,
                        )
                    if self.isinrect(
                        cursor_pos,
                        [
                            self._TitleLabel.x(),
                            self._TitleLabel.x() + self._TitleLabel.width(),
                            self._TitleLabel.y(),
                            self._TitleLabel.y()
                            + self._TitleLabel.height()
                            + self._padding,
                        ],
                    ):
                        self.entersignal.emit()
                    time.sleep(0.1)
                # 结束时取消穿透(可能以快捷键终止)
                windows.SetWindowLong(
                    int(self.winId()),
                    windows.GWL_EXSTYLE,
                    windows.GetWindowLong(hwnd, windows.GWL_EXSTYLE)
                    & ~windows.WS_EX_TRANSPARENT,
                )

            if self.mousetransparent:
                # globalconfig['locktools']=True #锁定，否则无法恢复。
                threading.Thread(target=_checkplace).start()
        elif idx == 1:
            self.backtransparent = not self.backtransparent
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
        gobject.baseobject.textsource.hwnd = hwnd if pid != _pid else None
        if not globalconfig["sourcestatus2"]["texthook"]["use"]:
            gobject.baseobject.textsource.pids = [pid] if pid != _pid else None
        self.isbindedwindow = pid != _pid
        self.refreshtoolicon()

    def changeshowhideraw(self):
        gobject.baseobject.settin_ui.show_original_switch.click()

    def changeTranslateMode(self):
        globalconfig["autorun"] = not globalconfig["autorun"]
        self.refreshtoolicon()

    def changetoolslockstate(self):
        globalconfig["locktools"] = not globalconfig["locktools"]
        self.refreshtoolicon()

    def textAreaChanged(self):
        if globalconfig["fixedheight"]:
            return
        if self.translate_text.cleared:
            return
        newHeight = self.document.size().height()
        width = self.width()
        self.resize(width, int(5 + newHeight + globalconfig["buttonsize"] * 1.5))

    def clickRange(self, auto):
        if globalconfig["sourcestatus2"]["ocr"]["use"] == False:
            return
        self.showhidestate = False

        rangeselct_function(self, self.afterrange, auto, auto)

    def afterrange(self, rect):
        gobject.baseobject.textsource.newrangeadjustor()
        gobject.baseobject.textsource.setrect(rect)
        self.showhideocrrange()
        if globalconfig["showrangeafterrangeselect"] == False:
            self.showhideocrrange()
        if globalconfig["ocrafterrangeselect"]:
            self.startTranslater()

    def langdu(self):
        gobject.baseobject.readcurrent(force=True)

    def startTranslater(self):
        if gobject.baseobject.textsource:
            threading.Thread(target=gobject.baseobject.textsource.runonce).start()

    def toolbarhidedelay(self):

        for button in self.buttons:
            button.hide()
        self._TitleLabel.hide()

    def enterEvent(self, QEvent):
        self.enterfunction()

    def enterfunction(self):

        for button in self.buttons[-2:] + self.showbuttons:
            button.show()
        self._TitleLabel.show()

        if globalconfig["locktools"]:
            return

        def makerect(_):
            x, y, w, h = _
            return [x, x + w, y, y + h]

        def __(s):
            c = QCursor()
            while self.isinrect(c.pos(), makerect(self.geometry().getRect())):
                time.sleep(0.1)
            time.sleep(0.5)
            if (globalconfig["locktools"] == False) and (
                self.isinrect(c.pos(), makerect(self.geometry().getRect())) == False
            ):
                s.toolbarhidedelaysignal.emit()

        threading.Thread(target=lambda: __(self)).start()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        wh = globalconfig["buttonsize"] * 1.5
        height = self.height() - wh

        self.translate_text.resize(self.width() - 5, height)
        for button in self.buttons[-2:]:
            button.adjast()
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())

    def showhidetoolbuttons(self):
        showed = 0
        self.showbuttons = []

        for i, button in enumerate(self.buttons[:-2]):
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
                    button.hide()
                    continue
            if (
                button.name in globalconfig["toolbutton"]["buttons"]
                and globalconfig["toolbutton"]["buttons"][button.name]["use"] == False
            ):
                button.hide()
                continue

            button.move(showed * button.width(), 0)
            self.showbuttons.append(button)
            # button.show()
            showed += 1
        self.enterEvent(None)

    def callwrap(self, call, _):
        try:
            call()
        except:
            print_exc()

    def takusanbuttons(
        self, _type, clickfunc, adjast=None, tips=None, save=None, belong=None
    ):

        button = QPushButton(self)
        if tips:
            button.setToolTip(_TR(tips))

        style = """
        QPushButton{
          background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;
      }
       
        """
        if _type == 1:
            style += (
                """
            QPushButton:hover{
           background-color: %s;
           border: 0px;
           font: 100 10pt;
            }"""
                % globalconfig["button_color_normal"]
            )
        elif _type == 2:
            style += """
             QPushButton:hover{
           background-color: %s;
           color: white;
           border: 0px;
           font: 100 10pt;
       }""" % (
                globalconfig["button_color_close"]
            )

        button.setStyleSheet(style)

        if clickfunc:
            button.clicked.connect(functools.partial(self.callwrap, clickfunc))
        else:
            button.lower()

        button.name = save
        button.belong = belong
        if adjast < 0:
            button.adjast = lambda: button.move(
                self.width() + adjast * button.width(), 0
            )
        else:
            button.adjast = None
        self.buttons.append(button)

    def closeEvent(self, a0) -> None:
        self.fullscreenmanager.end()
        gobject.baseobject.isrunning = False
        self.tray.hide()
        self.tray = None
        self.hide()

        if gobject.baseobject.textsource:

            gobject.baseobject.textsource = None

        saveallconfig()

        endsubprocs()
        os._exit(0)
