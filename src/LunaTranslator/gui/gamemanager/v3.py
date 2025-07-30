from qtsymbols import *
import os, functools, uuid, threading, NativeUtils
from traceback import print_exc
from myutils.config import (
    savehook_new_list,
    savehook_new_data,
    savegametaged,
    get_launchpath,
    extradatas,
    globalconfig,
)
from myutils.hwnd import clipboard_set_image
from myutils.utils import get_time_stamp, getimageformatlist, targetmod
from gui.inputdialog import autoinitdialog
from gui.specialwidget import stackedlist, shrinkableitem, shownumQPushButton
from gui.usefulwidget import pixmapviewer, makesubtab_lazy, tabadd_lazy, request_delete_ok
from gui.gamemanager.setting import dialog_setting_game_internal
from gui.gamemanager.common import (
    getalistname,
    startgamecheck,
    getreflist,
    calculatetagidx,
    opendirforgameuid,
    getcachedimage,
    CreateShortcutForUid,
    getpixfunctionAlign,
    addgamesingle,
    addgamebatch,
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
        for image in savehook_new_data[uid].get("imagepath_all", []):
            fr = extradatas["imagefrom"].get(image)
            if fr:
                targetmod.get(fr).dispatchdownloadtask(image)
        icon = getpixfunctionAlign(uid, small=True, iconfirst=True)
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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0)
        self.setGraphicsEffect(effect)
        self.effect = effect

        self.setStyleSheet("""QLabel{background-color: rgba(255,255,255, 0);}""")
        self.animation = QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setDirection(QPropertyAnimation.Direction.Forward)

    def enterEvent(self, a0):
        self.animation.stop()
        self.effect.setOpacity(1)
        return super().enterEvent(a0)

    def leaveEvent(self, a0):
        self.animation.start()
        return super().leaveEvent(a0)

    def showmenu(self, _):
        menu = QMenu(self)
        copy = LAction("复制", menu)
        menu.addAction(copy)

        action = menu.exec(QCursor.pos())
        if action == copy:
            NativeUtils.ClipBoard.text = self.text()


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
                        item = self.itemFromIndex(index)
                        if not item:
                            continue
                        if image.isNull():
                            item.setHidden(True)
                        else:
                            if self.item(self.currentRow()).isHidden():
                                self.setCurrentRow(row)
                            item.setIcon(QIcon(image))
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

        self.list.setDragEnabled(True)
        self.list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.lay.addWidget(self.list)

    def tolastnext(self, dx):
        if self.list.count() == 0:
            return self.list.setCurrentRow(-1)
        first = (self.list.currentRow() + dx) % self.list.count()
        test = first
        while True:
            if not self.list.item(test).isHidden():
                self.list.setCurrentRow(test)
                break
            test = (test + dx) % self.list.count()
            if test == first:
                break

    def dumppaths(self):
        nlst = []
        for i in range(self.list.model().rowCount()):
            nlst.append(self.list.model().data(self.list.model().index(i, 0), PathRole))
        return nlst

    def additems(self, paths, clear=True, insert=False):
        self.list.blockSignals(True)
        if clear:
            self.list.clear()
        for path in paths:
            item = QListWidgetItem()
            item.setData(PathRole, path)
            item.setData(ImageRequestedRole, False)
            if insert:
                self.list.insertItem(self.list.currentRow() + 1, item)
            else:
                self.list.addItem(item)
        self.list.blockSignals(False)

    def setpixmaps(self, paths: list, currentpath):
        self.list.setCurrentRow(-1)
        self.additems(paths)
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

    def sizeHint(self):
        return QSize(400, 400)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pixmapviewer = pixmapviewer(self)
        self.pixmapviewer.tolastnext.connect(self.tolastnext)
        self.bottombtn = hoverbtn("开始游戏", self)
        self.bottombtn.clicked.connect(self.startgame)
        self.infoview = fadeoutlabel(self)
        self.infoview.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.infoview.setScaledContents(True)
        self.currentimage = None

    def resizeEvent(self, e: QResizeEvent):
        self.pixmapviewer.resize(e.size())
        self.infoview.resize(e.size().width(), self.infoview.height())
        self.bottombtn.setGeometry(
            e.size().width() // 5,
            7 * e.size().height() // 10,
            3 * e.size().width() // 5,
            3 * e.size().height() // 10,
        )
        super().resizeEvent(e)

    def changepixmappath(self, path):
        t = path
        self.currentimage = path
        try:
            if not os.path.isfile(extradatas["localedpath"].get(path, path)):
                raise Exception()
            t += "\n" + get_time_stamp(
                ct=os.path.getctime(extradatas["localedpath"].get(path, path)), ms=False
            )
        except:
            pass

        self.infoview.setText(t)
        self.infoview.resize(
            self.infoview.width(), self.infoview.heightForWidth(self.infoview.width())
        )
        if not path:
            pixmap = QPixmap()
        else:
            pixmap = QPixmap.fromImage(
                QImage(extradatas["localedpath"].get(path, path))
            )
        self.pixmapviewer.showpixmap(pixmap)


