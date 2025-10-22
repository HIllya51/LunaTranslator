from qtsymbols import *
import gobject, os
import qtawesome, NativeUtils, functools, json
from myutils.config import globalconfig, _TR
from myutils.utils import get_time_stamp
from gui.usefulwidget import closeashidewindow, WebviewWidget, Exteditor
from gui.dynalang import LAction
from urllib.parse import quote
from myutils.wrapper import threader
from traceback import print_exc
from gui.setting.display_text import extrahtml
from network.server.servicecollection_1 import WSForEach, transhistwsoutputsave
import time, threading, windows


class somecommon:

    def debugeval(self, js: str): ...

    def calllunaloadready(self):

        self.debugeval(
            "showhideorigin({})".format(int(globalconfig["history"]["showorigin"]))
        )
        self.debugeval(
            "showhidetransname({})".format(
                int(globalconfig["history"]["showtransname"])
            )
        )
        self.debugeval(
            "showhidetrans({})".format(int(globalconfig["history"]["showtrans"]))
        )
        self.debugeval(
            "showhidetime({})".format(int(globalconfig["history"]["showtime"]))
        )
        self.setf()
        self.refresh()

    def refresh(self):
        self.debugeval(
            'fastinit("{}");'.format(quote(json.dumps(gobject.base.transhis.trace)))
        )

    def setf(self):
        key = "histfont"
        fontstring = globalconfig.get(key, "")
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            _style = "font-size:{}pt;".format(_f.pointSize())
            _style += 'font-family:"{}";'.format(_f.family())
            self.debugeval("setfont('body{{{}}}')".format(quote(_style)))

    def addbr(self):
        self.debugeval("addbr();")

    def getnewsentence(self, sentence):
        self.addbr()
        sentence = sentence[1]
        self.debugeval(
            'getnewsentence({},"{}");'.format(sentence[0], quote(sentence[1]))
        )

    def getnewtrans(self, sentence):
        sentence = sentence[1]
        self.debugeval(
            'getnewtrans({},"{}","{}");'.format(
                sentence[0], quote(sentence[1]), quote(sentence[2])
            )
        )

    def showhideraw(self):
        self.debugeval(
            "showhideorigin({})".format(int(globalconfig["history"]["showorigin"]))
        )

    def showtrans(self):
        self.debugeval(
            "showhidetrans({})".format(int(globalconfig["history"]["showtrans"]))
        )

    def showtransname(self):
        self.debugeval(
            "showhidetransname({})".format(
                int(globalconfig["history"]["showtransname"])
            )
        )

    def showhidetime(self):
        self.debugeval(
            "showhidetime({})".format(int(globalconfig["history"]["showtime"]))
        )


