"""FluentNavTree —— WinUI NavigationView 风格导航树。

移植自 FluentUIStyle/PyQt5Examples/exwidgets.py 的 ExNavTreeWidget
（对应 C++ ExWidgets/navigation/exnavtreewidget.cpp）：
- 紧凑(30px)/展开(200px)两种宽度 + 280ms OutCubic 动画
- navigationViewIndicator / navigationIconMode / ItemHeight 属性由
  FluentUI3 插件消费（选中指示条、图标模式等）
- 图标用 Segoe Fluent Icons 字形绘制（插件内嵌字体），随调色板/样式变化刷新
"""

from qtsymbols import (
    QAbstractItemView,
    QColor,
    QEvent,
    QEasingCurve,
    QFont,
    QFrame,
    QIcon,
    QHeaderView,
    QPainter,
    QPalette,
    QPixmap,
    QRect,
    QRectF,
    QSize,
    Qt,
    QToolButton,
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

# 折叠（图标模式）宽度：图标的绘制区是贴格左缘的 30px 画布（原生尺寸），
# 格宽 30 时图标恰好居中（ink 中心≈14 vs 格中心 15）；汉堡按钮同宽对齐
NAV_COMPACT_WIDTH = 38


def create_fluent_icon(icon_code, color=None, size=30, glyph=None):
    """用 Segoe Fluent Icons 字形绘制图标（插件构造时已注册内嵌字体）。
    glyph=字形像素字号，缺省 25（导航图标惯例）；Gallery 标题栏搜索图标
    用 glyph=size（exwidgets._search_icon 同款：32x32 画布 32px 字形）。"""
    if glyph is None:
        glyph = 25
    pixmap = QPixmap(size, size)
    pixmap.setDevicePixelRatio(1)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHints(
        QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform
    )
    font = QFont("Segoe Fluent Icons")
    font.setPixelSize(glyph)
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


class FluentNavToggleButton(QToolButton):
    """导航窗格的折叠/展开汉堡（游戏管理与设置窗口共用）。

    与导航项（尤其折叠态）同款渲染，而不是 caption 按钮样式——插件对
    win_caption_* 的悬停画的是无圆角全幅矩形（fluentui3style.cpp
    PE_Widget 分支末尾 drawRect），与导航项的 subtle 圆角填充不一致：
    - 悬停/按下：2px 内缩 + 4px 圆角的 subtle 填充
      （winUI3Colors：浅色=黑 4%/5.5% alpha，深色=白 6.05%/4.19%）
    - 图标：16px 字形（WinUI NavigationView 的窗格切换钮规格）在按钮内
      居中——按钮宽 = 折叠宽度 NAV_COMPACT_WIDTH，与导航项图标列对齐"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        _f = QFont("Segoe Fluent Icons")
        _f.setPixelSize(16)
        self.setFont(_f)
        self.setFixedSize(NAV_COMPACT_WIDTH, 38)

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dark = False
        app = QApplication.instance()
        if app is not None:
            cs = app.property("_q_colorscheme")
            if cs is not None:
                try:
                    dark = int(cs) == 1
                except Exception:
                    dark = self.palette().color(
                        QPalette.Active, QPalette.Window).lightness() < 128
        fill = None
        if self.isDown():
            # subtlePressed：浅=黑 5.5% (alpha 14)，深=白 4.19% (alpha 11)
            fill = QColor(255, 255, 255, 11) if dark else QColor(0, 0, 0, 14)
        elif self.underMouse():
            # subtleHighlight：浅=黑 4% (alpha 10)，深=白 6.05% (alpha 15)
            fill = QColor(255, 255, 255, 15) if dark else QColor(0, 0, 0, 10)
        if fill is not None:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(fill)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(2, 2, -2, -2), 4, 4)
        painter.setFont(self.font())
        painter.setPen(self.palette().color(QPalette.Active, QPalette.Text))
        painter.drawText(QRect(0, 0, self.width(), self.height()),
                         Qt.AlignmentFlag.AlignCenter, self.text())


class FluentNavTree(QTreeWidget):
    pageIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FluentNavTree")
        self._navigation_expanded = False
        self._navigation_compact_width = NAV_COMPACT_WIDTH
        self._navigation_expanded_width = 200
        self._restorable_child = None
        self._in_mode_update = False  # 模式切换内部处理中（不触发联动）
        # 双击才展开/折叠父项（单击只选中）；默认关闭=单击选中并展开
        self._expand_on_doubleclick = False

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
        # 折叠模式下任何形式展开/选中子项 -> 自动展开侧边栏
        self.itemExpanded.connect(self._on_item_expanded)

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
        # 新状态优先：终止进行中的过渡（animation.start() 会同步投递一次
        # 起始值的 valueChanged，残留的旧动画会与新状态竞态）
        self._width_animation.stop()
        target_width = (self._navigation_expanded_width if expanded
                        else self._navigation_compact_width)
        if not animated:
            self._update_navigation_view_by_width(target_width)
            return
        current_width = self.width()
        if current_width == target_width:
            return
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
        if mode_flipped:
            # 同 Gallery：选中子项时收起——把选中（指示条）提升到顶层
            # 祖先（图标模式只有顶层可见，指示条跟随选中项）；展开时恢复
            if will_be_icon_mode:
                current = self.currentItem()
                if current is not None and current.parent() is not None:
                    top_level = current
                    while top_level.parent() is not None:
                        top_level = top_level.parent()
                    # 保存真实子节点，恢复展开模式时重新选中。
                    # 程序性提升不通知宿主（避免收起侧栏时宿主切页/加载数据）
                    self._restorable_child = current
                    self.blockSignals(True)
                    self.setCurrentItem(top_level)
                    self.blockSignals(False)
            else:
                current = self.currentItem()
                if current is not None and current.parent() is None:
                    saved_child = self._restorable_child
                    if saved_child is not None:
                        self.setCurrentItem(saved_child)
                        self._restorable_child = None

        self.setProperty("navigationIconMode", will_be_icon_mode)

        # 模式切换自身的展开/收起（保存态恢复）不应再触发"展开侧边栏"联动
        self._in_mode_update = True
        try:
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
        finally:
            self._in_mode_update = False

        self.setUpdatesEnabled(True)
        self.viewport().update()

    # ---- 事件 ----
    def _handle_item_selection(self, current, _previous):
        if current is not None and current.parent() is not None:
            self._reveal_child(current)
        if current is None:
            return
        page_data = current.data(0, NAV_PAGE_ROLE)
        if page_data is None:
            return
        self.pageIndexChanged.emit(int(page_data))

    # ---- 子项可见性联动 ----
    def _on_item_expanded(self, item):
        """折叠（图标）模式下任何分组被展开：图标模式子项不可见，保持
        折叠会表现为"展开丢失"——记录展开态（退出图标模式时保持）并
        自动展开侧边栏。构造期建树（恢复保存的展开态）不触发。"""
        if item is None or self._navigation_expanded:
            return
        if self._in_mode_update or not self.isVisible():
            return
        item.setData(0, NAV_WAS_EXPANDED_ROLE, True)
        self.setNavigationExpanded(True)

    def _reveal_child(self, item):
        """子项被（程序性）选中：展开其祖先链；若侧边栏处于折叠模式
        则一并展开——否则选中落在不可见的子项上（指示条消失）。"""
        p = item.parent()
        while p is not None:
            p.setExpanded(True)  # 图标模式下经 _on_item_expanded 记录并展开侧边栏
            p = p.parent()
        if not self._navigation_expanded and self.isVisible():
            self.setNavigationExpanded(True)

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
            if self._expand_on_doubleclick:
                # 双击展开模式：单击仅选中（展开/折叠交给 mouseDoubleClickEvent）
                self.setCurrentIndex(index)
                event.accept()
                return
            # 已处于此项（父项或其子项被选中）时再点 -> 折叠
            cur = self.currentIndex()
            is_current = (cur == index) or (
                cur.isValid() and cur.parent() == index
            )
            # 首子项复用父项页面（同 page_index）时，选中焦点跳到首子项
            # ——否则页面显示的是首子页、焦点却停在父项上
            target = index
            child = index.child(0, 0)
            if (
                child.isValid()
                and child.data(NAV_PAGE_ROLE) is not None
                and child.data(NAV_PAGE_ROLE) == index.data(NAV_PAGE_ROLE)
            ):
                target = child
            self.setCurrentIndex(target)
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
