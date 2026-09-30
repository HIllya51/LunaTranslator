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
from gui.dynalang import LTabWidget
from gui.fluent.nav import FluentNavTree, FluentNavToggleButton, NAV_PAGE_ROLE, NAV_ICON_ROLE

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
TABBAR_STYLE_NAVIGATION = 8  # Navigation
TABBAR_STYLE_PIVOT_GROW = 3  # Pivot_Grow

# 直角面板（FluentSquarePane）配色
PANE_COLORS_PAGE = 0  # 同页卡（FluentPageCard 配方）
PANE_COLORS_CARD = 1  # 同内容卡（插件 isCard 配方）


class FluentCardSeparator(QFrame):
    """侧边栏分割线（游戏管理与设置窗口共用）：颜色与页卡描边一致
    （_pagecard_colors 的描边色，随明暗主题）。
    默认隐藏，followNavScroll 后仅在导航内容溢出（需要滚动）时显示。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.hide()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.fillRect(self.rect(), _pagecard_colors(self)[1])

    def followNavScroll(self, nav):
        """导航内容溢出（需要滚动）时才显示分割线；空间充足时留白。"""
        def sync(*_):
            self.setVisible(nav.verticalScrollBar().maximum() > 0)
        nav.verticalScrollBar().rangeChanged.connect(sync)
        sync()


def _is_dark_theme(w: QWidget):
    """明暗判定：应用级 _q_colorscheme 优先，回退调色板亮度。"""
    app = QApplication.instance()
    if app is not None:
        cs = app.property("_q_colorscheme")
        if cs is not None:
            try:
                return int(cs) == 1
            except Exception:
                pass
    return w.palette().color(QPalette.Window).lightness() < 128


def _pagecard_colors(w: QWidget):
    """页卡配色（FluentPageCard / FluentSquarePane(page) / 分割线共用）：
    浅色 = 调色板 Base(249) + #E9E9E9 描边；暗色 = 窗口色上叠 4% 白
    (≈41) + 白@0x12 描边（插件 pane 的 frameColorLight——偏白，与
    Gallery 暗色页卡一致）。"""
    if _is_dark_theme(w):
        wc = w.palette().color(QPalette.Window)
        fill = QColor(
            round(wc.red() + (255 - wc.red()) * 0.04),
            round(wc.green() + (255 - wc.green()) * 0.04),
            round(wc.blue() + (255 - wc.blue()) * 0.04))
        border = QColor(255, 255, 255, 0x12)
    else:
        fill = QColor(w.palette().color(QPalette.Base))
        border = QColor(0xE9, 0xE9, 0xE9)
    return fill, border


def _contentcard_colors(w: QWidget):
    """内容卡配色（FluentSquarePane(card)，插件 isCard 的 PE_Widget
    配方）：底色 = winUI3CardBackgroundColor（浅色白@179 叠 Base≈253、
    暗色白@13 叠 Base），描边 = cardStrokeColorBalanced（#E9E9E9 /
    #252525，不透明）。"""
    dark = _is_dark_theme(w)
    base = QColor(w.palette().color(QPalette.Base))
    if base.alpha() == 0:
        base = QColor(w.palette().color(QPalette.Window))
    if base.alpha() == 0:
        base = QColor(0x1E, 0x1E, 0x1E) if dark else QColor(0xFF, 0xFF, 0xFF)
    card = QColor(255, 255, 255, 13) if dark else QColor(255, 255, 255, 179)
    alpha = card.alphaF()
    fill = QColor(
        round(base.red() * (1 - alpha) + card.red() * alpha),
        round(base.green() * (1 - alpha) + card.green() * alpha),
        round(base.blue() * (1 - alpha) + card.blue() * alpha))
    border = QColor(0x25, 0x25, 0x25) if dark else QColor(0xE9, 0xE9, 0xE9)
    return fill, border


