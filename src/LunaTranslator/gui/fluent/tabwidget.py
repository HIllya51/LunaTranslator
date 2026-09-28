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
    QApplication,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPalette,
    QRectF,
    QSizePolicy,
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
    apply_segmented_tabbar_style(tabwidget.tabBar())
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

        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()
        # 插件给 QTabWidget 的 pane 画 1px 边框 + Base 底色（PE_FrameTabWidget），
        # 会与页面卡的描边叠成双边框——去掉 pane 绘制
        self.tab_widget.setStyleSheet(
            "QTabWidget::pane{border:0;background:transparent;}"
        )

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
