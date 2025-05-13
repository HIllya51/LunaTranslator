from qtsymbols import *
import gobject, qtawesome, os, json, functools, uuid
import NativeUtils, re
from myutils.config import globalconfig, get_launchpath, savehook_new_data
from myutils.wrapper import Singleton
from myutils.utils import getimagefilefilter, getimageformat, loopbackrecorder, _TR
from gui.rangeselect import rangeselct_function
from myutils.ocrutil import imageCut
from myutils.mecab import mecab
from gui.inputdialog import autoinitdialog
from myutils.hwnd import grabwindow, getExeIcon
from gui.usefulwidget import (
    saveposwindow,
    makesubtab_lazy,
    mayberelpath,
    IconButton,
    auto_select_webview,
)
from gui.dynalang import LAction
from gui.markdownhighlighter import MarkdownHighlighter


class HtmlPlainTextEdit(QTextEdit):

    def contextMenuEvent(self, event: QContextMenuEvent):
        data = QApplication.clipboard().mimeData()
        if not (data.hasHtml() and not data.hasImage()):
            return super().contextMenuEvent(event)
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        custom_action = LAction("粘贴纯文本", self)
        custom_action.setShortcut("Ctrl+Shift+V")
        custom_action.triggered.connect(self.handle_custom_action)
        menu.addAction(custom_action)

        menu.exec_(event.globalPos())

    def handle_custom_action(self):
        self.insertPlainText(NativeUtils.ClipBoard.text)

    def __init__(self, ref: str):
        self.ref = os.path.dirname(ref)
        super().__init__()
        try:
            self.setTabStopDistance(self.fontMetrics().size(0, " ").width() * 8)
        except:
            self.setTabStopWidth(self.fontMetrics().size(0, " ").width() * 8)
        self.upper_shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.upper_shortcut.activated.connect(self.handle_custom_action)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hl = MarkdownHighlighter(self)

    def createMimeDataFromSelection(self) -> QMimeData:
        mime_data = super().createMimeDataFromSelection()
        if mime_data is not None:
            text = mime_data.text()
            mime_data = QMimeData()
            mime_data.setText(text)
        return mime_data

    def insertFromMimeData(self, source: QMimeData):

        if source.hasImage():
            image: QImage = source.imageData()
            p = os.path.join(self.ref, str(uuid.uuid4()) + ".webp")
            image.save(p)
            fn = os.path.basename(p)
            source = QMimeData()
            source.setText("\n![img]({})\n".format(fn))
        elif source.hasHtml():
            html = source.html()
            if html.startswith("<html>"):
                html = html[6:]
            if html.startswith("\n"):
                html = html[1:]
            if html.startswith("<body>"):
                html = html[6:]
            if html.startswith("\n"):
                html = html[1:]
            if html.endswith("</html>"):
                html = html[:-7]
            if html.endswith("\n"):
                html = html[:-1]
            if html.endswith("</body>"):
                html = html[:-7]
            if html.endswith("\n"):
                html = html[:-1]

            source = QMimeData()
            source.setText("\n{}\n".format(html))
        super().insertFromMimeData(source)


def convert_newlines(text):
    # 修改markdown规则，使其更符合非计算机人员直觉
    # 对于```code```，不进行修改
    # 对于一个\n，直接替换成\n\n，使其满足markdown换行语法
    # 对于两个\n\n，不进行修改，以使得大部分正确语法的markdown格式得以保持
    # 两个以上\n，插入n-2个<br>来便捷的进行换行。

    # 例外：
    # | MD_FLAG_TABLES
    # [ 图标
    # - MD_FLAG_TASKLISTS

    parts = re.split(r"(```.*?```)", text, flags=re.DOTALL)

    processed_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            processed_parts.append(part)
            continue

        laststart = [0]

        def replace_newlines(laststart: "list[int]", match: re.Match):
            thisline: str = match.string[laststart[0] : match.start()]
            laststart[0] = match.end()

            if thisline.startswith(("[", "|")):
                return match.group(0)
            if re.match(" *-", thisline):
                # MD_FLAG_TASKLISTS
                return match.group(0)

            n = len(match.group(0))
            if n == 1:
                return "\n\n"
            else:
                return "\n\n" + "\n\n<br>\n\n" * (n - 2)

        part = re.sub(r"\n+", functools.partial(replace_newlines, laststart), part)
        processed_parts.append(part)
    return "".join(processed_parts)


def parsetasklistcheckbox(md: str):
    # MD_FLAG_TASKLISTS
    # 解析不太正确，修复一下。
    md = md.replace(
        '<input type="checkbox" class="task-list-item-checkbox" disabled checked><p>',
        '<p><input type="checkbox" class="task-list-item-checkbox" disabled checked>',
    )
    md = md.replace(
        '<input type="checkbox" class="task-list-item-checkbox" disabled><p>',
        '<p><input type="checkbox" class="task-list-item-checkbox" disabled>',
    )
    return md


