from qtsymbols import *
import gobject, qtawesome, os, json, functools, uuid
from myutils.config import globalconfig, get_launchpath, savehook_new_data
from myutils.wrapper import Singleton_close
from myutils.utils import getimagefilefilter, getimageformat, loopbackrecorder, _TR
from gui.rangeselect import rangeselct_function
from myutils.ocrutil import imageCut
from gui.inputdialog import autoinitdialog
from myutils.hwnd import grabwindow, getExeIcon
from gui.usefulwidget import (
    saveposwindow,
    makesubtab_lazy,
    mayberelpath,
    clearlayout,
    IconButton,
    auto_select_webview,
    PopupWidget,
    getIconButton,
)
from gui.dynalang import LAction


class TextEditOrPlain(QStackedWidget):
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.edit2 = QPlainTextEdit()
        self.edit2.textChanged.connect(functools.partial(self.__changed1, 1))
        self.edit = QTextEdit()
        self.edit.textChanged.connect(functools.partial(self.__changed1, 0))
        self.addWidget(self.edit)
        self.addWidget(self.edit2)

    def text(self):
        return self.edit2.toPlainText()

    def settext(self, text):
        self.edit.setHtml(text)
        self.edit2.setPlainText(text)

    def __changed1(self, i):
        if i == 0:
            if self.currentIndex() == 0:
                html = self.edit.toHtml()
                self.edit2.setPlainText(html)
                self.textChanged.emit(html)
        elif i == 1:
            if self.currentIndex() == 1:
                self.edit.setHtml(self.text())
                self.textChanged.emit(self.text())

    def inserttext(self, text):
        if self.currentIndex() == 0:
            self.edit.insertHtml(text)

        elif self.currentIndex() == 1:
            self.edit2.insertPlainText(text)