class sharedfunctions:
    startuptime = time.time()
    logfilename = "cache/history/{}.txt".format(get_time_stamp(forfilename=True))
    writelogfilelock = threading.Lock()

    @staticmethod
    def autosavecheckifneedninit(trace):
        with sharedfunctions.writelogfilelock:
            text = sharedfunctions.createSaveContent(trace)
            has = os.path.exists(sharedfunctions.logfilename)
            if not text and not has:
                return
            try:
                os.makedirs("cache/history", exist_ok=True)
                with open(
                    sharedfunctions.logfilename,
                    "w",
                    encoding="utf8",
                ) as ff:
                    ff.write(text)
            except:
                print_exc()

    @staticmethod
    def savesrt(self, trace):
        ff = QFileDialog.getSaveFileName(self, directory="save.srt")
        if ff[0] == "":
            return
        _ = sharedfunctions.createSaveContentSrt(trace)
        with open(ff[0], "w", encoding="utf8") as ff:
            ff.write(_)

    @staticmethod
    def savetxt(self, trace):
        ff = QFileDialog.getSaveFileName(self, directory="save.txt")
        if ff[0] == "":
            return
        _ = sharedfunctions.createSaveContent(trace)
        with open(ff[0], "w", encoding="utf8") as ff:
            ff.write(_)

    @staticmethod
    def createSaveContentSrt(hist):
        blocks = []
        block = []
        for line in hist:
            if line[0] == 0:
                if block:
                    blocks.append(block)
                block = []
            block.append(line)
        if block:
            blocks.append(block)
        ii = 1
        results = []

        def formattime(t):
            local_time = time.gmtime(t)
            data_head = time.strftime("%H:%M:%S", local_time)
            data_secs = (t - int(t)) * 1000
            time_stamp = "%s.%03d" % (data_head, data_secs)
            return time_stamp

        blocks.append([(0, (time.time(), 0))])
        for i in range(len(blocks) - 1):
            result = sharedfunctions.visblocksrt(blocks[i])
            if not result:
                continue
            start = formattime(blocks[i][0][1][0] - sharedfunctions.startuptime)
            end = formattime(blocks[i + 1][0][1][0] - sharedfunctions.startuptime)
            result = "{} --> {}\n{}".format(start, end, result)
            results.append("{}\n{}".format(ii, result))
            ii += 1
        return "\n\n".join(results)

    @staticmethod
    def visblocksrt(block):
        result = []
        for line in block:
            ii, line = line
            if ii == 0:
                tm, sentence = line
                if not globalconfig["history"]["showorigin"]:
                    continue
                result.append(sentence)
            elif ii == 1:
                tm, api, sentence = line
                if not globalconfig["history"]["showtrans"]:
                    continue
                if globalconfig["history"]["showtransname"]:
                    sentence = api + " " + sentence
                result.append(sentence)
        if not result:
            return
        return "\n".join(result)

    @staticmethod
    def createSaveContent(hist):
        collect = ""
        seted = False
        for line in hist:
            if seted and (line[0] == 0):
                collect += "\n"
                seted = True
            line = sharedfunctions.visline(line)
            if line:
                if seted:
                    collect += "\n"
                collect += line
                seted = True
        return collect

    @staticmethod
    def ifformatchangedrewriteautosave(trace):
        if not globalconfig["history"]["autosave"]:
            return
        sharedfunctions.autosavecheckifneedninit(trace)

    @staticmethod
    def autosave(line):
        if not globalconfig["history"]["autosave"]:
            return
        l = sharedfunctions.visline(line)
        with sharedfunctions.writelogfilelock:
            has = os.path.exists(sharedfunctions.logfilename)
            out = ""
            if line[0] == 0:
                if has:
                    out += "\n"
            if l:
                if has:
                    out += "\n"
                out += l
            try:
                if out:
                    os.makedirs("cache/history", exist_ok=True)
                    with open(
                        sharedfunctions.logfilename,
                        "a",
                        encoding="utf8",
                    ) as ff:
                        ff.write(out)
            except:
                print_exc()

    @staticmethod
    def visline(line):
        ii, line = line
        if ii == 0:
            tm, sentence = line
            if not globalconfig["history"]["showorigin"]:
                return
            else:
                if globalconfig["history"]["showtime"]:
                    sentence = get_time_stamp(tm) + " " + sentence
                return sentence
        elif ii == 1:
            tm, api, sentence = line
            if not globalconfig["history"]["showtrans"]:
                return
            if globalconfig["history"]["showtransname"]:
                sentence = api + " " + sentence
            if globalconfig["history"]["showtime"]:
                sentence = get_time_stamp(tm) + " " + sentence
            return sentence


