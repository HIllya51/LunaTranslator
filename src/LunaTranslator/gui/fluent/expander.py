"""ExExpander —— FluentUI 折叠面板（Gallery exwidgets.py 的 ExExpander 移植）。
连续卡片外观：Header 与 Content 组成一张完整的圆角卡片，
chevron 按钮随展开进度旋转 180°。"""

from gui.fluent.icons import ICON_CHEVRON_DOWN_MED

from qtsymbols import (
    QAbstractSpinBox,
    QComboBox,
    QObject,
    QEvent,
    QEasingCurve,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
    pyqtSignal,
    QApplication,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QAbstractButton,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Segoe Fluent Icons 码点


# 设计常量（同 exexpander.cpp 匿名命名空间）
_EXP_CORNER_RADIUS = 4
_EXPANDER_MIN_WIDTH = 96
_EXP_HEADER_MIN_HEIGHT = 48
_EXP_HEADER_CONTENT_PADDING = 16
_EXP_CONTENT_PADDING = 16
_EXP_CHEVRON_CONTENT_SPACING = 20
_EXP_CHEVRON_TRAILING_MARGIN = 8
_EXP_CHEVRON_BUTTON_SIZE = 32
# 内容面板右侧让位（chevron_side 60 - 面板边距 16），使内容右缘与折叠条控件对齐
_EXP_CONTENT_CHEVRON_RESERVE = 44


def _exp_is_dark_palette(palette):
    app = QApplication.instance()
    if app is not None:
        color_scheme = app.property("_q_colorscheme")
        if color_scheme is not None:
            return int(color_scheme) == 1
    return palette.color(QPalette.Window).lightness() < 128


def _exp_card_background(palette):
    """winUI3CardBackgroundColor 的等价实现（普通模式预合成到不透明）。"""
    dark = _exp_is_dark_palette(palette)
    wallpaper_mode = False
    app = QApplication.instance()
    if app is not None:
        mode = app.property("_q_widget_mode")
        wallpaper_mode = mode is not None and int(mode) >= 1

    base = QColor(palette.color(QPalette.Base))
    if base.alpha() == 0:
        base = QColor(palette.color(QPalette.Window))
    if base.alpha() == 0:
        base = QColor(0x1E, 0x1E, 0x1E) if dark else QColor(0xFF, 0xFF, 0xFF)

    card = QColor(255, 255, 255, 13) if dark else QColor(255, 255, 255, 179)
    if card.alpha() == 255:
        return QColor(card)

    alpha = card.alphaF()
    result = QColor(round(base.red() * (1.0 - alpha) + card.red() * alpha),
                    round(base.green() * (1.0 - alpha) + card.green() * alpha),
                    round(base.blue() * (1.0 - alpha) + card.blue() * alpha))
    if wallpaper_mode:
        result.setAlpha(max(72 if dark else 92, min(160, base.alpha())))
    return result


def _exp_card_border(palette):
    # cardStrokeColorBalanced
    return QColor(0x25, 0x25, 0x25) if _exp_is_dark_palette(palette) else QColor(0xE9, 0xE9, 0xE9)


def _exp_chevron_button_background(palette, is_down):
    # subtlePressedColor / subtleHighlightColor
    if _exp_is_dark_palette(palette):
        return QColor(255, 255, 255, 11) if is_down else QColor(255, 255, 255, 15)
    return QColor(0, 0, 0, 14) if is_down else QColor(0, 0, 0, 10)


def _exp_rounded_panel_path(rect, round_top_left, round_top_right, round_bottom_right, round_bottom_left):
    from PyQt5.QtGui import QPainterPath

    radius = min(float(_EXP_CORNER_RADIUS), min(rect.width(), rect.height()) * 0.5)
    path = QPainterPath()
    path.moveTo(rect.left() + (radius if round_top_left else 0.0), rect.top())
    path.lineTo(rect.right() - (radius if round_top_right else 0.0), rect.top())
    if round_top_right:
        path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius)
    else:
        path.lineTo(rect.right(), rect.top())
    path.lineTo(rect.right(), rect.bottom() - (radius if round_bottom_right else 0.0))
    if round_bottom_right:
        path.quadTo(rect.right(), rect.bottom(), rect.right() - radius, rect.bottom())
    else:
        path.lineTo(rect.right(), rect.bottom())
    path.lineTo(rect.left() + (radius if round_bottom_left else 0.0), rect.bottom())
    if round_bottom_left:
        path.quadTo(rect.left(), rect.bottom(), rect.left(), rect.bottom() - radius)
    else:
        path.lineTo(rect.left(), rect.bottom())
    path.lineTo(rect.left(), rect.top() + (radius if round_top_left else 0.0))
    if round_top_left:
        path.quadTo(rect.left(), rect.top(), rect.left() + radius, rect.top())
    else:
        path.lineTo(rect.left(), rect.top())
    path.closeSubpath()
    return path


