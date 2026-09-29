"""FluentNavTree —— WinUI NavigationView 风格导航树。

移植自 FluentUIStyle/PyQt5Examples/exwidgets.py 的 ExNavTreeWidget
（对应 C++ ExWidgets/navigation/exnavtreewidget.cpp）：
- 紧凑(44px)/展开(200px)两种宽度 + 280ms OutCubic 动画
- navigationViewIndicator / navigationIconMode / ItemHeight 属性由
  FluentUI3 插件消费（选中指示条、图标模式等）
- 图标用 Segoe Fluent Icons 字形绘制（插件内嵌字体），随调色板/样式变化刷新
"""

from qtsymbols import (
    QAbstractItemView,
    QEvent,
    QEasingCurve,
    QFont,
    QFrame,
    QIcon,
    QHeaderView,
    QPainter,
    QPalette,
    QPixmap,
    QSize,
    Qt,
    QVariantAnimation,
    pyqtSignal,
    QTimer,
    QTreeWidget,
    QTreeWidgetItem,
)
from qtsymbols import QApplication

NAV_PAGE_ROLE = Qt.UserRole          # 页面索引
NAV_ICON_ROLE = Qt.UserRole + 1      # 图标码点
NAV_TEXT_ROLE = Qt.UserRole + 2      # 文本（紧凑模式下清空显示）
NAV_WAS_EXPANDED_ROLE = Qt.UserRole + 3


def create_fluent_icon(icon_code, color=None):
    """用 Segoe Fluent Icons 字体绘制 30x30 图标（插件构造时已注册内嵌字体）。"""
    pixmap = QPixmap(30, 30)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHints(
        QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform
    )
    font = QFont("Segoe Fluent Icons")
    font.setPixelSize(25)
    painter.setFont(font)
    if color is not None and color.isValid():
        pen_color = color
    else:
        is_dark = QApplication.instance().property("_q_colorscheme") == 1
        pen_color = Qt.white if is_dark else Qt.black
    painter.setPen(pen_color)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, icon_code)
    painter.end()
    return QIcon(pixmap)


