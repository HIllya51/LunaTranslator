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
    getimagefilefilter,
)
from gui.usefulwidget import (
    makesubtab_lazy,
    tabadd_lazy,
    MyInputDialog,
    request_delete_ok,
    IconButton,
    getspinbox,
    makescrollgrid,
    makecardrow,
    D_getsimpleswitch,
)

from gui.gamemanager.common import tagitem
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
from gui.dynalang import LAction, LMenu, LFormLayout
from gui.fluent.nav import FluentNavTree, FluentNavToggleButton, create_fluent_icon
from gui.fluent.tabwidget import FluentPageCard, FluentCardSeparator
from gui.fluent.titlebar import create_fluent_caption_button
from gui.gamemanager.widgets import ItemWidget
from gui.fluent.breadcrumb import ExBreadcrumbBar
from gui.fluent.carousel import ExCarousel
from gui.specialwidget import lazyscrollflow
from gui.usefulwidget import SplitLine, ColorButton, getsimplecombobox, makescroll
from gui.fluent.icons import (
    ICON_GLOBAL_NAV,
    ICON_SEARCH,
    ICON_SORT,
    ICON_SETTINGS,
    ICON_SETTINGS_SOLID,
    ICON_LIBRARY,
    ICON_RECENT,
    ICON_LIST,
)


# ---- 模块常量 ----
PathRole = Qt.ItemDataRole.UserRole + 1
ImageRequestedRole = PathRole + 1
ImageSizeRole = ImageRequestedRole + 1   # 缩略图原始尺寸（QSize，按比例定项高/宽）
TAGID_ROLE = Qt.ItemDataRole.UserRole + 5   # 列表 tagid（主项）
GAMEUID_ROLE = TAGID_ROLE + 1               # 游戏 uid（子项）
# 列表主项图标
_ICON_TAG_ALL = ICON_LIBRARY
_ICON_TAG_RECENT = ICON_RECENT
_ICON_TAG_CUSTOM = ICON_LIST


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


