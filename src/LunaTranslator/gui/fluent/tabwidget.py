"""FluentTabWidget —— 设置页导航容器（WinUI NavigationView 版）。

左侧主导航（7 项）+ 分隔线 + 底部固定导航（关于软件）+ 右侧 QTabWidget。
兼容 makesubtab_lazy / tabadd_lazy / about.py 动态加页 / setCurrentIndex /
currentChanged / updatelangtext 的全部调用面。
"""

from qtsymbols import (
    QEvent,
    Qt,
    QFont,
    QFrame,
    QHBoxLayout,
    QModelIndex,
    QTabBar,
    QTabWidget,
    QToolButton,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
    QApplication,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPalette,
    QRectF,
    QSizePolicy,
)

import functools

from myutils.config import _TR
from gui.fluent.nav import FluentNavTree, NAV_PAGE_ROLE, NAV_ICON_ROLE

from gui.fluent.icons import (
    ICON_SETTINGS,
    ICON_CHARACTERS,
    ICON_SETTINGS_DISPLAY_SOUND,
    ICON_PROCESSING,
    ICON_DICTIONARY,
    ICON_AUDIO,
    ICON_KEYBOARD_CLASSIC,
    ICON_INFO,
    ICON_NAV_FALLBACK,
    ICON_GLOBAL_NAV,
)

# 按标题取图标：层级子页加入主 stack 后，位置索引与树序不再一一对应
NAV_ICONS = {
    "核心设置": ICON_SETTINGS,
    "翻译设置": ICON_CHARACTERS,
    "显示设置": ICON_SETTINGS_DISPLAY_SOUND,
    "文本处理": ICON_PROCESSING,
    "辞书设置": ICON_DICTIONARY,
    "语音合成": ICON_AUDIO,
    "快捷按键": ICON_KEYBOARD_CLASSIC,
}

# fluentui3styleproperties.h —— enum TabBarStyle
TABBAR_STYLE_SEGMENTED_WINUI3 = 9  # Segmented_WinUI3
TABBAR_STYLE_NAVIGATION = 8  # Navigation