class FluentPageCard(QWidget):
    """tab 页的圆角包裹卡：底色介于窗口与内容卡之间——
    浅色 = 调色板 Base(249)，暗色 = 窗口色上叠 4% 白(≈41)——
    使「窗口 243/32 → 页面 249/41 → 内容卡 253/50」三级都可分辨。"""

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        fill, border = _pagecard_colors(self)
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 4, 4)
        painter.fillPath(path, fill)
        painter.setPen(QPen(border, 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)


class FluentSquarePane(QWidget):
    """直角面板（Gallery 子页签内容的统一包裹，插件 QTabWidget::pane
    直角面板的等价自绘）：四角直角。colorstyle 选配色——'page' 同
    页卡（_pagecard_colors）或 'card' 同内容卡（_contentcard_colors）。"""

    def __init__(self, parent=None, colorstyle=PANE_COLORS_PAGE):
        super().__init__(parent)
        self.colorstyle = colorstyle

    def paintEvent(self, e):
        painter = QPainter(self)
        if self.colorstyle == PANE_COLORS_CARD:
            fill, border = _contentcard_colors(self)
        else:
            fill, border = _pagecard_colors(self)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.fillRect(rect, fill)
        painter.setPen(QPen(border, 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)


def apply_pivot_bar_style(bar: QTabBar):
    """裸 QTabBar 的 Pivot_Grow 配置（segmented 全面退场的替代）：
    无样式化底（插件对带底 QTabBar 画分段容器底）、drawBase 默认值经
    插件 PE_FrameTabBarBase 空实现不画、紧凑排布（不均分宽度；
    需均分的调用方随后自行 setExpanding(True)）。"""
    bar.setProperty("tabBarStyle", TABBAR_STYLE_PIVOT_GROW)
    bar.setAttribute(Qt.WA_StyledBackground, False)
    bar.setDrawBase(True)
    bar.setExpanding(False)


class FluentPaneTabWidget(LTabWidget):
    """Gallery 式页签组（pageaudiolevelmeter.cpp 基础/刻度/动画/颜色
    tab 同款）：tabbar 样式可参数化（tabbar_style，默认 Pivot_Grow——
    无底文字页签 + 选中底部 24px 强调色圆头短横线，切换时指示条自
    旧位置拉伸过渡至新位置），各页统一包在直角面板里（四角直角，
    面板顶边紧贴 tabbar）。colorstyle 选面板配色——PANE_COLORS_PAGE
    （同页卡，默认）或 PANE_COLORS_CARD（同内容卡 isCard）。
    addTab 自动包裹页 widget（懒加载页的 lazyfunction 属性随页迁移）。
    宿主一般再包一张内容卡（make_content_card）。"""

    def __init__(self, parent=None, tabbar_style=TABBAR_STYLE_PIVOT_GROW,
                 colorstyle=PANE_COLORS_PAGE):
        super().__init__(parent)
        self._colorstyle = colorstyle
        bar = self.tabBar()
        bar.setProperty("tabBarStyle", tabbar_style)
        # 无底文字页签：bar 无样式化底（drawBase 默认值经插件
        # PE_FrameTabBarBase 空实现不画任何东西）
        bar.setAttribute(Qt.WA_StyledBackground, False)
        bar.setDrawBase(True)
        # pane 清零：面板由页自带，插件 pane 内边距不叠加
        self.setStyleSheet(
            "QTabWidget::pane{border:0;margin:0;padding:0;}")

    def addTab(self, w, t):
        if self._colorstyle == 3:
            return LTabWidget.addTab(self, w, t)
        q = QWidget()
        v = QVBoxLayout(q)
        v.setContentsMargins(0, 0, 0, 0)
        pane = FluentSquarePane(colorstyle=self._colorstyle)
        v.addWidget(pane)
        inner = QVBoxLayout(pane)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.addWidget(w)
        if hasattr(w, "lazyfunction"):
            q.lazyfunction = w.lazyfunction
        return LTabWidget.addTab(self, q, t)


def make_content_card(w, margins=(16, 8, 16, 16)):
    """内容卡（isCard）包裹——Gallery propertiesCard 同款；
    margins 默认 (16, 8, 16, 16)：内容距卡左右 16、顶 8（bar 下移）、底 16。"""
    card = QWidget()
    card.setAttribute(Qt.WA_StyledBackground, True)
    card.setProperty("isCard", True)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(*margins)
    lay.addWidget(w)
    return card


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
    q.lazyfunction = functools.partial(getrealwidgetfunction, v)
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
        # 汉堡：导航窗格第一行（同游戏管理器共用组件；标题栏不放导航按钮）
        self.nav_toggle_button = FluentNavToggleButton(main_container)
        self.nav_toggle_button.setText(ICON_GLOBAL_NAV)
        self.nav_toggle_button.setToolTip("折叠/展开侧边栏")
        self.nav_toggle_button.clicked.connect(self.toggleNavigation)
        main_lay.addWidget(self.nav_toggle_button)
        self.nav = FluentNavTree(main_container)
        main_lay.addWidget(self.nav)

        # 分隔线：整宽、页卡描边色；仅导航溢出（可滚动）时显示
        self._nav_separator = FluentCardSeparator(nav_pane)
        self._nav_separator.followNavScroll(self.nav)

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
        # 插件给 QTabWidget pane 自带内边距（页卡四边被缩进 2-4px，
        # 右侧离窗口框架不贴）——置空 pane 边距，页卡与窗口边缘重合
        self.tab_widget.setStyleSheet(
            "QTabWidget::pane{border:0;margin:0;padding:0;}")

        lay.addWidget(nav_pane)
        lay.addWidget(self.tab_widget, 1)

        # 单一发射点：stack 变化 -> currentChanged（makesubtab_lazy 据此懒加载）
        self.nav.pageIndexChanged.connect(self.__nav_changed)
        self.nav_footer.pageIndexChanged.connect(self.__nav_changed)
        # 主导航展开/收起 -> 底部导航跟随（两棵树独立）
        self.nav.navigationExpandedChanged.connect(
            self.nav_footer.setNavigationExpanded)
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
        # 底部导航由 navigationExpandedChanged 信号跟随——这里再显式
        # toggle 会把它翻回去（信号先设一次，相对翻转会抵消）
        self.nav.toggleNavigationMode()

    def setNavigationExpanded(self, expanded, animated=True):
        """展开/收起侧边栏（主导航；底部导航经信号跟随）。"""
        self.nav.setNavigationExpanded(expanded, animated)

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