class editswitchTextBrowserEx(QWidget):
    textChanged = pyqtSignal(str)

    def delayload(self, i):
        if i == 1 and self.readoreditstack.count() == 1:
            self.browser = auto_select_webview(self, loadex=False)
            self.readoreditstack.addWidget(self.browser)
            self.switch(i)

    def switch(self, i):
        if i == 1:
            if os.path.isfile(self.fn):
                with open(self.fn, "r", encoding="utf8") as ff:
                    text = ff.read()
                self.__markdown(text)
            else:
                self.browser.setHtml("")

    def __markdown(self, text: str):
        with open(
            "files/static/github-markdown-css/template.html", "r", encoding="utf8"
        ) as ff:
            template = ff.read()
        md = parsetasklistcheckbox(NativeUtils.Markdown2Html(convert_newlines(text)))
        md = template.replace("__MARKDOWN__BODY__", md)
        with open(self.cache, "w", encoding="utf8") as ff:
            ff.write(md)
        self.browser.navigate(self.cache)

    def textchanged(self, text):
        self.textChanged.emit(text)

    def __init__(self, parent: "dialog_memory", fn: str, config: dict):
        super().__init__(parent)
        self.browser = None
        self.parent1 = parent
        self.fn = fn
        readoreditstack = QStackedWidget()
        self.cache = self.fn + ".cache.html"
        self.readoreditstack = readoreditstack
        readoreditstack.currentChanged.connect(self.switch)
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(readoreditstack)
        self.editstack = HtmlPlainTextEdit(ref=self.fn)
        self.editstack.textChanged.connect(
            lambda: self.textchanged(self.editstack.toPlainText())
        )
        readoreditstack.addWidget(self.editstack)
        try:
            with open(fn, "r", encoding="utf8") as ff:
                text = ff.read()
        except:
            text = ""
        self.settext(text)
        self.textChanged.connect(functools.partial(self.save, fn))
        self.delayload(1 - config.get("edit", True))
        self.readoreditstack.setCurrentIndex(1 - config.get("edit", True))

    def save(self, fn, text) -> None:
        with open(fn, "w", encoding="utf8") as ff:
            ff.write(text)
        if self.readoreditstack.currentIndex() == 1:
            self.__markdown(text)

    def settext(self, text):
        self.editstack.setPlainText(text)

    def text(self):
        return self.editstack.toPlainText()

    @property
    def sourcefile(self):
        if self.readoreditstack.currentIndex() == 1:
            return self.cache
        else:
            return self.fn

    def sourcefileopen(self):
        f = self.sourcefile
        if not os.path.isfile(f):
            with open(f, "w") as ff:
                pass
        os.startfile(f)


