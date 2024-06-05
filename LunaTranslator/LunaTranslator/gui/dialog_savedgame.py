from PyQt5.QtGui import QMouseEvent
from qtsymbols import *
import os, functools, uuid, threading
from datetime import datetime, timedelta
from traceback import print_exc
import windows, gobject, winsharedutils
from myutils.vndb import parsehtmlmethod
from myutils.config import (
    savehook_new_list,
    savehook_new_data,
    savegametaged,
    vndbtagdata,
    _TR,
    _TRL,
    globalconfig,
    static_data,
)
from myutils.hwnd import getExeIcon
from myutils.wrapper import Singleton_close, Singleton, threader, tryprint
from myutils.utils import checkifnewgame, str2rgba, vidchangedtask, titlechangedtask
from gui.inputdialog import noundictconfigdialog1, autoinitdialog
from gui.specialwidget import (
    ScrollFlow,
    chartwidget,
    lazyscrollflow,
    stackedlist,
    shrinkableitem,
)
from gui.usefulwidget import (
    yuitsu_switch,
    saveposwindow,
    getsimplepatheditor,
    getboxlayout,
    getlineedit,
    MySwitch,
    auto_select_webview,
    Prompt_dialog,
    getsimplecombobox,
    D_getsimpleswitch,
    getspinbox,
    getcolorbutton,
    D_getcolorbutton,
    makesubtab_lazy,
    tabadd_lazy,
    getsimpleswitch,
    getspinbox,
    selectcolor,
    listediter,
    listediterline,
)


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

    def click(self):
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

    def mousePressEvent(self, ev) -> None:
        self.click()

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
                self.likelink,
                icon="fa.heart",
                constcolor="#FF69B4",
                sizefixed=True,
            )
        )
        hlay.addWidget(
            getcolorbutton(
                "",
                "",
                lambda: self.urlclicked((None, None, self.current)),
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


class dialog_setting_game_internal(QWidget):
    def selectexe(self):
        f = QFileDialog.getOpenFileName(directory=self.exepath)
        res = f[0]
        if res != "":

            res = os.path.normpath(res)
            if res in savehook_new_list:
                return
            savehook_new_list[savehook_new_list.index(self.exepath)] = res
            savehook_new_data[res] = savehook_new_data[self.exepath]
            _icon = getExeIcon(res, cache=True)

            self.setWindowIcon(_icon)
            self.editpath.setText(res)
            self.exepath = res

    def __init__(self, parent, exepath) -> None:
        super().__init__(parent)
        vbox = QVBoxLayout(self)
        self.setLayout(vbox)
        formLayout = QFormLayout()
        self.exepath = exepath
        self.editpath = QLineEdit(exepath)
        self.editpath.setReadOnly(True)
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

        vndbid = QLineEdit(str(savehook_new_data[exepath]["vid"]))
        vndbid.setValidator(QIntValidator())
        vndbid.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        vndbid.textEdited.connect(functools.partial(vidchangedtask, exepath))

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

        methodtab, do = makesubtab_lazy(
            _TRL(
                [
                    "启动",
                    "HOOK",
                    "预翻译",
                    "语音",
                    "标签",
                    "统计信息",
                    "存档备份",
                    "封面",
                ]
            ),
            [
                functools.partial(self.doaddtab, self.starttab, exepath),
                functools.partial(self.doaddtab, self.gethooktab, exepath),
                functools.partial(self.doaddtab, self.getpretranstab, exepath),
                functools.partial(self.doaddtab, self.getttssetting, exepath),
                functools.partial(self.doaddtab, self.getlabelsetting, exepath),
                functools.partial(self.doaddtab, self.getstatistic, exepath),
                functools.partial(self.doaddtab, self.getbackup, exepath),
                functools.partial(self.doaddtab, self.fengmiantab, exepath),
            ],
            delay=True,
        )

        vbox.addLayout(formLayout)
        vbox.addWidget(methodtab)
        do()

    def fengmiantab(self, exepath):
        _w = QWidget()
        formLayout = QFormLayout()
        _w.setLayout(formLayout)

        def selectimg(res):
            savehook_new_data[exepath]["imagepath"] = res
            savehook_new_data[exepath]["isimagepathusersetted"] = True

        formLayout.addRow(
            _TR("封面"),
            getsimplepatheditor(
                savehook_new_data[exepath]["imagepath"],
                False,
                False,
                None,
                selectimg,
                True,
            ),
        )

        def selectimg2(ress):
            savehook_new_data[exepath]["isimagepathusersetted_much"] = True
            savehook_new_data[exepath]["imagepath_much2"] = ress

        formLayout.addRow(
            _TR("封面_大"),
            getsimplepatheditor(
                savehook_new_data[exepath]["imagepath_much2"],
                True,
                False,
                None,
                selectimg2,
                True,
            ),
        )
        return _w

    def doaddtab(self, wfunct, exe, layout):
        w = wfunct(exe)
        layout.addWidget(w)

    def getbackup(self, exepath):
        _w = QWidget()
        formLayout = QFormLayout()
        _w.setLayout(formLayout)

        formLayout.addRow(
            _TR("路径"),
            getsimplepatheditor(
                savehook_new_data[exepath]["autosavesavedata"],
                False,
                True,
                None,
                lambda _: savehook_new_data[exepath].__setitem__(
                    "autosavesavedata", os.path.normpath(_)
                ),
                True,
            ),
        )

        formLayout.addRow(
            _TR("备份到"),
            getsimplepatheditor(
                (
                    globalconfig["backupsavedatato"]
                    if os.path.exists(globalconfig["backupsavedatato"])
                    else os.path.abspath("./cache/backup")
                ),
                False,
                True,
                None,
                lambda _: savehook_new_data[exepath].__setitem__(
                    "backupsavedatato", os.path.normpath(_)
                ),
                True,
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
        t = QTimer(self)
        t.setInterval(1000)
        t.timeout.connect(self.refresh)
        t.start(0)
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
                    listediterline(
                        _TR("禁止自动朗读的人名"),
                        _TR("人名"),
                        savehook_new_data[exepath]["allow_tts_auto_names_v4"],
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

        def selectimg(exepath, key, res):
            savehook_new_data[exepath][key] = res

        for showname, key, filt in [
            ("json翻译文件", "gamejsonfile", "*.json"),
            ("sqlite翻译记录", "gamesqlitefile", "*.sqlite"),
        ]:
            formLayout.addRow(
                _TR(showname),
                getsimplepatheditor(
                    savehook_new_data[exepath][key],
                    False,
                    False,
                    filt,
                    functools.partial(selectimg, exepath, key),
                    True,
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


@Singleton_close
class dialog_setting_game(QDialog):

    def __init__(self, parent, exepath) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        global _global_dialog_setting_game
        _global_dialog_setting_game = self

        self.setWindowTitle(savehook_new_data[exepath]["title"])

        self.setWindowIcon(getExeIcon(exepath, cache=True))
        _ = dialog_setting_game_internal(self, exepath)

        _.setMinimumSize(QSize(600, 500))
        l = QHBoxLayout(self)
        self.setLayout(l)
        l.addWidget(_)
        l.setContentsMargins(0, 0, 0, 0)
        self.show()
        try:
            self.setGeometry(
                calculate_centered_rect(
                    _global_dialog_savedgame_new.parent().parent().geometry(),
                    self.size(),
                )
            )
        except:
            pass


@Singleton
class dialog_syssetting(QDialog):

    def __init__(self, parent, type_=1) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(_TR("其他设置"))
        formLayout = QFormLayout(self)

        formLayout.addRow(
            QLabel(_TR("隐藏不存在的游戏")),
            getsimpleswitch(globalconfig, "hide_not_exists"),
        )
        if type_ == 1:
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
        elif type_ == 2:
            for key, name in [
                ("listitemheight", "文字区高度"),
                ("listitemwidth", "高度"),
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
        if type_ == 1:
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

        if type_ == 1:
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


def _getpixfunction(kk):
    _pix = QPixmap(savehook_new_data[kk]["imagepath"])
    if _pix.isNull():
        _pix = getExeIcon(kk, False, cache=True)
    return _pix


def startgamecheck(self, game):
    if not game:
        return
    if not os.path.exists(game):
        return
    if globalconfig["startgamenototop"] == False:
        idx = savehook_new_list.index(game)
        savehook_new_list.insert(0, savehook_new_list.pop(idx))
    self.parent().parent().close()
    startgame(game)


def addgamesingle(callback, targetlist):
    f = QFileDialog.getOpenFileName(options=QFileDialog.Option.DontResolveSymlinks)

    res = f[0]
    if res == "":
        return
    res = os.path.normpath(res)
    if checkifnewgame(targetlist, res):
        callback(res)


def addgamebatch(callback, targetlist):
    res = QFileDialog.getExistingDirectory(
        options=QFileDialog.Option.DontResolveSymlinks
    )
    if res == "":
        return
    for _dir, _, _fs in os.walk(res):
        for _f in _fs:
            path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
            if path.lower().endswith(".exe") == False:
                continue
            if checkifnewgame(targetlist, path):
                callback(path)


@Singleton_close
class dialog_savedgame_integrated(saveposwindow):

    def selectlayout(self, type):
        try:
            globalconfig["gamemanager_integrated_internal_layout"] = type
            klass = [
                dialog_savedgame_new,
                dialog_savedgame_v3,
                dialog_savedgame_lagacy,
            ][type]

            [self.layout1btn, self.layout2btn, self.layout3btn][(type) % 3].setEnabled(
                False
            )
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 1) % 3
            ].setEnabled(False)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 2) % 3
            ].setEnabled(False)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 1) % 3
            ].setChecked(False)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 2) % 3
            ].setChecked(False)
            _old = self.internallayout.takeAt(0).widget()
            _old.hide()
            _ = klass(self)
            self.internallayout.addWidget(_)
            _.directshow()
            _old.deleteLater()
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 1) % 3
            ].setEnabled(True)
            [self.layout1btn, self.layout2btn, self.layout3btn][
                (type + 2) % 3
            ].setEnabled(True)
        except:
            print_exc()

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            flags=Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint,
            dic=globalconfig,
            key="savegamedialoggeo",
        )
        self.setWindowTitle(_TR("游戏管理"))

        w, self.internallayout = getboxlayout(
            [], margin0=True, makewidget=True, both=True
        )

        self.internallayout.addWidget(QWidget())
        self.setCentralWidget(w)
        colors = ["#7f7f7f", "#7f7f7f", "#FF69B4", "#FF69B4"]
        self.layout1btn = MySwitch(
            self, icons=["fa.th", "fa.th"], size=20, colors=colors
        )
        self.layout2btn = MySwitch(
            self, icons=["fa.th-list", "fa.th-list"], size=20, colors=colors
        )
        self.layout3btn = MySwitch(
            self, icons=["fa.list", "fa.list"], size=20, colors=colors
        )
        self.layout1btn.clicked.connect(functools.partial(self.selectlayout, 0))
        self.layout2btn.clicked.connect(functools.partial(self.selectlayout, 1))
        self.layout3btn.clicked.connect(functools.partial(self.selectlayout, 2))
        self.layout1btn.setFixedSize(QSize(20, 20))
        self.layout2btn.setFixedSize(QSize(20, 20))
        self.layout3btn.setFixedSize(QSize(20, 20))
        self.show()
        self.selectlayout(globalconfig["gamemanager_integrated_internal_layout"])

    def resizeEvent(self, e: QResizeEvent):
        self.layout1btn.move(e.size().width() - self.layout1btn.width(), 0)
        self.layout2btn.move(
            e.size().width() - self.layout2btn.width() - self.layout1btn.width(), 0
        )
        self.layout3btn.move(
            e.size().width()
            - self.layout3btn.width()
            - self.layout2btn.width()
            - self.layout1btn.width(),
            0,
        )


