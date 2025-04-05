from qtsymbols import *
import gobject, os
import qtawesome, winsharedutils, functools, json
from myutils.config import globalconfig, _TR
from myutils.utils import get_time_stamp
from gui.usefulwidget import closeashidewindow, WebviewWidget, Exteditor
from gui.dynalang import LAction
from urllib.parse import quote
from myutils.wrapper import threader
from traceback import print_exc
from gui.setting.display_text import extrahtml
from services.servicecollection_1 import WSForEach, transhistwsoutputsave


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
            'fastinit("{}");'.format(
                quote(json.dumps(gobject.baseobject.transhis.trace))
            )
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
            'getnewsentence("{}","{}");'.format(quote(sentence[0]), quote(sentence[1]))
        )

    def getnewtrans(self, sentence):
        sentence = sentence[1]
        self.debugeval(
            'getnewtrans("{}","{}","{}");'.format(
                quote(sentence[0]), quote(sentence[1]), quote(sentence[2])
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


class wvtranshist(WebviewWidget, somecommon):
    pluginsedit = pyqtSignal()
    reloadx = pyqtSignal()

    def scrollend(self):
        self.debugeval("scrollend()")

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
            lambda: _TR("显示原文"),
            self.showhideraw_,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showorigin"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示翻译"),
            self.showtrans_,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showtrans"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示翻译器名称"),
            self.showtransname_,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showtransname"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("显示时间"),
            self.showhidetime_,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showtime"],
        )
        nexti = self.add_menu_noselect(nexti)

        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("使用Webview2显示"),
            self.useweb,
            True,
            getchecked=lambda: globalconfig["history"]["usewebview2"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("附加HTML"),
            functools.partial(
                extrahtml,
                self,
                "extrahtml_transhist.html",
                r"files\html\uiwebview\extrahtml\transhist.html",
                self,
            ),
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("附加浏览器插件"),
            threader(self.reloadx.emit),
            True,
            getchecked=lambda: globalconfig["history"]["webviewLoadExt"],
        )
        nexti = self.add_menu_noselect(
            nexti,
            lambda: _TR("浏览器插件"),
            threader(self.pluginsedit.emit),
            False,
            getuse=lambda: globalconfig["history"]["webviewLoadExt"],
        )
        nexti = self.add_menu_noselect(nexti)

        nexti = self.add_menu(
            0,
            lambda: _TR("查词"),
            threader(
                lambda w: gobject.baseobject.searchwordW.search_word.emit(
                    w.replace("\n", "").strip(), False
                )
            ),
        )
        nexti = self.add_menu(
            nexti, lambda: _TR("翻译"), gobject.baseobject.textgetmethod
        )
        nexti = self.add_menu(nexti, lambda: _TR("朗读"), gobject.baseobject.read_text)
        nexti = self.add_menu(nexti)
        self.loadex()

    def loadex(self, extra=None):
        self.navigate(self.loadex_(extra=extra))

    @staticmethod
    def loadex_(extra=None):
        if not extra:
            extra = wvtranshist.loadextra()
        basepath = r"files\html\uiwebview\transhist.html"
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
            "userconfig/extrahtml_transhist.html",
            r"files\html\uiwebview\extrahtml\transhist.html",
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
            self.parent().setf()

    def appendext(self):
        globalconfig["history"]["webviewLoadExt"] = not globalconfig["history"][
            "webviewLoadExt"
        ]
        self.parent().loadviewer()

    def useweb(self):
        globalconfig["history"]["usewebview2"] = not globalconfig["history"][
            "usewebview2"
        ]
        self.parent().loadviewer()

    def clear(self, _=None):
        self.debugeval("clear()")
        self.parent().trace.clear()

    def debugeval(self, js):
        # print(js)
        self.eval(js)

    def showhideraw_(self):
        globalconfig["history"]["showorigin"] = not globalconfig["history"][
            "showorigin"
        ]
        self.showhideraw()
        self.parent().showhideraw()

    def showtrans_(self):
        globalconfig["history"]["showtrans"] = not globalconfig["history"]["showtrans"]
        self.showtrans()
        self.parent().showtrans()

    def showtransname_(self):
        globalconfig["history"]["showtransname"] = not globalconfig["history"][
            "showtransname"
        ]
        self.showtransname()
        self.parent().showtransname()

    def showhidetime_(self):
        globalconfig["history"]["showtime"] = not globalconfig["history"]["showtime"]
        self.showhidetime()
        self.parent().showhidetime()