class pixwrapper(QWidget):
    startgame = pyqtSignal()

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Delete:
            self.removecurrent(False)
        elif e.key() == Qt.Key.Key_Left:
            self.previewimages.tolastnext(-1)
        elif e.key() == Qt.Key.Key_Right:
            self.previewimages.tolastnext(1)
        elif e.key() == Qt.Key.Key_Down:
            self.previewimages.tolastnext(1)
        elif e.key() == Qt.Key.Key_Up:
            self.previewimages.tolastnext(-1)
        elif e.key() == Qt.Key.Key_Return:
            startgamecheck(
                self.ref,
                getreflist(self.ref.reftagid),
                self.ref.currentfocusuid,
            )
        return super().keyPressEvent(e)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        newf = []
        sups = getimageformatlist()
        for f in files:
            if f in savehook_new_data[self.k].get("imagepath_all", []):
                continue
            ext = os.path.splitext(f)[1]
            if ext.lower()[1:] not in sups:
                continue
            newf.append(f)
        if not newf:
            return

        if "imagepath_all" not in savehook_new_data[self.k]:
            savehook_new_data[self.k]["imagepath_all"] = []
        self.previewimages.additems(newf, clear=False, insert=True)
        self._rowsMoved()

    def _rowsMoved(self):
        lst: list = savehook_new_data[self.k]["imagepath_all"]
        lst.clear()
        lst.extend(self.previewimages.dumppaths())

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

    def __init__(self, p: "dialog_savedgame_v3") -> None:
        super().__init__(p)
        self.ref = p
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        rank = (globalconfig["viewlistpos"] // 2) == 0
        hor = (globalconfig["viewlistpos"] % 2) == 0

        self.previewimages = previewimages(self)
        self.previewimages.list.model().rowsMoved.connect(self._rowsMoved)
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

        setimage = LAction("设为封面", menu)
        curr = savehook_new_data[self.k].get("currentvisimage")
        curricon = savehook_new_data[self.k].get("currenticon")
        seticon = LAction("设为图标", menu)
        seticon.setCheckable(True)
        seticon.setChecked(curr == curricon)
        deleteimage = LAction("删除图片", menu)
        copyimage = LAction("复制图片", menu)
        deleteimage_x = LAction("删除图片文件", menu)
        pos = LAction("位置", menu)
        if curr and os.path.exists(extradatas["localedpath"].get(curr, curr)):
            menu.addAction(setimage)
            menu.addAction(seticon)
            menu.addAction(copyimage)
            menu.addAction(deleteimage)
            menu.addAction(deleteimage_x)
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
        lst = savehook_new_data[self.k].get("imagepath_all", [])
        lst.pop(lst.index(path))

    def changepixmappath(self, path):
        if path:
            savehook_new_data[self.k]["currentvisimage"] = path
        self.pixview.changepixmappath(path)

    def setpix(self, k):
        self.k = k
        pixmaps = savehook_new_data[k].get("imagepath_all", []).copy()
        self.previewimages.setpixmaps(
            pixmaps, savehook_new_data[k].get("currentvisimage")
        )
        self.pixview.bottombtn.setVisible(os.path.exists(get_launchpath(k)))


class dialog_savedgame_v3(QWidget):
    def deleteLater(self):

        if not isqt5:
            try:
                self.fuckqt6.fuckcombo.setEditable(False)
            except:
                pass
        super().deleteLater()

    def viewitem(self, k):
        try:
            self.pixview.setpix(k)
            self.currentfocusuid = k
            currvis = self.righttop.currentIndex()
            if self.righttop.count() > 1:
                self.righttop.removeTab(1)

            def __(v: QLayout):
                _ = dialog_setting_game_internal(
                    self, k, keepindexobject=self.keepindexobject
                )
                self.fuckqt6 = _
                v.addWidget(_)

            tabadd_lazy(self.righttop, "设置", __)
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

        addlist = LAction("创建列表", menu)
        startgame = LAction("开始游戏", menu)
        delgame = LAction("删除游戏", menu)
        opendir = LAction("打开目录", menu)
        addtolist = LAction("添加到列表", menu)
        createlnk = LAction("创建快捷方式", menu)
        if not self.currentfocusuid:

            menu.addAction(addlist)
        else:
            exists = os.path.exists(get_launchpath(self.currentfocusuid))
            lc = get_launchpath(self.currentfocusuid)
            exists = os.path.exists(lc)
            if exists:
                menu.addAction(startgame)
                menu.addAction(opendir)
                menu.addAction(createlnk)
            elif os.path.exists(os.path.dirname(lc)):
                menu.addAction(opendir)

            menu.addAction(delgame)
            menu.addSeparator()
            menu.addAction(addtolist)

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
        elif action == createlnk:
            CreateShortcutForUid(self.currentfocusuid)

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

    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        parent.setWindowTitle("游戏管理")
        self.currentfocusuid = None
        self.reftagid = None
        self.reallist = {}
        self.keepindexobject = {}

        class ___(stackedlist):
            def __init__(self_, ref: dialog_savedgame_v3):
                super().__init__()
                self_.ref = ref

            def keyPressEvent(self_, e: QKeyEvent):
                if self_.ref.currentfocusuid:
                    if e.key() == Qt.Key.Key_Return:
                        startgamecheck(
                            self_.ref,
                            getreflist(self_.ref.reftagid),
                            self_.ref.currentfocusuid,
                        )
                    elif e.key() == Qt.Key.Key_Delete:
                        self_.ref.shanchuyouxi()
                    elif e.key() == Qt.Key.Key_Left:
                        self_.ref.moverank(-1)
                    elif e.key() == Qt.Key.Key_Right:
                        self_.ref.moverank(1)
                    elif e.key() == Qt.Key.Key_Down:
                        self_.ref.movefocus(1)
                        return e.ignore()
                    elif e.key() == Qt.Key.Key_Up:
                        self_.ref.movefocus(-1)
                        return e.ignore()
                super().keyPressEvent(e)

        self.stack = ___(self)
        self.stack.setheight(
            globalconfig["dialog_savegame_layout"]["listitemheight"] + 1
        )
        self.stack.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.stack.customContextMenuRequested.connect(self.stack_showmenu)

        self.stack.bgclicked.connect(clickitem.clearfocus)
        self.setstyle()
        spl = QSplitter()
        _l = QHBoxLayout(self)
        _l.setContentsMargins(0, 0, 0, 0)
        _l.addWidget(spl)

        spl.addWidget(self.stack)
        self.righttop = makesubtab_lazy()
        self.pixview = pixwrapper(self)
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
        editname = LAction("修改列表名称", menu)
        addlist = LAction("创建列表", menu)
        dellist = LAction("删除列表", menu)
        Upaction = LAction("上移", menu)
        Downaction = LAction("下移", menu)
        addgame = LAction("添加游戏", menu)
        batchadd = LAction("批量添加", menu)
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
        if not request_delete_ok(self, "bf4aa76a-41a5-4b07-a095-0c34c616ed2d"):
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
