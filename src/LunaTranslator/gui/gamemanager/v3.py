from qtsymbols import *
import os, functools, uuid, threading, NativeUtils, windows, qtawesome
from functools import cmp_to_key
from traceback import print_exc
from myutils.config import (
    savehook_new_list,
    _TR,
    savehook_new_data,
    savegametaged,
    get_launchpath,
    ui_settings,
    extradatas,
    globalconfig,
)
from myutils.hwnd import clipboard_set_image
from myutils.utils import (
    get_time_stamp,
    getimageformatlist,
    targetmod,
    getimagefilefilter,
)
from gui.usefulwidget import (
    pixmapviewer,
    makesubtab_lazy,
    tabadd_lazy,
    MyInputDialog,
    request_delete_ok,
    IconButton,
    getspinbox,
)

from gui.gamemanager.common import loadvisinternal, dialog_syssetting
from gui.gamemanager.setting import dialog_setting_game_internal
from gui.gamemanager.common import (
    getfonteditor,
    loadrecentlist,
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
from gui.dynalang import LAction, LLabel, LMenu
from gui.fluent.nav import FluentNavTree
from gui.gamemanager.widgets import TagWidget, ItemWidget
from gui.specialwidget import lazyscrollflow
from gui.usefulwidget import getIconButton
from gui.fluent.icons import ICON_GLOBAL_NAV


class fadeoutlabel(QWidget):
    def setText(self, t):
        self.text.setText(t)
        self.resize(
            self.width(),
            max(self.btn.height() * 2, self.text.heightForWidth(self.text.width())),
        )

    def wheelEvent(self, e: QWheelEvent) -> None:
        self.wheelto.wheelEvent(e)

    def addimage(self):
        f = QFileDialog.getOpenFileNames(filter=getimagefilefilter())
        res = f[0]
        self.parent1.addimages(res)

    def delimage(self):
        if not request_delete_ok(self, "9b524251-9639-478c-b3f9-2d254ef50084"):
            return
        self.parent1.removecurrent(False)

    def __init__(self, p, wheelto: QWidget, parent: "pixwrapper"):
        super().__init__(p)
        self.parent1 = parent
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)
        self.text = QLabel()
        self.text.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.text.setScaledContents(True)
        l.addWidget(self.text)
        hb = QVBoxLayout()
        hb.setContentsMargins(0, 0, 0, 0)
        hb.setSpacing(0)
        l.addLayout(hb)
        self.btn = IconButton("fa.plus", tips="添加图片")
        self.xbtn = IconButton("fa.times", tips="删除图片")
        self.btn.clicked.connect(self.addimage)
        self.xbtn.clicked.connect(self.delimage)
        hb.addWidget(self.btn)
        hb.addWidget(self.xbtn)
        self.wheelto = wheelto
        self.text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.showmenu)
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
        self.setText("")

    def enterEvent(self, a0):
        self.animation.stop()
        self.effect.setOpacity(1)
        return super().enterEvent(a0)

    def leaveEvent(self, a0):
        self.animation.start()
        return super().leaveEvent(a0)

    def showmenu(self, _):
        t = self.text.text()
        if not t:
            return
        menu = QMenu(self)
        copy = LAction("复制", menu)
        menu.addAction(copy)

        action = menu.exec(QCursor.pos())
        if action == copy:
            NativeUtils.ClipBoard.text = self.text.text()


PathRole = Qt.ItemDataRole.UserRole + 1
ImageRequestedRole = PathRole + 1