class _ExpanderContentPanel(QWidget):
    """Content 面板：与 Header 组成连续容器，只有最远端保留外圆角。"""

    def __init__(self, expander, content, pad_right=False):
        super().__init__(expander)
        self._expander = expander
        self._outer_edge = False
        self.setMinimumHeight(_EXP_HEADER_MIN_HEIGHT)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            _EXP_CONTENT_PADDING, _EXP_CONTENT_PADDING,
            _EXP_CONTENT_PADDING + (_EXP_CONTENT_CHEVRON_RESERVE if pad_right else 0),
            _EXP_CONTENT_PADDING)
        layout.setSpacing(0)
        content.setParent(self)
        layout.addWidget(content)
        content.show()

    def setOuterEdge(self, outer_edge):
        if self._outer_edge == outer_edge:
            return
        self._outer_edge = outer_edge
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bounds = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        # 本移植仅支持向下展开（Down）：上边开放，下边在最外层面板时保留圆角
        fill_path = _exp_rounded_panel_path(bounds, False, False,
                                            self._outer_edge, self._outer_edge)
        painter.fillPath(fill_path, _exp_card_background(self.palette()))

        # 只绘制左右边与远离 Header 的横边（该横边同时是分隔线）
        border_path = QPainterPath()
        border_path.moveTo(bounds.left(), bounds.top())
        border_path.lineTo(bounds.left(),
                           bounds.bottom() - (_EXP_CORNER_RADIUS if self._outer_edge else 0))
        if self._outer_edge:
            border_path.quadTo(bounds.left(), bounds.bottom(),
                               bounds.left() + _EXP_CORNER_RADIUS, bounds.bottom())
        else:
            border_path.lineTo(bounds.left(), bounds.bottom())
        border_path.lineTo(bounds.right() - (_EXP_CORNER_RADIUS if self._outer_edge else 0),
                           bounds.bottom())
        if self._outer_edge:
            border_path.quadTo(bounds.right(), bounds.bottom(),
                               bounds.right(), bounds.bottom() - _EXP_CORNER_RADIUS)
        else:
            border_path.lineTo(bounds.right(), bounds.bottom())
        border_path.lineTo(bounds.right(), bounds.top())
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(_exp_card_border(self.palette()), 1.0))
        painter.drawPath(border_path)


class _ExpanderContentStack(QWidget):
    def __init__(self, expander):
        super().__init__(expander)
        self.setMinimumWidth(_EXPANDER_MIN_WIDTH)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


