import time
from datetime import datetime, timedelta
from gui.specialwidget import ScrollFlow, chartwidget, lazyscrollflow
from qtsymbols import *
import functools, threading
from traceback import print_exc
import windows
import os

from gui.usefulwidget import (
    getsimplecombobox,
    getspinbox,
    getcolorbutton,
    getsimpleswitch,
    getspinbox,
    selectcolor,
)
import os
from myutils.config import savehook_new_list, savehook_new_data, vndbtagdata
from myutils.hwnd import getExeIcon
import gobject
from myutils.config import _TR, _TRL, globalconfig, static_data
import winsharedutils
from myutils.wrapper import Singleton_close, Singleton, threader, tryprint
from myutils.utils import (
    checkifnewgame,
    str2rgba,
    vidchangedtask,
    titlechangedtask,
    imgchangedtask,
)
from gui.usefulwidget import (
    yuitsu_switch,
    saveposwindow,
    getboxlayout,
    getlineedit,
    auto_select_webview,
    Prompt_dialog,
)
from myutils.vndb import parsehtmlmethod
from gui.inputdialog import noundictconfigdialog1


class ItemWidget(QWidget):
    focuschanged = pyqtSignal(bool, str)
    doubleclicked = pyqtSignal(str)
    globallashfocus = None

    @classmethod
    def clearfocus(cls):
        try:  # 可能已被删除
            if ItemWidget.globallashfocus:
                ItemWidget.globallashfocus.focusOut()
        except:
            pass
        ItemWidget.globallashfocus = None

    def mousePressEvent(self, ev) -> None:
        try:
            self.bottommask.setStyleSheet(
                f'background-color: {str2rgba(globalconfig["dialog_savegame_layout"]["onselectcolor"],globalconfig["dialog_savegame_layout"]["transparent"])};'
            )

            if self != ItemWidget.globallashfocus:
                ItemWidget.clearfocus()
            ItemWidget.globallashfocus = self
            self.focuschanged.emit(True, self.exe)
        except:
            print_exc()

    def focusOut(self):
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.focuschanged.emit(False, self.exe)

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.exe)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())

    def __init__(self, exe, pixmap, file) -> None:
        super().__init__()
        self.itemw = globalconfig["dialog_savegame_layout"]["itemw"]
        self.itemh = globalconfig["dialog_savegame_layout"]["itemh"]
        # self.imgw = globalconfig["dialog_savegame_layout"]["imgw"]
        # self.imgh = globalconfig["dialog_savegame_layout"]["imgh"]
        # margin = (
        #     self.itemw - self.imgw
        # ) // 2  # globalconfig['dialog_savegame_layout']['margin']
        margin = globalconfig["dialog_savegame_layout"]["margin"]
        textH = globalconfig["dialog_savegame_layout"]["textH"]
        self.imgw = self.itemw - 2 * margin
        self.imgh = self.itemh - textH - 2 * margin
        #
        self.setFixedSize(QSize(self.itemw, self.itemh))
        # self.setFocusPolicy(Qt.StrongFocus)
        self.maskshowfileexists = QLabel(self)
        self.bottommask = QLabel(self)
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._img = IMGWidget(self.imgw, self.imgh, pixmap)
        _w = QWidget()
        _w.setStyleSheet("background-color: rgba(255,255,255, 0);")
        wrap = QVBoxLayout()
        _w.setLayout(wrap)
        _w.setFixedHeight(self.imgh + 2 * margin)
        wrap.setContentsMargins(margin, margin, margin, margin)
        wrap.addWidget(self._img)
        layout.addWidget(_w)
        layout.setSpacing(0)
        self._lb = QLabel()
        if globalconfig["showgametitle"]:
            self._lb.setText(file)
        self._lb.setWordWrap(True)
        self._lb.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self._lb.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._lb)
        self.setLayout(layout)
        self.exe = exe
        c = globalconfig["dialog_savegame_layout"][
            ("onfilenoexistscolor", "backcolor")[os.path.exists(exe)]
        ]
        c = str2rgba(c, globalconfig["dialog_savegame_layout"]["transparent"])
        self.maskshowfileexists.setStyleSheet(f"background-color:{c};")