class FluentPageCard(QWidget):
    """tab 页的圆角包裹卡：底色介于窗口与内容卡之间——
    浅色 = 调色板 Base(249)，暗色 = 窗口色上叠 4% 白(≈41)——
    使「窗口 243/32 → 页面 249/41 → 内容卡 253/50」三级都可分辨。"""

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        dark = False
        app = QApplication.instance()
        if app is not None:
            cs = app.property("_q_colorscheme")
            if cs is not None:
                try:
                    dark = int(cs) == 1
                except Exception:
                    dark = self.palette().color(QPalette.Window).lightness() < 128
        if dark:
            w = self.palette().color(QPalette.Window)
            fill = QColor(
                round(w.red() + (255 - w.red()) * 0.04),
                round(w.green() + (255 - w.green()) * 0.04),
                round(w.blue() + (255 - w.blue()) * 0.04))
            border = QColor(0x25, 0x25, 0x25)
        else:
            fill = QColor(self.palette().color(QPalette.Base))
            border = QColor(0xE9, 0xE9, 0xE9)
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 4, 4)
        painter.fillPath(path, fill)
        painter.setPen(QPen(border, 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)


def apply_segmented_tabbar_style(bar: QTabBar):
    """QTabBar 本体的 Segmented WinUI3 配置
    （QTabWidget 与裸 QTabBar 通用，Gallery pagetab.cpp winUi3IconOnlyBar 同款）。"""
    bar.setProperty("tabBarStyle", TABBAR_STYLE_SEGMENTED_WINUI3)
    bar.setAttribute(Qt.WA_StyledBackground, True)
    bar.setDrawBase(False)
    bar.setExpanding(False)


def apply_segmented_tabbar(tabwidget: QTabWidget):
    """把 QTabWidget 配成 Segmented WinUI3 风格
    （Gallery pagetab.cpp setupSegmentedTabs / addTabBarSection 同款），
    并去掉 pane 边框。"""
    # pane 的去除由 LTabWidget.paintEvent 置空完成（不用 QSS——
    # 容器级样式表会给全部后代套 QStyleSheetStyle）
    apply_segmented_tabbar_style(tabwidget.tabBar())


def apply_navigation_tabbar(tabwidget: QTabWidget):
    """把 QTabWidget 配成 Navigation TabBar（Gallery pagetab.cpp setupNavigationTabs
    同款）：左侧垂直导航页签，选中指示条变长效果。"""
    bar = tabwidget.tabBar()
    tabwidget.setTabPosition(QTabWidget.West)
    bar.setShape(QTabBar.RoundedWest)
    bar.setDrawBase(False)
    bar.setExpanding(False)
    bar.setAttribute(Qt.WA_StyledBackground, False)
    bar.setProperty(
        "TextAlign", int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    )
    bar.setProperty("tabBarStyle", TABBAR_STYLE_NAVIGATION)


class _NoPaneTabWidget(QTabWidget):
    """QTabWidget::paintEvent 只画 pane（PE_FrameTabWidget：1px 边框 +
    Base 底色）。置空以去掉 pane——不能用 QSS，容器级样式表会给全部
    后代套 QStyleSheetStyle，破坏插件渲染与字体继承。"""

    def paintEvent(self, e):
        pass


def make_lazy_page(getrealwidgetfunction, main=True):
    """懒加载页占位：FluentPageCard 圆角卡包裹 + lazyfunction（构建由
    首次选中触发）。main=True 主 stack 页（_fluent_main_grid），否则为
    子页签卡内网格（_fluent_card_grid）。"""
    q = QWidget()
    v = QVBoxLayout(q)
    v.setContentsMargins(0, 0, 0, 0)
    card = FluentPageCard()
    v.addWidget(card)
    innerlay = QVBoxLayout(card)
    innerlay.setContentsMargins(0, 0, 0, 0)
    innerlay.setProperty("_fluent_main_grid" if main else "_fluent_card_grid", True)
    q.lazyfunction = functools.partial(getrealwidgetfunction, innerlay)
    return q


class FluentTabWidget(QWidget):
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__titles = []
        self.__child_pages = []  # (QTreeWidgetItem, 原始标题)——层级子节点
        self.__syncing = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ---- 导航栏结构照抄 Gallery ExWinUINavigationView ----
        nav_pane = QWidget(self)
        nav_lay = QVBoxLayout(nav_pane)
        nav_lay.setContentsMargins(0, 0, 0, 0)
        nav_lay.setSpacing(0)

        # 主导航（可伸展）；容器边距 (6,6,6,0)——下边贴分隔线
        main_container = QWidget(nav_pane)
        main_lay = QVBoxLayout(main_container)
        main_lay.setContentsMargins(6, 6, 6, 0)
        main_lay.setSpacing(0)
        # 汉堡：导航窗格第一行（同游戏管理器；标题栏不放导航按钮）
        self.nav_toggle_button = QToolButton(main_container)
        self.nav_toggle_button.setObjectName("win_caption_pin")
        self.nav_toggle_button.setAutoRaise(True)
        self.nav_toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextOnly)
        _f = QFont("Segoe Fluent Icons")
        _f.setPixelSize(16)
        self.nav_toggle_button.setFont(_f)
        self.nav_toggle_button.setText(ICON_GLOBAL_NAV)
        self.nav_toggle_button.setFixedSize(44, 38)
        self.nav_toggle_button.setToolTip("折叠/展开侧边栏")
        self.nav_toggle_button.clicked.connect(self.toggleNavigation)
        main_lay.addWidget(self.nav_toggle_button)
        self.nav = FluentNavTree(main_container)
        main_lay.addWidget(self.nav)

        # 分隔线：整宽、无边距（与窗口边缘/页面卡描边连成闭合回路）
        self._nav_separator = QFrame(nav_pane)
        self._nav_separator.setFrameShape(QFrame.HLine)
        self._nav_separator.setFrameShadow(QFrame.Sunken)
        self._nav_separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # 底部固定导航（关于软件，不参与伸展）；容器边距 (6,0,6,6)——上边贴分隔线
        footer_container = QWidget(nav_pane)
        footer_lay = QVBoxLayout(footer_container)
        footer_lay.setContentsMargins(6, 0, 6, 6)
        footer_lay.setSpacing(0)
        self.nav_footer = FluentNavTree(footer_container)
        self.nav_footer.setFixedHeight(38)
        footer_lay.addWidget(self.nav_footer)

        nav_lay.addWidget(main_container, 1)
        nav_lay.addWidget(self._nav_separator, 0)
        nav_lay.addWidget(footer_container, 0)

        self.tab_widget = _NoPaneTabWidget(self)
        self.tab_widget.tabBar().hide()
        # 插件给 QTabWidget pane 自带内边距（实测页卡四边被缩进 2-4px，
        # 右侧离窗口框架不贴）——置空 pane 的边距/内边距，页卡与窗口
        # 边缘完全重合
        self.tab_widget.setStyleSheet(
            "QTabWidget::pane{border:0;margin:0;padding:0;}")

        lay.addWidget(nav_pane)
        lay.addWidget(self.tab_widget, 1)

        # 单一发射点：stack 变化 -> currentChanged（makesubtab_lazy 据此懒加载）
        self.nav.pageIndexChanged.connect(self.__nav_changed)
        self.nav_footer.pageIndexChanged.connect(self.__nav_changed)
        self.tab_widget.currentChanged.connect(self.__stack_changed)

        # 跨导航取消选中（点主导航时清底部，反之亦然）
        self.nav.currentItemChanged.connect(
            lambda cur, _prev: self.__cross_select(self.nav_footer))
        self.nav_footer.currentItemChanged.connect(
            lambda cur, _prev: self.__cross_select(self.nav))

        # 默认展开（同 Win11 设置）
        self.nav.setNavigationExpanded(True, animated=False)
        self.nav_footer.setNavigationExpanded(True, animated=False)

    # ---- 跨导航取消选中 ----
    def __cross_select(self, peer):
        if peer.selectionModel() and peer.selectionModel().hasSelection():
            peer.blockSignals(True)
            peer.clearSelection()
            peer.setCurrentIndex(QModelIndex())
            peer.blockSignals(False)
            if peer.viewport():
                peer.viewport().update()

    # ---- TabWidget 兼容面 ----
    def addTab(self, widget, title):
        self.__titles.append(title)
        self.tab_widget.addTab(widget, _TR(title))
        idx = self.tab_widget.count() - 1
        if "关于" in title:
            # 底部固定导航，不自动选中
            self.nav_footer.addNavigationItem(
                _TR(title), idx, ICON_INFO, auto_select=False)
        else:
            icon = NAV_ICONS.get(title, ICON_NAV_FALLBACK)
            self.nav.addNavigationItem(_TR(title), idx, icon)

    # ---- 层级子导航（同 Gallery mainwindow 的 add_nav_child） ----
    def navPageIndex(self, title):
        """顶层页标题 -> stack 索引（__titles 与 stack 顺序一致）。"""
        try:
            return self.__titles.index(title)
        except ValueError:
            return None

    def addNavChildPage(self, parent_title, title, getrealwidgetfunction=None,
                        page_index=None):
        """把页面挂为 parent_title 导航项的子节点（WinUI 层级导航）。
        page_index 给定时复用已有页面（父项与首子项同页），否则新建
        懒加载页加入主 stack。返回页索引。"""
        if page_index is None:
            q = make_lazy_page(getrealwidgetfunction)
            self.tab_widget.addTab(q, _TR(title))
            page_index = self.tab_widget.count() - 1
        parent_page = self.navPageIndex(parent_title)
        parent = self._find_item_by_page(parent_page) if parent_page is not None else None
        if parent is not None:
            child = QTreeWidgetItem(parent)
            self.nav.configureNavigationItem(child, _TR(title), page_index, "")
            self.__child_pages.append((child, title))
            # 父项默认折叠（单击父项整行展开/折叠，见 FluentNavTree）
        return page_index

    def _find_item_by_page(self, page_index):
        """在主导航/底部导航中递归查找指向 page_index 的节点（含子节点）。"""
        if page_index is None:
            return None
        for tree in (self.nav, self.nav_footer):
            item = self._find_item_by_page_r(tree.invisibleRootItem(), page_index)
            if item is not None:
                return item
        return None

    @staticmethod
    def _find_item_by_page_r(root, page_index):
        for i in range(root.childCount()):
            item = root.child(i)
            if item.data(0, NAV_PAGE_ROLE) == page_index:
                return item
            found = FluentTabWidget._find_item_by_page_r(item, page_index)
            if found is not None:
                return found
        return None

    def setCurrentIndex(self, idx):
        if idx < 0 or idx >= self.tab_widget.count():
            return
        item = self._find_item_by_page(idx)
        if item is not None:
            # 子节点需展开祖先链才可见
            p = item.parent()
            while p is not None:
                p.setExpanded(True)
                p = p.parent()
            tree = item.treeWidget()
            if tree.currentItem() is not item:
                tree.setCurrentItem(item)
            return
        # 兜底：直接切 stack
        if self.tab_widget.currentIndex() != idx:
            self.tab_widget.setCurrentIndex(idx)

    def currentIndex(self):
        return self.tab_widget.currentIndex()

    def currentWidget(self):
        return self.tab_widget.currentWidget()

    def widget(self, idx):
        return self.tab_widget.widget(idx)

    def count(self):
        return self.tab_widget.count()

    def adjust_list_widget_width(self):
        pass  # 导航宽度固定（44/200），无需按字体测量

    def toggleNavigation(self):
        self.nav.toggleNavigationMode()
        self.nav_footer.toggleNavigationMode()

    def navigationExpanded(self):
        return self.nav.navigationExpanded()

    # ---- 语言切换 ----
    def updatelangtext(self):
        for i, title in enumerate(self.__titles):
            self.tab_widget.setTabText(i, _TR(title))
        for i in range(self.nav.topLevelItemCount()):
            item = self.nav.topLevelItem(i)
            if item is not None:
                self.nav.configureNavigationItem(
                    item, _TR(self.__titles[item.data(0, NAV_PAGE_ROLE)]),
                    item.data(0, NAV_PAGE_ROLE), item.data(0, NAV_ICON_ROLE))
        for i in range(self.nav_footer.topLevelItemCount()):
            item = self.nav_footer.topLevelItem(i)
            if item is not None:
                self.nav_footer.configureNavigationItem(
                    item, _TR(self.__titles[item.data(0, NAV_PAGE_ROLE)]),
                    item.data(0, NAV_PAGE_ROLE), item.data(0, NAV_ICON_ROLE))
        for item, title in self.__child_pages:
            if item is not None:
                self.nav.configureNavigationItem(
                    item, _TR(title), item.data(0, NAV_PAGE_ROLE), "")

    def changeEvent(self, event):
        if event is not None and event.type() == QEvent.Type.LanguageChange:
            self.updatelangtext()
        return super().changeEvent(event)

    # ---- 内部 ----
    def __nav_changed(self, idx):
        if self.__syncing:
            return
        self.__syncing = True
        try:
            if self.tab_widget.currentIndex() != idx:
                self.tab_widget.setCurrentIndex(idx)
        finally:
            self.__syncing = False

    def __stack_changed(self, idx):
        self.currentChanged.emit(idx)