@Singleton
class dialog_memory(saveposwindow):
    # _sigleton=False

    def prepare(self):
        self.rwpath = gobject.getuserconfigdir("memory/{}".format(self.gameuid))
        try:
            with open(
                os.path.join(self.rwpath, "config.json"), "r", encoding="utf8"
            ) as ff:
                self.config = json.load(ff)
        except:
            self.config = []
        os.makedirs(self.rwpath, exist_ok=True)
        rwpath = gobject.getuserconfigdir("memory/{}.html".format(self.gameuid))
        if os.path.isfile(rwpath):
            try:
                os.rename(rwpath, os.path.join(self.rwpath, "0.html"))
                self.config.append({"title": "  0  ", "file": "0.html"})
            except:
                pass

    def createview(self, config: dict, i, lay: QHBoxLayout):

        fn = os.path.join(self.rwpath, config.get("file", str(i) + ".md"))
        showtext = editswitchTextBrowserEx(self, fn, config)
        lay.addWidget(showtext)

    def createnewconfig(self, i):
        self.config.insert(i, {"file": str(i) + ".md", "title": "  {}  ".format(i)})
        self.saveconfig()
        return self.config[i]

    def saveconfig(self):
        try:
            with open(
                os.path.join(self.rwpath, "config.json"), "w", encoding="utf8"
            ) as ff:
                json.dump(self.config, ff)
        except:
            pass

    @property
    def gameuid(self):
        if self._gameuid:
            return self._gameuid
        return 0 if self.xx else gobject.baseobject.gameuid

    def __init__(self, parent, x=False, gameuid=None) -> None:
        self.xx = x
        self._gameuid = gameuid
        super().__init__(
            parent,
            flags=Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinMaxButtonsHint,
            poslist=globalconfig["memorydialoggeo"],
        )
        self.setWindowTitle(
            "备忘录"
            + (
                ("_-_[[{}]]".format(savehook_new_data[self.gameuid]["title"]))
                if self.gameuid
                else ""
            )
        )
        self.prepare()
        self.setWindowIcon(
            getExeIcon(get_launchpath(self.gameuid), cache=True)
            if self.gameuid
            else qtawesome.icon(globalconfig["toolbutton"]["buttons"]["memory"]["icon"])
        )
        self.buttons = QWidget()
        self.buttonslayout = QHBoxLayout(self.buttons)
        self.buttonslayout.setContentsMargins(0, 0, 0, 0)
        self.buttonslayout.setSpacing(0)
        self.btnplus = IconButton(parent=self, icon="fa.plus")
        self.btnplus.clicked.connect(self._plus)
        self.switch = IconButton(
            parent=self, icon="fa.edit", checkable=True, tips="编辑_/_查看"
        )
        self.switch.setChecked(True)
        self.switch.clicked.connect(self.switchreadonly)
        self.insertpicbtn = IconButton(
            parent=self, icon="fa.picture-o", tips="插入图片"
        )
        self.insertaudiobtn = IconButton(parent=self, icon="fa.music", tips="插入音频")
        self.insertaudiobtnisrecoding = False
        self.textbtn = IconButton(parent=self, icon="fa.text-height", tips="插入文本")
        openfile = IconButton(parent=self, icon="fa.external-link", tips="打开文件")
        openfile.clicked.connect(lambda: self.editororview.sourcefileopen())
        self.buttonslayout.addWidget(self.textbtn)
        self.buttonslayout.addWidget(self.insertaudiobtn)
        self.buttonslayout.addWidget(self.insertpicbtn)
        self.buttonslayout.addWidget(self.switch)
        self.buttonslayout.addWidget(openfile)
        self.insertpicbtn.clicked.connect(self.Picselect)
        self.insertaudiobtn.clicked.connect(self.AudioSelect)
        self.textbtn.clicked.connect(self.TextInsert)
        self.tab = makesubtab_lazy(
            titles=list(_.get("title", str(i)) for i, _ in enumerate(self.config)),
            functions=list(
                functools.partial(self.createview, _, i)
                for i, _ in enumerate(self.config)
            ),
        )
        self.tab.setUpdatesEnabled(True)
        self.tab.currentChanged.connect(self._add_trace)
        self.tab.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab.tabBar().customContextMenuRequested.connect(self.tabmenu)
        self.tab.setCornerWidget(self.buttons)
        self.tab.setCornerWidget(self.btnplus, Qt.Corner.TopLeftCorner)
        self.setCentralWidget(self.tab)
        self._add_trace(0)
        self.show()

    def startorendrecord(self, btn: QPushButton, idx):
        if idx:
            try:

                def safestop(recored: loopbackrecorder):
                    recored.stop()

                self.recorders = loopbackrecorder()
                self.destroyed.connect(functools.partial(safestop, self.recorders))
            except Exception as e:
                self.recorders = None
                QMessageBox.critical(self, _TR("错误"), str(e))
                btn.click()
                return
        else:
            if not self.recorders:
                return
            file = self.recorders.stop_save()
            self.recorders = None
            self.audiocallback(file)

    def AudioSelect(self):
        if self.insertaudiobtnisrecoding:
            self.startorendrecord(self.insertaudiobtn, False)
            self.insertaudiobtnisrecoding = False
            return
        menu = QMenu(self)
        record = LAction("录音", menu)
        audio = LAction("音频", menu)
        record.setIcon(qtawesome.icon("fa.microphone"))
        audio.setIcon(qtawesome.icon("fa.folder-open"))
        menu.addAction(record)
        menu.addAction(audio)
        action = menu.exec(QCursor.pos())
        if action == record:
            self.insertaudiobtnisrecoding = True
            self.startorendrecord(self.insertaudiobtn, True)
            self.insertaudiobtn.setIcon(qtawesome.icon("fa.stop"))
        elif action == audio:
            f = QFileDialog.getOpenFileName()
            res = f[0]
            self.audiocallback(res)

    def audiocallback(self, path):
        if not path:
            return
        tgt = os.path.join(self.rwpath, os.path.basename(path))
        os.rename(path, tgt)
        tgt = mayberelpath(tgt)
        html = """\n<audio controls src="{}"></audio>\n""".format(
            os.path.basename(path)
        )
        self.editor.insertPlainText(html)

    def Picselect(self):
        menu = QMenu(self)
        crop = LAction("截图", menu)
        crop2 = LAction("隐藏并截图", menu)
        crophwnd = LAction("窗口截图_gdi", menu)
        crophwnd2 = LAction("窗口截图_winrt", menu)
        select = LAction("图片", menu)
        crop.setIcon(qtawesome.icon("fa.crop"))
        crop2.setIcon(qtawesome.icon("fa.crop"))
        crophwnd.setIcon(qtawesome.icon("fa.camera"))
        crophwnd2.setIcon(qtawesome.icon("fa.camera"))
        select.setIcon(qtawesome.icon("fa.folder-open"))
        menu.addAction(crop)
        menu.addAction(crop2)
        menu.addAction(crophwnd)
        menu.addAction(crophwnd2)
        menu.addAction(select)
        action = menu.exec(QCursor.pos())
        if action == crop:
            self.crophide()
        elif action == crop2:
            self.crophide(s=True)
        elif action == crophwnd:
            grabwindow(getimageformat(), self.cropcallback, usewgc=False)
        elif action == crophwnd2:
            grabwindow(getimageformat(), self.cropcallback, usewgc=True)
        elif action == select:
            f = QFileDialog.getOpenFileName(filter=getimagefilefilter())
            res = f[0]
            self.cropcallback(res)

    def crophide(self, s=False):
        currpos = gobject.baseobject.translation_ui.pos()
        currpos2 = self.window().pos()
        if s:
            self.window().move(-9999, -9999)
            gobject.baseobject.translation_ui.move(-9999, -9999)

        def ocroncefunction(rect, img=None):
            if not img:
                img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            if img.isNull():
                return
            fname = gobject.gettempdir(str(uuid.uuid4()) + "." + getimageformat())
            img.save(fname)
            self.cropcallback(fname)

        def __ocroncefunction(rect, img=None):
            ocroncefunction(rect, img=img)
            if s:
                gobject.baseobject.translation_ui.move(currpos)
                self.window().move(currpos2)

        rangeselct_function(__ocroncefunction)

    def cropcallback(self, path):
        if not path:
            return
        tgt = os.path.join(self.rwpath, os.path.basename(path))
        os.rename(path, tgt)
        tgt = mayberelpath(tgt)
        self.editor.insertPlainText("\n![img]({})\n".format(os.path.basename(path)))

    def TextInsert(self):
        menu = QMenu(self)
        origin = LAction("原文", menu)
        ts = LAction("翻译", menu)
        origin_hira = LAction("原文_+_注音", menu)
        menu.addAction(origin)
        menu.addAction(ts)
        menu.addAction(origin_hira)
        action = menu.exec(QCursor.pos())
        if action == origin:
            self.__wrap(gobject.baseobject.currenttext)
        elif action == ts:
            self.__wrap(gobject.baseobject.currenttranslate)
        elif action == origin_hira:
            self.__wrap(
                mecab.makerubyhtml(
                    gobject.baseobject.parsehira(gobject.baseobject.currenttext)
                )
            )

    def __wrap(self, t: str):
        self.editor.insertPlainText(t + "\n")

    @property
    def editor(self):
        return self.editororview.editstack

    @property
    def editororview(self) -> editswitchTextBrowserEx:
        return self.tab.currentWidget().layout().itemAt(0).widget()

    def switchreadonly(self, i):
        self.editororview.delayload(1 - i)
        self.editororview.readoreditstack.setCurrentIndex(1 - i)
        self.btnvisible(i)
        self.config[self.tab.currentIndex()]["edit"] = i
        self.saveconfig()

    def _plus(self):
        index = self.tab.count()
        W = QWidget()
        self.tab.addTab(W, "  {}  ".format(index))
        lay = QVBoxLayout(W)
        lay.setContentsMargins(0, 0, 0, 0)
        config = self.createnewconfig(index)
        self.createview(config, index, lay)
        self.tab.setCurrentIndex(index)

    def _add_trace(self, index):
        if index == -1:
            return
        if index >= len(self.config):
            return
        config: dict = self.config[index]
        self.insertpicbtn.setChecked(config.get("edit", True))
        self.switch.setChecked(config.get("edit", True))
        i = config.get("edit", True)
        self.btnvisible(i)

    def btnvisible(self, i):
        self.insertpicbtn.setVisible(i)
        self.insertaudiobtn.setVisible(i)
        self.textbtn.setVisible(i)

    def tabmenu(self, position):
        index = self.tab.tabBar().tabAt(position)
        if index == -1:
            return
        menu = QMenu(self)
        openfile = LAction("打开文件", menu)
        rename = LAction("重命名", menu)
        rm = LAction("删除", menu)
        file = self.config[index].get("file")
        file = os.path.join(self.rwpath, file)
        if not self.switch.isChecked():
            file += ".cache.html"
        if os.path.isfile(file):
            menu.addAction(openfile)
        menu.addAction(rename)
        menu.addAction(rm)
        action = menu.exec(QCursor.pos())
        if action == rm:
            self.config.pop(index)
            self.tab.removeTab(index)
            self.saveconfig()

        elif action == openfile:
            os.startfile(file)
        elif action == rename:
            before = self.tab.tabText(index)
            __d = {"k": before}

            def cb(__d):
                title = __d["k"]
                self.tab.setTabText(index, title)
                self.config[index]["title"] = title
                self.saveconfig()

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