class ImageDelegate(QStyledItemDelegate):

    def initStyleOption(self, opt: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(opt, index)
        if not index.data(ImageRequestedRole):
            opt.features |= QStyleOptionViewItem.ViewItemFeature.HasDecoration
            opt.decorationSize = QSize(100, 100)


class previewimages(QListWidget):
    changepixmappath = pyqtSignal(str)
    removepath = pyqtSignal(str)

    def wheelEvent(self, event: QWheelEvent):
        if self.flow() == QListView.Flow.LeftToRight:
            h_bar = self.horizontalScrollBar()
            if h_bar.isVisible():
                delta = event.angleDelta().y()
                new_value = h_bar.value() - delta
                h_bar.setValue(new_value)
                event.accept()
                return
        super().wheelEvent(event)

    def __init__(self, p=None):
        super(previewimages, self).__init__(p)
        self.setObjectName("NOBORDER")
        self.imageDelegate = ImageDelegate(self)
        self.setItemDelegate(self.imageDelegate)
        self.lock = threading.Lock()
        self.loadTimer = QTimer(interval=25, timeout=self.loadImage)
        self.loadTimer.start()
        self.currentRowChanged.connect(self._visidx)

        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

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

        if hor:
            self.setIconSize(QSize(self.height(), self.height()))
        else:
            self.setIconSize(QSize(self.width(), self.width()))

    def sizeHint(self):
        return QSize(100, 100)

    def tolastnext(self, dx):
        if self.count() == 0:
            return self.setCurrentRow(-1)
        first = (self.currentRow() + dx) % self.count()
        test = first
        while True:
            if not self.item(test).isHidden():
                self.setCurrentRow(test)
                break
            test = (test + dx) % self.count()
            if test == first:
                break

    def dumppaths(self):
        nlst = []
        for i in range(self.model().rowCount()):
            nlst.append(self.model().data(self.model().index(i, 0), PathRole))
        return nlst

    def additems(self, paths, clear=True, insert=False):
        self.blockSignals(True)
        if clear:
            self.clear()
        first = None
        for path in paths:
            item = QListWidgetItem()
            if first is None:
                first = item
            item.setData(PathRole, path)
            item.setData(ImageRequestedRole, False)
            if insert:
                self.insertItem(self.currentRow() + 1, item)
            else:
                self.addItem(item)
        self.blockSignals(False)
        if first:
            self.setCurrentItem(first)

    def setpixmaps(self, paths: list, currentpath):
        self.setCurrentRow(-1)
        self.additems(paths)
        pixmapi = 0
        if currentpath in paths:
            pixmapi = paths.index(currentpath)
        self.setCurrentRow(pixmapi)

    def _visidx(self, _):
        item = self.currentItem()
        if item is None:
            pixmap_ = None
        else:
            pixmap_ = item.data(PathRole)
        self.changepixmappath.emit(pixmap_)

    def removecurrent(self, delfile):
        idx = self.currentRow()
        item = self.currentItem()
        if item is None:
            return
        path = item.data(PathRole)
        self.removepath.emit(path)
        self.takeItem(idx)
        if delfile:
            try:
                os.remove(extradatas["localedpath"].get(path, path))
            except:
                pass

    def resizeEvent(self, e: QResizeEvent):
        if self.flow() == QListView.Flow.LeftToRight:
            self.setIconSize(QSize(self.height(), self.height()))
        else:
            self.setIconSize(QSize(self.width(), self.width()))
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
            }""" % (min(self.height(), self.width()) // 3)
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
        self.infoview = fadeoutlabel(self, self.pixmapviewer, parent)
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
        if not path:
            pixmap = QPixmap()
        else:
            pixmap = QPixmap.fromImage(
                QImage(extradatas["localedpath"].get(path, path))
            )
        self.pixmapviewer.showpixmap(pixmap)


class pixwrapper(QSplitter):
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
            ext = os.path.splitext(f)[1]
            if ext.lower()[1:] not in sups:
                continue
            newf.append(f)
        if not newf:
            return
        self.addimages(newf)

    def addimages(self, files):
        newf = []
        for f in files:
            if f in savehook_new_data[self.k].get("imagepath_all", []):
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
            self.addWidget(self.pixview)
            self.addWidget(self.previewimages)
        else:
            self.addWidget(self.previewimages)
            self.addWidget(self.pixview)

    def sethor(self, hor):
        if hor:

            self.setOrientation(Qt.Orientation.Vertical)
        else:

            self.setOrientation(Qt.Orientation.Horizontal)
        self.previewimages.sethor(hor)

    def __init__(self, p: "dialog_savedgame_v3") -> None:
        super().__init__(p)
        self.setObjectName("NOBORDER")
        self.ref = p
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        rank = (globalconfig.get("viewlistpos", 0) // 2) == 0
        hor = (globalconfig.get("viewlistpos", 0) % 2) == 0

        self.previewimages = previewimages(self)
        self.previewimages.model().rowsMoved.connect(self._rowsMoved)
        self.pixview = viewpixmap_x(self)
        self.pixview.startgame.connect(self.startgame)
        self.setHandleWidth(1)
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
        sxzy = tuple(LAction(x) for x in "下右上左")
        pos = LMenu("位置", menu)
        pos.addActions(sxzy)
        for i, _ in enumerate(sxzy):
            _.setCheckable(True)
            _.setChecked(i == globalconfig.get("viewlistpos", 0))
        if curr and os.path.exists(extradatas["localedpath"].get(curr, curr)):
            menu.addAction(setimage)
            menu.addAction(seticon)
            menu.addAction(copyimage)
            menu.addAction(deleteimage)
            menu.addAction(deleteimage_x)
        if _1:
            menu.addSeparator()
            menu.addMenu(pos)
        action = menu.exec(QCursor.pos())
        if action == deleteimage:
            if not request_delete_ok(self, "9b524251-9639-478c-b3f9-2d254ef50084"):
                return
            self.removecurrent(False)
        elif copyimage == action:
            clipboard_set_image(extradatas["localedpath"].get(curr, curr))
        elif action == deleteimage_x:
            if not request_delete_ok(self, "d836ae43-b895-46e1-be0b-949dd5e2d4de"):
                return
            self.removecurrent(True)
        elif action in sxzy:
            self.switchpos(sxzy.index(action))

        elif action == setimage:
            savehook_new_data[self.k]["currentmainimage"] = curr
        elif action == seticon:
            if curr == curricon:
                savehook_new_data[self.k].pop("currenticon")
            else:
                savehook_new_data[self.k]["currenticon"] = curr

    def switchpos(self, pos):
        globalconfig["viewlistpos"] = pos
        rank = (pos // 2) == 0
        hor = (pos % 2) == 0
        self.setrank(rank)
        self.sethor(hor)

    def removepath(self, path):
        lst: list = savehook_new_data[self.k].get("imagepath_all", [])
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


TAGID_ROLE = Qt.ItemDataRole.UserRole + 5   # 列表 tagid（主项）
GAMEUID_ROLE = TAGID_ROLE + 1               # 游戏 uid（子项）

_placeholder_icon_cache = None


def _placeholder_icon():
    """透明占位图标：无图标的游戏也保留图标区，文字与有图标的对齐。"""
    global _placeholder_icon_cache
    if _placeholder_icon_cache is None:
        pm = QPixmap(20, 20)
        pm.fill(Qt.GlobalColor.transparent)
        _placeholder_icon_cache = QIcon(pm)
    return _placeholder_icon_cache

_ICON_TAG_ALL = ""    # Library
_ICON_TAG_RECENT = ""  # Recent
_ICON_TAG_CUSTOM = ""  # List


class _gamelistnav(FluentNavTree):
    """游戏管理左侧导航：列表=主项，游戏=子项（同设置窗口的 NavTree）。
    常驻展开（200px 文字模式）。游戏图标延迟加载：仅 viewport 可见的
    待加载项被逐个生成（25ms/个），滚动/展开时再激活——大量游戏时
    建树零图标成本。"""

    def __init__(self, ref=None):
        super().__init__(ref)
        self.ref = ref
        self._icon_pending = {}
        self._icon_timer = QTimer(self)
        self._icon_timer.setInterval(25)
        self._icon_timer.timeout.connect(self._load_one_visible_icon)
        self.verticalScrollBar().valueChanged.connect(self._kick_icon_timer)
        self.itemExpanded.connect(lambda _1: self._kick_icon_timer())

    def request_item_icon(self, item, uid):
        self._icon_pending[id(item)] = (item, uid)
        self._icon_timer.start()

    def _kick_icon_timer(self, *_):
        if self._icon_pending:
            self._icon_timer.start()

    def _load_one_visible_icon(self):
        if not self._icon_pending:
            self._icon_timer.stop()
            return
        vp = self.viewport().rect()
        for key in list(self._icon_pending):
            item, uid = self._icon_pending[key]
            try:
                rect = self.visualItemRect(item)
            except Exception:
                rect = QRect()
            if rect.isValid() and rect.intersects(vp):
                self._icon_pending.pop(key)
                try:
                    icon = getpixfunctionAlign(uid, small=True, iconfirst=True)
                    if not icon.isNull():
                        icon.setDevicePixelRatio(self.devicePixelRatioF())
                        item.setIcon(0, QIcon(icon))
                    # 无图标：保留占位，文字仍对齐
                except Exception:
                    print_exc()
                if not self._icon_pending:
                    self._icon_timer.stop()
                return
        # 可见区暂无待加载项：停下等滚动/展开再激活
        self._icon_timer.stop()

    def keyPressEvent(self, e):
        ref = self.ref
        if ref.currentfocusuid:
            if e.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    ref.moverank(1 if e.key() == Qt.Key.Key_Down else -1)
                    e.ignore()
                    return
            elif e.key() == Qt.Key.Key_Return:
                startgamecheck(ref, getreflist(ref.reftagid), ref.currentfocusuid)
                e.ignore()
                return
            elif e.key() == Qt.Key.Key_Delete:
                ref.shanchuyouxi()
                e.ignore()
                return
        super().keyPressEvent(e)




class _gridpage(QWidget):
    """网格视图页：当前列表的游戏大图表（原 dialog_savedgame_new 视图
    的核心，并入 v3）。单击图表 -> 侧栏指向该游戏（右侧切画廊/设置）；双击启动。"""

    def __init__(self, ref: "dialog_savedgame_v3"):
        super().__init__()
        self.ref = ref
        self.reftagid = None
        self._loaded = False  # 区分"未显示过"与"显示所有游戏(None)"
        self.reflist = []
        self.currtags = tuple()
        self.currentfocusuid = None
        self._focus_programmatic = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        # 顶栏：标签过滤 + 排序
        top = QWidget()
        toplay = QHBoxLayout(top)
        toplay.setContentsMargins(8, 4, 8, 4)
        toplay.setSpacing(4)
        self.tagswidget = TagWidget(self)
        self.tagswidget.tagschanged.connect(self.tagschanged)
        toplay.addWidget(self.tagswidget, 1)
        toplay.addWidget(
            getIconButton(
                icon="fa.sort-amount-asc", callback=self.sortgamecallback, tips="排序"
            )
        )
        toplay.addWidget(
            getIconButton(
                icon="fa.gear",
                callback=lambda: dialog_syssetting(self.ref),
                tips="界面设置",
            )
        )
        lay.addWidget(top)
        _w = QWidget()
        self.flowcontainer = QHBoxLayout(_w)
        self.flowcontainer.setContentsMargins(0, 0, 0, 0)
        self.flow = QWidget()
        lay.addWidget(_w, 1)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)

    def showmenu(self, p):
        # 复用 v3 的右键分发：图表上 -> 游戏菜单；空白 -> 创建列表
        self.ref.nav_showmenu(self.ref.nav.mapFrom(self, p))

    def showtag(self, tagid):
        self.reftagid = tagid
        self._loaded = True
        # 与建树同款三分支（getreflist(None) 会返回哨兵 1，不可迭代）
        if tagid is None:
            self.reflist = savehook_new_list
        elif tagid == 1:
            self.reflist = loadrecentlist()
        else:
            self.reflist = getreflist(tagid)
        self.tagschanged(self.currtags)

    def _makeitem(self, k):
        gameitem = ItemWidget(k)
        gameitem.doubleclicked.connect(
            functools.partial(startgamecheck, self, self.reflist)
        )
        gameitem.focuschanged.connect(self._itemfocus)
        # 不做初始 click 高亮：click 会经 point_game 联动侧栏抢走选中
        return gameitem

    def _itemfocus(self, b, k):
        self.currentfocusuid = k if b else None
        if b and not getattr(self, "_focus_programmatic", False):
            # 图表单击：侧栏指向该游戏（focusgame 的被动高亮不回写）
            self.ref.point_game(k)

    def tagschanged(self, tags):
        self.currtags = tags
        newtags = tags
        self.flow.hide()
        self.flow.deleteLater()
        self.flow = lazyscrollflow(self._keypressed)
        self.flow.setObjectName("NOBORDER")
        self.flow.bgclicked.connect(ItemWidget.clearfocus)
        self.flow.setsize(
            QSize(
                ui_settings["dialog_savegame_layout"].get("itemw", 130),
                ui_settings["dialog_savegame_layout"].get("itemh", 190),
            )
        )
        self.flow.setSpacing(ui_settings["dialog_savegame_layout"].get("margin", 6))
        self.flowcontainer.addWidget(self.flow)
        idx = 0
        for k in self.reflist:
            if newtags != self.currtags:
                break
            if globalconfig.get("hide_not_exists", False):
                if not os.path.exists(get_launchpath(k)):
                    continue
            notshow = False
            webtags = [
                globalconfig["tagNameRemap"].get(tag, tag)
                for tag in savehook_new_data[k]["webtags"]
            ]
            for tag, _type, _ in tags:
                if _type == tagitem.TYPE_EXISTS:
                    if os.path.exists(get_launchpath(k)) == False:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_DEVELOPER:
                    if tag not in savehook_new_data[k]["developers"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_TAG:
                    if tag not in webtags:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_USERTAG:
                    if tag not in savehook_new_data[k]["usertags"]:
                        notshow = True
                        break
                elif _type == tagitem.TYPE_SEARCH:
                    if (
                        tag not in webtags
                        and tag not in savehook_new_data[k]["usertags"]
                        and tag not in savehook_new_data[k]["title"]
                        and tag not in savehook_new_data[k]["developers"]
                    ):
                        notshow = True
                        break
            if notshow:
                continue
            self.flow.addwidget(functools.partial(self._makeitem, k))
            idx += 1
        self.flow.directshow()

    def focusgame(self, uid):
        """侧栏选中子项时，网格页对应图表高亮并滚动到可视区。
        懒加载未实例化的项先手动建出（同 doshowlazywidget 的步骤——
        工厂 partial 携带 uid）。高亮是被动联动：不回写侧栏（同一游戏
        可能在多个列表，回写会把选中拉到当前网格列表的同名子项上）。"""
        if not isinstance(self.flow, lazyscrollflow):
            return
        self._focus_programmatic = True
        try:
            ItemWidget.clearfocus()
            for i, w in enumerate(self.flow.widgets):
                if isinstance(w, ItemWidget):
                    _uid = w.gameuid
                elif callable(w) and getattr(w, "args", None):
                    _uid = w.args[0]
                else:
                    continue
                if _uid != uid:
                    continue
                if not isinstance(w, QWidget):
                    self.flow.widgets[i] = None
                    w = w()
                    w.setParent(self.flow.internalwid)
                    w.adjustSize()
                    w.setVisible(True)
                    w.setGeometry(self.flow.fakegeos[i])
                    self.flow.widgets[i] = w
                self.flow.ensureWidgetVisible(w)
                w.click()
                return
        finally:
            self._focus_programmatic = False

    def _keypressed(self, e):
        if self.currentfocusuid:
            if e.key() == Qt.Key.Key_Return:
                startgamecheck(self, self.reflist, self.currentfocusuid)
            elif e.key() == Qt.Key.Key_Delete:
                self.ref.shanchuyouxi()

    def directshow(self):
        self.flow.directshow()

    def callchange(self, _=None):
        self.flow.setsize(
            QSize(
                ui_settings["dialog_savegame_layout"].get("itemw", 130),
                ui_settings["dialog_savegame_layout"].get("itemh", 190),
            )
        )
        self.flow.setSpacing(ui_settings["dialog_savegame_layout"].get("margin", 6))
        self.flow.resizeandshow()
        for _ in self.flow.widgets:
            if not isinstance(_, ItemWidget):
                continue
            _.others()

    def sortgamecallback(self):
        if self.reflist == 1:
            return
        menu = QMenu(self)
        sortbytime = LAction("按添加时间排序", menu)
        sortbytime.setIcon(qtawesome.icon("fa.sort-numeric-asc"))
        menu.addAction(sortbytime)
        sortbytimede = LAction("按添加时间排序_降序", menu)
        sortbytimede.setIcon(qtawesome.icon("fa.sort-numeric-desc"))
        menu.addAction(sortbytimede)
        sortbyname = LAction("按名称排序", menu)
        sortbyname.setIcon(qtawesome.icon("fa.sort-alpha-asc"))
        menu.addAction(sortbyname)
        sortbynamedesc = LAction("按名称排序_降序", menu)
        sortbynamedesc.setIcon(qtawesome.icon("fa.sort-alpha-desc"))
        menu.addAction(sortbynamedesc)
        action = menu.exec(QCursor.pos())

        def unsafetrygettime(uid: str):
            __ = savehook_new_data[uid]
            t = __.get("createtime")
            if not t:
                try:
                    t = float(uid.split("_")[0])
                except:
                    t = 0
            return t

        if action in (sortbytime, sortbytimede):
            self.reflist.sort(key=unsafetrygettime, reverse=action != sortbytimede)
            self.tagschanged(self.currtags)
        elif action in (sortbyname, sortbynamedesc):
            def paircmp(a, b):
                return windows.StrCmpLogicalW(
                    savehook_new_data[a]["title"], savehook_new_data[b]["title"]
                )
            self.reflist.sort(
                key=cmp_to_key(paircmp),
                reverse=action == sortbynamedesc,
            )
            self.tagschanged(self.currtags)

class dialog_savedgame_v3(QWidget):
    # 当前实例（游戏设置页点标签时联动网格页的标签过滤）
    reference = None

    def createsettings(self, formLayout: QFormLayout):

        spin = getspinbox(
            10,
            1000,
            ui_settings["dialog_savegame_layout"],
            "listitemheight",
            default=30,
        )
        formLayout.addRow("高度", spin)
        spin.valueChanged.connect(self.callchange)
        formLayout.addRow(
            "字体",
            getfonteditor(
                d=globalconfig, k="savegame_textfont2", callback=self.setstyle
            ),
        )
        # 列表底色/选中色不再适用——导航树外观由 FluentUI3 插件渲染

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

            tabadd_lazy(self.righttop, "_设置_", __)
            self.righttop.setCurrentIndex(currvis)
        except:
            print_exc()

    # ---- 导航树辅助 ----
    def _tagicon(self, tagid):
        if tagid is None:
            return _ICON_TAG_ALL
        if tagid == 1:
            return _ICON_TAG_RECENT
        return _ICON_TAG_CUSTOM

    def _tagtitle(self, tagid):
        # 内置两项动态 i18n（updatelangtext 刷新）；自定义列表名不翻译
        if tagid is None:
            return _TR("所有游戏")
        if tagid == 1:
            return _TR("最近游戏")
        return savegametaged[calculatetagidx(tagid)]["title"]

    def _addtagitem(self, index, tagid, opened):
        self.reallist[tagid] = []
        item = QTreeWidgetItem()
        self.nav.configureNavigationItem(
            item, self._tagtitle(tagid), None, self._tagicon(tagid)
        )
        item.setData(0, TAGID_ROLE, tagid)
        self.nav.insertTopLevelItem(index, item)
        item.setExpanded(opened)
        return item

    def _makegameitem(self, uid):
        child = QTreeWidgetItem()
        title = savehook_new_data[uid]["title"]
        # 经 configure 设 NAV_TEXT_ROLE（展开模式刷新靠它回填文字）
        self.nav.configureNavigationItem(child, title, None, "")
        child.setData(0, GAMEUID_ROLE, uid)
        # 先挂占位图标保证文字对齐；真图标延迟按需加载（见 _gamelistnav）
        child.setIcon(0, _placeholder_icon())
        self.nav.request_item_icon(child, uid)
        return child

    def _itemfortag(self, tagid):
        for i in range(self.nav.topLevelItemCount()):
            it = self.nav.topLevelItem(i)
            if it.data(0, TAGID_ROLE) == tagid:
                return it

    def _updatetagtext(self, item):
        tagid = item.data(0, TAGID_ROLE)
        n = len(self.reallist.get(tagid, []))
        self.nav.configureNavigationItem(
            item,
            "{} ({})".format(self._tagtitle(tagid), n),
            None,
            self._tagicon(tagid),
        )

    def _navcurrent(self, item, _=None):
        if item is None:
            return
        uid = item.data(0, GAMEUID_ROLE)
        if uid:
            # 单击子项：只更新状态并联动网格高亮（不打开画廊——双击才打开）
            self.reftagid = item.parent().data(0, TAGID_ROLE)
            self.currentfocusuid = uid
            self.gridpage.focusgame(uid)
        else:
            # 主项：右侧切网格页（大图表），展示该列表。
            # 网格已在该列表（子项→主项返回）时不重建，只清高亮
            tagid = item.data(0, TAGID_ROLE)
            self.reftagid = tagid
            self.currentfocusuid = None
            if (not self.gridpage._loaded) or (self.gridpage.reftagid != tagid):
                self.gridpage.showtag(tagid)
            else:
                ItemWidget.clearfocus()
            self.stack.setCurrentWidget(self.gridpage)

    def _navclicked(self, item, _col):
        uid = item.data(0, GAMEUID_ROLE)
        if uid:
            # 网格空白区清焦后重选同一子项：恢复高亮（focusgame 幂等）
            self.gridpage.focusgame(uid)

    def _navdouble(self, item, _col):
        uid = item.data(0, GAMEUID_ROLE)
        if not uid:
            return
        self.viewitem(uid)
        self.stack.setCurrentWidget(self.righttop)

    def point_game(self, uid):
        """网格页图表点击：侧栏指向该游戏子项（_navcurrent 接管切页加载）。"""
        group = self._itemfortag(self.gridpage.reftagid)
        if group is None:
            return
        for j in range(group.childCount()):
            child = group.child(j)
            if child.data(0, GAMEUID_ROLE) == uid:
                if self.nav.currentItem() is not child:
                    self.nav.setCurrentItem(child)
                return

    def _navexpand(self, exp, item):
        if item.parent() is not None:
            return
        # 侧栏收起（图标模式）引起的自动折叠不改列表展开存档——
        # 否则收起侧栏会把所有列表记成"已折叠"
        if (not exp) and self.nav.property("navigationIconMode"):
            return
        tagid = item.data(0, TAGID_ROLE)
        if tagid is None:
            globalconfig["global_list_opened"] = exp
        elif tagid == 1:
            globalconfig["recent_list_opened"] = exp
        else:
            savegametaged[calculatetagidx(tagid)]["opened"] = exp

    def newline(self, res):
        self.reallist[self.reftagid].insert(0, res)
        group = self._itemfortag(self.reftagid)
        group.insertChild(0, self._makegameitem(res))
        self._updatetagtext(group)

    def nav_showmenu(self, p):
        item = self.nav.itemAt(p)
        if item is None:
            self._blankmenu()
        elif item.parent() is None:
            self.tagbuttonmenu(item.data(0, TAGID_ROLE))
        else:
            self.nav.setCurrentItem(item)
            self._gamemenu()

    def _blankmenu(self):
        menu = QMenu(self)
        addlist = LAction("创建列表", menu)
        menu.addAction(addlist)
        action = menu.exec(QCursor.pos())
        if addlist == action:
            self.createlist(True, None)

    def _gamemenu(self):
        menu = QMenu(self)
        startgame = LAction("开始游戏", menu)
        delgame = LAction("删除游戏", menu)
        opendir = LAction("打开目录", menu)
        createlnk = LAction("创建快捷方式", menu)
        lc = get_launchpath(self.currentfocusuid)
        if os.path.exists(lc):
            menu.addAction(startgame)
            menu.addAction(opendir)
            menu.addAction(createlnk)
        elif os.path.exists(os.path.dirname(lc)):
            menu.addAction(opendir)

        if self.reftagid not in (1,):
            menu.addAction(delgame)
        menu.addSeparator()
        __vis, __uid = loadvisinternal(
            True, self.reftagid, recent=False, global_=False
        )
        if __uid:
            addtolist = LMenu("添加到列表", menu)
            menu.addMenu(addtolist)
            for _ in range(len(__vis)):
                a = LAction(__vis[_], addtolist)
                a.setData(__uid[_])
                addtolist.addAction(a)

        action = menu.exec(QCursor.pos())
        if action == startgame:
            startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
        elif action == delgame:
            self.shanchuyouxi()
        elif action == opendir:
            self.clicked4()
        elif action == createlnk:
            CreateShortcutForUid(self.currentfocusuid)
        elif action:  # addtolist
            __uid = action.data()
            if __uid:
                self.addtolistcallback(__uid, self.currentfocusuid)

    def addtolistcallback(self, uid, gameuid):

        __save = self.reftagid
        self.reftagid = uid

        if gameuid not in getreflist(self.reftagid):
            getreflist(self.reftagid).insert(0, gameuid)
            self.newline(gameuid)
        else:
            idx = getreflist(self.reftagid).index(gameuid)
            getreflist(self.reftagid).insert(0, getreflist(self.reftagid).pop(idx))
            group = self._itemfortag(self.reftagid)
            child = group.takeChild(idx)
            group.insertChild(0, child)
        self.reftagid = __save

    def directshow(self):
        pass

    def callexists(self, _):
        pass

    def callchange(self, _=None):
        self.nav.setProperty(
            "ItemHeight",
            ui_settings["dialog_savegame_layout"].get("listitemheight", 30),
        )
        self.nav.style().unpolish(self.nav)
        self.nav.style().polish(self.nav)
        self.nav.doItemsLayout()

    def setstyle(self, _=None):
        fontstring = globalconfig.get("savegame_textfont2", "")
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            self.nav.setFont(_f)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        dialog_savedgame_v3.reference = self
        self.currentfocusuid = None
        self.reftagid: str = None
        self.reallist: "dict[str,list]" = {}
        self.keepindexobject = {}

        self.nav = _gamelistnav(self)
        # 折叠/展开模式在建树之后应用（见建树循环后）——放建树前时树为空，
        # 父项折叠空转，建树又会按存档把子项展开
        self.nav.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.nav.customContextMenuRequested.connect(self.nav_showmenu)
        self.nav.currentItemChanged.connect(self._navcurrent)
        self.nav.itemDoubleClicked.connect(self._navdouble)
        # 重复点击同一子项（current 不变，currentItemChanged 不触发）也要联动
        self.nav.itemClicked.connect(self._navclicked)
        self.nav.itemExpanded.connect(functools.partial(self._navexpand, True))
        self.nav.itemCollapsed.connect(functools.partial(self._navexpand, False))
        self.setstyle()

        # 侧边栏容器：第一项是折叠/展开汉堡（同设置窗口标题栏汉堡），
        # 下面是导航树
        navcontainer = QWidget()
        navlay = QVBoxLayout(navcontainer)
        navlay.setContentsMargins(0, 0, 0, 0)
        navlay.setSpacing(0)
        hamburger = QToolButton()
        hamburger.setObjectName("win_caption_pin")
        hamburger.setAutoRaise(True)
        hamburger.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        _f = QFont("Segoe Fluent Icons")
        _f.setPixelSize(16)
        hamburger.setFont(_f)
        hamburger.setText(ICON_GLOBAL_NAV)
        hamburger.setFixedSize(44, 38)
        hamburger.setToolTip("折叠/展开侧边栏")
        hamburger.clicked.connect(self._toggle_nav)
        navlay.addWidget(hamburger)
        navlay.addWidget(self.nav, 1)
        self.righttop = makesubtab_lazy()
        self.righttop.currentChanged.connect(
            lambda idx: (
                self.righttop.setStyleSheet(
                    "QTabWidget::pane{border:0;margin:0;padding:0;}" if idx == 0 else ""
                ),
            )
        )
        self.pixview = pixwrapper(self)
        self.pixview.startgame.connect(
            lambda: startgamecheck(
                self, getreflist(self.reftagid), self.currentfocusuid
            )
        )
        self.righttop.addTab(self.pixview, "_画廊_")
        # 右侧两页：0=网格大图表（主项点击） 1=画廊/设置（子项点击）
        self.stack = QStackedWidget()
        self.gridpage = _gridpage(self)
        self.stack.addWidget(self.gridpage)
        self.stack.addWidget(self.righttop)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(navcontainer)
        lay.addWidget(self.stack, 1)
        self.setObjectName("NOBORDER")

        for i, tag in enumerate(savegametaged):
            if tag is None:
                lst = savehook_new_list
                tagid = None
                opened = globalconfig.get("global_list_opened", True)
            elif tag == 1:
                lst = loadrecentlist()
                tagid = 1
                opened = globalconfig.get("recent_list_opened", True)
            else:
                lst = tag["games"]
                tagid = tag["uid"]
                opened = tag.get("opened", True)
            group0 = self._addtagitem(i, tagid, opened)
            rowreal = 0
            for k in lst:
                if globalconfig.get("hide_not_exists", False):
                    if not os.path.exists(get_launchpath(k)):
                        continue
                self.reallist[tagid].append(k)
                group0.addChild(self._makegameitem(k))
                rowreal += 1
            self._updatetagtext(group0)
        # 初始聚焦第一个（展开的）主项：右侧先显示网格页，而非游戏子项
        first = None
        for i in range(self.nav.topLevelItemCount()):
            it = self.nav.topLevelItem(i)
            if it.childCount() and it.isExpanded():
                first = it
                break
        if first is None and self.nav.topLevelItemCount():
            first = self.nav.topLevelItem(0)
        if first is not None:
            self.nav.setCurrentItem(first)
        # 树建好后应用存档的折叠/展开：图标模式会折叠全部父项并把
        # 选中的子项提升到顶层（指示条位置正确）
        self.nav.setNavigationExpanded(
            not globalconfig.get("gamemanager_nav_collapsed", False), animated=False
        )

    def updatelangtext(self):
        # 语言切换：内置列表项（所有游戏/最近游戏）刷新；自定义列表名不翻译
        for i in range(self.nav.topLevelItemCount()):
            item = self.nav.topLevelItem(i)
            if item.data(0, TAGID_ROLE) in (None, 1):
                self._updatetagtext(item)

    def _toggle_nav(self):
        exp = not self.nav.navigationExpanded()
        self.nav.setNavigationExpanded(exp)
        globalconfig["gamemanager_nav_collapsed"] = not exp

    def taglistrerank(self, tagid, dx):
        idx1 = calculatetagidx(tagid)

        idx2 = (idx1 + dx) % len(savegametaged)
        savegametaged.insert(idx2, savegametaged.pop(idx1))
        item = self.nav.takeTopLevelItem(idx1)
        self.nav.insertTopLevelItem(idx2, item)

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
        if tagid not in (None, 1):
            menu.addAction(editname)
        menu.addAction(addlist)
        if tagid not in (None, 1):
            menu.addAction(dellist)
        menu.addSeparator()
        if tagid not in (1,):
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
            navidx = self.nav.indexOfTopLevelItem(self._itemfortag(tagid))
            self.nav.takeTopLevelItem(navidx)
            self.reallist.pop(tagid)

    def createlist(self, create, tagid):

        def cb(title):
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
                group0 = self._addtagitem(i, tag["uid"], True)
                self._updatetagtext(group0)
            else:
                savegametaged[i]["title"] = title
                self._updatetagtext(self._itemfortag(tagid))

        __ = "" if create else savegametaged[calculatetagidx(tagid)]["title"]
        cb(
            MyInputDialog(
                self,
                "创建列表" if create else "修改列表名称",
                "名称",
                __,
            )
        )

    def moverank(self, dx):
        if self.reftagid == 1:
            return
        uid = self.currentfocusuid
        idx1 = self.reallist[self.reftagid].index(uid)
        idx2 = (idx1 + dx) % len(self.reallist[self.reftagid])
        uid2 = self.reallist[self.reftagid][idx2]
        self.reallist[self.reftagid].insert(
            idx2, self.reallist[self.reftagid].pop(idx1)
        )

        group0 = self._itemfortag(self.reftagid)
        child = group0.takeChild(idx1)
        group0.insertChild(idx2, child)
        self.nav.setCurrentItem(child)
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
            group0 = self._itemfortag(self.reftagid)
            group0.takeChild(idx2)
            self._updatetagtext(group0)
            cnt = group0.childCount()
            if cnt:
                self.nav.setCurrentItem(group0.child(min(idx2, cnt - 1)))
            else:
                self.currentfocusuid = None
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
            group = self._itemfortag(self.reftagid)
            child = group.takeChild(idx)
            group.insertChild(0, child)
            self.nav.setCurrentItem(child)
        self._updatetagtext(self._itemfortag(self.reftagid))

    def clicked3_batch(self):
        addgamebatch(self.addgame, getreflist(self.reftagid))

    def clicked3(self):
        addgamesingle(self, self.addgame, getreflist(self.reftagid))

    def clicked(self):
        startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
