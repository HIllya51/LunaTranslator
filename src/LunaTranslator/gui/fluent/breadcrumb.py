"""ExBreadcrumbBar —— WinUI 3 BreadcrumbBar 风格面包屑。

移植自 FluentUIStyle/ExWidgets/navigation/exbreadcrumbbar.cpp：
- 路径项为 QToolButton 自绘（Subtle 悬停/按下微底色、当前项加粗主色、
  祖先项次级文字色 72% alpha）
- 分隔符为 Segoe Fluent Icons 的 Chevron（65% alpha，paintEvent 绘制）
- 宽度不足时从末尾保留项，前置溢出按钮 "…" + 菜单（最近父级在最上）
- 键盘：左右方向/Home/End/Enter
- 路径由调用方维护，点击只发 itemClicked(index, item)，不自动截断
"""

from qtsymbols import (
    QColor,
    QEvent,
    QFont,
    QFontMetrics,
    QHBoxLayout,
    QMenu,
    QPainter,
    QPalette,
    QRect,
    QRectF,
    QSize,
    QSizePolicy,
    Qt,
    QToolButton,
    QWidget,
    QStyle,
    QStyleOptionFocusRect,
    pyqtSignal,
    QApplication,
)

# WinUI 3 BreadcrumbBarChevronFontSize=12，Chevron 区域宽度 16px
_SEPARATOR_WIDTH = 16
_ITEM_HORIZONTAL_PADDING = 8
_ITEM_HEIGHT = 28
_ITEM_CORNER_RADIUS = 4.0

_ICON_CHEVRON_RIGHT = "\ue76c"   # ChevronRight
_ICON_CHEVRON_LEFT = "\ue76b"    # ChevronLeft


def _is_dark_palette(palette):
    return palette.color(QPalette.Window).lightness() < 128


class _BreadcrumbButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.is_overflow = False
        self.drop_down = False

    @property
    def _current(self):
        # 由 bar 在重建时按 objectName 标记：当前项 = 路径最后一项
        return self.property("bcCurrent")

    def sizeHint(self):
        font = self.font()
        if self._current:
            font.setBold(True)
        fm = QFontMetrics(font)
        text_w = fm.horizontalAdvance(self.text())
        w = text_w + _ITEM_HORIZONTAL_PADDING * 2
        h = max(_ITEM_HEIGHT, fm.height() + 8)
        return QSize(w, h)

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        is_dark = _is_dark_palette(self.palette())
        current = bool(self._current)
        interactive = (not current) or self.is_overflow or self.drop_down

        # 1. WinUI 3 Subtle 悬停/按下微底色（当前项不绘制背景）
        if interactive and (self.underMouse() or self.isDown()):
            if self.isDown():
                hover = QColor(255, 255, 255, 24) if is_dark else QColor(0, 0, 0, 24)
            else:
                hover = QColor(255, 255, 255, 18) if is_dark else QColor(0, 0, 0, 15)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
                _ITEM_CORNER_RADIUS, _ITEM_CORNER_RADIUS,
            )

        # 2. 标准分级文字
        text_font = self.font()
        if current:
            text_font.setBold(True)
        painter.setFont(text_font)
        fm = QFontMetrics(text_font)
        text_color = self.palette().color(
            QPalette.Active if self.isEnabled() else QPalette.Disabled,
            QPalette.WindowText,
        )
        if self.isEnabled() and not current and not self.underMouse():
            # 常规祖先项：次级文字色（约 72% alpha）
            text_color.setAlphaF(text_color.alphaF() * 0.72)
        text_rect = self.rect().adjusted(
            _ITEM_HORIZONTAL_PADDING, 0, -_ITEM_HORIZONTAL_PADDING, 0)
        painter.setPen(text_color)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeading
            | Qt.TextFlag.TextSingleLine,
            fm.elidedText(self.text(), Qt.TextElideMode.ElideRight,
                          max(0, text_rect.width())),
        )
        # 键盘焦点框
        if self.hasFocus():
            focus = QStyleOptionFocusRect()
            focus.initFrom(self)
            focus.rect = self.rect().adjusted(1, 1, -1, -1)
            self.style().drawPrimitive(
                QStyle.PrimitiveElement.PE_FrameFocusRect, focus, painter, self)