class ImageDelegate(QStyledItemDelegate):

    def initStyleOption(self, opt: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(opt, index)
        if not index.data(ImageRequestedRole):
            opt.features |= QStyleOptionViewItem.ViewItemFeature.HasDecoration
            opt.decorationSize = QSize(100, 100)
        else:
            # 已加载：图标铺满项矩形（项尺寸已按图片长宽比设置，
            # 见 previewimages._itemsize），避免方形 decoration 留边
            sz = index.data(Qt.ItemDataRole.SizeHintRole)
            if isinstance(sz, QSize) and sz.isValid():
                opt.decorationSize = sz


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
        # 背景透明：缩略图浮在所在内容卡(isCard)上（单控件级 QSS，
        # 不影响后代之外的渲染）
        self.setStyleSheet("previewimages{background:transparent;}")
        self.imageDelegate = ImageDelegate(self)
        self.setItemDelegate(self.imageDelegate)
        self.lock = threading.Lock()
        self.loadTimer = QTimer(interval=25, timeout=self.loadImage)
        self.loadTimer.start()
        self.currentRowChanged.connect(self._visidx)

        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

    # 长宽比钳制：极端比例（如长截图）的项不过高/过宽
    _RATIO_MIN = 1 / 3
    _RATIO_MAX = 3

    def _itemsize(self, imgsize):
        """项尺寸跟随图片长宽比（未加载时方形占位；比例钳制在
        [_RATIO_MIN, _RATIO_MAX]）。横向条带：高 = 条带厚度、
        宽 = 厚度×宽高比；纵向条带反之。"""
        base = self.iconSize()
        if (not isinstance(imgsize, QSize) or not imgsize.isValid()
                or imgsize.width() <= 0 or imgsize.height() <= 0):
            return base
        s = base.width()
        ratio = max(self._RATIO_MIN, min(
            self._RATIO_MAX, imgsize.width() / imgsize.height()))
        if self.flow() == QListView.Flow.LeftToRight:
            return QSize(max(1, round(s * ratio)), s)
        return QSize(s, max(1, round(s / ratio)))

    def _syncitemsize(self):
        """显式设置项尺寸（按各图长宽比）。插件 CT_ItemViewItem 对
        ListMode 强制 32px 行高，缩略图会被压扁堆叠（左/右位置的
        单列条带最明显）；显式 item sizeHint 绕开该强制。"""
        for i in range(self.count()):
            it = self.item(i)
            if it is not None:
                it.setSizeHint(self._itemsize(it.data(ImageSizeRole)))

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
                            item.setData(ImageSizeRole, image.size())
                            item.setSizeHint(self._itemsize(image.size()))

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
        self._syncitemsize()

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
        self._syncitemsize()
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

    def setpathcurrent(self, path):
        """按路径选中行（轮播翻页联动；已是当前行则不动，避免回环）。"""
        for i in range(self.count()):
            if self.item(i).data(PathRole) == path:
                if self.currentRow() != i:
                    self.setCurrentRow(i)
                return

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
        self._syncitemsize()
        return super().resizeEvent(e)


class viewpixmap_x(QWidget):
    """画廊主视图：ExCarousel 轮播图集（替换原自绘 pixmapviewer）。
    图片全分辨率延迟加载（25ms/张；异步下载未就绪的页 1.5s 后重试，
    上限 20 轮，超时丢弃——同缩略图的隐藏语义）。"""

    def sizeHint(self):
        return QSize(400, 400)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.carousel = ExCarousel(self)
        # 导航按钮悬停显现（同画廊 infoview/开始按钮的悬停风格，平时不遮图）
        self.carousel.setNavigationButtonTrigger(ExCarousel.OnHover)
        # 自动播放不因悬停暂停——轮播占满整个画廊视图，鼠标常驻其上，
        # 默认的 pauseOnHover 会让自动播放永远不触发
        self.carousel.setPauseOnHover(False)
        self.infoview = fadeoutlabel(self, self.carousel, parent)
        self.currentimage = None
        # 轮播页序对应的路径（与 slide 一一对应；同步全部按路径而非行号，
        # 缩略图隐藏/轮播丢页不会错位）
        self._paths = []
        self._pending = []  # [(slide, path)] 待延迟加载
        self._failed = []   # 未就绪（异步下载中）的 (slide, path)
        self._rounds = 0    # 重试轮数（每轮 1.5s，上限 20）
        self._loadtimer = QTimer(self)
        self._loadtimer.setInterval(25)
        self._loadtimer.timeout.connect(self._load_one)

    def resizeEvent(self, e: QResizeEvent):
        size = e.size()
        self.carousel.resize(size)
        self.infoview.resize(size.width(), self.infoview.height())
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
        # 缩略图选中 -> 轮播翻到对应页。不做 idx != currentIndex() 前置
        # 判断——动画中 currentIndex 仍是起点，点回起点会被整个吞掉
        # （切换完成即把选中拉回目标页）；轮播自身会判定同页/目标页
        # 为无操作，动画中则记入 pending
        if path in self._paths:
            self.carousel.setCurrentIndex(self._paths.index(path))

    # ---- 轮播内容管理 ----
    def setpaths(self, paths, currentpath):
        """重建轮播（切换游戏）。画廊是查看器语义：全分辨率、保持宽高比。"""
        self._loadtimer.stop()
        self._pending.clear()
        self._failed.clear()
        self._rounds = 0
        self._paths = []  # 先断开映射：clear 期间残留的信号按越界丢弃
        car = self.carousel
        car.clear()
        self._paths = list(paths)
        if not self._paths:
            return
        slides = []
        for _p in self._paths:
            slides.append(car.slideAt(car.addPixmap(
                QPixmap(), aspectMode=Qt.AspectRatioMode.KeepAspectRatio)))
        self._pending = list(zip(slides, self._paths))
        if currentpath in self._paths:
            ci = self._paths.index(currentpath)
            # 内容整体重建：直接就位不播动画，且当前页优先加载
            car.setCurrentIndexImmediate(ci)
            self._pending = self._pending[ci:] + self._pending[:ci]
        self._loadtimer.start()

    def reorderpaths(self, newpaths):
        """路径集不变、仅顺序变化（缩略图拖拽重排）：takeSlide/insertSlide
        复用已加载页，不重建不闪空。集合变化则回退整建。"""
        if sorted(newpaths) != sorted(self._paths):
            self.setpaths(newpaths, self.currentimage)
            return
        car = self.carousel
        car.stopTransition()
        widgets = {}
        for p in list(self._paths):
            widgets[p] = car.takeSlide(0)
        self._paths = []
        for p in newpaths:
            if widgets.get(p) is not None:
                car.addSlide(widgets[p])
        self._paths = list(newpaths)
        # 待加载队列按新页序重排
        order = {p: i for i, p in enumerate(newpaths)}
        self._pending.sort(key=lambda sp: order.get(sp[1], 0))
        if self.currentimage in newpaths:
            car.setCurrentIndexImmediate(newpaths.index(self.currentimage))

    def removepath(self, path):
        """删除一页（缩略图删除联动）。"""
        if path not in self._paths:
            return
        slide = self.carousel.slideAt(self._paths.index(path))
        if slide is not None:
            self.carousel.removeSlideWidget(slide)
        self._paths.pop(self._paths.index(path))
        self._pending = [(s, p) for s, p in self._pending if p != path]
        self._failed = [(s, p) for s, p in self._failed if p != path]

    def _load_one(self):
        if not self._pending:
            self._loadtimer.stop()
            if self._failed and self._rounds < 20:
                self._rounds += 1
                self._pending = self._failed
                self._failed = []
                QTimer.singleShot(1500, self._kickload)
                return
            # 超时仍失效：丢弃该页（同缩略图隐藏语义）
            for slide, p in self._failed:
                self.carousel.removeSlideWidget(slide)
                if p in self._paths:
                    self._paths.pop(self._paths.index(p))
            self._failed = []
            return
        slide, path = self._pending.pop(0)
        pix = getcachedimage(path, False)
        if pix.isNull():
            self._failed.append((slide, path))
        else:
            slide.setPixmap(pix)

    def _kickload(self):
        if self._pending:
            self._loadtimer.start()


class pixwrapper(QSplitter):
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
        # 轮播页序跟随（集合不变时复用已加载页，不闪空）
        self.pixview.reorderpaths(self.previewimages.dumppaths())

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
        self.setHandleWidth(1)
        self.setrank(rank)
        self.sethor(hor)
        self.previewimages.changepixmappath.connect(self.changepixmappath)
        self.previewimages.removepath.connect(self.removepath)
        self.pixview.carousel.currentIndexChanged.connect(self._carouselindex)
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
        self.pixview.removepath(path)

    def changepixmappath(self, path):
        if path:
            savehook_new_data[self.k]["currentvisimage"] = path
        self.pixview.changepixmappath(path)

    def _carouselindex(self, idx):
        """轮播翻页（按钮/圆点/滚轮/自动播放）-> currentvisimage +
        缩略图选中（按路径同步；setpathcurrent 同行不动，无回环）。"""
        paths = self.pixview._paths
        if self.k is None or idx < 0 or idx >= len(paths):
            return
        if self.pixview.carousel._pendingIndex >= 0:
            # 快速连点：动画队列里还有下一次切换，这是中间态——
            # 不同步缩略图选中（否则会把刚点的项拉回上一个），
            # 最终态的 currentIndexChanged 会再进来同步
            return
        path = paths[idx]
        if not path:
            return
        savehook_new_data[self.k]["currentvisimage"] = path
        self.previewimages.setpathcurrent(path)

    def setpix(self, k):
        self.k = k
        pixmaps = savehook_new_data[k].get("imagepath_all", []).copy()
        self.previewimages.setpixmaps(
            pixmaps, savehook_new_data[k].get("currentvisimage")
        )
        self.pixview.setpaths(pixmaps, savehook_new_data[k].get("currentvisimage"))


_placeholder_icon_cache = None


def _placeholder_icon():
    """透明占位图标：无图标的游戏也保留图标区，文字与有图标的对齐。"""
    global _placeholder_icon_cache
    if _placeholder_icon_cache is None:
        pm = QPixmap(20, 20)
        pm.fill(Qt.GlobalColor.transparent)
        _placeholder_icon_cache = QIcon(pm)
    return _placeholder_icon_cache


class _gamelistnav(FluentNavTree):
    """游戏管理左侧导航：列表=主项，游戏=子项（同设置窗口的 NavTree）。
    常驻展开（200px 文字模式）。游戏图标延迟加载：仅 viewport 可见的
    待加载项被逐个生成（25ms/个），滚动/展开时再激活——大量游戏时
    建树零图标成本。"""

    def __init__(self, ref=None):
        super().__init__(ref)
        self.ref = ref
        # 拖拽排序：自管 DnD（不用 Qt 的 InternalMove —— QTreeWidget model
        # 不支持 moveRows，startDrag 在 MoveAction 完成后会 clearOrRemove()
        # 再删一次源项，表现为"拖完就没了"）
        self.setAcceptDrops(True)
        self._dragitem = None
        self._dragpos = None
        # 单击主项只选中（切网格页），双击才展开/折叠
        self._expand_on_doubleclick = True
        self.setExpandsOnDoubleClick(False)   # 关掉 QTreeView 默认（会双重 toggle）
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 双击窗口延迟：鼠标单击的页面切换动作延迟 doubleClickInterval 执行，
        # 期间发生双击则取消——避免"双击先触发单击副作用"
        self._click_pending = False
        self._deferred_item = None
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(QApplication.doubleClickInterval() // 2)
        self._click_timer.timeout.connect(self._flush_click)
        self._icon_pending = {}
        self._icon_timer = QTimer(self)
        self._icon_timer.setInterval(25)
        self._icon_timer.timeout.connect(self._load_one_visible_icon)
        self.verticalScrollBar().valueChanged.connect(self._kick_icon_timer)
        # rangeChanged：布局/尺寸变化使滚动范围变动时也能重新激活
        self.verticalScrollBar().rangeChanged.connect(
            lambda *_: self._kick_icon_timer())
        self.itemExpanded.connect(lambda _1: self._kick_icon_timer())

    def request_item_icon(self, item, uid):
        self._icon_pending[id(item)] = (item, uid)
        self._icon_timer.start()

    def showEvent(self, e):
        super().showEvent(e)
        # 建树发生在 show 前，图标计时器可能已空转停止——布局完成后重启
        QTimer.singleShot(0, self._kick_icon_timer)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._kick_icon_timer()

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

    # ---- 拖拽（自管 DnD，见 __init__ 注释）----
    def mousePressEvent(self, ev):
        self._dragitem = self.itemAt(ev.pos())
        self._dragpos = ev.pos()
        # 单击的页面动作延迟到双击窗口后（双击会取消）
        self._click_pending = True
        self._click_timer.start()
        if (
            self._dragitem is not None
            and self._dragitem is self.currentItem()
        ):
            # 点击的已是当前项（主项或子项，如双击展开/打开画廊后再
            # 单击）：currentItemChanged 不会触发，手动记录延迟动作
            # （子项：唤出画廊/设置页；主项：同列表不重建）
            self._deferred_item = self._dragitem
        return super().mousePressEvent(ev)

    def _flush_click(self):
        self._click_pending = False
        item, self._deferred_item = self._deferred_item, None
        if item is not None:
            try:
                if item.data(0, GAMEUID_ROLE):
                    # 单击子项：唤出画廊/设置页（网格同步由双击承担）
                    self.ref._navopen(item)
                else:
                    self.ref._navcurrent(item)
            except Exception:
                print_exc()

    def mouseDoubleClickEvent(self, e):
        # 双击：取消单击的延迟副作用
        self._click_timer.stop()
        self._click_pending = False
        self._deferred_item = None
        item = self.itemAt(e.pos())
        if item is not None and item.parent() is None:
            # 主项：双击展开/折叠（单击只选中）
            item.setExpanded(not item.isExpanded())
            # 双击切换列表时，若网格聚焦的游戏属于新列表，侧边栏跟随选中
            self.ref._sync_current_to_gridlist(item)
            e.accept()
            return
        super().mouseDoubleClickEvent(e)

    def mouseMoveEvent(self, e):
        _filtered = bool(self.ref.gridpage.currtags) or globalconfig.get(
            "hide_not_exists", False)
        _is_child = self._dragitem is not None and (
            self._dragitem.parent() is not None)
        if (
            self._dragitem is not None
            and not (_filtered and _is_child)  # 有过滤时子项不拖
            and (e.buttons() & Qt.MouseButton.LeftButton)
            and (e.pos() - self._dragpos).manhattanLength()
            >= QApplication.startDragDistance()
        ):
            item = self._dragitem
            mime = QMimeData()
            if item.parent() is None:
                mime.setText("lunanavmove:tag")
            else:
                mime.setText("lunanavmove:uid")
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(e)

    def dragEnterEvent(self, e):
        if e.mimeData().text().startswith("lunanavmove:"):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().text().startswith("lunanavmove:"):
            e.acceptProposedAction()
        else:
            e.ignore()

    def _visible_candidates(self, top_only=False):
        """视口内可见的候选项 [(item, rect)]（折叠/滚动外的项不可见，
        不参与直觉判断）。"""
        vp = self.viewport().rect()
        cands = []
        for i in range(self.topLevelItemCount()):
            top = self.topLevelItem(i)
            items = [top]
            if not top_only:
                items += [top.child(j) for j in range(top.childCount())]
            for item in items:
                if item is None or item.isHidden():
                    continue
                r = self.visualRect(self.indexFromItem(item))
                if r.isValid() and r.intersects(vp):
                    cands.append((item, r))
        return cands

    def dropEvent(self, e):
        if not e.mimeData().text().startswith("lunanavmove:"):
            e.ignore()
            return
        src = self._dragitem
        _filtered = bool(self.ref.gridpage.currtags) or globalconfig.get(
            "hide_not_exists", False)
        if _filtered and src is not None and src.parent() is not None:
            e.ignore()  # 有过滤时子项拖放无效（主项排序仍可用）
            return
        if src is None:
            e.ignore()
            return
        pos = e.pos()
        top_only = src.parent() is None
        cands = self._visible_candidates(top_only=top_only)
        if not cands:
            e.ignore()
            return
        e.acceptProposedAction()
        # 拖到可见内容之上/之下：主项 -> 内容最前/最后；
        # 子项 -> 最近可见项判定（下面统一处理，走最近分支）
        if top_only and pos.y() > max(r.bottom() for _, r in cands):
            self.ref._tagmove(src.data(0, TAGID_ROLE), self.topLevelItemCount())
            return
        if top_only and pos.y() < min(r.top() for _, r in cands):
            self.ref._tagmove(src.data(0, TAGID_ROLE), 0)
            return
        # 最近可见项（按中心距离）
        dst_item, dst_rect = min(
            cands,
            key=lambda ir: (ir[1].center().x() - pos.x()) ** 2
            + (ir[1].center().y() - pos.y()) ** 2,
        )
        below = pos.y() > dst_rect.center().y()
        if src.parent() is None:
            # ---- 主项拖动：调整列表顺序（含内置项，位置任意）----
            src_tag = src.data(0, TAGID_ROLE)
            if dst_item.parent() is not None:
                dst_item = dst_item.parent()
            if dst_item.data(0, TAGID_ROLE) == src_tag:
                return
            base = self.indexOfTopLevelItem(dst_item)
            self.ref._tagmove(src_tag, base + 1 if below else base)
            return
        # ---- 子项拖动 ----
        uid = src.data(0, GAMEUID_ROLE)
        src_tag = src.parent().data(0, TAGID_ROLE)
        if dst_item.parent() is None:
            # 最近目标是主项：
            # - 上半 -> 列表最前
            # - 展开主项的下半（紧贴第一个子项，即"第一个子项之前"）-> 最前
            # - 收起主项的下半 -> 追加末尾
            dst_tag = dst_item.data(0, TAGID_ROLE)
            if below and not dst_item.isExpanded():
                dst_idx = dst_item.childCount()
            else:
                dst_idx = 0
        else:
            dst_tag = dst_item.parent().data(0, TAGID_ROLE)
            base = dst_item.parent().indexOfChild(dst_item)
            dst_idx = base + 1 if below else base
        if dst_tag == 1:
            return  # 最近游戏是动态列表，不可拖入（拖出是复制，允许）
        self.ref._navmove(uid, src_tag, dst_tag, dst_idx)

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
        # 顶栏控件（搜索/面包屑/排序/齿轮）不建在本页——由 build_topbar
        # 建到对话框的常驻顶栏里（跨页可见）
        # 内容区：网格 + 右侧设置面板（隐藏，齿轮切换显隐）
        _content = QWidget()
        _cl = QHBoxLayout(_content)
        _cl.setContentsMargins(0, 0, 0, 0)
        _cl.setSpacing(0)
        _w = QWidget()
        self.flowcontainer = QHBoxLayout(_w)
        self.flowcontainer.setContentsMargins(0, 0, 0, 0)
        self.flow = QWidget()
        _cl.addWidget(_w, 1)
        # 右侧设置面板：内容整体包在一张大 isCard 卡里
        self._settings_panel = QWidget()
        self._settings_panel.setFixedWidth(320)
        _sl = QVBoxLayout(self._settings_panel)
        _sl.setContentsMargins(8, 8, 8, 8)
        self._settings_scroll = makescroll()
        self._settings_panel_inner = QWidget()
        # 大卡（同 FluentCard/makecardrow 配方：插件渲染 WinUI 圆角卡底）
        self._settings_panel_inner.setAttribute(Qt.WA_StyledBackground, True)
        self._settings_panel_inner.setProperty("isCard", True)
        self._settings_scroll.setWidget(self._settings_panel_inner)
        _sl.addWidget(self._settings_scroll)
        self._settings_panel.hide()
        _cl.addWidget(self._settings_panel)
        lay.addWidget(_content, 1)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        # 接受网格拖拽（空白处）：拖到空白 = 移到末尾
        self.setAcceptDrops(True)

    def build_titlebar(self, titlebar):
        """把本页的控件装进宿主无边框窗口的标题栏：搜索手动居中
        （右侧按钮/面包屑变化不推动它），面包屑紧贴其右（从左向右），
        排序/齿轮在右侧（仅网格页显示，见 _sync_titlebar_pagecontrols）。"""
        self.searchedit = QLineEdit()
        self.searchedit.returnPressed.connect(self._search)
        self.searchedit.setPlaceholderText("搜索")
        # Gallery 同款：宽 300、高度走样式自然尺寸；图标 32x32 画布 32px 字形
        self.searchedit.setClearButtonEnabled(True)
        self._search_action = _act = QAction(self.searchedit)
        _act.setIcon(create_fluent_icon(ICON_SEARCH, size=32, glyph=32))
        self.searchedit.addAction(_act, QLineEdit.ActionPosition.TrailingPosition)
        self.searchedit.installEventFilter(self)
        # 期望宽 300（空间不足时按 让位次序 收窄，见 FluentTitleBar）
        titlebar.addCenterWidget(self.searchedit, 300)
        # 面包屑：紧贴搜索框右侧、从左向右；有 tag 时显示；root 为 ALL，
        # 点 ALL 清空（显隐不移动搜索框）
        self.breadcrumb = ExBreadcrumbBar(self)
        self.breadcrumb.itemClicked.connect(self._breadcrumb_clicked)
        self.breadcrumb.hide()
        titlebar.addSideWidget(self.breadcrumb)
        # 排序/齿轮：Gallery「置顶窗口」同款 caption 按钮（win_caption_pin
        # 悬停由插件渲染）
        self.sortbtn = create_fluent_caption_button(
            titlebar, ICON_SORT, "排序")
        self.sortbtn.clicked.connect(self.sortgamecallback)
        titlebar.addTrailingWidget(self.sortbtn)
        # 齿轮带开关态（Gallery updatePinButton 同款字形切换；不用
        # checkable——插件把勾选态 caption 字形画成白色，浅色下不可见）：
        # 实心齿轮=面板开
        self.gearbtn = create_fluent_caption_button(
            titlebar, ICON_SETTINGS, "设置")
        self.gearbtn.clicked.connect(self.toggle_settings_panel)
        titlebar.addTrailingWidget(self.gearbtn)

    def _sync_gear_state(self):
        """齿轮按钮的开关态与设置面板显隐同步（实心=开）。"""
        on = not self._settings_panel.isHidden()
        self.gearbtn.setText(ICON_SETTINGS_SOLID if on else ICON_SETTINGS)
        self.gearbtn.setToolTip("收起设置" if on else "设置")
        self.gearbtn.update()

    def toggle_settings_panel(self):
        """常驻顶栏齿轮：切回网格页并切换右侧设置面板显隐（首次构建内容）。
        用 isHidden 判逻辑开合——人在其他页时 isVisible 会因祖先隐藏而误判。
        面板状态回写齿轮的开关态字形。"""
        self.ref._show_gridpage()
        if self._settings_panel.isHidden():
            if not getattr(self, "_settings_built", False):
                self._build_settings_panel()
                self._settings_built = True
            self._settings_panel.show()
        else:
            self._settings_panel.hide()
        self._sync_gear_state()

    def _build_settings_panel(self):
        """在右侧面板中构建网格设置（行标签经 LFormLayout 翻译）。"""
        host = QVBoxLayout(self._settings_panel_inner)
        host.setContentsMargins(0, 0, 0, 0)
        # LFormLayout：行标签经 LLabel 翻译（语言切换自动更新）
        _fl = LFormLayout()
        _fl.setContentsMargins(16, 8, 16, 16)
        host.addLayout(_fl)
        self.ref.createsettings(_fl)

    def _bgclicked(self):
        # 网格空白点击：清网格高亮 + 侧边栏选中回到主项（保持一致）。
        # 不依赖信号链（_click_pending 等状态可能拦截），直接清。
        ItemWidget.clearfocus()
        self.currentfocusuid = None
        self.ref.currentfocusuid = None
        # 注意 tagid=None 是「所有游戏」的合法值，不能当无效处理
        group = self.ref._itemfortag(self.reftagid)
        if group is not None:
            self.ref.nav.blockSignals(True)
            try:
                self.ref.nav.setCurrentItem(group)
            finally:
                self.ref.nav.blockSignals(False)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event is None:
            return
        if event.type() in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
        ):
            # 明暗切换：重画搜索图标（create_fluent_icon 按当前调色板着色）
            self._refresh_search_icon()

    def _refresh_search_icon(self):
        act = getattr(self, "_search_action", None)
        if act is not None:
            act.setIcon(create_fluent_icon(ICON_SEARCH))

    def eventFilter(self, obj, ev):
        if obj is self.searchedit:
            if ev.type() == QEvent.Type.Enter:
                obj.setCursor(Qt.CursorShape.IBeamCursor)
            elif ev.type() == QEvent.Type.Leave:
                obj.unsetCursor()   # 恢复继承（比 setCursor(Arrow) 更彻底）
        return super().eventFilter(obj, ev)

    def _search(self):
        text = self.searchedit.text().strip()
        if text:
            # 顶栏常驻：在其他页回车时先切回网格页再过滤
            self.ref._show_gridpage()
            self._apply_tags(tuple(self.currtags)
                             + ((text, tagitem.TYPE_SEARCH, None),))
            self.searchedit.clear()

    def _breadcrumb_clicked(self, index, item):
        # 点任意层级（ALL 或中间 tag）：截断到该层级（后面的 tag 清除）
        # 面包屑项 0=ALL（清空全部），项 i 对应 currtags[i-1]
        self._apply_tags(tuple(self.currtags[:index]))

    def _apply_tags(self, tags):
        """统一入口：更新 tag -> 刷新面包屑 -> 重建网格。"""
        self.currtags = tuple(tags)
        # 面包屑：无 tag 隐藏；有 tag 显示 [ALL, tag...]
        if not self.currtags:
            self.breadcrumb.hide()
            self.breadcrumb.setItemsSource([])
        else:
            self.breadcrumb.setItemsSource(
                ["ALL"] + [t for t, _ty, _d in self.currtags])
            self.breadcrumb.show()
        self.tagschanged(self.currtags)

    def dragEnterEvent(self, e):
        if e.mimeData().text().startswith("lunamovegame:"):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().text().startswith("lunamovegame:"):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        txt = e.mimeData().text()
        if not txt.startswith("lunamovegame:"):
            e.ignore()
            return
        e.acceptProposedAction()
        uid = txt.split(":", 1)[1]
        # 内容坐标（viewport + 滚动偏移）
        p = self.flow.mapFrom(self, e.pos())
        p = QPoint(
            p.x() + self.flow.horizontalScrollBar().value(),
            p.y() + self.flow.verticalScrollBar().value(),
        )
        self.ref._gridmove_to(uid, self._insertion_index_at(p))

    def _insertion_index_at(self, p):
        """内容坐标 p 处的插入索引：项间隙按行内就近（左侧最近项之后）；
        最上行之上 = 最前；最下行之下 = 末尾。"""
        if not isinstance(self.flow, lazyscrollflow):
            return 0
        rl = self.ref.reallist.get(self.reftagid, [])
        best_i, best_d = None, None
        min_top = None
        for i, g in enumerate(self.flow.fakegeos):
            if not g.isValid():
                continue
            if min_top is None or g.top() < min_top:
                min_top = g.top()
            if p.y() < g.top() or p.y() > g.bottom():
                continue
            d = abs(g.center().x() - p.x())
            if best_d is None or d < best_d:
                best_d, best_i = d, i
        if best_i is None:
            if min_top is not None and p.y() < min_top:
                return 0  # 最上行之上 -> 最前
            return len(rl)  # 最下行之下 -> 末尾
        # 行内：最近项中心的左右侧决定插前/插后
        g = self.flow.fakegeos[best_i]
        return best_i + 1 if p.x() >= g.center().x() else best_i

    def showEvent(self, e):
        super().showEvent(e)
        # showtag 可能发生在本页不可见/切页瞬间（visibleRegion 为空、
        # 尺寸未定）——布局与懒加载都没跑。显示后延后一拍重算
        if isinstance(self.flow, lazyscrollflow):
            QTimer.singleShot(0, self._refit_flow)

    def _refit_flow(self):
        if isinstance(self.flow, lazyscrollflow):
            # zero-timer 会先于排队的 LayoutRequest 执行——此刻 flow 的
            # 布局仍可能未激活（尺寸 0），必须先泵一轮事件让布局完成
            QApplication.processEvents()
            self.flow.resizeandshow()

    def showmenu(self, p):
        # 网格页右键：图表上（右键按下已先触发 click 选中）-> 游戏菜单；
        # 空白（bgclicked 已清焦）-> 创建列表。按焦点状态分发，不做坐标换算
        if self.currentfocusuid:
            self.ref._gamemenu()
        else:
            self.ref._blankmenu()

    def showtag(self, tagid):
        self.reftagid = tagid
        self._loaded = True
        # 列表切换：最近游戏下排序按钮隐藏（其余列表恢复）
        self.ref._sync_titlebar_pagecontrols()
        # 与建树同款三分支（getreflist(None) 会返回哨兵 1，不可迭代）
        if tagid is None:
            self.reflist = savehook_new_list
        elif tagid == 1:
            self.reflist = loadrecentlist()
        else:
            self.reflist = getreflist(tagid)
        # 创建 flow（全部项），再应用 tag 过滤
        self._build_flow()
        if self.currtags:
            self._apply_tag_filter()
        QTimer.singleShot(0, self._refit_flow)
        self.tagschanged(self.currtags)

    def _makeitem(self, k):
        gameitem = ItemWidget(k)
        gameitem.setAcceptDrops(
            not (self.currtags or globalconfig.get("hide_not_exists", False)))
        gameitem.doubleclicked.connect(
            functools.partial(startgamecheck, self, self.reflist)
        )
        gameitem.focuschanged.connect(self._itemfocus)
        gameitem.droppedgame.connect(self.ref._gridmove)
        # 不做初始 click 高亮：click 会经 point_game 联动侧栏抢走选中
        return gameitem

    def _itemfocus(self, b, k):
        self.currentfocusuid = k if b else None
        if not b:
            # 焦点清除（空白点击/主项选中/联动清焦）
            return
        if not getattr(self, "_focus_programmatic", False):
            # 图表单击：侧栏指向该游戏（focusgame 的被动高亮不回写）
            self.ref.point_game(k)

    def _matches_tags(self, k, tags, tagid=None):
        """游戏 k 是否通过 tag 过滤（TYPE_SEARCH 大小写不敏感 /
        TYPE_EXISTS 路径存在）。hide_not_exists 不作用于最近游戏。"""
        if (
            tagid != 1
            and globalconfig.get("hide_not_exists", False)
        ):
            if not os.path.exists(get_launchpath(k)):
                return False
        for tag, _type, _ in tags:
            if _type == tagitem.TYPE_EXISTS:
                if not os.path.exists(get_launchpath(k)):
                    return False
            elif _type == tagitem.TYPE_SEARCH:
                tag_l = tag.lower()
                _d = savehook_new_data[k]
                if (
                    tag_l not in _d["title"].lower()
                    and not any(
                        tag_l in d.lower() for d in _d.get("developers", []))
                ):
                    return False
        return True

    def _build_flow(self):
        """创建包含全部游戏项的 flow。"""
        if isinstance(self.flow, lazyscrollflow):
            self.flow.hide()
            self.flow.deleteLater()
        self.flow = lazyscrollflow(self._keypressed)
        self.flow.setObjectName("NOBORDER")
        self.flow.bgclicked.connect(self._bgclicked)
        self.flow.setsize(
            QSize(
                ui_settings["dialog_savegame_layout"].get("itemw", 130),
                ui_settings["dialog_savegame_layout"].get("itemh", 190),
            )
        )
        self.flow.setSpacing(ui_settings["dialog_savegame_layout"].get("margin", 6))
        self.flowcontainer.addWidget(self.flow)
        for k in self.reflist:
            self.flow.addwidget(functools.partial(self._makeitem, k))

    def _apply_tag_filter(self):
        """隐藏不匹配项（网格 + 侧边栏子项 + 主项计数），不销毁 flow。
        有过滤时直接关闭 drag/drop（比事件拦截可靠）。"""
        tags = self.currtags
        # 有过滤时网格禁拖（侧边栏保留 drag/drop——主项排序仍可用，
        # 子项拖拽在 mouseMoveEvent/dropEvent 里按过滤状态拦截）
        self.setAcceptDrops(not (
            bool(tags) or globalconfig.get("hide_not_exists", False)))
        # 网格
        for i, w in enumerate(self.flow.widgets):
            uid = None
            if isinstance(w, ItemWidget):
                uid = w.gameuid
            elif callable(w) and getattr(w, "args", None):
                uid = w.args[0]
            if uid is None:
                continue
            self.flow.setWidgetHidden(i, not self._matches_tags(
                uid, tags, self.reftagid))
        # 已实例化的网格项也切 acceptDrops
        for w in self.flow.widgets:
            if isinstance(w, ItemWidget):
                w.setAcceptDrops(not (
                    bool(tags) or globalconfig.get("hide_not_exists", False)))
        self.flow.resizeandshow()
        # 侧边栏子项 + 主项计数
        nav = self.ref.nav
        for ti in range(nav.topLevelItemCount()):
            top = nav.topLevelItem(ti)
            for ci in range(top.childCount()):
                child = top.child(ci)
                uid = child.data(0, GAMEUID_ROLE)
                if uid is None:
                    continue
                _tagid = top.data(0, TAGID_ROLE)
                child.setHidden(not self._matches_tags(uid, tags, _tagid))
            self.ref._updatetagtext(top)

    def tagschanged(self, tags):
        """tag 变化：更新过滤（隐藏/显示），不销毁重建 flow。"""
        self.currtags = tags
        if not isinstance(self.flow, lazyscrollflow):
            return
        self._apply_tag_filter()

    def _flow_find(self, uid):
        """flow.widgets 中的索引（未实例化的 partial 工厂也携带 uid）。"""
        if not isinstance(self.flow, lazyscrollflow):
            return None
        for i, w in enumerate(self.flow.widgets):
            if isinstance(w, ItemWidget):
                _u = w.gameuid
            elif callable(w) and getattr(w, "args", None):
                _u = w.args[0]
            else:
                continue
            if _u == uid:
                return i
        return None

    def flow_move_idx(self, i1, i2):
        """网格内单项移动（不重建整个 flow）。结构变化后 hidden 索引失效，
        需重算过滤。"""
        if not isinstance(self.flow, lazyscrollflow):
            return
        if i1 == i2 or i1 < 0 or i2 < 0:
            return
        self.flow.widgets.insert(i2, self.flow.widgets.pop(i1))
        self.flow.fakegeos.insert(i2, self.flow.fakegeos.pop(i1))
        if self.currtags:
            self._apply_tag_filter()
        else:
            self.flow.resizeandshow()

    def flow_remove(self, uid):
        """从网格移除一项（跨列表移出时；不重建）。"""
        i = self._flow_find(uid)
        if i is None:
            return
        w = self.flow.widgets.pop(i)
        self.flow.fakegeos.pop(i)
        if isinstance(w, QWidget):
            w.hide()
            w.deleteLater()
        if self.currtags:
            self._apply_tag_filter()
        else:
            self.flow.resizeandshow()

    def flow_insert(self, uid, idx):
        """网格插入一项（跨列表移入当前列表时；不重建）。"""
        if not isinstance(self.flow, lazyscrollflow):
            return
        idx = min(max(idx, 0), len(self.flow.widgets))
        self.flow.widgets.insert(idx, functools.partial(self._makeitem, uid))
        self.flow.fakegeos.insert(idx, QRect())
        if self.currtags:
            self._apply_tag_filter()
        else:
            self.flow.resizeandshow()

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
        # 顶栏常驻：排序作用于网格列表，先切回网格页
        self.ref._show_gridpage()
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
        elif action in (sortbyname, sortbynamedesc):
            def paircmp(a, b):
                return windows.StrCmpLogicalW(
                    savehook_new_data[a]["title"], savehook_new_data[b]["title"]
                )
            self.reflist.sort(
                key=cmp_to_key(paircmp),
                reverse=action == sortbynamedesc,
            )
        else:
            return
        # 持久列表顺序已变：同步 reallist + nav 子项，再重建网格
        self.ref._sync_from_reflist(self.reftagid)
        self.tagschanged(self.currtags)

class dialog_savedgame_v3(QWidget):
    # 当前实例（游戏设置页点标签时联动网格页的标签过滤）
    reference = None

    def createsettings(self, formLayout: QFormLayout):
        # 网格（图表）设置（原 dialog_savedgame_new 的全套）
        for i, (key, name, default) in enumerate(
            [
                ("itemw", "宽度", 130),
                ("itemh", "高度", 190),
                ("margin", "边距_inter", 6),
                ("margin2", "边距_intra", 6),
                ("radius", "圆角", 10),
                ("borderW", "边框宽度", 1),
            ]
        ):
            minv = 0 if i >= 2 else 32
            spin = getspinbox(
                minv, 1000, ui_settings["dialog_savegame_layout"], key, default=default
            )
            formLayout.addRow(name, spin)
            spin.valueChanged.connect(self.gridpage.callchange)

        formLayout.addRow(
            "缩放",
            getsimplecombobox(
                ["填充", "适应", "拉伸", "居中"],
                globalconfig,
                "imagewrapmode",
                callback=self.gridpage.callchange,
                default=0,
            ),
        )

        formLayout.addRow(SplitLine())
        for key, name, default in [
            ("backcolor2", "颜色", "#40ffffff"),
            ("onselectcolor2", "颜色_选中时", "#40007fff"),
            ("onfilenoexistscolor2", "游戏不存在时颜色", "#40acacac"),
            ("borderColor", "边框颜色", "#10000000"),
            ("borderColor2", "边框颜色_选中时", "#ff000000"),
        ]:
            formLayout.addRow(
                name,
                ColorButton(
                    self,
                    ui_settings["dialog_savegame_layout"],
                    key,
                    callback=self.gridpage.callchange,
                    alpha=True,
                    default=default,
                ),
            )
        formLayout.addRow(SplitLine())
        formLayout.addRow(
            "文字区_高度",
            getspinbox(
                0,
                1000,
                ui_settings["dialog_savegame_layout"],
                "textH2",
                callback=self.gridpage.callchange,
                double=False,
                default=1,
            ),
        )
        formLayout.addRow(
            "文字区_布局",
            getsimplecombobox(
                ["上下", "悬浮"],
                ui_settings["dialog_savegame_layout"],
                "layout",
                callback=self.gridpage.callchange,
                internal=["updown", "overlay"],
                default="updown",
            ),
        )
        formLayout.addRow(
            "字体",
            getfonteditor(
                d=globalconfig,
                k="savegame_textfont1",
                callback=self.gridpage.callchange,
            ),
        )
        formLayout.addRow(
            "颜色_文字",
            ColorButton(
                self,
                ui_settings["dialog_savegame_layout"],
                "textColor",
                callback=self.gridpage.callchange,
                default="#000000",
            ),
        )
        formLayout.addRow(
            "颜色_文字区",
            ColorButton(
                self,
                ui_settings["dialog_savegame_layout"],
                "textbackColor",
                callback=self.gridpage.callchange,
                alpha=True,
                default="#ffffffff",
            ),
        )

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
            # 画廊(0) 常驻；移除旧的游戏设置/游戏数据两页。升序删：
            # 当前页随索引左移（同一控件）不触发多余的懒构建
            while self.righttop.count() > 1:
                self.righttop.removeTab(1)
            # 上一游戏的状态宿主回收：统计 页的刷新 QTimer 以它为
            # parent，不删会常驻滴答
            old = getattr(self, "fuckqt6", None)
            if old is not None:
                old.deleteLater()
            dgi = dialog_setting_game_internal(
                self, k, keepindexobject=self.keepindexobject
            )
            self.fuckqt6 = dgi
            # 游戏设置/游戏数据 上提为 righttop 顶层 tab（画廊之后）
            for title, wfunct in dgi.toplevelpages():
                # bare：直角面板由 FluentPaneTabWidget.addTab 统一包裹
                tabadd_lazy(
                    self.righttop,
                    title,
                    functools.partial(dgi.doaddtab, wfunct, k),
                )
            self.righttop.setCurrentIndex(
                min(currvis, self.righttop.count() - 1))
        except:
            print_exc()

    def navigate_to_settings(self, uid, setindexhook=None):
        """外部入口（选择文本窗口/托盘菜单）：导航到该游戏的 游戏设置
        页。侧边栏同步指向该游戏（仅当选中项可见——列表已展开且未被
        过滤；不主动展开列表），右侧重建 游戏设置/游戏数据 两页并停在
        游戏设置。setindexhook 为其 L3 子页签（1=HOOK、3=文本处理），
        写入 keepindexobject，构建时经 initial 直达。"""
        child = None
        for i in range(self.nav.topLevelItemCount()):
            top = self.nav.topLevelItem(i)
            if not top.isExpanded():
                continue
            for j in range(top.childCount()):
                c = top.child(j)
                if not c.isHidden() and c.data(0, GAMEUID_ROLE) == uid:
                    child = c
                    break
            if child is not None:
                break
        # setCurrentItem 触发 _navcurrent 子项分支（网格切到所属列表并
        # 高亮；其 _show_gridpage 随后被下方的 stack 切换覆盖）
        if child is not None and self.nav.currentItem() is not child:
            self.nav.setCurrentItem(child)
        if setindexhook is not None:
            self.keepindexobject["gamesetting"] = setindexhook
        self.viewitem(uid)
        self.stack.setCurrentWidget(self.righttop_card)
        self.righttop.setCurrentIndex(1)   # 1=游戏设置（0=画廊 2=游戏数据）

    def _show_gridpage(self):
        """右侧切到网格页（gridpage 包在 FluentPageCard 页卡里，
        页卡才是 stack 的页）。"""
        self.stack.setCurrentWidget(self.gridpage_card)

    def _sync_titlebar_pagecontrols(self, _=None):
        """标题栏的排序/齿轮只在网格页显示（作用于网格列表）；排序不适用
        于最近游戏（动态只读列表），该列表下排序按钮也隐藏。"""
        gp = self.gridpage
        ongrid = self.stack.currentWidget() is self.gridpage_card
        gp.sortbtn.setVisible(ongrid and gp.reftagid != 1)
        gp.gearbtn.setVisible(ongrid)

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
        idx = calculatetagidx(tagid)
        if idx is None or idx >= len(savegametaged):
            return ""  # tag 已不在 savegametaged（清理竞态防御）
        t = savegametaged[idx]
        if not isinstance(t, dict):
            return ""
        return t["title"]

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
        total = len(self.reallist.get(tagid, []))
        gp = self.gridpage
        # 有 tag 或隐藏不存在开关时显示 (可见/总数)
        if gp.currtags or globalconfig.get("hide_not_exists", False):
            visible = sum(
                1 for uid in self.reallist.get(tagid, [])
                if gp._matches_tags(uid, gp.currtags, tagid))
            count = "{}/{}".format(visible, total)
        else:
            count = str(total)
        self.nav.configureNavigationItem(
            item,
            "{} ({})".format(self._tagtitle(tagid), count),
            None,
            self._tagicon(tagid),
        )

    def _navcurrent(self, item, _=None):
        # 主 nav 选中 -> 清 footernav 的选中（两棵树互斥）
        if item is not None:
            self._footernav.blockSignals(True)
            self._footernav.setCurrentItem(None)
            self._footernav.blockSignals(False)
        if item is None:
            return
        if self.nav._click_pending:
            # 鼠标单击驱动：延迟到双击窗口后执行（双击会取消）
            self.nav._deferred_item = item
            return
        uid = item.data(0, GAMEUID_ROLE)
        if uid:
            # 程序化选中子项（网格图表点击/同步等）：右侧显示其所属
            # 主项的网格并联动高亮——鼠标单击/双击经延迟窗口分流，
            # 不进此分支（见 _gamelistnav._flush_click / _navdouble）
            self.reftagid = item.parent().data(0, TAGID_ROLE)
            self.currentfocusuid = uid
            if (not self.gridpage._loaded) or (
                self.gridpage.reftagid != self.reftagid
            ):
                self.gridpage.showtag(self.reftagid)
            self._show_gridpage()
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
            self._show_gridpage()

    def _navopen(self, item):
        """单击子项：唤出画廊/设置页（双击窗口后执行，见 _flush_click）。
        已在展示该游戏时不重建（原地刷新会闪、tab/设置页全部重建），
        只确保停在画廊/设置页。"""
        uid = item.data(0, GAMEUID_ROLE)
        if not uid:
            return
        self.reftagid = item.parent().data(0, TAGID_ROLE)
        self.currentfocusuid = uid
        dgi = getattr(self, "fuckqt6", None)
        if dgi is None or dgi.gameuid != uid:
            self.viewitem(uid)
        self.stack.setCurrentWidget(self.righttop_card)

    def _getreflist(self, tagid):
        # 持久列表（最近游戏(1)是动态的，返回 None 表示不可改）
        if tagid is None:
            return savehook_new_list
        if tagid == 1:
            return None
        return savegametaged[calculatetagidx(tagid)]["games"]

    def _findchild(self, group, uid):
        for j in range(group.childCount()):
            if group.child(j).data(0, GAMEUID_ROLE) == uid:
                return j
        return None

    def _navmove(self, uid, src_tag, dst_tag, dst_idx):
        """侧边栏拖动。同列表 = 移动；跨列表 = 复制（源保留；目标已有
        该 uid 则丢弃）。item + reallist + 持久列表 + 网格 四方同步。"""
        src_group = self._itemfortag(src_tag)
        dst_group = self._itemfortag(dst_tag)
        if src_group is None or dst_group is None:
            return
        if src_tag != dst_tag:
            # ---- 跨列表：复制 ----
            if uid in self.reallist.get(dst_tag, []):
                return  # 目标已有该游戏：丢弃
            _idx = max(0, min(dst_idx, dst_group.childCount()))
            dst_group.insertChild(_idx, self._makegameitem(uid))
            self.reallist[dst_tag].insert(_idx, uid)
            pl_dst = self._getreflist(dst_tag)
            if pl_dst is not None and uid not in pl_dst:
                pl_dst.insert(min(_idx, len(pl_dst)), uid)
            self._updatetagtext(dst_group)
            if self.gridpage.reftagid == dst_tag:
                self.gridpage.flow_insert(uid, _idx)
            return
        # ---- 同列表：移动 ----
        ca = self._findchild(src_group, uid)
        if ca is None:
            return
        ch = src_group.takeChild(ca)
        _idx = dst_idx
        if _idx > ca:
            _idx -= 1
        _idx = max(0, min(_idx, dst_group.childCount()))
        dst_group.insertChild(_idx, ch)
        self.nav.setCurrentItem(ch)
        # 数据
        self.reallist[src_tag].remove(uid)
        self.reallist[dst_tag].insert(_idx, uid)
        pl_src = self._getreflist(src_tag)
        pl_dst = self._getreflist(dst_tag)
        if pl_src is not None and uid in pl_src:
            pl_src.remove(uid)
        if pl_dst is not None:
            pl_dst.insert(min(_idx, len(pl_dst)), uid)
        # 计数 + 网格同步（单项移动，不重建）——仅当网格正显示该列表
        self._updatetagtext(src_group)
        if self.gridpage.reftagid == src_tag:
            self.gridpage.flow_move_idx(ca, _idx)

    def _sync_from_reflist(self, tagid):
        """排序等操作改写持久列表后，同步 reallist + nav 子项顺序
        （reallist 项集可能被 hide_not_exists 过滤，按持久序重建）。"""
        if tagid == 1:
            # 最近游戏是动态列表：排序只影响本次展示（gridpage.reflist），
            # reallist/nav 同步跳过
            return
        reflist = getreflist(tagid)
        if reflist is None:
            return
        oldset = set(self.reallist.get(tagid, []))
        newlist = [u for u in reflist if u in oldset]
        self.reallist[tagid] = newlist
        group = self._itemfortag(tagid)
        if group is None:
            return
        # 重排期间屏蔽 nav 信号：removeChild 循环会让 current 在子项间
        # 跳变，每次跳变都触发 _navcurrent -> focusgame 的
        # ensureWidgetVisible，表现为"疯狂滚动显示所有项"。
        # 排序即取消聚焦（选中回到主项），滚动风暴与错位高亮一并消除。
        self.currentfocusuid = None
        self.nav.blockSignals(True)
        try:
            items = {}
            for j in range(group.childCount()):
                ch = group.child(j)
                items[ch.data(0, GAMEUID_ROLE)] = ch
            for ch in list(items.values()):
                group.removeChild(ch)
            for u in newlist:
                if u in items:
                    group.addChild(items[u])
            self.nav.setCurrentItem(group)
        finally:
            self.nav.blockSignals(False)

    def _tagmove(self, tagid, dst_idx):
        """主项（列表）拖动：nav 树 + savegametaged 同步重排（位置任意）。"""
        src_idx = self.nav.indexOfTopLevelItem(self._itemfortag(tagid))
        if src_idx < 0:
            return
        item = self.nav.takeTopLevelItem(src_idx)
        if dst_idx > src_idx:
            dst_idx -= 1
        dst_idx = max(0, min(dst_idx, self.nav.topLevelItemCount()))
        self.nav.insertTopLevelItem(dst_idx, item)
        savegametaged.insert(dst_idx, savegametaged.pop(src_idx))
        self.nav.setCurrentItem(item)

    def _gridmove(self, uid, dst_uid, before=False):
        """网格项拖到另一图表上：before=插到目标前，否则目标之后一位。"""
        lst = self.reallist.get(self.gridpage.reftagid) or []
        if dst_uid is None or dst_uid not in lst or uid not in lst:
            self._gridmove_to(uid, len(lst))
            return
        iu = lst.index(uid)
        idst = lst.index(dst_uid)
        # remove(uid) 后目标会前移一位（当 uid 原在目标之前）
        if before:
            self._gridmove_to(uid, idst if iu > idst else idst - 1)
        else:
            self._gridmove_to(uid, idst + 1 if iu > idst else idst)

    def _gridmove_to(self, uid, idx):
        """网格内把 uid 移到 reallist 的 idx 位置（0..len，len=末尾）。
        flow + reallist + 持久列表 + nav 树四方同步（单项，不重建）。
        所有同步都以"移动后 uid 的后一项"为参照锚点——pl/flow 与
        reallist 的项集可能不同（过滤/懒加载），裸索引换算会错位。"""
        tagid = self.gridpage.reftagid
        if tagid == 1:
            return  # 最近游戏不排序
        lst = self.reallist.get(tagid)
        if not lst or uid not in lst:
            return
        lst.remove(uid)
        idx = max(0, min(idx, len(lst)))
        lst.insert(idx, uid)
        nxt = lst[idx + 1] if idx + 1 < len(lst) else None
        prv = lst[idx - 1] if idx > 0 else None
        # 持久列表：参照锚点插入（可能含 reallist 没有的项）
        pl = self._getreflist(tagid)
        if pl is not None and uid in pl:
            pl.remove(uid)
            if nxt is not None and nxt in pl:
                pl.insert(pl.index(nxt), uid)
            elif prv is not None and prv in pl:
                pl.insert(pl.index(prv) + 1, uid)
            else:
                pl.append(uid)
        # flow.widgets / fakegeos（工厂也支持参照）
        fw = self.gridpage.flow
        a = self.gridpage._flow_find(uid)
        if a is not None:
            w = fw.widgets.pop(a)
            g = fw.fakegeos.pop(a)
            nxtf = self.gridpage._flow_find(nxt) if nxt else None
            if nxtf is not None:
                fw.widgets.insert(nxtf, w)
                fw.fakegeos.insert(nxtf, g)
            else:
                fw.widgets.append(w)
                fw.fakegeos.append(g)
            fw.resizeandshow()
        # nav 树
        group = self._itemfortag(tagid)
        ca = self._findchild(group, uid)
        if ca is not None:
            ch = group.takeChild(ca)
            cb = self._findchild(group, nxt) if nxt else None
            if cb is not None:
                group.insertChild(cb, ch)
            else:
                group.addChild(ch)
            self.nav.setCurrentItem(ch)

    def _sync_current_to_gridlist(self, main_item):
        """双击主项展开/折叠后调用：网格正聚焦着该列表的游戏时，
        侧边栏立即聚焦到对应的子项（展开时）或主项（折叠时）。"""
        uid = self.currentfocusuid
        if not uid or uid not in savehook_new_data:
            return
        if self.gridpage.reftagid != main_item.data(0, TAGID_ROLE):
            return  # 网格聚焦的游戏不属于该列表：不动
        target = main_item
        if main_item.isExpanded():
            # 展开：聚焦到网格当前聚焦游戏对应的子项
            for j in range(main_item.childCount()):
                child = main_item.child(j)
                if child.data(0, GAMEUID_ROLE) == uid:
                    target = child
                    break
        if self.nav.currentItem() is not target:
            self.nav.setCurrentItem(target)
        self.currentfocusuid = uid  # 分支可能清聚焦，补回

    def _navdouble(self, item, _col):
        uid = item.data(0, GAMEUID_ROLE)
        if not uid:
            return
        # 双击子项：与其所属主项的网格同步（切网格页 + 高亮）；
        # 打开画廊/设置由单击承担（与单击语义交换）
        self.reftagid = item.parent().data(0, TAGID_ROLE)
        self.currentfocusuid = uid
        if (not self.gridpage._loaded) or (
            self.gridpage.reftagid != self.reftagid
        ):
            self.gridpage.showtag(self.reftagid)
        self._show_gridpage()
        self.gridpage.focusgame(uid)

    def point_game(self, uid):
        """网格页图表点击：侧边栏指向该游戏——主项展开时选中子项；
        主项折叠时选中留在主项（不展开它），仅更新聚焦状态。"""
        group = self._itemfortag(self.gridpage.reftagid)
        if group is None:
            return
        self.currentfocusuid = uid
        self.reftagid = group.data(0, TAGID_ROLE)
        if group.isExpanded():
            # 展开：选中子项（_navcurrent 子项分支联动高亮）
            for j in range(group.childCount()):
                child = group.child(j)
                if child.data(0, GAMEUID_ROLE) == uid:
                    if self.nav.currentItem() is not child:
                        self.nav.setCurrentItem(child)
                    return
        elif self.nav.currentItem() is not group:
            # 折叠：选中留在主项（_navcurrent 主项分支：同列表不重建网格）
            self.nav.setCurrentItem(group)
            self.currentfocusuid = uid  # 主项分支会清聚焦，补回

    def _navexpand(self, exp, item):
        if item.parent() is not None:
            return
        # point_game 选中隐藏子项引起的自动展开/回折不写存档
        if getattr(self, "_suppress_navexpand", False):
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
        if not self.currentfocusuid or (
            self.currentfocusuid not in savehook_new_data
        ):
            return  # 无有效选中游戏（右键空白/主项时防御）
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

        action = menu.exec(QCursor.pos())
        if action == startgame:
            startgamecheck(self, getreflist(self.reftagid), self.currentfocusuid)
        elif action == delgame:
            self.shanchuyouxi()
        elif action == opendir:
            self.clicked4()
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
            group = self._itemfortag(self.reftagid)
            child = group.takeChild(idx)
            group.insertChild(0, child)
        self.reftagid = __save

    def directshow(self):
        pass

    def callexists(self, _):
        # 隐藏不存在开关：过滤刷新（含 drag/drop 切换）+ 计数刷新
        gp = self.gridpage
        gp.tagschanged(gp.currtags)  # 内部走 _apply_tag_filter（切 drag/drop）
        for i in range(self.nav.topLevelItemCount()):
            self._updatetagtext(self.nav.topLevelItem(i))

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
        self.nav.itemExpanded.connect(functools.partial(self._navexpand, True))
        self.nav.itemCollapsed.connect(functools.partial(self._navexpand, False))
        self.setstyle()

        # 侧边栏容器：内容距边 6px（同设置窗口 FluentTabWidget 的
        # main/footer 容器边距），汉堡是导航窗格第一行（共用组件）
        navcontainer = QWidget()
        navlay = QVBoxLayout(navcontainer)
        navlay.setContentsMargins(0, 0, 0, 0)
        navlay.setSpacing(0)
        main_container = QWidget()
        main_lay = QVBoxLayout(main_container)
        main_lay.setContentsMargins(6, 6, 6, 0)
        main_lay.setSpacing(0)
        hamburger = FluentNavToggleButton()
        hamburger.setText(ICON_GLOBAL_NAV)
        hamburger.setToolTip("折叠/展开侧边栏")
        hamburger.clicked.connect(self._toggle_nav)
        main_lay.addWidget(hamburger)
        main_lay.addWidget(self.nav, 1)
        navlay.addWidget(main_container, 1)
        # 底部：分隔线（页卡描边色，仅导航溢出时显示，共用组件） + 设置项
        _sep = FluentCardSeparator()
        _sep.followNavScroll(self.nav)
        navlay.addWidget(_sep)
        self._footernav = FluentNavTree()
        self._footernav.setProperty("ItemHeight", 38)
        self._footernav.setFixedHeight(38)
        self._footernav.addNavigationItem("设置", -1, ICON_SETTINGS,
                                          auto_select=False)
        self._footernav.pageIndexChanged.connect(
            lambda _: self._open_settings())
        footer_container = QWidget()
        footer_lay = QVBoxLayout(footer_container)
        footer_lay.setContentsMargins(6, 0, 6, 6)
        footer_lay.setSpacing(0)
        footer_lay.addWidget(self._footernav)
        navlay.addWidget(footer_container)
        # 主导航展开/收起（含双击展开分组触发的自动展开）-> 底部导航跟随
        self.nav.navigationExpandedChanged.connect(
            self._footernav.setNavigationExpanded)
        # 折叠状态持久化：任意来源（汉堡/双击展开联动/程序性）都保存
        self.nav.navigationExpandedChanged.connect(
            lambda exp: globalconfig.__setitem__(
                "gamemanager_nav_collapsed", not exp))
        self.righttop = makesubtab_lazy(type=1)
        self.righttop.setStyleSheet(
            "QTabWidget::pane{border:0;margin:0;padding:0;}"
            "QTabWidget::tab-bar{left:8px;}")
        self.pixview = pixwrapper(self)
        # 画廊/游戏设置/游戏数据：页为裸容器，直角面板由
        # FluentPaneTabWidget.addTab 统一包裹；后两页由 viewitem 重建
        tabadd_lazy(self.righttop, "画廊",
                    lambda lay: lay.addWidget(self.pixview))
        # 右侧两页：0=网格大图表（主项点击） 1=画廊/游戏设置/游戏数据
        # （子项点击）。righttop 整体（含 tabbar）包一张页卡——tabbar 也在卡内
        righttopcard = FluentPageCard()
        _rl = QVBoxLayout(righttopcard)
        _rl.setContentsMargins(16, 0, 16, 12)
        _rl.addWidget(self.righttop)
        self.righttop_card = righttopcard
        self.stack = QStackedWidget()
        self.gridpage = _gridpage(self)
        gridcard = FluentPageCard()
        _glay2 = QVBoxLayout(gridcard)
        _glay2.setContentsMargins(0, 0, 0, 0)
        _glay2.addWidget(self.gridpage)
        # gridpage 包在页卡里：切页统一走 _show_gridpage（页卡是 stack 的页）
        self.gridpage_card = gridcard
        self.stack.addWidget(gridcard)
        self.stack.addWidget(righttopcard)
        # 标题栏的排序/齿轮只作用于网格列表——仅网格页显示
        self.stack.currentChanged.connect(self._sync_titlebar_pagecontrols)
        # 标题栏控件（搜索居中/面包屑/排序/齿轮尾部）装进宿主无边框
        # 窗口的 FluentTitleBar（跨页常驻）
        self.gridpage.build_titlebar(parent._fluent_title_bar)
        self._sync_titlebar_pagecontrols()
        # 布局：侧边栏 | 内容。内容区四边 0 边距——页卡与侧边栏右缘、
        # 标题栏下沿、窗口右/下框完全重合（同设置窗口的满铺页卡）
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(navcontainer)
        body = QWidget()
        bodylay = QHBoxLayout(body)
        bodylay.setContentsMargins(0, 0, 0, 0)
        bodylay.addWidget(self.stack, 1)
        lay.addWidget(body, 1)
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
                self.reallist[tagid].append(k)
                group0.addChild(self._makegameitem(k))
                rowreal += 1
            self._updatetagtext(group0)
        # 初始聚焦排在最前的主项：右侧先显示网格页，而非游戏子项
        if self.nav.topLevelItemCount():
            self.nav.setCurrentItem(self.nav.topLevelItem(0))
        # 树建好后应用当前过滤（hide_not_exists / tag）
        self.gridpage._apply_tag_filter()
        # 应用存档的折叠/展开：图标模式会折叠全部父项并把
        # 选中的子项提升到顶层（指示条位置正确）
        _nav_expanded = not globalconfig.get(
            "gamemanager_nav_collapsed", False)
        self.nav.setNavigationExpanded(_nav_expanded, animated=False)
        self._footernav.setNavigationExpanded(_nav_expanded, animated=False)

    def updatelangtext(self):
        # 语言切换：内置列表项（所有游戏/最近游戏）刷新；自定义列表名不翻译
        for i in range(self.nav.topLevelItemCount()):
            item = self.nav.topLevelItem(i)
            if item.data(0, TAGID_ROLE) in (None, 1):
                self._updatetagtext(item)

    def _open_settings(self):
        # footernav「设置」：清主 nav 选中（互斥）+ 卡片式设置页（两个通用项）
        self.nav.blockSignals(True)
        self.nav.setCurrentItem(None)
        self.nav.blockSignals(False)
        if getattr(self, "_settingspage", None) is not None:
            self.stack.setCurrentWidget(self._settingspage)
            return
        # 页面包 FluentPageCard 背景卡（同设置窗口主页面），内容卡浮其上
        page = FluentPageCard()
        _host = QVBoxLayout(page)
        _host.setContentsMargins(0, 0, 0, 0)
        _host.setProperty("_fluent_main_grid", True)
        grid = [
            [(makecardrow(
                "隐藏不存在的游戏",
                D_getsimpleswitch(
                    globalconfig, "hide_not_exists",
                    callback=lambda v: self.callexists(v),
                    default=False)(),
            ), 0)],
            [(makecardrow(
                "启动游戏不修改顺序",
                D_getsimpleswitch(
                    globalconfig, "startgamenotop", default=True)(),
            ), 0)],
        ]
        makescrollgrid(grid, _host)
        self._settingspage = page
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

    def _toggle_nav(self):
        # 折叠状态由 navigationExpandedChanged 信号统一持久化
        exp = not self.nav.navigationExpanded()
        self.nav.setNavigationExpanded(exp)
        self._footernav.setNavigationExpanded(exp)

    def tagbuttonmenu(self, tagid):
        self.currentfocusuid = None
        self.reftagid = tagid
        menu = QMenu(self)
        editname = LAction("修改列表名称", menu)
        addlist = LAction("创建列表", menu)
        dellist = LAction("删除列表", menu)
        addgame = LAction("添加游戏", menu)
        batchadd = LAction("批量添加", menu)
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
        elif action == editname or action == addlist:
            self.createlist(action == addlist, tagid)

        elif action == dellist:
            if not request_delete_ok(self, "v3-dellist-confirm"):
                return
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
                # 新列表放到最后（而非插入到来源列表之前）
                savegametaged.append(tag)
                group0 = self._addtagitem(
                    len(savegametaged) - 1, tag["uid"], True)
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
        # 网格同步（当前显示该列表时）
        if self.gridpage.reftagid == self.reftagid:
            self.gridpage.flow_move_idx(idx1, idx2)
        idx1 = getreflist(self.reftagid).index(uid)
        idx2 = getreflist(self.reftagid).index(uid2)
        getreflist(self.reftagid).insert(idx2, getreflist(self.reftagid).pop(idx1))

    def shanchuyouxi(self):
        if not self.currentfocusuid:
            return
        if self.reftagid == 1:
            return  # 最近游戏是动态只读列表，不可删除
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
            # 网格同步删除（当前显示该列表时）
            if self.gridpage.reftagid == self.reftagid:
                self.gridpage.flow_remove(uid)
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