class _ExpanderContentViewport(QWidget):
    """外层视口：展开时一次性占满高度，动画只改变内部裁剪窗口。"""

    def __init__(self, expander, panel):
        super().__init__(expander)
        self._expander = expander
        self._clip_viewport = QWidget(self)
        self._panel = panel
        self.setMinimumWidth(_EXPANDER_MIN_WIDTH)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        panel.setParent(self._clip_viewport)
        panel.installEventFilter(self)
        self._clip_viewport.show()
        panel.show()
        self._full_height = 0
        self._viewport_progress = 0.0

    def prepareAnimation(self):
        self._set_full_height(self._full_panel_height())
        self._update_panel_geometry()

    def setViewportProgress(self, progress):
        self._viewport_progress = max(0.0, min(1.0, progress))
        self._update_layout_height()
        self._update_panel_geometry()

    def sizeHint(self):
        result = self._panel.sizeHint().expandedTo(QSize(_EXPANDER_MIN_WIDTH, 0))
        result.setHeight(self._layout_height())
        return result

    def minimumSizeHint(self):
        return QSize(_EXPANDER_MIN_WIDTH, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize().width() != event.size().width():
            self._set_full_height(self._full_panel_height())
        self._update_panel_geometry()

    def eventFilter(self, watched, event):
        if (watched is self._panel and event.type() == QEvent.LayoutRequest
                and self._expander._expansion_animation.state() != QVariantAnimation.Running):
            self.prepareAnimation()
        return super().eventFilter(watched, event)

    def _layout_height(self):
        if self._expander.isExpanded():
            return self._full_height
        return round(self._full_height * self._viewport_progress)

    def _set_full_height(self, height):
        height = max(0, height)
        if self._full_height == height:
            # expanded 状态可能刚切换，布局高度计算方式已变
            self._update_layout_height()
            return
        self._full_height = height
        self._update_layout_height()

    def _update_layout_height(self):
        height = self._layout_height()
        if self.maximumHeight() == height:
            return
        # min 与 max 同步：否则父布局（如滚动区里空间不足的 QGridLayout）
        # 会把 Maximum 垂直策略的折叠卡压缩到只剩头部
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)
        self.updateGeometry()
        self._expander._root_layout.invalidate()
        self._expander.updateGeometry()

    def _full_panel_height(self):
        return max(0, self._panel.sizeHint().height())

    def _update_panel_geometry(self):
        visible_height = round(self._full_height * self._viewport_progress)
        clip_geometry = QRect(0, 0, self.width(), visible_height)
        if self._clip_viewport.geometry() != clip_geometry:
            self._clip_viewport.setGeometry(clip_geometry)
        panel_geometry = QRect(0, 0, self.width(), self._full_height)
        if self._panel.geometry() != panel_geometry:
            self._panel.setGeometry(panel_geometry)


