"""FluentTabWidget —— 设置页导航容器（WinUI NavigationView 版）。

替换 gui/setting/setting.py 的 TabWidget（LListWidget + 隐藏 tabBar 的 QTabWidget）：
左侧 FluentNavTree（图标 + 文字，可 44/200 收展）+ 右侧 QTabWidget（tabBar 隐藏）。
兼容 makesubtab_lazy / tabadd_lazy / about.py 动态加页 / setCurrentIndex /
currentChanged / updatelangtext 的全部调用面。
"""

from qtsymbols import (
    QEvent,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)

from gui.fluent.nav import FluentNavTree, NAV_ICON_ROLE

# 8 个一级分类的 Segoe Fluent Icons 码点（兜底 E9D2）
NAV_ICONS = ["\ue713", "\ue8c1", "\ue7f3", "\ue9f5", "\ue82d", "\ue8d6", "\ue765", "\ue946"]
NAV_ICON_FALLBACK = "\ue9d2"


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
        self.nav = FluentNavTree(nav_pane)
        nav_lay.addWidget(self.nav)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.tabBar().hide()

        lay.addWidget(nav_pane)
        lay.addWidget(self.tab_widget, 1)

        # 单一发射点：stack 变化 -> currentChanged（makesubtab_lazy 据此懒加载）
        self.nav.pageIndexChanged.connect(self.__nav_changed)
        self.tab_widget.currentChanged.connect(self.__stack_changed)

        # 默认展开（同 Win11 设置）；可用标题栏汉堡收起
        self.nav.setNavigationExpanded(True, animated=False)

    # ---- TabWidget 兼容面 ----
    def addTab(self, widget, title):
        self.__titles.append(title)
        from myutils.config import _TR

        self.tab_widget.addTab(widget, _TR(title))
        idx = self.tab_widget.count() - 1
        icon = (NAV_ICONS[idx] if idx < len(NAV_ICONS) else NAV_ICON_FALLBACK)
        self.nav.addNavigationItem(_TR(title), idx, icon)

    def setCurrentIndex(self, idx):
        if idx < 0 or idx >= self.tab_widget.count():
            return
        item = self.nav.topLevelItem(idx)
        if item is not None and self.nav.currentItem() is not item:
            self.nav.setCurrentItem(item)  # -> pageIndexChanged -> __nav_changed
        elif self.tab_widget.currentIndex() != idx:
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

    def navigationExpanded(self):
        return self.nav.navigationExpanded()

    # ---- 语言切换 ----
    def updatelangtext(self):
        from myutils.config import _TR

        for i, title in enumerate(self.__titles):
            self.tab_widget.setTabText(i, _TR(title))
            item = self.nav.topLevelItem(i)
            if item is not None:
                self.nav.configureNavigationItem(
                    item, _TR(title), i, item.data(0, NAV_ICON_ROLE))

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