class IMGWidget(QLabel):

    def adaptsize(self, size: QSize):

        if globalconfig["imagewrapmode"] == 0:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r < max_r:
                new_w = self.width()
                new_h = int(new_w / r)
            else:
                new_h = self.height()
                new_w = int(new_h * r)
            return QSize(new_w, new_h)
        elif globalconfig["imagewrapmode"] == 1:
            h, w = size.height(), size.width()
            r = float(w) / h
            max_r = float(self.width()) / self.height()
            if r > max_r:
                new_w = self.width()
                new_h = int(new_w / r)
            else:
                new_h = self.height()
                new_w = int(new_h * r)
            return QSize(new_w, new_h)
        elif globalconfig["imagewrapmode"] == 2:
            return self.size()
        elif globalconfig["imagewrapmode"] == 3:
            return size

    def setimg(self, pixmap):
        if type(pixmap) != QPixmap:
            pixmap = pixmap()

        rate = self.devicePixelRatioF()
        newpixmap = QPixmap(self.size() * rate)
        newpixmap.setDevicePixelRatio(rate)
        newpixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(newpixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(self.getrect(pixmap.size()), pixmap)
        painter.end()

        self.setPixmap(newpixmap)

    def getrect(self, size):
        size = self.adaptsize(size)
        rect = QRect()
        rect.setX(int((self.width() - size.width()) / 2))
        rect.setY(int((self.height() - size.height()) / 2))
        rect.setSize(size)
        return rect

    def __init__(self, w, h, pixmap) -> None:
        super().__init__()
        self.setFixedSize(QSize(w, h))
        self.setScaledContents(True)
        self.setimg(pixmap)


class CustomTabBar(QTabBar):
    lastclick = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        index = self.tabAt(event.pos())
        if index == self.count() - 1 and event.button() == Qt.MouseButton.LeftButton:
            self.lastclick.emit()
        else:
            super().mousePressEvent(event)


class ClickableLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setClickable(True)

    def setClickable(self, clickable):
        self._clickable = clickable

    def mousePressEvent(self, event):
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    clicked = pyqtSignal()


class tagitem(QWidget):
    # website
    TYPE_GLOABL_LIKE = 3
    TYPE_GAME_LIKE = 1
    # search game
    TYPE_RAND = 0
    TYPE_DEVELOPER = 1
    TYPE_TAG = 2
    TYPE_USERTAG = 3
    TYPE_EXISTS = 4
    removesignal = pyqtSignal(tuple)
    labelclicked = pyqtSignal(tuple)

    def remove(self):
        self.hide()
        _lay = self.layout()
        _ws = []
        for i in range(_lay.count()):
            witem = _lay.itemAt(i)
            _ws.append(witem.widget())
        for w in _ws:
            _lay.removeWidget(w)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._type == tagitem.TYPE_RAND:
            border_color = Qt.GlobalColor.black
        elif self._type == tagitem.TYPE_DEVELOPER:
            border_color = Qt.GlobalColor.red
        elif self._type == tagitem.TYPE_TAG:
            border_color = Qt.GlobalColor.green
        elif self._type == tagitem.TYPE_USERTAG:
            border_color = Qt.GlobalColor.blue
        elif self._type == tagitem.TYPE_EXISTS:
            border_color = Qt.GlobalColor.yellow
        border_width = 1
        pen = QPen(border_color)
        pen.setWidth(border_width)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    def __init__(self, tag, removeable=True, _type=TYPE_RAND, refdata=None) -> None:
        super().__init__()
        tagLayout = QHBoxLayout()
        tagLayout.setContentsMargins(0, 0, 0, 0)
        tagLayout.setSpacing(0)
        self._type = _type
        key = (tag, _type, refdata)
        self.setLayout(tagLayout)
        lb = ClickableLabel()
        lb.setStyleSheet("background: transparent;")
        lb.setText(tag)
        lb.clicked.connect(functools.partial(self.labelclicked.emit, key))
        tagLayout.addWidget(lb)
        if removeable:
            button = getcolorbutton(
                None,
                None,
                functools.partial(self.removesignal.emit, key),  # self.removeTag(tag),
                icon="fa.times",
                constcolor="#FF69B4",
                sizefixed=True,
            )
            tagLayout.addWidget(button)


class TagWidget(QWidget):
    tagschanged = pyqtSignal(tuple)  # ((tag,type,refdata),)
    linepressedenter = pyqtSignal(str)
    tagclicked = pyqtSignal(tuple)  # tag,type,refdata

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.lineEdit = QComboBox()
        self.lineEdit.setLineEdit(QLineEdit())

        self.lineEdit.lineEdit().returnPressed.connect(
            lambda: self.linepressedenter.emit(self.lineEdit.currentText())
        )

        self.lineEdit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )

        layout.addWidget(self.lineEdit)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.tag2widget = {}

    def addTags(self, tags, signal=True):
        for key in tags:
            self.__addTag(key)
        self.__calltagschanged(signal)

    @tryprint
    def __addTag(self, key):
        tag, _type, refdata = key
        if not tag:
            return
        if key in self.tag2widget:
            return
        qw = tagitem(tag, _type=_type, refdata=refdata)
        qw.removesignal.connect(self.removeTag)
        qw.labelclicked.connect(self.tagclicked.emit)
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, qw)
        self.tag2widget[key] = qw
        self.lineEdit.setFocus()

    def addTag(self, tag, _type, refdata=None, signal=True):
        self.__addTag((tag, _type, refdata))
        self.__calltagschanged(signal)

    @tryprint
    def __removeTag(self, key):
        _w = self.tag2widget[key]
        _w.remove()

        self.layout().removeWidget(_w)
        self.tag2widget.pop(key)

    def removeTag(self, key, signal=True):
        self.__removeTag(key)
        self.__calltagschanged(signal)

    def __calltagschanged(self, signal):
        if signal:
            self.tagschanged.emit(tuple(self.tag2widget.keys()))

    def clearTag(self, signal=True):
        for key in self.tag2widget.copy():
            self.__removeTag(key)
        self.__calltagschanged(signal)


@Singleton
class browserdialog(saveposwindow):
    seturlsignal = pyqtSignal(str)

    def parsehtml(self, url):
        try:
            newpath = parsehtmlmethod(url)
        except:
            print_exc()
            newpath = url
        if newpath[:4].lower() != "http":
            newpath = os.path.abspath(newpath)
        return newpath

    def startupsettitle(self, exepath):

        if exepath:
            title = savehook_new_data[exepath]["title"]
        else:
            title = "LunaTranslator"
        self.setWindowTitle(title)

    def loadalllinks(self, exepath):
        items = []
        if exepath:
            self.setWindowTitle(savehook_new_data[exepath]["title"])

        for link in globalconfig["relationlinks"]:
            items.append((link[0], tagitem.TYPE_GLOABL_LIKE, link[1]))
        if exepath:
            for link in savehook_new_data[self.exepath]["relationlinks"]:
                items.append((link[0], tagitem.TYPE_GAME_LIKE, link[1]))

        self.tagswidget.clearTag(False)
        self.tagswidget.addTags(items)

    def startupnavi(self, exepath):
        for idx in range(1, 100):
            if idx == 1:
                if exepath:
                    hasvndb = bool(
                        savehook_new_data[exepath]["infopath"]
                        and os.path.exists(savehook_new_data[exepath]["infopath"])
                    )
                    if hasvndb:
                        navitarget = self.parsehtml(
                            savehook_new_data[exepath]["infopath"]
                        )
                        break
            elif idx == 2:

                if exepath:
                    if len(savehook_new_data[exepath]["relationlinks"]):
                        navitarget = savehook_new_data[exepath]["relationlinks"][-1][1]
                        break
            elif idx == 3:
                if len(globalconfig["relationlinks"]):
                    navitarget = globalconfig["relationlinks"][-1][1]
                    break
            else:
                navitarget = None
                break
        if navitarget:
            self.browser.navigate(navitarget)
            self.urlchanged(navitarget)

    def urlchanged(self, url):
        self.tagswidget.lineEdit.setCurrentText(url)
        self.current = url

    def likelink(self):
        _dia = Prompt_dialog(
            self,
            _TR("收藏"),
            "",
            [
                [_TR("名称"), ""],
                [_TR("网址"), self.current],
            ],
        )

        if _dia.exec():

            text = []
            for _t in _dia.text:
                text.append(_t.text())
            if self.exepath:
                savehook_new_data[self.exepath]["relationlinks"].append(text)
                self.tagswidget.addTag(text[0], tagitem.TYPE_GAME_LIKE, text[1])
            else:
                globalconfig["relationlinks"].append(text)
                self.tagswidget.addTag(text[0], tagitem.TYPE_GLOABL_LIKE, text[1])

    def tagschanged(self, tags):
        __ = []
        __2 = []
        for _name, _type, _url in tags:
            if _type == tagitem.TYPE_GLOABL_LIKE:
                __.append([_name, _url])
            elif _type == tagitem.TYPE_GAME_LIKE:
                __2.append([_name, _url])
        globalconfig["relationlinks"] = __
        if self.exepath:
            savehook_new_data[self.exepath]["relationlinks"] = __2

    def reinit(self, exepath=None):

        self.exepath = exepath
        self.loadalllinks(exepath)
        self.startupnavi(exepath)
        self.startupsettitle(exepath)

    def __init__(self, parent, exepath=None) -> None:
        super().__init__(parent, globalconfig, "browserwidget")
        if exepath:
            self.setWindowIcon(getExeIcon(exepath, cache=True))
        self.browser = auto_select_webview(self)

        self.tagswidget = TagWidget(self)
        self.tagswidget.tagschanged.connect(self.tagschanged)

        self.tagswidget.tagclicked.connect(self.urlclicked)
        self.tagswidget.linepressedenter.connect(self.browser.navigate)
        self.browser.on_load.connect(self.urlchanged)

        hlay = QHBoxLayout()
        hlay.addWidget(self.tagswidget)

        hlay.addWidget(
            getcolorbutton(
                "",
                "",
                lambda _: self.likelink(),
                icon="fa.heart",
                constcolor="#FF69B4",
                sizefixed=True,
            )
        )
        hlay.addWidget(
            getcolorbutton(
                "",
                "",
                lambda _: self.urlclicked((None, None, self.current)),
                icon="fa.repeat",
                constcolor="#FF69B4",
                sizefixed=True,
            )
        )
        _topw = QWidget()
        _topw.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        _topw.setLayout(hlay)
        layout = QVBoxLayout()
        layout.setContentsMargins(*(0 for i in range(4)))
        hlay.setContentsMargins(*(0 for i in range(4)))
        layout.addWidget(_topw)
        layout.addWidget(self.browser)
        layout.setSpacing(0)
        __w = QWidget()
        __w.setLayout(layout)
        self.setCentralWidget(__w)

        self.reinit(exepath)
        self.show()

    def urlclicked(self, _):
        tag, _, url = _
        if url.startswith("./cache/vndb"):
            url = self.parsehtml(url)
        self.browser.navigate(url)

    def showmenu(self, p):
        tab_index = self.nettab.tabBar().tabAt(p)
        if (self.hasvndb and tab_index == 0) or tab_index == self.nettab.count() - 1:
            return
        menu = QMenu(self)
        shanchu = QAction(_TR("删除"))
        menu.addAction(shanchu)
        action = menu.exec(self.mapToGlobal(p))
        if action == shanchu:
            self.nettab.setCurrentIndex(0)
            self.nettab.removeTab(tab_index)
            savehook_new_data[self.exepath]["relationlinks"].pop(
                tab_index - self.hasvndb
            )


