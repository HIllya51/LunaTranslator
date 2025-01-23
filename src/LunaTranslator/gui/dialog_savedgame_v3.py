from qtsymbols import *
import os, functools, uuid, threading, shutil, time
from traceback import print_exc
import gobject
from myutils.config import (
    savehook_new_list,
    savehook_new_data,
    savegametaged,
    get_launchpath,
    extradatas,
    globalconfig,
)
from myutils.hwnd import clipboard_set_image
from myutils.utils import (
    get_time_stamp,
    loopbackrecorder,
    getimagefilefilter,
    targetmod,
)
from myutils.audioplayer import playonce
from gui.inputdialog import autoinitdialog
from gui.specialwidget import stackedlist, shrinkableitem, shownumQPushButton
from gui.usefulwidget import (
    pixmapviewer,
    IconButton,
    makesubtab_lazy,
    tabadd_lazy,
    listediter,
)
from gui.dialog_savedgame_setting import (
    dialog_setting_game_internal,
)
from gui.dialog_savedgame_common import (
    getalistname,
    startgamecheck,
    getreflist,
    calculatetagidx,
    opendirforgameuid,
    getcachedimage,
    getpixfunction,
    addgamesingle,
    addgamebatch,
    addgamebatch_x,
)
from gui.dynalang import LAction, LLabel


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
        self.doubleclicked.emit(self.uid)

    def click(self):
        try:
            self.bottommask.show()
            if self != clickitem.globallashfocus:
                clickitem.clearfocus()
            clickitem.globallashfocus = self
            self.focuschanged.emit(True, self.uid)
        except:
            print_exc()

    def mousePressEvent(self, ev) -> None:
        self.click()

    def focusOut(self):
        self.bottommask.hide()
        self.focuschanged.emit(False, self.uid)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())
        self.bottomline.resize(a0.size())
        size = globalconfig["dialog_savegame_layout"]["listitemheight"]
        margin = min(3, int(size / 15))
        self.lay1.setContentsMargins(margin, margin, margin, margin)
        self._.setFixedSize(QSize(size - 2 * margin, size - 2 * margin))
        self._2.setFixedHeight(size)

    def __init__(self, uid):
        super().__init__()

        self.uid = uid
        self.lay = QHBoxLayout(self)
        self.lay.setSpacing(0)
        lay1 = QHBoxLayout()
        self.lay1 = lay1
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.maskshowfileexists = QLabel(self)
        exists = os.path.exists(get_launchpath(uid))
        self.maskshowfileexists.setObjectName("savegame_exists" + str(exists))
        self.bottommask = QLabel(self)
        self.bottommask.hide()
        self.bottommask.setObjectName("savegame_onselectcolor1")
        _ = QLabel(self)
        _.setStyleSheet("background:transparent")
        self.bottomline = _
        _ = QLabel()
        self._ = _
        _.setScaledContents(True)
        _.setStyleSheet("background:transparent")
        for image in savehook_new_data[uid]["imagepath_all"]:
            fr = extradatas["imagefrom"].get(image)
            if fr:
                targetmod.get(fr).dispatchdownloadtask(image)
        icon = getpixfunction(uid, small=True, iconfirst=True)
        icon.setDevicePixelRatio(self.devicePixelRatioF())
        _.setPixmap(icon)
        lay1.addWidget(_)
        self.lay.addLayout(lay1)
        _ = QLabel(savehook_new_data[uid]["title"])
        _.setWordWrap(True)
        self._2 = _
        _.setObjectName("savegame_textfont2")
        self.lay.addWidget(_)