class _ExpanderHeaderButton(QAbstractButton):
    def __init__(self, expander):
        super().__init__(expander)
        self._expander = expander
        self._progress = 0.0
        self._header_widget = None
        self.setCheckable(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(_EXPANDER_MIN_WIDTH, _EXP_HEADER_MIN_HEIGHT)
        # Header 只采用自身内容高度，不参与 Content 的展开/收起动画
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_Hover, True)

        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(0)
        self._update_layout_margins()

        self._label = QLabel(self)
        # 同 makecardrow 卡片标题 15px：不设显式字体时继承应用字体(13px)，
        # 会与普通卡标题不一致
        labelfont = self._label.font()
        labelfont.setPixelSize(15)
        self._label.setFont(labelfont)
        self._label.setWordWrap(True)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._layout.addWidget(self._label, 1)

    def setHeader(self, text):
        self._label.setText(text)
        self._label.setVisible(self._header_widget is None and bool(text))
        self.updateGeometry()

    def setHeaderWidget(self, widget):
        if self._header_widget is widget:
            self._label.setVisible(widget is None and bool(self._label.text()))
            return
        if self._header_widget is not None:
            self._layout.removeWidget(self._header_widget)
            self._header_widget.setParent(None)
        self._header_widget = widget
        if widget is not None:
            widget.setParent(self)
            self._layout.addWidget(widget, 1)
            widget.show()
        self._label.setVisible(widget is None and bool(self._label.text()))
        self.updateGeometry()

    def takeHeaderWidget(self):
        widget = self._header_widget
        if widget is not None:
            self._layout.removeWidget(widget)
            widget.setParent(None)
            self._header_widget = None
            self._label.setVisible(bool(self._label.text()))
            self.updateGeometry()
        return widget

    def headerWidgetDestroyed(self):
        self._header_widget = None
        self._label.setVisible(bool(self._label.text()))
        self.updateGeometry()

    def setExpansionProgress(self, progress):
        self._progress = max(0.0, min(1.0, progress))
        self.update()

    def event(self, event):
        result = super().event(event)
        if event.type() in (QEvent.Enter, QEvent.Leave, QEvent.HoverEnter, QEvent.HoverLeave,
                            QEvent.EnabledChange, QEvent.LayoutDirectionChange):
            if event.type() == QEvent.LayoutDirectionChange:
                self._update_layout_margins()
            self.update()
        return result

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainterPath
        from PyQt5.QtWidgets import QStyle, QStyleOptionFocusRect

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        connected = self._expander.isExpanded() and self._expander.hasContentWidgets()
        # 向下展开：顶部圆角；底部在未连接内容时保留圆角
        bounds = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        header_path = _exp_rounded_panel_path(bounds, True, True, not connected, not connected)
        painter.fillPath(header_path, _exp_card_background(self.palette()))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(_exp_card_border(self.palette()), 1.0))
        painter.drawPath(header_path)

        # chevron 按钮区（悬停/按下时 subtle 高亮）与折叠箭头——仅可折叠时
        # 绘制；无内容时折叠卡退化为普通卡（setFoldable(False)）
        if self._expander._foldable:
            rtl = self.layoutDirection() == Qt.RightToLeft
            chevron_x = (_EXP_CHEVRON_TRAILING_MARGIN if rtl
                         else self.width() - _EXP_CHEVRON_TRAILING_MARGIN - _EXP_CHEVRON_BUTTON_SIZE)
            chevron_rect = QRectF(chevron_x, (self.height() - _EXP_CHEVRON_BUTTON_SIZE) * 0.5,
                                  _EXP_CHEVRON_BUTTON_SIZE, _EXP_CHEVRON_BUTTON_SIZE)
            if self.isEnabled() and (self.underMouse() or self.isDown()):
                painter.setPen(Qt.NoPen)
                painter.setBrush(_exp_chevron_button_background(self.palette(), self.isDown()))
                painter.drawRoundedRect(chevron_rect, _EXP_CORNER_RADIUS, _EXP_CORNER_RADIUS)

            # chevron 图标随展开进度旋转 180°
            angle = 180.0 * self._progress
            painter.save()
            painter.translate(chevron_rect.center())
            painter.rotate(angle)
            painter.setPen(self.palette().color(
                QPalette.Active if self.isEnabled() else QPalette.Disabled, QPalette.Text))
            icon_font = QFont("Segoe Fluent Icons")
            icon_font.setPixelSize(15)
            painter.setFont(icon_font)
            glyph_rect = QRectF(-_EXP_CHEVRON_BUTTON_SIZE * 0.5, -_EXP_CHEVRON_BUTTON_SIZE * 0.5,
                                _EXP_CHEVRON_BUTTON_SIZE, _EXP_CHEVRON_BUTTON_SIZE)
            painter.drawText(glyph_rect, Qt.AlignCenter, ICON_CHEVRON_DOWN_MED)
            painter.restore()

        if self.hasFocus():
            option = QStyleOptionFocusRect()
            option.initFrom(self)
            option.rect = self.rect().adjusted(3, 3, -3, -3)
            option.backgroundColor = self.palette().color(QPalette.Window)
            self.style().drawPrimitive(QStyle.PE_FrameFocusRect, option, painter, self)

    def _update_layout_margins(self):
        chevron_side = (_EXP_CHEVRON_CONTENT_SPACING + _EXP_CHEVRON_BUTTON_SIZE
                        + _EXP_CHEVRON_TRAILING_MARGIN)
        if self.layoutDirection() == Qt.RightToLeft:
            self._layout.setContentsMargins(chevron_side, 0, _EXP_HEADER_CONTENT_PADDING, 0)
        else:
            self._layout.setContentsMargins(_EXP_HEADER_CONTENT_PADDING, 0, chevron_side, 0)