class Picselect(PopupWidget):
    def cropcallback(self, path):
        if not path:
            return
        tgt = os.path.join(self.moveto, os.path.basename(path))
        os.rename(path, tgt)
        tgt = mayberelpath(tgt)
        w = self.p.tab.currentWidget().layout().itemAt(0).widget()
        w.editstack.inserttext(
            '\n<img src="{}" style="max-width: 100%">\n'.format(os.path.basename(path))
        )

    def insertpic(self):
        f = QFileDialog.getOpenFileName(filter=getimagefilefilter())
        res = f[0]
        self.cropcallback(res)

    def __init__(self, p: "dialog_memory"):
        super().__init__(p)
        self.p = p
        self.moveto = p.rwpath
        hbox = QHBoxLayout(self)
        self.insertpicbtn = IconButton(parent=self, icon="fa.camera")
        self.insertpicbtn.clicked.connect(
            lambda: grabwindow(getimageformat(), self.cropcallback)
        )
        self.crop = getIconButton(
            icon="fa.crop",
            callback=functools.partial(self.crophide, False),
            callback2=functools.partial(self.crophide, True),
        )
        self.select = IconButton(parent=self, icon="fa.folder-open")
        self.select.clicked.connect(self.insertpic)
        hbox.addWidget(self.crop)
        hbox.addWidget(self.insertpicbtn)
        hbox.addWidget(self.select)
        self.display()

    def crophide(self, s=False):
        currpos = gobject.baseobject.translation_ui.pos()
        currpos2 = self.window().pos()
        if s:
            self.window().move(-9999, -9999)
            gobject.baseobject.translation_ui.move(-9999, -9999)

        def ocroncefunction(rect, img=None):
            if not img:
                img = imageCut(0, rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            fname = gobject.gettempdir(str(uuid.uuid4()) + "." + getimageformat())
            img.save(fname)
            self.cropcallback(fname)
            if s:
                gobject.baseobject.translation_ui.move(currpos)
                self.window().move(currpos2)

        rangeselct_function(ocroncefunction)


class AudioSelect(PopupWidget):
    def cropcallback(self, path):
        if not path:
            return
        tgt = os.path.join(self.moveto, os.path.basename(path))
        os.rename(path, tgt)
        tgt = mayberelpath(tgt)
        html = """\n<audio controls src="{b64}"></audio>\n""".format(
            b64=os.path.basename(path)
        )
        w = self.p.tab.currentWidget().layout().itemAt(0).widget()
        w.editstack.inserttext(html)

    def insertpic(self):
        f = QFileDialog.getOpenFileName()
        res = f[0]
        self.cropcallback(res)

    def __init__(self, p: "dialog_memory"):
        super().__init__(p)
        self.p = p
        self.moveto = p.rwpath
        self.recorders = None
        hbox = QHBoxLayout(self)
        recordbtn1 = IconButton(icon=["fa.microphone", "fa.stop"], checkable=True)
        recordbtn1.clicked.connect(functools.partial(self.startorendrecord, recordbtn1))
        self.select = IconButton(parent=self, icon="fa.folder-open")
        self.select.clicked.connect(self.insertpic)
        hbox.addWidget(recordbtn1)
        hbox.addWidget(self.select)
        self.display()

    @staticmethod
    def safestop(recored: loopbackrecorder):
        recored.stop()

    def startorendrecord(self, btn: QPushButton, idx):
        if idx:
            try:
                self.recorders = loopbackrecorder()
                self.destroyed.connect(
                    functools.partial(AudioSelect.safestop, self.recorders)
                )
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
            self.cropcallback(file)


class editswitchTextBrowserEx(QWidget):
    textChanged = pyqtSignal(str)

    def delayload(self, i):
        if i == 1 and self.readoreditstack.count() == 1:
            self.browser = auto_select_webview(self, loadex=False)
            self.readoreditstack.addWidget(self.browser)
            if os.path.isfile(self.fn):
                self.browser.navigate(self.fn)
            else:
                self.browser.setHtml("")

    def textchanged(self, text):
        self.textChanged.emit(text)

    def __init__(self, parent: "dialog_memory", fn, config):
        super().__init__(parent)
        self.parent1 = parent
        readoreditstack = QStackedWidget()

        self.readoreditstack = readoreditstack
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(readoreditstack)
        editstack = TextEditOrPlain()
        self.editstack = editstack
        editstack.textChanged.connect(self.textchanged)
        readoreditstack.addWidget(editstack)
        self.fn = fn
        try:
            with open(fn, "r", encoding="utf8") as ff:
                text = ff.read()
        except:
            text = ""
        self.settext(text)
        self.textChanged.connect(functools.partial(self.save, fn))
        self.delayload(1 - config.get("edit", True))
        self.readoreditstack.setCurrentIndex(1 - config.get("edit", True))
        self.editstack.setCurrentIndex(config.get("plain", True))

    def save(self, fn, text) -> None:
        with open(fn, "w", encoding="utf8") as ff:
            ff.write(text)
        if self.readoreditstack.count() > 1:
            self.browser.navigate(self.fn)

    def settext(self, text):
        self.editstack.settext(text)

    def text(self):
        return self.editstack.text()


@Singleton_close
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
                self.config.append({"title": "0", "file": "0.html"})
            except:
                pass

    def createview(self, config, i, lay: QHBoxLayout):

        fn = os.path.join(self.rwpath, config.get("file", str(i) + ".html"))
        showtext = editswitchTextBrowserEx(self, fn, config)
        lay.addWidget(showtext)

    def createnewconfig(self, i):
        self.config.insert(i, {"file": str(i) + ".html", "title": str(i)})
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
        return 0 if self.xx else gobject.baseobject.gameuid

    def __init__(self, parent, x=False) -> None:
        self.xx = x
        super().__init__(
            parent,
            flags=Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinMaxButtonsHint,
            poslist=globalconfig["memorydialoggeo"],
        )
        self.setWindowTitle(
            "备忘录"
            + (
                ("_-_" + savehook_new_data[self.gameuid]["title"])
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
        self.switch = IconButton(parent=self, icon="fa.edit", checkable=True)
        self.switch.clicked.connect(self.switchreadonly)
        self.switch3 = IconButton(parent=self, icon="fa.file-code-o", checkable=True)
        self.switch3.clicked.connect(self.__switch)
        self.insertpicbtn = IconButton(parent=self, icon="fa.picture-o")
        self.insertaudiobtn = IconButton(parent=self, icon="fa.music")
        self.buttonslayout.addWidget(self.insertaudiobtn)
        self.buttonslayout.addWidget(self.insertpicbtn)
        self.buttonslayout.addWidget(self.switch3)
        self.buttonslayout.addWidget(self.switch)
        self.insertpicbtn.clicked.connect(functools.partial(Picselect, self))
        self.insertaudiobtn.clicked.connect(functools.partial(AudioSelect, self))

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

    def __switch(self, x):
        w = self.tab.currentWidget().layout().itemAt(0).widget()
        w.editstack.setCurrentIndex(x)
        self.config[self.tab.currentIndex()]["plain"] = x
        self.saveconfig()

    def switchreadonly(self, i):
        w = self.tab.currentWidget().layout().itemAt(0).widget()
        w.delayload(1 - i)
        w.readoreditstack.setCurrentIndex(1 - i)
        self.insertpicbtn.setVisible(i)
        self.insertaudiobtn.setVisible(i)
        self.switch3.setVisible(i)
        self.config[self.tab.currentIndex()]["edit"] = i
        self.saveconfig()

    def _plus(self):
        index = self.tab.count()
        W = QWidget()
        self.tab.addTab(W, str(index))
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
        config = self.config[index]
        self.switch3.setChecked(config.get("plain", True))
        self.insertpicbtn.setChecked(config.get("edit", True))
        self.switch.setChecked(config.get("edit", True))
        i = config.get("edit", True)
        self.insertpicbtn.setVisible(i)
        self.insertaudiobtn.setVisible(i)
        self.switch3.setVisible(i)

    def tabmenu(self, position):
        index = self.tab.tabBar().tabAt(position)
        if index == -1:
            return
        menu = QMenu(self)
        rename = LAction("重命名", menu)
        rm = LAction("删除", menu)
        menu.addAction(rename)
        menu.addAction(rm)
        action = menu.exec(QCursor.pos())
        if action == rm:
            self.config.pop(index)
            self.tab.removeTab(index)
            self.saveconfig()

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