class fadeoutlabel(QLabel):
    def __init__(self, p=None):
        super().__init__(p)

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self.setStyleSheet("""background-color: rgba(255,255,255, 0);""")
        self.animation = QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(4000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setDirection(QPropertyAnimation.Direction.Forward)

    def setText(self, t):
        super().setText(t)
        self.animation.stop()
        self.animation.start()


def getselectpos(parent, callback):
    __d = {"k": 0}
    __vis, __uid = ["下", "右", "上", "左"], [0, 1, 2, 3]

    def __wrap(callback, __d, __uid):
        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        callback(uid)

    if len(__uid) > 1:
        autoinitdialog(
            parent,
            __d,
            "位置",
            600,
            [
                {
                    "type": "combo",
                    "name": "位置",
                    "k": "k",
                    "list": __vis,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(__wrap, callback, __d, __uid),
                },
            ],
        )
    else:
        callback(__uid[0])


PathRole = Qt.ItemDataRole.UserRole + 1
ImageRequestedRole = PathRole + 1


class ImageDelegate(QStyledItemDelegate):
    def initStyleOption(self, opt: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(opt, index)
        if not index.data(ImageRequestedRole):
            opt.features |= QStyleOptionViewItem.ViewItemFeature.HasDecoration
            opt.decorationSize = QSize(100, 100)


class MyQListWidget(QListWidget):

    def sethor(self, hor):
        if hor:
            self.setFlow(QListWidget.Flow.LeftToRight)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.setFlow(QListWidget.Flow.TopToBottom)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def __init__(self, p=None):
        super(MyQListWidget, self).__init__(p)
        self.imageDelegate = ImageDelegate(self)
        self.setItemDelegate(self.imageDelegate)
        self.lock = threading.Lock()
        self.loadTimer = QTimer(interval=25, timeout=self.loadImage)
        self.loadTimer.start()

    def loadImage(self):
        try:
            start = self.indexAt(self.viewport().rect().topLeft()).row()
            end = self.indexAt(self.viewport().rect().bottomRight()).row()
            if start < 0:
                return
            with self.lock:
                model = self.model()
                if end < 0:
                    end = model.rowCount()
                for row in range(start, end + 1):
                    index = model.index(row, 0)
                    if not index.data(ImageRequestedRole):
                        self.model().setData(index, True, ImageRequestedRole)
                        image = getcachedimage(index.data(PathRole), True)
                        if image.isNull():
                            self.takeItem(index.row())
                        else:
                            self.item(index.row()).setIcon(QIcon(image))
        except:
            print_exc()


class previewimages(QWidget):
    changepixmappath = pyqtSignal(str)
    removepath = pyqtSignal(str)

    def sethor(self, hor):
        self.hor = hor
        self.list.sethor(hor)

        if self.hor:
            self.list.setIconSize(QSize(self.height(), self.height()))
        else:
            self.list.setIconSize(QSize(self.width(), self.width()))

    def sizeHint(self):
        return QSize(100, 100)

    def __init__(self, p) -> None:
        super().__init__(p)
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.list = MyQListWidget(self)
        self.list.currentRowChanged.connect(self._visidx)
        self.lay.addWidget(self.list)

    def tolastnext(self, dx):
        if self.list.count() == 0:
            return self.list.setCurrentRow(-1)
        self.list.setCurrentRow((self.list.currentRow() + dx) % self.list.count())

    def setpixmaps(self, paths, currentpath):
        self.list.setCurrentRow(-1)
        self.list.blockSignals(True)
        self.list.clear()
        for path in paths:
            item = QListWidgetItem()
            item.setData(PathRole, path)
            item.setData(ImageRequestedRole, False)
            self.list.addItem(item)
        self.list.blockSignals(False)
        pixmapi = 0
        if currentpath in paths:
            pixmapi = paths.index(currentpath)
        self.list.setCurrentRow(pixmapi)

    def _visidx(self, _):
        item = self.list.currentItem()
        if item is None:
            pixmap_ = None
        else:
            pixmap_ = item.data(PathRole)
        self.changepixmappath.emit(pixmap_)

    def removecurrent(self, delfile):
        idx = self.list.currentRow()
        item = self.list.currentItem()
        if item is None:
            return
        path = item.data(PathRole)
        self.removepath.emit(path)
        self.list.takeItem(idx)
        if delfile:
            try:
                os.remove(extradatas["localedpath"].get(path, path))
            except:
                pass

    def resizeEvent(self, e: QResizeEvent):
        if self.hor:
            self.list.setIconSize(QSize(self.height(), self.height()))
        else:
            self.list.setIconSize(QSize(self.width(), self.width()))
        return super().resizeEvent(e)


class hoverbtn(LLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        return super().mousePressEvent(a0)

    def __init__(self, *argc):
        super().__init__(*argc)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, e):
        style = r"""QLabel{
                background: transparent; 
                border-radius:0;
                font-size: %spx;
                color:transparent; 
            }
            QLabel:hover{
                background-color: rgba(255,255,255,0.5); 
                color:black;
            }""" % (
            min(self.height(), self.width()) // 3
        )
        self.setStyleSheet(style)
        super().resizeEvent(e)


class viewpixmap_x(QWidget):
    tolastnext = pyqtSignal(int)
    startgame = pyqtSignal()
    switchstop = pyqtSignal()

    def sizeHint(self):
        return QSize(400, 400)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pixmapviewer = pixmapviewer(self)
        self.pixmapviewer.tolastnext.connect(self.tolastnext)
        self.maybehavecomment = hoverbtn(self)
        self.bottombtn = hoverbtn("开始游戏", self)
        self.bottombtn.clicked.connect(self.startgame)
        self.maybehavecomment.clicked.connect(self.viscomment)
        self.commentedit = QPlainTextEdit(self)
        self.commentedit.textChanged.connect(self.changecommit)
        self.centerwidget = QWidget(self)
        self.centerwidgetlayout = QVBoxLayout(self.centerwidget)
        audio = QHBoxLayout()
        self.recordbtn = IconButton(icon=["fa.microphone", "fa.stop"], checkable=True)
        self.recordbtn.clicked.connect(self.startorendrecord)
        self.centerwidgetlayout.addWidget(self.commentedit)
        self.centerwidgetlayout.addLayout(audio)
        audio.addWidget(self.recordbtn)
        self.btnplay = IconButton(icon=["fa.play", "fa.stop"], checkable=True)
        audio.addWidget(self.btnplay)
        self.btnplay.clicked.connect(self.playorstop)
        gobject.baseobject.hualang_recordbtn = self.recordbtn
        self.centerwidget.setVisible(False)
        self.pathview = fadeoutlabel(self)
        self.infoview = fadeoutlabel(self)
        self.infoview.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.currentimage = None
        self.play_context = None
        self.recorder = None
        self.switchstop.connect(self.switchstop_f)
        self.maybehavecomment.raise_()

    def switchstop_f(self):
        if self.play_context:
            self.btnplay.click()

    def checkplayable(self):
        if not self.currentimage:
            return False
        mp3 = extradatas.get("imagerefmp3", {}).get(self.currentimage, None)
        if mp3 is None:
            return False
        if not os.path.exists(mp3):
            return False
        return True

    def playorstop(self, check):
        if not self.checkplayable():
            return
        mp3 = extradatas["imagerefmp3"][self.currentimage]
        if check:
            self.play_context = playonce(mp3, globalconfig["ttscommon"]["volume"])
            self.sigtime = time.time()

            def __(tm):
                while self.play_context and self.play_context.isplaying:
                    time.sleep(1)
                if self.sigtime == tm:
                    self.switchstop.emit()

            threading.Thread(target=__, args=(self.sigtime,)).start()
        else:
            if not self.play_context:
                return
            self.play_context = None

    def startorendrecord(self, check):
        if check:
            if self.play_context:
                self.btnplay.click()
            self.btnplay.setEnabled(False)
            self.recorder = loopbackrecorder()
        else:
            self.btnplay.setEnabled(False)

            def _cb(image, path):
                if not image:
                    return
                tgt = image + os.path.splitext(path)[1]
                shutil.copy(path, tgt)
                extradatas["imagerefmp3"][image] = tgt

                self.btnplay.setEnabled(self.checkplayable())

            if not self.recorder:
                return
            self.recorder.end(callback=functools.partial(_cb, self.currentimage))
            self.recorder = None

    def changecommit(self):
        extradatas["imagecomment"][self.currentimage] = self.commentedit.toPlainText()

    def viscomment(self):
        self.centerwidget.setVisible(not self.centerwidget.isVisible())

    def resizeEvent(self, e: QResizeEvent):
        self.pixmapviewer.resize(e.size())
        self.pathview.resize(e.size().width(), self.pathview.height())
        self.infoview.resize(e.size().width(), self.infoview.height())
        self.bottombtn.setGeometry(
            e.size().width() // 5,
            7 * e.size().height() // 10,
            3 * e.size().width() // 5,
            3 * e.size().height() // 10,
        )
        self.maybehavecomment.setGeometry(
            e.size().width() // 5, 0, 3 * e.size().width() // 5, e.size().height() // 10
        )
        self.centerwidget.setGeometry(
            e.size().width() // 5,
            e.size().height() // 10,
            3 * e.size().width() // 5,
            3 * e.size().height() // 5,
        )
        super().resizeEvent(e)

    def changepixmappath(self, path):
        if self.recorder:
            self.recordbtn.click()
        if self.play_context:
            self.btnplay.click()

        self.currentimage = path
        self.centerwidget.setVisible(False)
        self.pathview.setText(path)
        try:
            timestamp = get_time_stamp(
                ct=os.path.getctime(extradatas["localedpath"].get(path, path)), ms=False
            )
        except:
            timestamp = None
        self.infoview.setText(timestamp)
        self.commentedit.setPlainText(extradatas.get("imagecomment", {}).get(path, ""))
        if not path:
            pixmap = QPixmap()
        else:
            pixmap = QPixmap.fromImage(
                QImage(extradatas["localedpath"].get(path, path))
            )
        self.pixmapviewer.showpixmap(pixmap)
        self.btnplay.setEnabled(self.checkplayable())


class pixwrapper(QWidget):
    startgame = pyqtSignal()

    def setrank(self, rank):
        if rank:
            self.spliter.addWidget(self.pixview)
            self.spliter.addWidget(self.previewimages)
        else:
            self.spliter.addWidget(self.previewimages)
            self.spliter.addWidget(self.pixview)

    def sethor(self, hor):
        if hor:

            self.spliter.setOrientation(Qt.Orientation.Vertical)
        else:

            self.spliter.setOrientation(Qt.Orientation.Horizontal)
        self.previewimages.sethor(hor)

    def __init__(self) -> None:
        super().__init__()
        rank = (globalconfig["viewlistpos"] // 2) == 0
        hor = (globalconfig["viewlistpos"] % 2) == 0

        self.previewimages = previewimages(self)
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.pixview = viewpixmap_x(self)
        self.pixview.startgame.connect(self.startgame)
        self.spliter = QSplitter(self)
        self.vlayout.addWidget(self.spliter)
        self.setrank(rank)
        self.sethor(hor)
        self.pixview.tolastnext.connect(self.previewimages.tolastnext)
        self.previewimages.changepixmappath.connect(self.changepixmappath)
        self.previewimages.removepath.connect(self.removepath)
        self.k = None
        self.removecurrent = self.previewimages.removecurrent

        self.previewimages.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.previewimages.customContextMenuRequested.connect(
            functools.partial(self.menu, True)
        )
        self.pixview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pixview.customContextMenuRequested.connect(
            functools.partial(self.menu, False)
        )

    def menu(self, _1, _):
        menu = QMenu(self)

        setimage = LAction("设为封面")
        curr = savehook_new_data[self.k]["currentvisimage"]
        curricon = savehook_new_data[self.k].get("currenticon")
        seticon = LAction("设为图标")
        seticon.setCheckable(True)
        seticon.setChecked(curr == curricon)
        deleteimage = LAction("删除图片")
        copyimage = LAction("复制图片")
        deleteimage_x = LAction("删除图片文件")
        hualang = LAction("画廊")
        pos = LAction("位置")
        if curr and os.path.exists(extradatas["localedpath"].get(curr, curr)):
            menu.addAction(setimage)
            menu.addAction(seticon)
            menu.addAction(copyimage)
            menu.addAction(deleteimage)
            menu.addAction(deleteimage_x)
        menu.addAction(hualang)
        if _1:
            menu.addSeparator()
            menu.addAction(pos)
        action = menu.exec(QCursor.pos())
        if action == deleteimage:
            self.removecurrent(False)
        elif copyimage == action:
            clipboard_set_image(extradatas["localedpath"].get(curr, curr))
        elif action == deleteimage_x:
            self.removecurrent(True)
        elif action == pos:
            getselectpos(self, self.switchpos)

        elif action == hualang:
            listediter(
                self,
                "画廊",
                savehook_new_data[self.k]["imagepath_all"],
                closecallback=lambda changed: self.setpix(self.k) if changed else None,
                ispathsedit=dict(filter1=getimagefilefilter()),
            )
        elif action == setimage:
            savehook_new_data[self.k]["currentmainimage"] = curr
        elif action == seticon:
            if curr == curricon:
                savehook_new_data[self.k].pop("currenticon")
            else:
                savehook_new_data[self.k]["currenticon"] = curr

    def switchpos(self, pos):
        globalconfig["viewlistpos"] = pos
        rank = (globalconfig["viewlistpos"] // 2) == 0
        hor = (globalconfig["viewlistpos"] % 2) == 0
        self.setrank(rank)
        self.sethor(hor)

    def removepath(self, path):
        lst = savehook_new_data[self.k]["imagepath_all"]
        lst.pop(lst.index(path))

    def changepixmappath(self, path):
        if path:
            savehook_new_data[self.k]["currentvisimage"] = path
        self.pixview.changepixmappath(path)

    def setpix(self, k):
        self.k = k
        pixmaps = savehook_new_data[k]["imagepath_all"].copy()
        self.previewimages.setpixmaps(pixmaps, savehook_new_data[k]["currentvisimage"])
        self.pixview.bottombtn.setVisible(os.path.exists(get_launchpath(k)))


class dialog_savedgame_v3(QWidget):
    def viewitem(self, k):
        try:
            self.pixview.setpix(k)
            self.currentfocusuid = k
            currvis = self.righttop.currentIndex()
            if self.righttop.count() > 1:
                self.righttop.removeTab(1)
            tabadd_lazy(
                self.righttop,
                "设置",
                lambda v: v.addWidget(
                    dialog_setting_game_internal(
                        self, k, keepindexobject=self.keepindexobject
                    )
                ),
            )
            self.righttop.setCurrentIndex(currvis)
        except:
            print_exc()

    def itemfocuschanged(self, reftagid, b, k):

        self.reftagid = reftagid
        if b:
            self.currentfocusuid = k
        else:
            self.currentfocusuid = None

        if self.currentfocusuid:
            self.viewitem(k)

    def delayitemcreater(self, k, select, reftagid, reflist):

        item = clickitem(k)
        item.doubleclicked.connect(functools.partial(startgamecheck, self, reflist))
        item.focuschanged.connect(functools.partial(self.itemfocuschanged, reftagid))
        if select:
            item.click()
        return item

    def newline(self, res):
        self.reallist[self.reftagid].insert(0, res)
        self.stack.w(calculatetagidx(self.reftagid)).insertw(
            0,
            functools.partial(
                self.delayitemcreater,
                res,
                True,
                self.reftagid,
                getreflist(self.reftagid),
            ),
        )
        self.stack.directshow()

    def stack_showmenu(self, p):
        menu = QMenu(self)

        addlist = LAction("创建列表")
        startgame = LAction("开始游戏")
        delgame = LAction("删除游戏")
        opendir = LAction("打开目录")
        addtolist = LAction("添加到列表")
        if not self.currentfocusuid:

            menu.addAction(addlist)
        else:
            exists = os.path.exists(get_launchpath(self.currentfocusuid))
            if exists:
                menu.addAction(startgame)
                menu.addAction(delgame)

                menu.addAction(opendir)

                menu.addSeparator()
                menu.addAction(addtolist)
            else:

                menu.addAction(addtolist)
                menu.addSeparator()
                menu.addAction(delgame)

        action = menu.exec(QCursor.pos())
        if action == startgame:
            startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
        elif addlist == action:

            self.createlist(True, None)

        elif action == delgame:
            self.shanchuyouxi()
        elif action == opendir:
            self.clicked4()
        elif action == addtolist:
            self.addtolist()

    def addtolistcallback(self, uid, gameuid):

        __save = self.reftagid
        self.reftagid = uid

        if gameuid not in getreflist(self.reftagid):
            getreflist(self.reftagid).insert(0, gameuid)
            self.newline(gameuid)
        else:
            idx = getreflist(self.reftagid).index(gameuid)
            getreflist(self.reftagid).insert(0, getreflist(self.reftagid).pop(idx))
            self.stack.w(calculatetagidx(self.reftagid)).torank1(idx)
        self.reftagid = __save

    def addtolist(self):
        getalistname(
            self,
            lambda x: self.addtolistcallback(x, self.currentfocusuid),
            True,
            self.reftagid,
        )

    def directshow(self):
        self.stack.directshow()

    def callexists(self, _):
        pass

    def callchange(self):
        self.stack.setheight(
            globalconfig["dialog_savegame_layout"]["listitemheight"] + 1
        )
        self.stack.directshow_1()

    def setstyle(self):
        key = "savegame_textfont2"
        fontstring = globalconfig.get(key, "")
        _style = """background-color: rgba(255,255,255, 0);"""
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            _style += "font-size:{}pt;".format(_f.pointSize())
            _style += 'font-family:"{}";'.format(_f.family())
        style = "#{}{{ {} }}".format(key, _style)

        style += "#savegame_existsTrue{{background-color:{};}}".format(
            globalconfig["dialog_savegame_layout"]["backcolor2"]
        )
        style += "#savegame_existsFalse{{background-color:{};}}".format(
            globalconfig["dialog_savegame_layout"]["onfilenoexistscolor2"]
        )
        style += "#savegame_onselectcolor1{{background-color: {};}}".format(
            globalconfig["dialog_savegame_layout"]["onselectcolor2"]
        )
        self.setStyleSheet(style)

    def movefocus(self, dx):
        uid = self.currentfocusuid
        idx1 = self.reallist[self.reftagid].index(uid)
        idx2 = (idx1 + dx) % len(self.reallist[self.reftagid])
        group0 = self.stack.w(calculatetagidx(self.reftagid))
        if idx1 == 0 and dx == -1:
            self.stack.verticalScrollBar().setValue(
                self.stack.verticalScrollBar().maximum()
            )
        else:
            try:
                self.stack.ensureWidgetVisible(group0.w(idx2))
            except:
                pass
        try:
            group0.w(idx2).click()
        except:
            pass

    def __init__(self, parent) -> None:
        super().__init__(parent)
        parent.setWindowTitle("游戏管理")
        self.setAcceptDrops(True)
        self.currentfocusuid = None
        self.reftagid = None
        self.reallist = {}
        self.keepindexobject = {}

        class ___(stackedlist):
            def keyPressEvent(self, e: QKeyEvent):
                if self.ref.currentfocusuid:
                    if e.key() == Qt.Key.Key_Return:
                        startgamecheck(
                            self.ref,
                            getreflist(self.ref.reftagid),
                            self.ref.currentfocusuid,
                        )
                    elif e.key() == Qt.Key.Key_Delete:
                        self.ref.shanchuyouxi()
                    elif e.key() == Qt.Key.Key_Left:
                        self.ref.moverank(-1)
                    elif e.key() == Qt.Key.Key_Right:
                        self.ref.moverank(1)
                    elif e.key() == Qt.Key.Key_Down:
                        self.ref.movefocus(1)
                        return e.ignore()
                    elif e.key() == Qt.Key.Key_Up:
                        self.ref.movefocus(-1)
                        return e.ignore()
                super().keyPressEvent(e)

        self.stack = ___()
        self.stack.ref = self
        self.stack.setheight(
            globalconfig["dialog_savegame_layout"]["listitemheight"] + 1
        )
        self.stack.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.stack.customContextMenuRequested.connect(self.stack_showmenu)

        self.stack.bgclicked.connect(clickitem.clearfocus)
        self.setstyle()
        spl = QSplitter()
        _l = QHBoxLayout(self)
        _l.addWidget(spl)

        spl.addWidget(self.stack)
        self.righttop = makesubtab_lazy()
        self.pixview = pixwrapper()
        self.pixview.startgame.connect(
            lambda: startgamecheck(
                self, getreflist(self.reftagid), self.currentfocusuid
            )
        )
        _w = QWidget()
        rightlay = QVBoxLayout(_w)
        rightlay.setContentsMargins(0, 0, 0, 0)
        self.righttop.addTab(_w, "画廊")
        spl.addWidget(self.righttop)

        def __(_):
            globalconfig["dialog_savegame_layout"]["listitemwidth_2"] = spl.sizes()

        spl.setSizes(globalconfig["dialog_savegame_layout"]["listitemwidth_2"])
        spl.splitterMoved.connect(__)
        spl.setStretchFactor(0, 0)
        spl.setStretchFactor(1, 1)
        rightlay.addWidget(self.pixview)

        isfirst = True
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
                opened = globalconfig["global_list_opened"]
            else:
                lst = tag["games"]
                title = tag["title"]
                tagid = tag["uid"]
                opened = tag.get("opened", True)
            group0, btn = self.createtaglist(self.stack, title, tagid, opened)
            self.stack.insertw(i, group0)
            rowreal = 0
            for row, k in enumerate(lst):
                if globalconfig["hide_not_exists"]:
                    if not os.path.exists(get_launchpath(k)):
                        continue
                self.reallist[tagid].append(k)
                if opened and isfirst and (rowreal == 0):
                    vis = True
                    isfirst = False
                else:
                    vis = False
                group0.insertw(
                    rowreal,
                    functools.partial(self.delayitemcreater, k, vis, tagid, lst),
                )

                rowreal += 1
            btn.setnum(rowreal)

    def taglistrerank(self, tagid, dx):
        idx1 = calculatetagidx(tagid)

        idx2 = (idx1 + dx) % len(savegametaged)
        savegametaged.insert(idx2, savegametaged.pop(idx1))
        self.stack.switchidx(idx1, idx2)

    def tagbuttonmenu(self, tagid):
        self.currentfocusuid = None
        self.reftagid = tagid
        menu = QMenu(self)
        editname = LAction("修改列表名称")
        addlist = LAction("创建列表")
        dellist = LAction("删除列表")
        Upaction = LAction("上移")
        Downaction = LAction("下移")
        addgame = LAction("添加游戏")
        batchadd = LAction("批量添加")
        menu.addAction(Upaction)
        menu.addAction(Downaction)
        menu.addSeparator()
        if tagid:
            menu.addAction(editname)
        menu.addAction(addlist)
        if tagid:
            menu.addAction(dellist)
        menu.addSeparator()
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
            self.createlist(action == addlist, tagid)

        elif action == dellist:
            i = calculatetagidx(tagid)
            savegametaged.pop(i)
            self.stack.popw(i)
            self.reallist.pop(tagid)

    def createlist(self, create, tagid):
        __d = {"k": ("" if create else savegametaged[calculatetagidx(tagid)]["title"])}

        def cb(__d):
            title = __d["k"]
            if not title:
                return
            i = calculatetagidx(tagid)
            if create:
                tag = {
                    "title": title,
                    "games": [],
                    "uid": str(uuid.uuid4()),
                    "opened": True,
                }
                savegametaged.insert(i, tag)
                group0, btn = self.createtaglist(self.stack, title, tag["uid"], True)
                self.stack.insertw(i, group0)
            else:
                self.stack.w(i).settitle(title)
                savegametaged[i]["title"] = title

        autoinitdialog(
            self,
            __d,
            "创建列表" if create else "修改列表名称",
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

    def createtaglist(self, p, title, tagid, opened):

        self.reallist[tagid] = []
        _btn = shownumQPushButton(title)
        _btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        _btn.clicked.connect(functools.partial(self._revertoepn, tagid))
        _btn.customContextMenuRequested.connect(
            functools.partial(self.tagbuttonmenu, tagid)
        )
        return shrinkableitem(p, _btn, opened), _btn

    def _revertoepn(self, tagid):
        item = savegametaged[calculatetagidx(tagid)]
        if item is None:
            globalconfig["global_list_opened"] = not globalconfig["global_list_opened"]
        else:
            savegametaged[calculatetagidx(tagid)]["opened"] = not savegametaged[
                calculatetagidx(tagid)
            ]["opened"]

    def moverank(self, dx):
        uid = self.currentfocusuid
        idx1 = self.reallist[self.reftagid].index(uid)
        idx2 = (idx1 + dx) % len(self.reallist[self.reftagid])
        uid2 = self.reallist[self.reftagid][idx2]
        self.reallist[self.reftagid].insert(
            idx2, self.reallist[self.reftagid].pop(idx1)
        )

        self.stack.w(calculatetagidx(self.reftagid)).switchidx(idx1, idx2)
        try:
            self.stack.ensureWidgetVisible(
                self.stack.w(calculatetagidx(self.reftagid)).w(idx2)
            )
        except:
            pass
        idx1 = getreflist(self.reftagid).index(uid)
        idx2 = getreflist(self.reftagid).index(uid2)
        getreflist(self.reftagid).insert(idx2, getreflist(self.reftagid).pop(idx1))

    def shanchuyouxi(self):
        if not self.currentfocusuid:
            return

        try:
            uid = self.currentfocusuid
            idx2 = getreflist(self.reftagid).index(uid)
            getreflist(self.reftagid).pop(idx2)

            idx2 = self.reallist[self.reftagid].index(uid)
            self.reallist[self.reftagid].pop(idx2)
            clickitem.clearfocus()
            group0 = self.stack.w(calculatetagidx(self.reftagid))
            group0.button().setnum(len(self.reallist[self.reftagid]))
            group0.popw(idx2)
            try:
                group0.w(idx2).click()
            except:
                group0.w(idx2 - 1).click()

        except:
            print_exc()

    def clicked4(self):
        opendirforgameuid(self.currentfocusuid)

    def addgame(self, uid):
        if uid not in self.reallist[self.reftagid]:
            self.newline(uid)
        else:
            idx = self.reallist[self.reftagid].index(uid)
            self.reallist[self.reftagid].pop(idx)
            self.reallist[self.reftagid].insert(0, uid)
            self.stack.w(calculatetagidx(self.reftagid)).torank1(idx)
        self.stack.w(calculatetagidx(self.reftagid)).button().setnum(
            len(self.reallist[self.reftagid])
        )

    def clicked3_batch(self):
        addgamebatch(self.addgame, getreflist(self.reftagid))

    def clicked3(self):
        addgamesingle(self, self.addgame, getreflist(self.reftagid))

    def clicked(self):
        startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        addgamebatch_x(self.addgame, savehook_new_list, files)