class dialog_savedgame_new(QWidget):
    def clicked2(self):
        try:
            game = self.currentfocuspath
            idx2 = savehook_new_list.index(game)
            savehook_new_list.pop(idx2)

            idx2 = self.idxsave.index(game)
            self.flow.removeidx(idx2)
            self.idxsave.pop(idx2)
            ItemWidget.clearfocus()
            try:
                self.flow.widget(idx2).click()
            except:
                self.flow.widget(idx2 - 1).click()

        except:
            print_exc()

    def clicked4(self):
        opendir(self.currentfocuspath)

    def clicked3_batch(self):
        addgamebatch(lambda res: self.newline(res, True), savehook_new_list)

    def clicked3(self):
        addgamesingle(lambda res: self.newline(res, True), savehook_new_list)

    def tagschanged(self, tags):
        self.currtags = tags
        newtags = tags
        self.idxsave.clear()
        ItemWidget.clearfocus()
        self.formLayout.removeWidget(self.flow)
        self.flow.deleteLater()
        self.flow = lazyscrollflow()
        self.flow.bgclicked.connect(ItemWidget.clearfocus)
        self.formLayout.insertWidget(self.formLayout.count() - 1, self.flow)
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
            exists = os.path.exists(self.currentfocuspath)
            if exists:
                menu.addAction(startgame)
            menu.addAction(gamesetting)
            menu.addAction(delgame)
            if exists:
                menu.addAction(opendir)
        else:
            menu.addAction(addgame)
            menu.addAction(batchadd)
            menu.addAction(othersetting)
        action = menu.exec(self.mapToGlobal(p))
        if action == startgame:
            startgamecheck(self, self.currentfocuspath)
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

    def directshow(self):
        self.flow.directshow()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        global _global_dialog_savedgame_new
        _global_dialog_savedgame_new = self
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
                    _TR("标签"),
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
        self.tagswidget.lineEdit.addItems(globalconfig["labelset"])
        self.tagswidget.lineEdit.setCurrentText("")
        self.tagswidget.linepressedenter.connect(callback)
        self.currtags = tuple()
        self.tagswidget.tagschanged.connect(self.tagschanged)
        _ = QLabel()
        _.setFixedWidth(60)
        layout.addWidget(self.tagswidget)
        layout.addWidget(_)
        formLayout.addLayout(layout)
        self.flow = QWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        formLayout.addWidget(self.flow)
        self.formLayout = formLayout
        buttonlayout = QHBoxLayout()
        self.buttonlayout = buttonlayout
        self.savebutton = []
        self.simplebutton(
            "开始游戏", True, lambda: startgamecheck(self, self.currentfocuspath), True
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
        self.idxsave = []
        self.setLayout(formLayout)
        self.activategamenum = 1
        self.itemfocuschanged(False, None)
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
        self.idxsave.insert(idx2, self.idxsave.pop(idx1))
        self.flow.switchidx(idx1, idx2)

        idx1 = savehook_new_list.index(game)
        idx2 = savehook_new_list.index(game2)
        savehook_new_list.insert(idx2, savehook_new_list.pop(idx1))

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

    def getagameitem(self, k):
        gameitem = ItemWidget(
            k, functools.partial(_getpixfunction, k), savehook_new_data[k]["title"]
        )
        gameitem.doubleclicked.connect(functools.partial(startgamecheck, self))
        gameitem.focuschanged.connect(self.itemfocuschanged)
        return gameitem

    def newline(self, k, first=False):

        itemw = globalconfig["dialog_savegame_layout"]["itemw"]
        itemh = globalconfig["dialog_savegame_layout"]["itemh"]

        if first:
            self.idxsave.insert(0, k)
            self.flow.insertwidget(
                0, (functools.partial(self.getagameitem, k), QSize(itemw, itemh))
            )
        else:
            self.idxsave.append(k)
            self.flow.addwidget(
                (functools.partial(self.getagameitem, k), QSize(itemw, itemh))
            )


class LazyLoadTableView(QTableView):
    def __init__(self, model: QStandardItemModel) -> None:
        super().__init__()
        self.widgetfunction = []
        self.lock = threading.Lock()
        self.setModel(model)
        self.started = False

    def starttraceir(self):
        self.started = True
        self.model().rowsRemoved.connect(functools.partial(self.insertremove))
        self.model().rowsInserted.connect(functools.partial(self.insert))

    def resizeEvent(self, e):
        self.loadVisibleRows()
        super().resizeEvent(e)

    def insertremove(self, index, start, end):
        off = end - start + 1
        with self.lock:
            collect = []
            for i in range(len(self.widgetfunction)):
                if self.widgetfunction[i][0] > end:
                    self.widgetfunction[i][0] -= off
                elif (
                    self.widgetfunction[i][0] >= start
                    and self.widgetfunction[i][0] <= end
                ):
                    collect.append(i)
            for i in collect:
                self.widgetfunction.pop(i)

        self.loadVisibleRows()

    def insert(self, index, start, end):
        off = end - start + 1
        with self.lock:
            for i in range(len(self.widgetfunction)):
                if self.widgetfunction[i][0] >= start:
                    self.widgetfunction[i][0] += off
                    print(self.widgetfunction[i])

        self.loadVisibleRows()

    def setIndexWidget(self, index: QModelIndex, widgetf):
        if not self.started:
            self.widgetfunction.append([index.row(), index.column(), widgetf])
            return
        if self.visualRect(index).intersects(self.viewport().rect()):
            w = widgetf()
            super().setIndexWidget(index, w)
        else:
            with self.lock:
                self.widgetfunction.append([index.row(), index.column(), widgetf])

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.loadVisibleRows()

    def loadVisibleRows(self):
        with self.lock:
            collect = []
            for i, index in enumerate(self.widgetfunction):
                row, col, wf = index
                if self.visualRect(self.model().index(row, col)).intersects(
                    self.viewport().rect()
                ):
                    collect.insert(0, i)

            for i in collect:
                row, col, wf = self.widgetfunction.pop(i)

                w = wf()
                super().setIndexWidget(self.model().index(row, col), w)


class dialog_savedgame_lagacy(QWidget):

    def directshow(self):
        pass

    def showsettingdialog(self, k):
        dialog_setting_game(self, k)

    def clicked2(self):
        try:

            idx = self.table.currentIndex().row()
            savehook_new_list.pop(idx)
            self.model.removeRow(self.table.currentIndex().row())
        except:
            pass

    def clicked3(self):
        def call(res):
            self.newline(0, res)
            self.table.setCurrentIndex(self.model.index(0, 0))

        addgamesingle(call)

    def clicked(self):
        startgamecheck(
            self, self.model.item(self.table.currentIndex().row(), 2).savetext
        )

    def delayloadicon(self, k):
        return getcolorbutton(
            "", "", functools.partial(opendir, k), qicon=getExeIcon(k, cache=True)
        )

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
            self.model.index(row, 0), D_getsimpleswitch(savehook_new_data[k], "leuse")
        )
        self.table.setIndexWidget(
            self.model.index(row, 1),
            functools.partial(self.delayloadicon, k),
        )

        self.table.setIndexWidget(
            self.model.index(row, 2),
            D_getcolorbutton(
                "",
                "",
                functools.partial(self.showsettingdialog, k),
                icon="fa.gear",
                constcolor="#FF69B4",
            ),
        )

    def __init__(self, parent) -> None:
        # if dialog_savedgame._sigleton :
        #         return
        # dialog_savedgame._sigleton=True
        super().__init__(parent)

        formLayout = QVBoxLayout(self)  #
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(_TRL(["转区", "", "设置", "游戏"]))  # ,'HOOK'])

        self.model = model

        table = LazyLoadTableView(model)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setStretchLastSection(True)
        # table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        self.table = table
        for row, k in enumerate(savehook_new_list):  # 2
            self.newline(row, k)
        self.table.starttraceir()
        bottom = QHBoxLayout()

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
        bottom.addWidget(button)
        bottom.addWidget(button2)
        bottom.addWidget(button3)
        _ = QLabel()
        _.setFixedHeight(20)
        _.setStyleSheet("background: transparent;")
        formLayout.addWidget(_)
        formLayout.addWidget(table)
        formLayout.addLayout(bottom)