class FluentNavTree(QTreeWidget):
    pageIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FluentNavTree")
        self._navigation_expanded = False
        self._navigation_compact_width = 44
        self._navigation_expanded_width = 200

        self.setAnimated(True)
        self.setIconSize(QSize(20, 20))
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setRootIsDecorated(False)

        self.viewport().setAutoFillBackground(False)
        self.viewport().setAttribute(Qt.WA_StyledBackground, False)
        self.setFrameShape(QFrame.NoFrame)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 构造期树高度未定（30px 默认），项添加后 range>0 会让滚动条
        # 进入可见态、首次显示时闪现一下再消失——首次布局完成前保持
        # 关闭，之后恢复按需显示
        self._vscroll_pending = True
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextElideMode(Qt.ElideRight)
        self.setProperty("navigationViewIndicator", True)
        self.setProperty("ItemHeight", 38)
        # Gallery 同款：子项缩进 20（插件 PM_TreeViewIndentation 默认 30，偏大）
        self.setIndentation(20)
        self.header().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setHeaderHidden(True)
        self.setColumnWidth(0, self._navigation_compact_width)
        self.setFixedWidth(self._navigation_compact_width)

        self._width_animation = QVariantAnimation(self)
        self._width_animation.setDuration(280)
        self._width_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._width_animation.valueChanged.connect(
            lambda value: self._update_navigation_view_by_width(int(value)))
        self._width_animation.finished.connect(self._on_width_animation_finished)

        self.currentItemChanged.connect(self._handle_item_selection)

    # ---- 滚动条 ----
    def showEvent(self, e):
        super().showEvent(e)
        if self._vscroll_pending:
            # 等本轮流式布局（树到达最终高度、range 归零）后再放开
            QTimer.singleShot(0, self._enable_vscroll_asneeded)

    def _enable_vscroll_asneeded(self):
        if not self.isVisible():
            return  # 已被隐藏：留待下次显示再试
        self._vscroll_pending = False
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # ---- 项管理 ----
    def addNavigationItem(self, text, page_index, icon_code="", auto_select=True):
        item = QTreeWidgetItem(self)
        self.configureNavigationItem(item, text, page_index, icon_code)
        if auto_select and self.topLevelItemCount() == 1 and self.currentItem() is None:
            self.setCurrentItem(item)
        return item

    def configureNavigationItem(self, item, text, page_index, icon_code=""):
        if item is None:
            return
        item.setData(0, NAV_PAGE_ROLE, page_index)
        item.setData(0, NAV_TEXT_ROLE, text)
        item.setData(0, NAV_ICON_ROLE, icon_code)
        item.setToolTip(0, text)
        self._update_navigation_item_icon(item)
        self._update_navigation_item_text(item, self._navigation_expanded)

    def _update_navigation_item_icon(self, item):
        if item is None:
            return
        icon_code = item.data(0, NAV_ICON_ROLE)
        if icon_code:
            item.setIcon(0, create_fluent_icon(icon_code, self.palette().color(QPalette.Text)))
        for i in range(item.childCount()):
            self._update_navigation_item_icon(item.child(i))

    def _update_navigation_item_text(self, item, expanded):
        if item is None:
            return
        item.setText(0, item.data(0, NAV_TEXT_ROLE) if expanded else "")
        for i in range(item.childCount()):
            self._update_navigation_item_text(item.child(i), expanded)

    def _update_navigation_item_expansion(self, item, show_text):
        if item is None:
            return
        if item.childCount() > 0:
            if not show_text:
                item.setData(0, NAV_WAS_EXPANDED_ROLE, item.isExpanded())
                item.setExpanded(False)
            else:
                was_expanded = item.data(0, NAV_WAS_EXPANDED_ROLE)
                item.setExpanded(was_expanded if was_expanded is not None else False)
                item.setData(0, NAV_WAS_EXPANDED_ROLE, None)
        for i in range(item.childCount()):
            self._update_navigation_item_expansion(item.child(i), show_text)

    def _update_navigation_item_visibility_for_depth(self, item, visible_depth, current_depth=0):
        if item is None:
            return
        item.setHidden(current_depth > visible_depth)
        for i in range(item.childCount()):
            self._update_navigation_item_visibility_for_depth(
                item.child(i), visible_depth, current_depth + 1)

    # ---- 展开 / 紧凑 ----
    def setNavigationExpanded(self, expanded, animated=True):
        self._navigation_expanded = expanded
        target_width = (self._navigation_expanded_width if expanded
                        else self._navigation_compact_width)
        if not animated:
            self._update_navigation_view_by_width(target_width)
            return
        current_width = self.width()
        if current_width == target_width:
            return
        self._width_animation.stop()
        self._width_animation.setStartValue(current_width)
        self._width_animation.setEndValue(target_width)
        self._width_animation.start()

    def navigationExpanded(self):
        return self._navigation_expanded

    def toggleNavigationMode(self):
        self.setNavigationExpanded(not self._navigation_expanded, True)

    def _on_width_animation_finished(self):
        target_width = (self._navigation_expanded_width if self._navigation_expanded
                        else self._navigation_compact_width)
        self._update_navigation_view_by_width(target_width)

    def _update_navigation_view_by_width(self, width):
        text_switch_width = self._navigation_compact_width + (
            self._navigation_expanded_width - self._navigation_compact_width) * 2 // 3
        show_text = width >= text_switch_width
        visible_depth = 2 ** 31 - 1 if show_text else 1

        old_icon_mode = self.property("navigationIconMode")
        will_be_icon_mode = not show_text
        mode_flipped = (bool(old_icon_mode) != will_be_icon_mode)

        self.setProperty("navigationIconMode", will_be_icon_mode)

        self.setUpdatesEnabled(False)
        self.setFixedWidth(width)

        scroll_bar_extent = self.style().pixelMetric(self.style().PM_ScrollBarExtent, None, self)
        frame_border_width = self.frameWidth() * 2
        safe_column_width = max(self._navigation_compact_width,
                                width - scroll_bar_extent - frame_border_width)
        self.setColumnWidth(0, safe_column_width)

        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            self._update_navigation_item_text(item, show_text)
            self._update_navigation_item_visibility_for_depth(item, visible_depth)
            if mode_flipped:
                self._update_navigation_item_expansion(item, show_text)

        self.setUpdatesEnabled(True)
        self.viewport().update()

    # ---- 事件 ----
    def _handle_item_selection(self, current, _previous):
        if current is None:
            return
        page_data = current.data(0, NAV_PAGE_ROLE)
        if page_data is None:
            return
        self.pageIndexChanged.emit(int(page_data))

    def changeEvent(self, event):
        super().changeEvent(event)
        if event is None:
            return
        if event.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange,
                            QEvent.StyleChange):
            for i in range(self.topLevelItemCount()):
                self._update_navigation_item_icon(self.topLevelItem(i))

    def mousePressEvent(self, event):
        pos = event.pos()
        index = self.indexAt(pos)
        # 有子项的父项：单击整行 = 选中（切到该页）并展开。仅当已经处于
        # 此项时，再次单击才折叠（从别的项切过来不关）；图标模式子项
        # 隐藏，父项仅作为普通项选中
        if (index.isValid() and self.model().hasChildren(index)
                and not self.property("navigationIconMode")):
            is_current = (self.currentIndex() == index)
            self.setCurrentIndex(index)
            if is_current:
                if self.isExpanded(index):
                    self.collapse(index)
                else:
                    self.expand(index)
            else:
                self.expand(index)
            event.accept()
            return
        self.setCurrentIndex(index)
        super().mousePressEvent(event)
