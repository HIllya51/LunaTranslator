"""FluentTabWidget —— 设置页导航容器（WinUI NavigationView 版）。

左侧主导航（7 项）+ 分隔线 + 底部固定导航（关于软件）+ 右侧 QTabWidget。
兼容 makesubtab_lazy / tabadd_lazy / about.py 动态加页 / setCurrentIndex /
currentChanged / updatelangtext 的全部调用面。
"""

from qtsymbols import (
    QEvent,
    Qt,
    QFrame,
    QHBoxLayout,
    QModelIndex,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)

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
)

NAV_ICONS = [
    ICON_SETTINGS, ICON_CHARACTERS, ICON_SETTINGS_DISPLAY_SOUND,
    ICON_PROCESSING, ICON_DICTIONARY, ICON_AUDIO, ICON_KEYBOARD_CLASSIC,
]

# fluentui3styleproperties.h —— enum TabBarStyle
TABBAR_STYLE_SEGMENTED_WINUI3 = 9  # Segmented_WinUI3
TABBAR_STYLE_NAVIGATION = 8  # Navigation


def apply_segmented_tabbar(tabwidget: QTabWidget):
    """把 QTabWidget 配成 Segmented WinUI3 风格
    （Gallery pagetab.cpp setupSegmentedTabs / addTabBarSection 同款），
    并去掉 pane 边框。"""
    bar = tabwidget.tabBar()
    bar.setProperty("tabBarStyle", TABBAR_STYLE_SEGMENTED_WINUI3)
    bar.setAttribute(Qt.WA_StyledBackground, True)
    bar.setDrawBase(False)
    bar.setExpanding(False)
    tabwidget.setStyleSheet("QTabWidget::pane{border:0;background:transparent;}")


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
    tabwidget.setStyleSheet("QTabWidget::pane{border:0;background:transparent;}")


class FluentTabWidget(QWidget):
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__titles = []
        self.__syncing = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        nav_pane = QWidget(self)
        nav_lay = QVBoxLayout(nav_pane)
        nav_lay.setContentsMargins(6, 6, 6, 6)
        nav_lay.setSpacing(0)

        # 主导航（可伸展）
        self.nav = FluentNavTree(nav_pane)
        nav_lay.addWidget(self.nav, 1)

        # 分隔线
        self._nav_separator = QFrame(nav_pane)
        self._nav_separator.setFrameShape(QFrame.HLine)
        self._nav_separator.setFrameShadow(QFrame.Sunken)
        nav_lay.addSpacing(4)
        nav_lay.addWidget(self._nav_separator)
        nav_lay.addSpacing(4)

        # 底部固定导航（关于软件，不参与伸展）
        self.nav_footer = FluentNavTree(nav_pane)
        self.nav_footer.setFixedHeight(38)
        nav_lay.addWidget(self.nav_footer)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()

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
        from myutils.config import _TR

        self.tab_widget.addTab(widget, _TR(title))
        idx = self.tab_widget.count() - 1
        if "关于" in title:
            # 底部固定导航，不自动选中
            self.nav_footer.addNavigationItem(
                _TR(title), idx, ICON_INFO, auto_select=False)
        else:
            icon = (NAV_ICONS[idx] if idx < len(NAV_ICONS) else ICON_NAV_FALLBACK)
            self.nav.addNavigationItem(_TR(title), idx, icon)

    def setCurrentIndex(self, idx):
        if idx < 0 or idx >= self.tab_widget.count():
            return
        # 主导航
        for i in range(self.nav.topLevelItemCount()):
            item = self.nav.topLevelItem(i)
            if item.data(0, NAV_PAGE_ROLE) == idx:
                if self.nav.currentItem() is not item:
                    self.nav.setCurrentItem(item)
                return
        # 底部导航
        for i in range(self.nav_footer.topLevelItemCount()):
            item = self.nav_footer.topLevelItem(i)
            if item.data(0, NAV_PAGE_ROLE) == idx:
                if self.nav_footer.currentItem() is not item:
                    self.nav_footer.setCurrentItem(item)
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
        from myutils.config import _TR

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