class clickitem(QWidget):
    focuschanged = pyqtSignal(bool, str)
    doubleclicked = pyqtSignal(str)
    globallashfocus = None

    @classmethod
    def clearfocus(cls):
        try:  # 可能已被删除
            if clickitem.globallashfocus:
                clickitem.globallashfocus.focusOut()
        except:
            pass
        clickitem.globallashfocus = None

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.exe)

    def click(self):
        try:
            self.bottommask.setStyleSheet(
                f'background-color: {str2rgba(globalconfig["dialog_savegame_layout"]["onselectcolor"],globalconfig["dialog_savegame_layout"]["transparent"])};'
            )

            if self != clickitem.globallashfocus:
                clickitem.clearfocus()
            clickitem.globallashfocus = self
            self.focuschanged.emit(True, self.exe)
        except:
            print_exc()

    def mousePressEvent(self, ev) -> None:
        self.click()

    def focusOut(self):
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.focuschanged.emit(False, self.exe)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())
        self.bottomline.resize(a0.size())

    def __init__(self, exe):
        super().__init__()

        self.exe = exe
        self.lay = QHBoxLayout()
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0, 0, 0, 0)

        self.maskshowfileexists = QLabel(self)

        c = globalconfig["dialog_savegame_layout"][
            ("onfilenoexistscolor", "backcolor")[os.path.exists(exe)]
        ]
        c = str2rgba(c, globalconfig["dialog_savegame_layout"]["transparent"])
        self.maskshowfileexists.setStyleSheet(f"background-color:{c};")
        self.bottommask = QLabel(self)
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        _ = QLabel(self)
        _.setStyleSheet(
            """background-color: rgba(255,255,255, 0);border-bottom: 1px solid gray;"""
        )
        self.bottomline = _
        size = globalconfig["dialog_savegame_layout"]["listitemheight"]
        _ = QLabel()
        _.setFixedSize(QSize(size, size))
        _.setScaledContents(True)
        _.setStyleSheet("background-color: rgba(255,255,255, 0);")
        icon = getExeIcon(exe, icon=False, cache=True)
        icon.setDevicePixelRatio(self.devicePixelRatioF())
        _.setPixmap(icon)
        self.lay.addWidget(_)
        _ = QLabel(savehook_new_data[exe]["title"])
        _.setWordWrap(True)
        _.setFixedHeight(size + 1)
        self.lay.addWidget(_)
        self.setLayout(self.lay)
        _.setStyleSheet("""background-color: rgba(255,255,255, 0);""")