class ExBreadcrumbBar(QWidget):
    """WinUI 3 面包屑。路径由调用方维护；点击祖先项发 itemClicked。"""

    itemClicked = pyqtSignal(int, object)  # index, item(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont(self.font())
        font.setPixelSize(14)
        self.setFont(font)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._items = []
        self._buttons = []
        self._separators = []
        self._first_visible = -1

        self._overflow_button = _BreadcrumbButton(self)
        self._overflow_button.is_overflow = True
        self._overflow_button.setText("…")
        self._overflow_button.setToolTip("显示折叠的路径")
        self._overflow_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        self._overflow_menu = QMenu(self._overflow_button)
        self._overflow_button.setMenu(self._overflow_menu)
        self._overflow_button.hide()

    # ---- API ----
    def setItemsSource(self, items):
        if list(items) == self._items:
            return
        self._items = list(items)
        self._rebuild_items()

    def itemsSource(self):
        return list(self._items)

    def setItems(self, items):
        self.setItemsSource(list(items))

    def sizeHint(self):
        w = 0
        h = max(32, QFontMetrics(self.font()).height() + 10)
        for button in self._buttons:
            w += button.sizeHint().width()
            h = max(h, button.sizeHint().height())
        sep_count = max(0, len(self._buttons) - 1)
        return QSize(w + sep_count * _SEPARATOR_WIDTH, h)

    def minimumSizeHint(self):
        if not self._items:
            return QSize(0, self.sizeHint().height())
        if len(self._items) == 1:
            return QSize(16, self.sizeHint().height())
        return QSize(56, self.sizeHint().height())

    # ---- 事件 ----
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._layout_items()

    def changeEvent(self, event):
        super().changeEvent(event)
        if not hasattr(self, "_buttons"):
            return  # __init__ 中 setFont 会提前触发 FontChange
        if event.type() in (
            QEvent.Type.FontChange,
            QEvent.Type.StyleChange,
            QEvent.Type.LayoutDirectionChange,
            QEvent.Type.PaletteChange,
        ):
            self._layout_items()
            self.updateGeometry()
            self.update()

    def paintEvent(self, _):
        if not self._separators:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        chevron_font = QFont("Segoe Fluent Icons")
        chevron_font.setPixelSize(13)
        painter.setFont(chevron_font)
        chevron_color = self.palette().color(
            QPalette.Active if self.isEnabled() else QPalette.Disabled,
            QPalette.WindowText,
        )
        chevron_color.setAlphaF(chevron_color.alphaF() * 0.65)
        painter.setPen(chevron_color)
        glyph = (
            _ICON_CHEVRON_LEFT if self.isRightToLeft()
            else _ICON_CHEVRON_RIGHT
        )
        for sep_rect in self._separators:
            painter.drawText(sep_rect, Qt.AlignmentFlag.AlignCenter, glyph)

    # ---- 内部 ----
    def _rebuild_items(self):
        focused = QApplication.focusWidget()
        had_focus = focused is not None and (
            focused is self or self.isAncestorOf(focused))

        self._overflow_menu.hide()
        self._overflow_menu.clear()
        for button in self._buttons:
            button.hide()
            button.deleteLater()
        self._buttons = []

        count = len(self._items)
        for i in range(count):
            text = str(self._items[i])
            button = _BreadcrumbButton(self)
            button.setProperty("bcCurrent", i == count - 1)
            button.setText(text)
            button.setToolTip(text)
            # 最后一项是只读的当前位置标识；祖先项可点击
            if i != count - 1:
                button.clicked.connect(
                    lambda _=False, idx=i: self._activate_item(idx))
            self._buttons.append(button)

        self._first_visible = -1
        self._layout_items()
        if had_focus and self._buttons:
            self._buttons[-1].setFocus(Qt.FocusReason.OtherFocusReason)
        self.updateGeometry()

    def _activate_item(self, index):
        if 0 <= index < len(self._items):
            self.itemClicked.emit(index, self._items[index])

    def _layout_items(self):
        self._separators = []
        count = len(self._buttons)
        if count == 0:
            self._overflow_button.hide()
            return
        available = max(0, self.contentsRect().width())
        overflow_width = max(28, self._overflow_button.sizeHint().width())

        # WinUI 3 BreadcrumbLayout：从末尾向前保留可完整容纳的项目
        first = 0
        if count > 1 and self.sizeHint().width() > available:
            first = count - 1
            used = (overflow_width + _SEPARATOR_WIDTH
                    + self._buttons[-1].sizeHint().width())
            while (first > 1
                   and used + _SEPARATOR_WIDTH
                   + self._buttons[first - 1].sizeHint().width() <= available):
                first -= 1
                used += _SEPARATOR_WIDTH + self._buttons[first].sizeHint().width()

        if first != self._first_visible:
            self._overflow_menu.hide()
            for act in self._overflow_menu.actions():
                self._overflow_menu.removeAction(act)
            # 溢出菜单：最近的父级在最上方
            for i in range(first - 1, -1, -1):
                text = str(self._items[i]).replace("&", "&&")
                act = self._overflow_menu.addAction(text)
                act.triggered.connect(
                    lambda _=False, idx=i: self._activate_item(idx))
            self._first_visible = first

        overflow = first > 0
        self._overflow_button.setVisible(overflow)

        x = self.contentsRect().left()
        h = min(self.contentsRect().height(), self.sizeHint().height())
        y = self.contentsRect().top() + (self.contentsRect().height() - h) // 2

        def place(widget, left, w):
            # visualRect：RTL 时自动镜像到右端（同 C++ ExBreadcrumbBar）
            widget.setGeometry(QStyle.visualRect(
                self.layoutDirection(), self.contentsRect(),
                QRect(left, y, max(0, w), h)))

        if overflow:
            place(self._overflow_button, x, min(available, overflow_width))
            x += overflow_width
            self._separators.append(QStyle.visualRect(
                self.layoutDirection(), self.contentsRect(),
                QRect(x, y, _SEPARATOR_WIDTH, h)))
            x += _SEPARATOR_WIDTH

        for i in range(count):
            button = self._buttons[i]
            button.setVisible(i >= first)
            if i < first:
                continue
            if i > first:
                self._separators.append(QStyle.visualRect(
                    self.layoutDirection(), self.contentsRect(),
                    QRect(x, y, _SEPARATOR_WIDTH, h)))
                x += _SEPARATOR_WIDTH
            w = min(button.sizeHint().width(),
                    max(0, self.contentsRect().right() + 1 - x))
            place(button, x, w)
            x += w
        self.update()