class wvtranshist(WebviewWidget, somecommon):
    pluginsedit = pyqtSignal()
    reloadx = pyqtSignal()

    def scrollend(self):
        self.debugeval("scrollend()")

    def autosavecb(self):
        globalconfig["history"]["autosave"] = not globalconfig["history"]["autosave"]
        if globalconfig["history"]["autosave"]:
            sharedfunctions.autosavecheckifneedninit(self.p.trace)

    def __init__(self, p):
        super().__init__(p, loadext=globalconfig["history"]["webviewLoadExt"])
        self.bind("calllunaloadready", self.calllunaloadready)
        self.pluginsedit.connect(functools.partial(Exteditor, self))
        self.reloadx.connect(self.appendext)
        nexti = self.add_menu_noselect(0, lambda: _TR("清空"), self.clear)
        nexti = self.add_menu_noselect(nexti, lambda: _TR("滚动到最后"), self.scrollend)
        nexti = self.add_menu_noselect(nexti, lambda: _TR("字体"), self.seletcfont)
        nexti = self.add_menu_noselect(nexti)
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("保存"),
            lambda: sharedfunctions.savetxt(self, self.p.trace),
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("保存_SRT"),
            lambda: sharedfunctions.savesrt(self, self.p.trace),
            getuse=lambda: windows.GetKeyState(windows.VK_CONTROL) < 0,
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("自动保存"),
            self.autosavecb,
            getchecked=lambda: globalconfig["history"]["autosave"],
        )
        nexti = self.add_menu_noselect(nexti)
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示原文"),
            self.showhideraw_,
            getchecked=lambda: globalconfig["history"]["showorigin"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示翻译"),
            self.showtrans_,
            getchecked=lambda: globalconfig["history"]["showtrans"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示翻译器名称"),
            self.showtransname_,
            getchecked=lambda: globalconfig["history"]["showtransname"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示时间"),
            self.showhidetime_,
            getchecked=lambda: globalconfig["history"]["showtime"],
        )
        nexti = self.add_menu_noselect(nexti)

        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("使用Webview2显示"),
            self.useweb,
            getchecked=lambda: globalconfig["history"]["usewebview2"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("附加HTML"),
            functools.partial(
                extrahtml,
                self,
                "extrahtml_transhist.html",
                r"LunaTranslator\htmlcode\uiwebview\extrahtml\transhist.html",
                self,
            ),
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("附加浏览器插件"),
            threader(self.reloadx.emit),
            getchecked=lambda: globalconfig["history"]["webviewLoadExt"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("浏览器插件"),
            threader(self.pluginsedit.emit),
            getuse=lambda: globalconfig["history"]["webviewLoadExt"],
        )
        nexti = self.add_menu_noselect(nexti)

        nexti = self.add_menu(
            0,
            lambda: _TR("查词"),
            threader(
                lambda w: gobject.base.searchwordW.search_word.emit(
                    w.replace("\n", "").strip(), None, False
                )
            ),
        )
        nexti = self.add_menu(nexti, lambda: _TR("翻译"), gobject.base.textgetmethod)
        nexti = self.add_menu(nexti, lambda: _TR("朗读"), gobject.base.read_text)
        nexti = self.add_menu(nexti)
        self.loadex()

    def loadex(self, extra=None):
        self.navigate(self.loadex_(extra=extra))

    @staticmethod
    def loadex_(extra=None):
        if not extra:
            extra = wvtranshist.loadextra()
        basepath = r"LunaTranslator\htmlcode\uiwebview\transhist.html"
        if not extra:
            return os.path.abspath(basepath)
        with open(basepath, "r", encoding="utf8") as ff:
            html = ff.read() + extra
        path = gobject.gettempdir("transhist.html")
        with open(path, "w", encoding="utf8") as ff:
            ff.write(html)
        return os.path.abspath(path)

    @staticmethod
    def loadextra():
        for _ in [
            gobject.getconfig("extrahtml_transhist.html"),
            r"LunaTranslator\htmlcode\uiwebview\extrahtml\transhist.html",
        ]:
            if not os.path.exists(_):
                continue
            with open(_, "r", encoding="utf8") as ff:
                return ff.read()

    def seletcfont(self):
        f = QFont()
        cur = globalconfig.get("histfont")
        if cur:
            f.fromString(cur)
        font, ok = QFontDialog.getFont(f, self)
        if ok:
            _s = font.toString()
            globalconfig["histfont"] = _s
            self.setf()
            self.p.setf()

    def appendext(self):
        globalconfig["history"]["webviewLoadExt"] = not globalconfig["history"][
            "webviewLoadExt"
        ]
        self.p.loadviewer()

    def useweb(self):
        globalconfig["history"]["usewebview2"] = not globalconfig["history"][
            "usewebview2"
        ]
        self.p.loadviewer()

    def clear(self, _=None):
        self.debugeval("clear()")
        self.p.trace.clear()

    def debugeval(self, js):
        # print(js)
        self.eval(js)

    def showhideraw_(self):
        globalconfig["history"]["showorigin"] = not globalconfig["history"][
            "showorigin"
        ]
        self.showhideraw()
        self.p.showhideraw()

    def showtrans_(self):
        globalconfig["history"]["showtrans"] = not globalconfig["history"]["showtrans"]
        self.showtrans()
        self.p.showtrans()

    def showtransname_(self):
        globalconfig["history"]["showtransname"] = not globalconfig["history"][
            "showtransname"
        ]
        self.showtransname()
        self.p.showtransname()

    def showhidetime_(self):
        globalconfig["history"]["showtime"] = not globalconfig["history"]["showtime"]
        self.showhidetime()
        self.p.showhidetime()

    @property
    def p(self) -> "transhist":
        return self.parent()


class Qtranshist(QPlainTextEdit):
    @property
    def p(self) -> "transhist":
        return self.parent()

    def __init__(self, p):
        super().__init__(p)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        self.setUndoRedoEnabled(False)
        self.setReadOnly(True)
        self.setf()
        self.refresh()

    def showmenu(self, _):
        menu = QMenu(self)
        qingkong = LAction("清空", menu)
        baocun = LAction("保存", menu)
        baocunauto = LAction("自动保存", menu)
        baocunauto.setCheckable(True)
        baocunauto.setChecked(globalconfig["history"]["autosave"])
        baocunfmt = LAction("保存_SRT", menu)
        tts = LAction("朗读", menu)
        copy = LAction("复制", menu)
        hideshowraw = LAction("显示原文", menu)
        hideshowraw.setCheckable(True)
        hideshowraw.setChecked(globalconfig["history"]["showorigin"])
        hideshowtrans = LAction("显示翻译", menu)
        hideshowtrans.setCheckable(True)
        hideshowtrans.setChecked(globalconfig["history"]["showtrans"])
        hideshowtransname = LAction("显示翻译器名称", menu)
        hideshowtransname.setCheckable(True)
        hideshowtransname.setChecked(globalconfig["history"]["showtransname"])
        hidetime = LAction("显示时间", menu)
        hidetime.setCheckable(True)
        hidetime.setChecked(globalconfig["history"]["showtime"])
        scrolltoend = LAction("滚动到最后", menu)
        font = LAction("字体", menu)
        search = LAction("查词", menu)
        translate = LAction("翻译", menu)
        webview2qt = LAction("使用Webview2显示", menu)
        webview2qt.setCheckable(True)
        webview2qt.setChecked(globalconfig["history"]["usewebview2"])
        if len(self.textCursor().selectedText()):
            menu.addAction(copy)
            menu.addAction(search)
            menu.addAction(translate)
            menu.addAction(tts)
        else:
            menu.addAction(qingkong)
            menu.addAction(scrolltoend)
            menu.addAction(font)
            menu.addSeparator()
            menu.addAction(baocun)
            if windows.GetKeyState(windows.VK_CONTROL) < 0:
                menu.addAction(baocunfmt)
            menu.addAction(baocunauto)
            menu.addSeparator()
            menu.addAction(hideshowraw)
            menu.addAction(hideshowtrans)
            menu.addAction(hideshowtransname)
            menu.addAction(hidetime)
            menu.addSeparator()
            menu.addAction(webview2qt)

        action = menu.exec(QCursor.pos())
        if action == qingkong:
            self.clear()
            self.p.trace.clear()
        elif action == baocunfmt:
            sharedfunctions.savesrt(self, self.p.trace)
        elif action == webview2qt:
            globalconfig["history"]["usewebview2"] = webview2qt.isChecked()
            self.p.loadviewer(True)
        elif action == baocunauto:
            globalconfig["history"]["autosave"] = baocunauto.isCheckable()
            if baocunauto.isCheckable():
                sharedfunctions.autosavecheckifneedninit(self.p.trace)
        elif action == search:
            gobject.base.searchwordW.search_word.emit(
                self.textCursor().selectedText(), None, False
            )
        elif action == translate:
            gobject.base.textgetmethod(self.textCursor().selectedText(), False)
        elif action == tts:
            gobject.base.read_text(self.textCursor().selectedText())
        elif action == copy:
            NativeUtils.ClipBoard.text = self.textCursor().selectedText()
        elif action == baocun:
            sharedfunctions.savetxt(self, self.p.trace)
        elif action == font:
            f = QFont()
            cur = globalconfig.get("histfont")
            if cur:
                f.fromString(cur)
            font, ok = QFontDialog.getFont(f, self)
            if ok:
                _s = font.toString()
                globalconfig["histfont"] = _s
                self.setf()
                self.p.setf()
        elif action == hideshowtransname:
            globalconfig["history"]["showtransname"] = hideshowtransname.isChecked()
            self.p.showtransname()
            self.refresh()
        elif action == hideshowtrans:
            globalconfig["history"]["showtrans"] = hideshowtrans.isChecked()
            self.p.showtrans()
            self.refresh()
        elif action == hideshowraw:
            globalconfig["history"]["showorigin"] = hideshowraw.isChecked()
            self.p.showhideraw()
            self.refresh()
        elif action == hidetime:
            globalconfig["history"]["showtime"] = hidetime.isChecked()
            self.p.showhidetime()
            self.refresh()
        elif action == scrolltoend:
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def setf(self):
        key = "histfont"
        fontstring = globalconfig.get(key, "")
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            _style = "font-size:{}pt;".format(_f.pointSize())
            _style += 'font-family:"{}";'.format(_f.family())
            self.setStyleSheet("QPlainTextEdit{" + _style + "}")

    def refresh(self):
        collect = sharedfunctions.createSaveContent(self.p.trace)
        self.setPlainText(collect)
        self.move_cursor_to_end()

    def move_cursor_to_end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def getnewsentence(self, sentence):
        self.appendPlainText("")
        line = sharedfunctions.visline(sentence)
        if line:
            self.appendPlainText(line)

    def getnewtrans(self, sentence):
        line = sharedfunctions.visline(sentence)
        if line:
            self.appendPlainText(line)


class transhist(closeashidewindow):

    getnewsentencesignal = pyqtSignal(str)
    getnewtranssignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(transhist, self).__init__(parent, globalconfig["hist_geo"])
        self.trace = []
        self.textOutput = None
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.getnewtranssignal.connect(self.getnewtrans)
        self.setWindowTitle("历史文本")
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"))
        self.state = 0

    def __load(self):
        if self.state != 0:
            return
        self.state = 1
        self.loadviewer()
        self.state = 2

    def showEvent(self, e):
        super().showEvent(e)
        self.__load()

    def setf(self):
        WSForEach(transhistwsoutputsave, lambda _: _.setf())

    def showtransname(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showtransname())
        sharedfunctions.ifformatchangedrewriteautosave(self.trace)

    def showhidetime(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showhidetime())
        sharedfunctions.ifformatchangedrewriteautosave(self.trace)

    def showtrans(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showtrans())
        sharedfunctions.ifformatchangedrewriteautosave(self.trace)

    def showhideraw(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showhideraw())
        sharedfunctions.ifformatchangedrewriteautosave(self.trace)

    def getnewsentence(self, sentence):
        tm = time.time()
        line = (0, (tm, sentence))
        self.trace.append(line)
        sharedfunctions.autosave(line)
        if self.state == 2:
            self.textOutput.getnewsentence(self.trace[-1])
        WSForEach(transhistwsoutputsave, lambda _: _.getnewsentence(self.trace[-1]))

    def getnewtrans(self, api, sentence):
        tm = time.time()
        line = (1, (tm, api, sentence))
        self.trace.append(line)
        sharedfunctions.autosave(line)
        if self.state == 2:
            self.textOutput.getnewtrans(self.trace[-1])
        WSForEach(transhistwsoutputsave, lambda _: _.getnewtrans(self.trace[-1]))

    def loadviewer(self, shoudong=False):
        if self.textOutput:
            self.textOutput.hide()
            self.textOutput.deleteLater()
        if globalconfig["history"]["usewebview2"]:
            try:
                self.textOutput = wvtranshist(self)
            except Exception as e:
                print_exc()
                if shoudong:
                    WebviewWidget.showError(e)
                globalconfig["history"]["usewebview2"] = False
                self.textOutput = Qtranshist(self)
        else:
            self.textOutput = Qtranshist(self)
        self.setCentralWidget(self.textOutput)