class Qtranshist(QPlainTextEdit):
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
            menu.addAction(baocun)
            menu.addAction(scrolltoend)
            menu.addAction(font)
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
            self.parent().trace.clear()
        elif action == webview2qt:
            globalconfig["history"]["usewebview2"] = webview2qt.isChecked()
            self.parent().loadviewer(True)
        elif action == search:
            gobject.baseobject.searchwordW.search_word.emit(
                self.textCursor().selectedText(), False
            )
        elif action == translate:
            gobject.baseobject.textgetmethod(self.textCursor().selectedText(), False)
        elif action == tts:
            gobject.baseobject.read_text(self.textCursor().selectedText())
        elif action == copy:
            winsharedutils.clipboard_set(self.textCursor().selectedText())
        elif action == baocun:
            ff = QFileDialog.getSaveFileName(self, directory="save.txt")
            if ff[0] == "":
                return
            with open(ff[0], "w", encoding="utf8") as ff:
                ff.write(self.toPlainText())
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
                self.parent().setf()
        elif action == hideshowtransname:
            globalconfig["history"]["showtransname"] = hideshowtransname.isChecked()
            self.parent().showtransname()
            self.refresh()
        elif action == hideshowtrans:
            globalconfig["history"]["showtrans"] = hideshowtrans.isChecked()
            self.parent().showtrans()
            self.refresh()
        elif action == hideshowraw:
            globalconfig["history"]["showorigin"] = hideshowraw.isChecked()
            self.parent().showhideraw()
            self.refresh()
        elif action == hidetime:
            globalconfig["history"]["showtime"] = hidetime.isChecked()
            self.parent().showhidetime()
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
        collect = ""
        seted = False
        for i, line in enumerate(self.parent().trace):
            if seted and (len(line[1]) == 2):
                collect += "\n"
                seted = True
            line = self.visline(line)
            if line:
                if seted:
                    collect += "\n"
                collect += line
                seted = True
        self.setPlainText(collect)
        self.move_cursor_to_end()

    def move_cursor_to_end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def visline(self, line):
        ii, line = line
        if ii == 0:
            tm, sentence = line
            if not globalconfig["history"]["showorigin"]:
                return
            else:
                if globalconfig["history"]["showtime"]:
                    sentence = tm + " " + sentence
                return sentence
        elif ii == 1:
            tm, api, sentence = line
            if not globalconfig["history"]["showtrans"]:
                return
            if globalconfig["history"]["showtransname"]:
                sentence = api + " " + sentence
            if globalconfig["history"]["showtime"]:
                sentence = tm + " " + sentence
            return sentence

    def getnewsentence(self, sentence):
        self.appendPlainText("")
        line = self.visline(sentence)
        if line:
            self.appendPlainText(line)

    def getnewtrans(self, sentence):
        line = self.visline(sentence)
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

    def showhidetime(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showhidetime())

    def showtrans(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showtrans())

    def showhideraw(self):
        WSForEach(transhistwsoutputsave, lambda _: _.showhideraw())

    def getnewsentence(self, sentence):
        tm = get_time_stamp()
        self.trace.append((0, (tm, sentence)))
        if self.state == 2:
            self.textOutput.getnewsentence(self.trace[-1])
        WSForEach(transhistwsoutputsave, lambda _: _.getnewsentence(self.trace[-1]))

    def getnewtrans(self, api, sentence):
        tm = get_time_stamp()
        self.trace.append((1, (tm, api, sentence)))
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