class ExExpander(QWidget):
    """折叠面板（对应 C++ ExWidgets/controls/exexpander.cpp，仅支持向下展开）。"""

    expanding = pyqtSignal()
    collapsed = pyqtSignal()
    expandedChanged = pyqtSignal(bool)
    expansionFinished = pyqtSignal(bool)
    headerChanged = pyqtSignal(str)

    def __init__(self, parent=None, content_pad=False):
        super().__init__(parent)
        # content_pad：内容右侧让出折叠按钮区（60px，与折叠条控件右缘对齐）
        self._content_pad = content_pad
        self._expanded = False
        self._foldable = True
        self._expand_direction = "down"
        self._animation_enabled = True
        self._animation_duration = 167
        self._expansion_progress = 0.0
        self._header = ""
        self._header_widget = None
        self._content_widgets = []
        self._content_panels = []

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self._header_button = _ExpanderHeaderButton(self)
        self._content_stack = _ExpanderContentStack(self)
        self._content_layout = QVBoxLayout(self._content_stack)
        self._content_container = _ExpanderContentViewport(self, self._content_stack)

        self._expansion_animation = QVariantAnimation(self)

        self.setMinimumWidth(_EXPANDER_MIN_WIDTH)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content_container.prepareAnimation()
        self._content_container.setViewportProgress(0.0)
        self._content_container.hide()

        self._rebuild_layout()

        self._header_button.clicked.connect(self.toggle)
        self._expansion_animation.valueChanged.connect(self._on_animation_value)
        self._expansion_animation.finished.connect(self._finish_transition)

    # ---- 状态 ----
    def header(self):
        return self._header

    def setHeader(self, header):
        if self._header == header:
            return
        self._header = header
        self._header_button.setHeader(header)
        self.headerChanged.emit(header)

    def isExpanded(self):
        return self._expanded

    def expandDirection(self):
        return self._expand_direction

    def animationDuration(self):
        return self._animation_duration

    def setAnimationDuration(self, duration):
        self._animation_duration = max(0, duration)

    def isAnimationEnabled(self):
        return self._animation_enabled

    def setAnimationEnabled(self, enabled):
        self._animation_enabled = enabled
        if not enabled and self._expansion_animation.state() == QVariantAnimation.Running:
            self._expansion_animation.stop()
            self._finish_transition()

    def headerWidget(self):
        return self._header_widget

    def setHeaderWidget(self, widget):
        if widget in (self, self._header_button, self._content_container, self._content_stack):
            return
        if self._header_widget is not None:
            self._header_button.takeHeaderWidget()
        self._header_button.setHeaderWidget(widget)
        self._header_widget = widget
        # 仅下拉/spin 这类高控件需要 72px 呼吸空间；
        # 开关/小按钮足够矮，维持 48px
        hasctl = bool(
            widget.findChildren(QComboBox)
            or widget.findChildren(QAbstractSpinBox)
        )
        self._header_button.setMinimumHeight(
            72 if hasctl else _EXP_HEADER_MIN_HEIGHT
        )
        self.updateGeometry()

    def takeHeaderWidget(self):
        widget = self._header_button.takeHeaderWidget()
        self._header_widget = None
        self.updateGeometry()
        return widget

    def contentWidgets(self):
        return list(self._content_widgets)

    def addContentWidget(self, widget):
        if widget is None or widget is self or widget is self._header_button:
            return
        if widget in self._content_widgets:
            return
        panel = _ExpanderContentPanel(self, widget, self._content_pad)
        self._content_widgets.append(widget)
        self._content_panels.append(panel)
        self._rebuild_content_layout()
        self._refresh_content_geometry()

    def hasContentWidgets(self):
        return bool(self._content_panels)

    def removeContentWidget(self, widget):
        """移除一个内容面板（内容随引擎/样式切换整体重建的场景）。"""
        if widget not in self._content_widgets:
            return
        idx = self._content_widgets.index(widget)
        panel = self._content_panels[idx]
        self._content_widgets.pop(idx)
        self._content_panels.pop(idx)
        self._content_layout.removeWidget(panel)
        # 先 hide 再脱离父对象：setParent(None) 会把它变成顶层窗口，
        # 保持可见态就会闪现一下
        panel.hide()
        panel.setParent(None)
        panel.deleteLater()
        self._rebuild_content_layout()
        self._refresh_content_geometry()

    def clearContentWidgets(self):
        for widget in list(self._content_widgets):
            self.removeContentWidget(widget)

    # ---- 展开/收起 ----
    def setFoldable(self, foldable):
        """无内容时退化为普通卡：不画折叠箭头、不可展开（如 Qt 引擎的
        显示引擎、直接启动的启动方式）；有内容时恢复折叠形态。"""
        if self._foldable == foldable:
            return
        self._foldable = foldable
        if not foldable:
            self.setExpanded(False)
        self._header_button.update()

    def setExpanded(self, expanded):
        if not self._foldable and expanded:
            return  # 已退化为普通卡：不可展开
        if self._expanded == expanded:
            return
        self._expanded = expanded
        self._header_button.setChecked(expanded)
        if expanded:
            self.expanding.emit()
        self.expandedChanged.emit(expanded)
        self._header_button.update()

        self._expansion_animation.stop()
        can_animate = (self._animation_enabled and self._animation_duration > 0
                       and self.parentWidget() is not None and self.parentWidget().isVisible())
        if not can_animate:
            self._expansion_progress = 1.0 if expanded else 0.0
            self._header_button.setExpansionProgress(self._expansion_progress)
            if expanded:
                self._content_container.setVisible(self.hasContentWidgets())
                self._content_stack.setVisible(self.hasContentWidgets())
                self._root_layout.activate()
            self._content_container.prepareAnimation()
            self._content_stack.setVisible(expanded and self.hasContentWidgets())
            self._content_container.setViewportProgress(self._expansion_progress)
            self._content_container.setVisible(expanded and self.hasContentWidgets())
            self.updateGeometry()
            if not expanded:
                self.collapsed.emit()
            self.expansionFinished.emit(expanded)
            return

        # 展开时外层视口先一次性进入最终布局，动画只改变内部裁剪窗口；
        # 收起时仍逐步回收布局高度，完成后再隐藏。
        self._content_container.setVisible(self.hasContentWidgets())
        self._content_stack.setVisible(self.hasContentWidgets())
        self._content_container.prepareAnimation()
        self._root_layout.activate()
        self._content_container.setViewportProgress(self._expansion_progress)

        if expanded:
            duration = max(1, self._animation_duration * 2 - 1)
            if self._expansion_progress < 1.0:
                self._expansion_animation.setDuration(
                    max(1, round(duration * (1.0 - self._expansion_progress))))
                self._expansion_animation.setEasingCurve(QEasingCurve.OutCubic)
                self._expansion_animation.setStartValue(self._expansion_progress)
                self._expansion_animation.setEndValue(1.0)
                self._expansion_animation.start()
            else:
                self._finish_transition()
            return

        if self._expansion_progress > 0.0:
            self._expansion_animation.setDuration(
                max(1, round(self._animation_duration * self._expansion_progress)))
            self._expansion_animation.setEasingCurve(QEasingCurve.OutCubic)
            self._expansion_animation.setStartValue(self._expansion_progress)
            self._expansion_animation.setEndValue(0.0)
            self._expansion_animation.start()
        else:
            self._finish_transition()

    def toggle(self):
        self.setExpanded(not self._expanded)

    def isAnimationRunning(self):
        return self._expansion_animation.state() == QVariantAnimation.Running

    # ---- 尺寸 ----
    def sizeHint(self):
        return self._root_layout.sizeHint()

    def minimumSizeHint(self):
        return self._root_layout.minimumSize()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange,
                            QEvent.StyleChange, QEvent.LayoutDirectionChange, QEvent.EnabledChange):
            self._header_button.update()
            for panel in self._content_panels:
                panel.update()

    # ---- 内部 ----
    def _on_animation_value(self, value):
        self._expansion_progress = float(value)
        self._header_button.setExpansionProgress(self._expansion_progress)
        self._content_container.setViewportProgress(self._expansion_progress)

    def _rebuild_content_layout(self):
        for panel in self._content_panels:
            self._content_layout.removeWidget(panel)
            panel.setOuterEdge(False)
        if not self._content_panels:
            return
        for panel in self._content_panels:
            self._content_layout.addWidget(panel)
            panel.show()
        # 最后追加的 Content 距离 Header 最远，负责整体外圆角
        self._content_panels[-1].setOuterEdge(True)

    def _refresh_content_geometry(self):
        self._content_layout.activate()
        self._content_container.prepareAnimation()
        self._content_container.setViewportProgress(self._expansion_progress)
        visible = ((self._expanded or self._expansion_animation.state() == QVariantAnimation.Running)
                   and self.hasContentWidgets())
        self._content_stack.setVisible(visible)
        self._content_container.setVisible(visible)
        self._header_button.update()
        self.updateGeometry()

    def _rebuild_layout(self):
        self._root_layout.removeWidget(self._header_button)
        self._root_layout.removeWidget(self._content_container)
        self._root_layout.addWidget(self._header_button)
        self._root_layout.addWidget(self._content_container)

    def _finish_transition(self):
        self._expansion_progress = 1.0 if self._expanded else 0.0
        self._header_button.setExpansionProgress(self._expansion_progress)
        self._content_container.prepareAnimation()
        self._content_container.setViewportProgress(self._expansion_progress)
        self._content_stack.setVisible(self._expanded and self.hasContentWidgets())
        self._content_container.setVisible(self._expanded and self.hasContentWidgets())
        self.updateGeometry()
        if not self._expanded:
            self.collapsed.emit()
        self.expansionFinished.emit(self._expanded)