def getvndbrealtags(vndbtags_naive):
    vndbtags = []
    for tagid in vndbtags_naive:
        if tagid in vndbtagdata:
            vndbtags.append(vndbtagdata[tagid])
    return vndbtags


_global_dialog_savedgame_new = None
_global_dialog_setting_game = None


def calculate_centered_rect(original_rect: QRect, size: QSize) -> QRect:
    original_center = original_rect.center()
    new_left = original_center.x() - size.width() // 2
    new_top = original_center.y() - size.height() // 2
    new_rect = QRect(new_left, new_top, size.width(), size.height())
    return new_rect


@Singleton_close
class dialog_setting_game(QDialog):
    def selectexe(self):
        f = QFileDialog.getOpenFileName(directory=self.exepath)
        res = f[0]
        if res != "":

            res = os.path.normpath(res)
            if res in savehook_new_list:
                return
            savehook_new_list[savehook_new_list.index(self.exepath)] = res
            savehook_new_data[res] = savehook_new_data[self.exepath]
            savehook_new_data.pop(self.exepath)
            _icon = getExeIcon(res, cache=True)

            self.setWindowIcon(_icon)
            self.editpath.setText(res)
            self.exepath = res

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.isopened = False
        return super().closeEvent(a0)

    def __init__(self, parent, exepath) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        global _global_dialog_setting_game
        _global_dialog_setting_game = self
        self.isopened = True
        vbox = QVBoxLayout(self)  # 配置layout
        self.setLayout(vbox)
        formwidget = QWidget()
        formLayout = QFormLayout()
        formwidget.setLayout(formLayout)
        self.exepath = exepath
        self.editpath = QLineEdit(exepath)
        self.editpath.setReadOnly(True)
        self.setWindowTitle(savehook_new_data[exepath]["title"])

        self.setWindowIcon(getExeIcon(exepath, cache=True))
        formLayout.addRow(
            _TR("路径"),
            getboxlayout(
                [
                    self.editpath,
                    getcolorbutton(
                        "",
                        "",
                        functools.partial(self.selectexe),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            ),
        )
        titleedit = QLineEdit(savehook_new_data[exepath]["title"])

        def _titlechange(x):
            titlechangedtask(exepath, x)
            self.setWindowTitle(x)

        titleedit.textChanged.connect(_titlechange)
        formLayout.addRow(_TR("标题"), titleedit)

        imgpath = QLineEdit(savehook_new_data[exepath]["imagepath"])
        imgpath.setReadOnly(True)

        def selectimg():
            f = QFileDialog.getOpenFileName(
                directory=savehook_new_data[exepath]["imagepath"]
            )
            res = f[0]
            if res != "":

                _pixmap = QPixmap(res)
                if _pixmap.isNull() == False:
                    imgchangedtask(exepath, res)
                    imgpath.setText(res)

        vndbid = QLineEdit(str(savehook_new_data[exepath]["vid"]))
        vndbid.setValidator(QIntValidator())
        vndbid.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        vndbid.textEdited.connect(functools.partial(vidchangedtask, exepath))

        formLayout.addRow(
            _TR("封面"),
            getboxlayout(
                [
                    imgpath,
                    getcolorbutton(
                        "", "", selectimg, icon="fa.gear", constcolor="#FF69B4"
                    ),
                ]
            ),
        )
        formLayout.addRow(
            "vndbid",
            getboxlayout(
                [
                    vndbid,
                    getcolorbutton(
                        "",
                        "",
                        lambda: browserdialog(gobject.baseobject.settin_ui, exepath),
                        icon="fa.book",
                        constcolor="#FF69B4",
                    ),
                    getcolorbutton(
                        "",
                        "",
                        lambda: os.startfile(
                            "https://vndb.org/v{}".format(
                                savehook_new_data[exepath]["vid"]
                            )
                        ),
                        icon="fa.chrome",
                        constcolor="#FF69B4",
                    ),
                    getcolorbutton(
                        "",
                        "",
                        lambda: vidchangedtask(
                            exepath, savehook_new_data[exepath]["vid"]
                        ),
                        icon="fa.refresh",
                        constcolor="#FF69B4",
                    ),
                ]
            ),
        )

        methodtab = QTabWidget()
        methodtab.addTab(self.starttab(exepath), _TR("启动"))
        methodtab.addTab(self.gethooktab(exepath), "HOOK")
        methodtab.addTab(self.getpretranstab(exepath), _TR("预翻译"))
        methodtab.addTab(self.getttssetting(exepath), _TR("语音"))
        methodtab.addTab(self.getlabelsetting(exepath), _TR("标签"))
        methodtab.addTab(self.getstatistic(exepath), _TR("统计信息"))
        methodtab.addTab(self.getbackup(exepath), _TR("存档备份"))

        vbox.addWidget(formwidget)
        vbox.addWidget(methodtab)

        self.show()
        self.resize(QSize(600, 1))
        self.adjustSize()
        self.resize(QSize(600, self.height()))
        try:
            self.setGeometry(
                calculate_centered_rect(
                    _global_dialog_savedgame_new.geometry(), self.size()
                )
            )
        except:
            pass

    def selectbackupdir(self, edit):
        res = QFileDialog.getExistingDirectory(
            directory=edit.text(),
            options=QFileDialog.Option.DontResolveSymlinks,
        )
        if not res:
            return
        res = os.path.abspath(res)
        edit.setText(res)

    def getbackup(self, exepath):
        _w = QWidget()
        formLayout = QFormLayout()
        _w.setLayout(formLayout)

        editpath = QLineEdit(savehook_new_data[exepath]["autosavesavedata"])
        editpath.textChanged.connect(
            lambda _: savehook_new_data[exepath].__setitem__("autosavesavedata", _)
        )
        editpath.setReadOnly(True)
        formLayout.addRow(
            _TR("路径"),
            getboxlayout(
                [
                    editpath,
                    getcolorbutton(
                        "",
                        "",
                        functools.partial(self.selectbackupdir, editpath),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            ),
        )

        editpath.textChanged.connect(
            lambda _: globalconfig.__setitem__("backupsavedatato", _)
        )
        editpath = QLineEdit(
            globalconfig["backupsavedatato"]
            if os.path.exists(globalconfig["backupsavedatato"])
            else os.path.abspath("./cache/backup")
        )
        editpath.setReadOnly(True)
        formLayout.addRow(
            _TR("备份到"),
            getboxlayout(
                [
                    editpath,
                    getcolorbutton(
                        "",
                        "",
                        functools.partial(self.selectbackupdir, editpath),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            ),
        )

        return _w

    def starttab(self, exepath):
        _w = QWidget()
        formLayout = QFormLayout()
        _w.setLayout(formLayout)

        b = windows.GetBinaryType(exepath)

        if b == 6:
            _methods = ["", "Locale_Remulator", "Ntleas"]
        else:
            _methods = ["Locale-Emulator", "Locale_Remulator", "Ntleas"]
        if b == 6 and savehook_new_data[exepath]["localeswitcher"] == 0:
            savehook_new_data[exepath]["localeswitcher"] = 2
        formLayout.addRow(
            _TR("转区启动"),
            getboxlayout(
                [
                    getsimpleswitch(savehook_new_data[exepath], "leuse"),
                    getsimplecombobox(
                        _TRL(_methods), savehook_new_data[exepath], "localeswitcher"
                    ),
                ]
            ),
        )

        formLayout.addRow(
            _TR("命令行启动"),
            getboxlayout(
                [
                    getsimpleswitch(savehook_new_data[exepath], "startcmduse"),
                    getlineedit(savehook_new_data[exepath], "startcmd"),
                ]
            ),
        )

        formLayout.addRow(
            _TR("自动切换到模式"),
            getsimplecombobox(
                _TRL(["不切换", "HOOK", "剪贴板", "OCR"]),
                savehook_new_data[exepath],
                "onloadautochangemode2",
            ),
        )

        formLayout.addRow(
            _TR("自动切换源语言"),
            getsimplecombobox(
                _TRL(["不切换"]) + _TRL(static_data["language_list_translator"]),
                savehook_new_data[exepath],
                "onloadautoswitchsrclang",
            ),
        )

        return _w

    def getstatistic(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()

        _w.setLayout(formLayout)
        formLayout.setContentsMargins(0, 0, 0, 0)
        chart = chartwidget()
        chart.xtext = lambda x: (
            "0" if x == 0 else str(datetime.fromtimestamp(x)).split(" ")[0]
        )
        chart.ytext = lambda y: self.formattime(y, False)

        self.chart = chart
        self._timelabel = QLabel()
        self._wordlabel = QLabel()
        self._wordlabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self._timelabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        formLayout.addLayout(getboxlayout([QLabel(_TR("文字计数")), self._wordlabel]))
        formLayout.addLayout(getboxlayout([QLabel(_TR("游戏时间")), self._timelabel]))

        formLayout.addWidget(chart)

        threading.Thread(target=self.refresh).start()
        return _w

    def split_range_into_days(self, times):
        everyday = {}
        for start, end in times:
            if start == 0:
                everyday[0] = end
                continue

            start_date = datetime.fromtimestamp(start)
            end_date = datetime.fromtimestamp(end)

            current_date = start_date
            while current_date <= end_date:
                end_of_day = current_date.replace(
                    hour=23, minute=59, second=59, microsecond=0
                )
                end_of_day = end_of_day.timestamp() + 1

                if end_of_day >= end_date.timestamp():
                    useend = end_date.timestamp()
                else:
                    useend = end_of_day
                duration = useend - current_date.timestamp()
                today = end_of_day - 1
                if today not in everyday:
                    everyday[today] = 0
                everyday[today] += duration
                current_date += timedelta(days=1)
                current_date = current_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
        lists = []
        for k in sorted(everyday.keys()):
            lists.append((k, everyday[k]))
        return lists

    def refresh(self):
        while self.isopened:
            self._timelabel.setText(
                self.formattime(savehook_new_data[self.exepath]["statistic_playtime"])
            )
            self._wordlabel.setText(
                str(savehook_new_data[self.exepath]["statistic_wordcount"])
            )
            self.chart.setdata(
                self.split_range_into_days(
                    savehook_new_data[self.exepath]["traceplaytime_v2"]
                )
            )
            time.sleep(1)

    def formattime(self, t, usingnotstart=True):
        t = int(t)
        s = t % 60
        t = t // 60
        m = t % 60
        t = t // 60
        h = t
        string = ""
        if h:
            string += str(h) + _TR("时")
        if m:
            string += str(m) + _TR("分")
        if s:
            string += str(s) + _TR("秒")
        if string == "":
            if usingnotstart:
                string = _TR("未开始")
            else:
                string = "0"
        return string

    def getlabelsetting(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()
        _w.setLayout(formLayout)
        formLayout.setContentsMargins(0, 0, 0, 0)
        self.labelflow = ScrollFlow()

        def newitem(text, removeable, first=False, _type=tagitem.TYPE_RAND):
            qw = tagitem(text, removeable, _type)

            def __(_qw, _):
                t, _type, _ = _
                _qw.remove()
                i = savehook_new_data[exepath]["usertags"].index(t)
                self.labelflow.removeidx(i)
                savehook_new_data[exepath]["usertags"].remove(t)

            if removeable:
                qw.removesignal.connect(functools.partial(__, qw))

            def safeaddtags(_):
                try:
                    _global_dialog_savedgame_new.tagswidget.addTag(*_)
                except:
                    pass

            qw.labelclicked.connect(safeaddtags)
            if first:
                self.labelflow.insertwidget(0, qw)
            else:
                self.labelflow.addwidget(qw)

        for tag in savehook_new_data[exepath]["usertags"]:
            newitem(tag, True, _type=tagitem.TYPE_USERTAG)
        for tag in savehook_new_data[exepath]["developers"]:
            newitem(tag, False, _type=tagitem.TYPE_DEVELOPER)
        for tag in getvndbrealtags(savehook_new_data[exepath]["vndbtags"]):
            newitem(tag, False, _type=tagitem.TYPE_TAG)
        formLayout.addWidget(self.labelflow)
        _dict = {"new": 0}

        formLayout.addWidget(self.labelflow)
        button = QPushButton(_TR("添加"))

        combo = getsimplecombobox(globalconfig["labelset"], _dict, "new")
        combo.setEditable(True)
        combo.clearEditText()

        def _add(_):

            tag = combo.currentText()
            # tag = globalconfig["labelset"][_dict["new"]]
            if tag and tag not in savehook_new_data[exepath]["usertags"]:
                savehook_new_data[exepath]["usertags"].insert(0, tag)
                newitem(tag, True, True, _type=tagitem.TYPE_USERTAG)
            combo.clearEditText()

        button.clicked.connect(_add)

        formLayout.addLayout(
            getboxlayout(
                [
                    combo,
                    button,
                ]
            )
        )
        return _w

    def getttssetting(self, exepath):
        _w = QWidget()
        formLayout = QVBoxLayout()
        formLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        _w.setLayout(formLayout)

        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("禁止自动朗读的人名")),
                    getcolorbutton(
                        "",
                        "",
                        lambda _: listediter(
                            self,
                            _TR("禁止自动朗读的人名"),
                            _TRL(
                                [
                                    "删除",
                                    "人名",
                                ]
                            ),
                            savehook_new_data[exepath]["allow_tts_auto_names_v4"],
                        ),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            )
        )
        formLayout.addLayout(
            getboxlayout(
                [
                    QLabel(_TR("语音修正")),
                    getsimpleswitch(savehook_new_data[exepath], "tts_repair"),
                    getcolorbutton(
                        globalconfig,
                        "",
                        callback=lambda x: noundictconfigdialog1(
                            self,
                            savehook_new_data[exepath],
                            "tts_repair_regex",
                            "语音修正",
                            ["正则", "原文", "替换"],
                        ),
                        icon="fa.gear",
                        constcolor="#FF69B4",
                    ),
                ]
            )
        )
        return _w

    def getpretranstab(self, exepath):
        _w = QWidget()
        formLayout = QFormLayout()
        _w.setLayout(formLayout)

        def selectimg(key, filter1, le):
            f = QFileDialog.getOpenFileName(
                directory=savehook_new_data[exepath][key], filter=filter1
            )
            res = f[0]
            if res != "":
                savehook_new_data[exepath][key] = res
                le.setText(res)

        for showname, key, filt in [
            ("json翻译文件", "gamejsonfile", "*.json"),
            ("sqlite翻译记录", "gamesqlitefile", "*.sqlite"),
        ]:
            editjson = QLineEdit(exepath)
            editjson.setReadOnly(True)
            editjson.setText(savehook_new_data[exepath][key])
            formLayout.addRow(
                _TR(showname),
                getboxlayout(
                    [
                        editjson,
                        getcolorbutton(
                            "",
                            "",
                            functools.partial(selectimg, key, filt, editjson),
                            icon="fa.gear",
                            constcolor="#FF69B4",
                        ),
                    ]
                ),
            )
        return _w

    def gethooktab(self, exepath):
        _w = QWidget()
        formLayout = QFormLayout()
        _w.setLayout(formLayout)
        formLayout.addRow(
            _TR("代码页"),
            getsimplecombobox(
                _TRL(static_data["codepage_display"]),
                savehook_new_data[exepath],
                "codepage_index",
                lambda x: gobject.baseobject.textsource.setsettings(),
            ),
        )

        formLayout.addRow(
            _TR("移除非选定hook"),
            getsimpleswitch(savehook_new_data[exepath], "removeuseless"),
        )

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(
            _TRL(
                [
                    "删除",
                    "特殊码",
                ]
            )
        )  # ,'HOOK'])

        self.hcmodel = model

        table = QTableView()
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setStretchLastSection(True)
        # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        table.setModel(model)
        self.hctable = table

        for row, k in enumerate(savehook_new_data[exepath]["needinserthookcode"]):  # 2
            self.newline(row, k)

        formLayout.addRow(self.hctable)

        formLayout.addRow(
            _TR("插入特殊码延迟(ms)"),
            getspinbox(0, 1000000, savehook_new_data[exepath], "inserthooktimeout"),
        )
        if (
            savehook_new_data[exepath]["use_saved_text_process"]
            or "save_text_process_info" in savehook_new_data[exepath]
        ):
            formLayout.addRow(
                _TR("使用保存的文本处理流程"),
                getsimpleswitch(savehook_new_data[exepath], "use_saved_text_process"),
            )
        return _w

    def clicked2(self):
        try:
            savehook_new_data[self.exepath]["needinserthookcode"].pop(
                self.hctable.currentIndex().row()
            )
            self.hcmodel.removeRow(self.hctable.currentIndex().row())
        except:
            pass

    def newline(self, row, k):

        self.hcmodel.insertRow(row, [QStandardItem(), QStandardItem(k)])

        self.hctable.setIndexWidget(
            self.hcmodel.index(row, 0),
            getcolorbutton(
                "", "", self.clicked2, icon="fa.times", constcolor="#FF69B4"
            ),
        )


@Singleton
class dialog_syssetting(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(_TR("其他设置"))
        formLayout = QFormLayout(self)
        formLayout.addRow(
            QLabel(_TR("隐藏不存在的游戏")),
            getsimpleswitch(globalconfig, "hide_not_exists"),
        )
        for key, name in [
            ("itemw", "宽度"),
            ("itemh", "高度"),
            # ("imgw", "图片宽度"),
            # ("imgh", "图片高度"),
            ("margin", "边距"),
            ("textH", "文字区高度"),
        ]:
            formLayout.addRow(
                (_TR(name)),
                getspinbox(0, 1000, globalconfig["dialog_savegame_layout"], key),
            )
        for key, name in [
            ("backcolor", "颜色"),
            ("onselectcolor", "选中时颜色"),
            ("onfilenoexistscolor", "游戏不存在时颜色"),
        ]:
            formLayout.addRow(
                (_TR(name)),
                getcolorbutton(
                    globalconfig["dialog_savegame_layout"],
                    key,
                    callback=functools.partial(
                        selectcolor,
                        self,
                        globalconfig["dialog_savegame_layout"],
                        key,
                        None,
                        self,
                        key,
                    ),
                    name=key,
                    parent=self,
                ),
            )
        formLayout.addRow(
            (_TR("不透明度")),
            getspinbox(0, 100, globalconfig["dialog_savegame_layout"], "transparent"),
        )
        formLayout.addRow(
            _TR("缩放"),
            getsimplecombobox(
                _TRL(["填充", "适应", "拉伸", "居中"]),
                globalconfig,
                "imagewrapmode",
            ),
        )
        formLayout.addRow(
            QLabel(_TR("启动游戏不修改顺序")),
            getsimpleswitch(globalconfig, "startgamenototop"),
        )
        formLayout.addRow(
            QLabel(_TR("显示标题")),
            getsimpleswitch(globalconfig, "showgametitle"),
        )
        self.show()


@threader
def startgame(game):
    try:
        if os.path.exists(game):
            mode = savehook_new_data[game]["onloadautochangemode2"]
            if mode > 0:
                _ = {1: "texthook", 2: "copy", 3: "ocr"}
                if globalconfig["sourcestatus2"][_[mode]]["use"] == False:
                    globalconfig["sourcestatus2"][_[mode]]["use"] = True

                    yuitsu_switch(
                        gobject.baseobject.settin_ui,
                        globalconfig["sourcestatus2"],
                        "sourceswitchs",
                        _[mode],
                        None,
                        True,
                    )
                    gobject.baseobject.starttextsource(use=_[mode], checked=True)

            dirpath = os.path.dirname(game)

            if savehook_new_data[game]["startcmduse"]:
                usearg = savehook_new_data[game]["startcmd"].format(exepath=game)
                windows.CreateProcess(
                    None,
                    usearg,
                    None,
                    None,
                    False,
                    0,
                    None,
                    dirpath,
                    windows.STARTUPINFO(),
                )
                return
            if savehook_new_data[game]["leuse"] == False or (
                game.lower()[-4:] not in [".lnk", ".exe"]
            ):
                # 对于其他文件，需要AssocQueryStringW获取命令行才能正确le，太麻烦，放弃。
                windows.ShellExecute(None, "open", game, "", dirpath, windows.SW_SHOW)
                return

            execheck3264 = game
            usearg = '"{}"'.format(game)
            if game.lower()[-4:] == ".lnk":
                exepath, args, iconpath, dirp = winsharedutils.GetLnkTargetPath(game)

                if args != "":
                    usearg = '"{}" {}'.format(exepath, args)
                elif exepath != "":
                    usearg = '"{}"'.format(exepath)

                if exepath != "":
                    execheck3264 = exepath

                if dirp != "":
                    dirpath = dirp

            localeswitcher = savehook_new_data[game]["localeswitcher"]
            b = windows.GetBinaryType(execheck3264)
            if b == 6 and localeswitcher == 0:
                localeswitcher = 1
            if localeswitcher == 2 and b == 6:
                _shareddllproxy = "shareddllproxy64"
            else:
                _shareddllproxy = "shareddllproxy32"
            shareddllproxy = os.path.abspath("./files/plugins/" + _shareddllproxy)
            _cmd = {0: "le", 1: "LR", 2: "ntleas"}[localeswitcher]
            windows.CreateProcess(
                None,
                '"{}" {} {}'.format(shareddllproxy, _cmd, usearg),
                None,
                None,
                False,
                0,
                None,
                dirpath,
                windows.STARTUPINFO(),
            )
    except:
        print_exc()


def opendir(f):
    f = os.path.dirname(f)
    if os.path.exists(f) and os.path.isdir(f):
        os.startfile(f)


@Singleton_close
class listediter(QDialog):
    def __init__(self, p, title, headers, lst, closecallback=None) -> None:
        super().__init__(p)
        self.lst = lst
        self.closecallback = closecallback
        try:
            self.setWindowTitle(title)
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)
            self.hcmodel = model

            table = QTableView()
            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            table.horizontalHeader().setStretchLastSection(True)
            # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers);
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
            table.setWordWrap(False)
            table.setModel(model)
            self.hctable = table

            for row, k in enumerate(lst):  # 2
                self.newline(row, k)
            formLayout = QVBoxLayout()
            formLayout.addWidget(self.hctable)
            button = QPushButton(_TR("添加行"))
            button.clicked.connect(lambda _: self.newline(0, ""))
            formLayout.addWidget(button)
            self.setLayout(formLayout)
            self.show()
        except:
            print_exc()

    def clicked2(self):
        try:
            self.lst.pop(self.hctable.currentIndex().row())
            self.hcmodel.removeRow(self.hctable.currentIndex().row())
        except:
            pass

    def closeEvent(self, a0: QCloseEvent) -> None:
        rows = self.hcmodel.rowCount()
        rowoffset = 0
        dedump = set()
        self.lst.clear()
        for row in range(rows):
            k = self.hcmodel.item(row, 1).text()
            if k == "" or k in dedump:
                rowoffset += 1
                continue
            self.lst.append(k)
            dedump.add(k)
        if self.closecallback:
            self.closecallback()

    def newline(self, row, k):
        self.hcmodel.insertRow(row, [QStandardItem(), QStandardItem(k)])
        self.hctable.setIndexWidget(
            self.hcmodel.index(row, 0),
            getcolorbutton(
                "", "", self.clicked2, icon="fa.times", constcolor="#FF69B4"
            ),
        )


@Singleton_close
class dialog_savedgame_new(saveposwindow):
    def startgame(self, game):
        if os.path.exists(game):
            if globalconfig["startgamenototop"] == False:
                idx = savehook_new_list.index(game)
                savehook_new_list.insert(0, savehook_new_list.pop(idx))
            self.close()
            startgame(game)

    def clicked2(self):
        try:
            game = self.currentfocuspath
            idx = savehook_new_list.index(game)
            savehook_new_list.pop(idx)
            if game in savehook_new_data:
                savehook_new_data.pop(game)

            idx2 = self.idxsave.index(game)
            self.flow.removeidx(idx2)
            self.idxsave.pop(idx2)
            self.flow.setfocus(idx2)
        except:
            pass

    def clicked4(self):
        opendir(self.currentfocuspath)

    def clicked3_batch(self):
        res = QFileDialog.getExistingDirectory(
            options=QFileDialog.Option.DontResolveSymlinks
        )
        if res != "":
            for _dir, _, _fs in os.walk(res):
                for _f in _fs:
                    path = os.path.abspath(os.path.join(_dir, _f))
                    if path.lower().endswith(".exe") == False:
                        continue
                    if path not in savehook_new_list:
                        checkifnewgame(path)
                        self.newline(path, True)

    def clicked3(self):

        f = QFileDialog.getOpenFileName(options=QFileDialog.Option.DontResolveSymlinks)

        res = f[0]
        if res != "":
            res = os.path.normpath(res)
            if res not in savehook_new_list:
                checkifnewgame(res)
                self.newline(res, True)

    def tagschanged(self, tags):
        self.currtags = tags
        newtags = tags

        ItemWidget.clearfocus()
        self.formLayout.removeWidget(self.flow)
        self.flow.deleteLater()
        self.idxsave.clear()
        self.flow = lazyscrollflow()
        self.flow.bgclicked.connect(ItemWidget.clearfocus)
        self.formLayout.insertWidget(self.formLayout.count() - 1, self.flow)
        QApplication.processEvents()
        for k in savehook_new_list:
            if newtags != self.currtags:
                break
            notshow = False
            for tag, _type, _ in tags:
                if _type == tagitem.TYPE_EXISTS:
                    if os.path.exists(k) == False:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_DEVELOPER:
                    if tag not in savehook_new_data[k]["developers"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_TAG:
                    if tag not in getvndbrealtags(savehook_new_data[k]["vndbtags"]):
                        notshow = True
                        break
                elif _type == tagitem.TYPE_USERTAG:
                    if tag not in savehook_new_data[k]["usertags"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_RAND:
                    if (
                        tag not in getvndbrealtags(savehook_new_data[k]["vndbtags"])
                        and tag not in savehook_new_data[k]["usertags"]
                        and tag not in savehook_new_data[k]["title"]
                        and tag not in savehook_new_data[k]["developers"]
                    ):
                        notshow = True
                        break
            if notshow:
                continue
            self.newline(k)

        QApplication.processEvents()
        self.flow.resizeandshow()

    def showmenu(self, p):
        menu = QMenu(self)
        startgame = QAction(_TR("开始游戏"))
        gamesetting = QAction(_TR("游戏设置"))
        delgame = QAction(_TR("删除游戏"))
        opendir = QAction(_TR("打开目录"))
        addgame = QAction(_TR("添加游戏"))
        batchadd = QAction(_TR("批量添加"))
        othersetting = QAction(_TR("其他设置"))

        if self.currentfocuspath:
            menu.addAction(startgame)
            menu.addAction(gamesetting)
            menu.addAction(delgame)
            menu.addAction(opendir)
        else:
            menu.addAction(addgame)
            menu.addAction(batchadd)
            menu.addAction(othersetting)
        action = menu.exec(self.mapToGlobal(p))
        if action == startgame:
            self.startgame(self.currentfocuspath)
        elif action == gamesetting:
            self.showsettingdialog()
        elif action == delgame:
            self.clicked2()
        elif action == opendir:
            self.clicked4()
        elif action == addgame:
            self.clicked3()
        elif action == batchadd:
            self.clicked3_batch()
        elif action == othersetting:
            dialog_syssetting(self)

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            flags=Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint,
            dic=globalconfig,
            key="savegamedialoggeo",
        )
        global _global_dialog_savedgame_new
        _global_dialog_savedgame_new = self
        self.setWindowTitle(_TR("游戏管理"))
        formLayout = QVBoxLayout()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(_TR("过滤")))

        def refreshcombo():
            _ = self.tagswidget.lineEdit.currentText()
            self.tagswidget.lineEdit.clear()
            self.tagswidget.lineEdit.addItems(globalconfig["labelset"])
            self.tagswidget.lineEdit.setCurrentText(_)

        layout.addWidget(
            getcolorbutton(
                "",
                "",
                lambda _: listediter(
                    parent,
                    _TR("标签集"),
                    _TRL(
                        [
                            "删除",
                            "标签",
                        ]
                    ),
                    globalconfig["labelset"],
                    closecallback=refreshcombo,
                ),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        )

        def callback(t):
            if t in globalconfig["labelset"]:
                tp = tagitem.TYPE_USERTAG
            else:
                tp = tagitem.TYPE_RAND
            self.tagswidget.addTag(t, tp)

            self.tagswidget.lineEdit.clear()
            self.tagswidget.lineEdit.addItems(globalconfig["labelset"])
            self.tagswidget.lineEdit.clearEditText()

        self.tagswidget = TagWidget(self)
        self.tagswidget.linepressedenter.connect(callback)
        self.currtags = tuple()
        self.tagswidget.tagschanged.connect(self.tagschanged)
        layout.addWidget(self.tagswidget)
        formLayout.addLayout(layout)
        self.flow = lazyscrollflow()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        formLayout.addWidget(self.flow)
        self.formLayout = formLayout
        buttonlayout = QHBoxLayout()
        self.buttonlayout = buttonlayout
        self.savebutton = []
        self.simplebutton(
            "开始游戏", True, lambda: self.startgame(self.currentfocuspath), True
        )
        self.simplebutton("游戏设置", True, self.showsettingdialog, False)
        self.simplebutton("删除游戏", True, self.clicked2, False)
        self.simplebutton("打开目录", True, self.clicked4, True)

        if globalconfig["startgamenototop"]:
            self.simplebutton("左移", True, functools.partial(self.moverank, -1), False)
            self.simplebutton("右移", True, functools.partial(self.moverank, 1), False)
        self.simplebutton("添加游戏", False, self.clicked3, 1)
        self.simplebutton("批量添加", False, self.clicked3_batch, 1)
        self.simplebutton("其他设置", False, lambda: dialog_syssetting(self), False)
        formLayout.addLayout(buttonlayout)
        _W = QWidget()
        _W.setLayout(formLayout)
        self.setCentralWidget(_W)
        self.activategamenum = 1
        self.itemfocuschanged(False, None)
        self.show()
        self.idxsave = []
        if globalconfig["hide_not_exists"]:
            self.tagswidget.addTag(_TR("存在"), tagitem.TYPE_EXISTS)
        else:
            self.tagschanged(tuple())

        class WindowEventFilter(QObject):
            def eventFilter(__, obj, event):
                try:
                    if obj == self:
                        global _global_dialog_setting_game
                        _global_dialog_setting_game.raise_()
                except:
                    pass
                return False

        self.__filter = WindowEventFilter()  # keep ref
        self.installEventFilter(self.__filter)

    def moverank(self, dx):
        game = self.currentfocuspath

        idx1 = self.idxsave.index(game)
        idx2 = (idx1 + dx) % len(self.idxsave)
        game2 = self.idxsave[idx2]
        self.idxsave[idx1], self.idxsave[idx2] = self.idxsave[idx2], self.idxsave[idx1]
        self.flow.switchidx(idx1, idx2)
        idx1 = savehook_new_list.index(game)
        idx2 = savehook_new_list.index(game2)
        savehook_new_list[idx1], savehook_new_list[idx2] = (
            savehook_new_list[idx2],
            savehook_new_list[idx1],
        )

    def showsettingdialog(self):
        try:
            dialog_setting_game(self.parent(), self.currentfocuspath)
        except:
            print_exc()

    def simplebutton(self, text, save, callback, exists):
        button5 = QPushButton()
        button5.setText(_TR(text))
        if save:
            self.savebutton.append((button5, exists))
        button5.clicked.connect(callback)
        button5.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.buttonlayout.addWidget(button5)
        return button5

    def itemfocuschanged(self, b, k):

        if b:
            self.currentfocuspath = k
        else:
            self.currentfocuspath = None

        for _btn, exists in self.savebutton:
            _able1 = b and (
                (not exists)
                or (self.currentfocuspath)
                and (os.path.exists(self.currentfocuspath))
            )
            _btn.setEnabled(_able1)

    def _getpixfunction(self, kk):
        _pix = QPixmap(savehook_new_data[kk]["imagepath"])
        if _pix.isNull():
            _pix = getExeIcon(kk, False, cache=True)
        return _pix

    def getagameitem(self, k):
        gameitem = ItemWidget(
            k, functools.partial(self._getpixfunction, k), savehook_new_data[k]["title"]
        )
        gameitem.doubleclicked.connect(self.startgame)
        gameitem.focuschanged.connect(self.itemfocuschanged)
        return gameitem

    def newline(self, k, first=False):

        itemw = globalconfig["dialog_savegame_layout"]["itemw"]
        itemh = globalconfig["dialog_savegame_layout"]["itemh"]

        if first:

            self.flow.insertwidget(
                0, (functools.partial(self.getagameitem, k), QSize(itemw, itemh))
            )
            self.idxsave.insert(0, k)
        else:
            self.flow.addwidget(
                (functools.partial(self.getagameitem, k), QSize(itemw, itemh))
            )
            # self.flow.addwidget( self.getagameitem(k))
            self.idxsave.append(k)


@Singleton_close
class dialog_savedgame_lagacy(QDialog):
    # _sigleton=False
    def closeEvent(self, a0) -> None:

        self.button.setFocus()
        rows = self.model.rowCount()

        for row in range(rows):
            savehook_new_data[self.model.item(row, 2).savetext]["title"] = (
                self.model.item(row, 3).text()
            )
        # dialog_savedgame._sigleton=False
        return QDialog().closeEvent(a0)

    def showsettingdialog(self, k, item):
        dialog_setting_game(self, k)

    def clicked2(self):
        try:
            key = savehook_new_list.pop(self.table.currentIndex().row())
            if key in savehook_new_data:
                savehook_new_data.pop(key)
            self.model.removeRow(self.table.currentIndex().row())
        except:
            pass

    def clicked3(self):

        f = QFileDialog.getOpenFileName(directory="")
        res = f[0]
        if res != "":
            row = 0  # model.rowCount()
            res = res.replace("/", "\\")
            if res in savehook_new_list:
                return

            self.newline(0, res)
            self.table.setCurrentIndex(self.model.index(0, 0))

    def clicked(self):
        if os.path.exists(self.model.item(self.table.currentIndex().row(), 2).savetext):
            savehook_new_list.insert(
                0, savehook_new_list.pop(self.table.currentIndex().row())
            )
            self.close()
            startgame(self.model.item(self.table.currentIndex().row(), 2).savetext)

    def newline(self, row, k):
        keyitem = QStandardItem()
        keyitem.savetext = k
        k = k.replace("/", "\\")
        self.model.insertRow(
            row,
            [
                QStandardItem(),
                QStandardItem(),
                keyitem,
                QStandardItem((savehook_new_data[k]["title"])),
            ],
        )
        self.table.setIndexWidget(
            self.model.index(row, 0), getsimpleswitch(savehook_new_data[k], "leuse")
        )
        self.table.setIndexWidget(
            self.model.index(row, 1),
            getcolorbutton("", "", functools.partial(opendir, k), qicon=getExeIcon(k)),
        )

        self.table.setIndexWidget(
            self.model.index(row, 2),
            getcolorbutton(
                "",
                "",
                functools.partial(self.showsettingdialog, k, keyitem),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        )

    def __init__(self, parent) -> None:
        # if dialog_savedgame._sigleton :
        #         return
        # dialog_savedgame._sigleton=True
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.setWindowTitle(_TR("已保存游戏"))
        formLayout = QVBoxLayout(self)  #
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(_TRL(["转区", "", "设置", "游戏"]))  # ,'HOOK'])

        self.model = model

        table = QTableView()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        # table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode((QAbstractItemView.SingleSelection))
        table.setWordWrap(False)
        table.setModel(model)
        self.table = table
        for row, k in enumerate(savehook_new_list):  # 2
            self.newline(row, k)
        button = QPushButton()
        button.setText(_TR("开始游戏"))
        self.button = button
        button.clicked.connect(self.clicked)
        button3 = QPushButton()
        button3.setText(_TR("添加游戏"))

        button3.clicked.connect(self.clicked3)
        button2 = QPushButton()
        button2.setText(_TR("删除游戏"))

        button2.clicked.connect(self.clicked2)

        formLayout.addWidget(table)
        formLayout.addWidget(button)
        formLayout.addWidget(button3)
        formLayout.addWidget(button2)
        self.resize(QSize(800, 400))
        self.show()