class pixwrapper(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.pixview = QLabel(self)
        self.pixmaps = []
        self.k = None
        self.pixmapi = 0
        self.pixview.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def tolastnext(self, dx):
        if len(self.pixmaps) == 0:
            return
        self.pixmapi = (self.pixmapi + dx) % len(self.pixmaps)
        self.visidx()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.pos().x() < self.width() * 2 / 5:
            self.tolastnext(-1)
        elif a0.pos().x() > self.width() * 3 / 5:
            self.tolastnext(1)
        else:
            pass
        return super().mousePressEvent(a0)

    def resizeEvent(self, e: QResizeEvent):
        self.pixview.resize(e.size().width(), e.size().height())
        self.visidx()

    def visidx(self):
        if self.k and len(self.pixmaps) == 0:
            self.pixmaps = [_getpixfunction(self.k)]
        if self.pixmapi < len(self.pixmaps):
            pixmap = self.pixmaps[self.pixmapi]
            if isinstance(pixmap, str):
                pixmap = QPixmap.fromImage(QImage(pixmap))
            if pixmap.isNull():
                self.pixmaps.pop(self.pixmapi)
                return self.visidx()
            pixmap.setDevicePixelRatio(self.devicePixelRatioF())
            self.pixview.setPixmap(self.scalepix(pixmap))

    def setpix(self, k):

        self.k = k
        self.pixmaps = savehook_new_data[k]["imagepath_much2"]
        self.pixmapi = 0
        self.visidx()

    def scalepix(self, pix: QPixmap):
        pix = pix.scaled(
            self.pixview.size() * self.devicePixelRatioF(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        return pix


class dialog_savedgame_v3(QWidget):
    def viewitem(self, k):
        try:
            self.pixview.setpix(k)
            self.currentfocuspath = k
            if self.righttop.count() > 1:
                self.righttop.removeTab(1)
            tabadd_lazy(
                self.righttop,
                savehook_new_data[k]["title"],
                lambda v: v.addWidget(dialog_setting_game_internal(self, k)),
            )

        except:
            print_exc()

    def itemfocuschanged(self, reftagid, b, k):

        self.reftagid = reftagid
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
        if self.currentfocuspath:
            self.viewitem(k)

    def delayitemcreater(self, k, select, reftagid):

        item = clickitem(k)
        item.doubleclicked.connect(functools.partial(startgamecheck, self))
        item.focuschanged.connect(functools.partial(self.itemfocuschanged, reftagid))
        if select:
            item.click()
        return item

    def newline(self, res):
        self.reallist[self.reftagid].insert(0, res)
        self.stack.w(self.calculatetagidx(self.reftagid)).insertw(
            0,
            functools.partial(
                self.delayitemcreater,
                res,
                True,
                self.reftagid,
            ),
            1 + globalconfig["dialog_savegame_layout"]["listitemheight"],
        )
        self.stack.directshow()

    def stack_showmenu(self, p):
        if not self.currentfocuspath:
            return
        menu = QMenu(self)
        startgame = QAction(_TR("开始游戏"))
        delgame = QAction(_TR("删除游戏"))
        opendir = QAction(_TR("打开目录"))
        addtolist = QAction(_TR("添加到列表"))

        exists = os.path.exists(self.currentfocuspath)
        if exists:
            menu.addAction(startgame)
        menu.addAction(delgame)
        if exists:
            menu.addAction(opendir)
        menu.addAction(addtolist)
        action = menu.exec(QCursor.pos())
        if action == startgame:
            startgamecheck(self, self.currentfocuspath)
        elif action == delgame:
            self.clicked2()
        elif action == opendir:
            self.clicked4()
        elif action == addtolist:
            self.addtolist()

    def addtolistcallback(self, __d, __uid, path):

        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        __save = self.reftagid
        self.reftagid = uid

        if path not in self.getreflist():
            self.getreflist().insert(0, path)
            self.newline(path)
        self.reftagid = __save

    def addtolist(self):
        __d = {"k": 0}

        __vis = []
        __uid = []
        for _ in savegametaged:
            if _ is None:
                __vis.append("GLOBAL")
                __uid.append(None)
            else:
                __vis.append(_["title"])
                __uid.append(_["uid"])
            if self.reftagid == __uid[-1]:
                __uid.pop(-1)
                __vis.pop(-1)
        autoinitdialog(
            self,
            _TR("目标"),
            600,
            [
                {
                    "type": "combo",
                    "name": _TR("目标"),
                    "d": __d,
                    "k": "k",
                    "list": __vis,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(
                        self.addtolistcallback, __d, __uid, self.currentfocuspath
                    ),
                },
            ],
        )

    def directshow(self):
        self.stack.directshow()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.currentfocuspath = None
        self.reftagid = None
        self.reallist = {}
        self.stack = stackedlist()
        self.stack.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.stack.customContextMenuRequested.connect(self.stack_showmenu)
        self.stack.setFixedWidth(
            globalconfig["dialog_savegame_layout"]["listitemwidth"]
        )
        self.stack.bgclicked.connect(clickitem.clearfocus)
        lay = QHBoxLayout()
        self.setLayout(lay)
        lay.addWidget(self.stack)
        lay.setSpacing(0)
        self.righttop = makesubtab_lazy()
        self.pixview = pixwrapper()
        _w = QWidget()
        rightlay = QVBoxLayout()
        rightlay.setContentsMargins(0, 0, 0, 0)
        _w.setLayout(rightlay)
        self.righttop.addTab(_w, _TR("封面"))
        lay.addWidget(self.righttop)
        rightlay.addWidget(self.pixview)
        self.pixview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pixview.customContextMenuRequested.connect(self.stack_showmenu)
        self.buttonlayout = QHBoxLayout()
        self.savebutton = []
        rightlay.addLayout(self.buttonlayout)

        self.simplebutton(
            "开始游戏", True, lambda: startgamecheck(self, self.currentfocuspath), True
        )
        self.simplebutton("删除游戏", True, self.clicked2, False)
        self.simplebutton("打开目录", True, self.clicked4, True)
        self.simplebutton("添加到列表", False, self.addtolist, 1)
        if globalconfig["startgamenototop"]:
            self.simplebutton("上移", True, functools.partial(self.moverank, -1), False)
            self.simplebutton("下移", True, functools.partial(self.moverank, 1), False)
        self.simplebutton("添加游戏", False, self.clicked3, 1)
        self.simplebutton("批量添加", False, self.clicked3_batch, 1)
        self.simplebutton(
            "其他设置", False, lambda: dialog_syssetting(self, type_=2), False
        )

        for i, tag in enumerate(savegametaged):
            # None
            # {
            #     "title":xxx
            #     "games":[]
            # }
            if tag is None:
                title = "GLOBAL"
                lst = savehook_new_list
                tagid = None
                opened = True
            else:
                lst = tag["games"]
                title = tag["title"]
                tagid = tag["uid"]
                opened = tag.get("opened", True)
            group0 = self.createtaglist(title, tagid, opened)
            self.stack.insertw(i, group0)
            rowreal = 0
            for row, k in enumerate(lst):
                if globalconfig["hide_not_exists"] and not os.path.exists(k):
                    continue
                self.reallist[tagid].append(k)
                group0.insertw(
                    rowreal,
                    functools.partial(
                        self.delayitemcreater, k, i == 0 and rowreal == 0, tagid
                    ),
                    1 + globalconfig["dialog_savegame_layout"]["listitemheight"],
                )

                rowreal += 1

    def taglistrerank(self, tagid, dx):
        idx1 = self.calculatetagidx(tagid)

        idx2 = (idx1 + dx) % len(savegametaged)
        savegametaged.insert(idx2, savegametaged.pop(idx1))
        self.stack.switchidx(idx1, idx2)

    def calculatetagidx(self, tagid):
        i = 0
        for save in savegametaged:
            if save is None and tagid is None:
                break
            elif save and tagid and save["uid"] == tagid:
                break
            i += 1

        return i

    def tagbuttonmenu(self, tagid):
        self.currentfocuspath = None
        self.reftagid = tagid
        menu = QMenu(self)
        editname = QAction(_TR("修改名称"))
        addlist = QAction(_TR("添加列表"))
        dellist = QAction(_TR("删除列表"))
        Upaction = QAction(_TR("上移"))
        Downaction = QAction(_TR("下移"))
        addgame = QAction(_TR("添加游戏"))
        batchadd = QAction(_TR("批量添加"))

        menu.addAction(Upaction)
        menu.addAction(Downaction)
        if tagid:
            menu.addAction(editname)
        menu.addAction(addlist)
        if tagid:
            menu.addAction(dellist)
        menu.addAction(addgame)
        menu.addAction(batchadd)
        action = menu.exec(QCursor.pos())
        if action == addgame:
            self.clicked3()
        elif action == batchadd:
            self.clicked3_batch()
        elif action == Upaction:
            self.taglistrerank(tagid, -1)
        elif action == Downaction:
            self.taglistrerank(tagid, 1)
        elif action == editname or action == addlist:
            _dia = Prompt_dialog(
                self,
                _TR("添加列表"),
                "",
                [
                    [_TR("名称"), ""],
                ],
            )

            if _dia.exec():

                title = _dia.text[0].text()
                if title != "":
                    i = self.calculatetagidx(tagid)
                    if action == addlist:
                        tag = {
                            "title": title,
                            "games": [],
                            "uid": str(uuid.uuid4()),
                            "opened": True,
                        }
                        savegametaged.insert(i, tag)
                        group0 = self.createtaglist(title, tag["uid"], True)
                        self.stack.insertw(i, group0)
                    elif action == editname:
                        self.stack.w(i).settitle(title)
                        savegametaged[i]["title"] = title

        elif action == dellist:
            i = self.calculatetagidx(tagid)
            savegametaged.pop(i)
            self.stack.popw(i)
            self.reallist.pop(tagid)

    def createtaglist(self, title, tagid, opened):

        self.reallist[tagid] = []
        _btn = QPushButton(title)
        _btn.customContextMenuRequested
        _btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        _btn.customContextMenuRequested.connect(
            functools.partial(self.tagbuttonmenu, tagid)
        )
        return shrinkableitem(_btn, opened)

    def getreflist(self):
        tag = savegametaged[self.calculatetagidx(self.reftagid)]
        if tag is None:
            return savehook_new_list
        return tag["games"]

    def getrefid(self):
        tag = savegametaged[self.calculatetagidx(self.reftagid)]
        if tag is None:
            return None
        return tag["uid"]

    def moverank(self, dx):
        game = self.currentfocuspath
        idx1 = self.reallist[self.getrefid()].index(game)
        idx2 = (idx1 + dx) % len(self.reallist[self.getrefid()])
        game2 = self.reallist[self.getrefid()][idx2]
        self.reallist[self.getrefid()].insert(
            idx2, self.reallist[self.getrefid()].pop(idx1)
        )

        self.stack.w(self.calculatetagidx(self.reftagid)).switchidx(idx1, idx2)
        idx1 = self.getreflist().index(game)
        idx2 = self.getreflist().index(game2)
        self.getreflist().insert(idx2, self.getreflist().pop(idx1))

    def clicked2(self):
        if not self.currentfocuspath:
            return

        try:
            game = self.currentfocuspath
            idx2 = self.getreflist().index(game)
            self.getreflist().pop(idx2)

            idx2 = self.reallist[self.getrefid()].index(game)
            self.reallist[self.getrefid()].pop(idx2)
            clickitem.clearfocus()
            group0 = self.stack.w(self.calculatetagidx(self.reftagid))
            group0.popw(idx2)
            try:
                group0.w(idx2).click()
            except:
                group0.w(idx2 - 1).click()
        except:
            print_exc()

    def clicked4(self):
        opendir(self.currentfocuspath)

    def clicked3_batch(self):
        addgamebatch(lambda res: self.newline(res), self.getreflist())

    def clicked3(self):
        addgamesingle(lambda res: self.newline(res), self.getreflist())

    def clicked(self):
        startgamecheck(self, self.currentfocuspath)

    def simplebutton(self, text, save, callback, exists):
        button5 = QPushButton()
        button5.setText(_TR(text))
        if save:
            self.savebutton.append((button5, exists))
        button5.clicked.connect(callback)
        button5.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.buttonlayout.addWidget(button5)
        return button5
