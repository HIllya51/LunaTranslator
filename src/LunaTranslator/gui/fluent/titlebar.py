"""FluentTitleBar —— Fluent 自定义标题栏（简化版）。

移植自 FluentUIStyle/PyQt5Examples/exwidgets.py 的 FluentTitleBar：
[导航切换][图标][标题][stretch][最小化][最大化/还原][关闭]，固定高 40。
caption 按钮使用 win_caption_* objectName —— FluentUI3 插件对该族有专门的
悬停/关闭红渲染（fluentui3style.cpp:2582-2599），无需自绘。
"""

from qtsymbols import (
    QEvent,
    Qt,
    QFont,
    QHBoxLayout,
    QLabel,
    QSize,
    QToolButton,
    QTimer,
    QWidget,
    QApplication,
    pyqtSignal,
)

from gui.fluent.icons import (
    ICON_MINIMIZE,
    ICON_MAXIMIZE,
    ICON_RESTORE,
    ICON_CLOSE,
    ICON_GLOBAL_NAV,
)


def _caption_icon_font(pixel_size=11):
    font = QFont("Segoe Fluent Icons")
    font.setPixelSize(pixel_size)
    font.setStyleStrategy(QFont.PreferAntialias)
    return font


def _create_caption_button(parent, object_name, glyph, width=46, pixel_size=11):
    button = QToolButton(parent)
    button.setObjectName(object_name)
    button.setAutoRaise(True)
    button.setToolButtonStyle(Qt.ToolButtonTextOnly)
    button.setFont(_caption_icon_font(pixel_size))
    button.setText(glyph)
    button.setFixedSize(width, 40)
    return button


def create_fluent_caption_button(parent, glyph, tooltip="", width=40):
    """Gallery 标题栏「置顶/主题」同款的 caption 风格按钮
    （win_caption_pin 悬停由插件渲染，40x40、16px 字形）。"""
    button = _create_caption_button(parent, "win_caption_pin", glyph, width, 16)
    if tooltip:
        button.setToolTip(tooltip)
    return button


class FluentTitleBar(QWidget):
    navToggleRequested = pyqtSignal()

    # 居中控件（搜索框）的最小宽度——收窄到此为止，之后才轮到侧控件省略
    _CENTER_MIN_WIDTH = 150

    def __init__(self, window, parent=None):
        super().__init__(parent or window)
        self.setObjectName("fluent-title-bar")
        self.setFixedHeight(40)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._window = window

        self._nav_button = _create_caption_button(
            self, "win_caption_pin", ICON_GLOBAL_NAV, 46, 16)
        self._nav_button.setToolTip("展开/收起导航")
        self._nav_button.clicked.connect(self.navToggleRequested)

        self._icon_label = QLabel(self)
        self._icon_label.setFixedSize(16, 16)
        self._icon_label.setScaledContents(True)

        self._title_label = QLabel(self)
        self._title_label.setObjectName("fluent-title-label")

        self._min_button = _create_caption_button(
            self, "win_caption_minimize", ICON_MINIMIZE)
        self._max_button = _create_caption_button(
            self, "win_caption_maximize", ICON_MAXIMIZE)
        # 不设 checkable：勾选态会把字形颜色画反（浅色下白色/深色下黑色，
        # 不可见）；最大化/还原图标已通过 setText 切换，无需勾选态
        self._close_button = _create_caption_button(
            self, "win_caption_close", ICON_CLOSE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 0, 0)
        # spacing=0 是为了 caption 按钮紧密相邻（WinUI 同款）；原 Gallery
        # 用全局 spacing=8（图标/标题间距即来自它），这里按处单独补
        layout.setSpacing(0)
        layout.addWidget(self._nav_button)
        layout.addSpacing(8)  # 导航按钮->图标；导航按钮隐藏时兼作左边距
        layout.addWidget(self._icon_label)
        layout.addSpacing(8)  # 图标->标题（原 Gallery spacing=8）
        layout.addWidget(self._title_label)
        layout.addStretch()
        layout.addWidget(self._min_button)
        layout.addWidget(self._max_button)
        layout.addWidget(self._close_button)

        self._center_widget = None   # 居中控件（手动定位，不进布局）
        self._center_side = None     # 紧挨其右侧的控件（面包屑）

        self._min_button.clicked.connect(window.showMinimized)

        def toggle_maximized():
            if window.isMaximized():
                window.showNormal()
            else:
                window.showMaximized()

        self._max_button.clicked.connect(toggle_maximized)
        self._close_button.clicked.connect(window.close)

        self.updateTitle()
        self.updateIcon()
        self.updateMaxButton()
        window.installEventFilter(self)

    # ---- 访问 ----
    def navButton(self):
        return self._nav_button

    def minButton(self):
        return self._min_button

    def maxButton(self):
        return self._max_button

    def closeButton(self):
        return self._close_button

    def iconLabel(self):
        return self._icon_label

    def titleLabel(self):
        return self._title_label

    def setNavButtonVisible(self, visible):
        self._nav_button.setVisible(visible)

    def addCenterWidget(self, w, pref_width=None):
        """居中控件（搜索框）：不进布局、手动定位。空间充足时保持
        pref_width 原宽居中；不足时依次：向左让位 -> 收窄到最小宽
        -> 才轮到侧控件（面包屑）溢出省略。"""
        self._center_widget = w
        if pref_width is None:
            pref_width = w.width()
        self._center_pref = max(int(pref_width), self._CENTER_MIN_WIDTH)
        w.setParent(self)
        w.adjustSize()
        w.setVisible(True)
        self._layout_center()

    def addSideWidget(self, w):
        """紧挨居中控件右侧的控件（面包屑，从左向右）；显隐/重建
        触发重定位（让位次序见 _layout_center）。"""
        self._center_side = w
        w.setParent(self)
        w.installEventFilter(self)
        self._layout_center()

    def addTrailingWidget(self, w):
        """插入尾部控件（最小化按钮之前，标题栏右侧）。"""
        lay = self.layout()
        lay.insertWidget(lay.indexOf(self._min_button), w)
        # 显隐会改变右簇宽度 -> 居中控件需重定位
        w.installEventFilter(self)

    # ---- 居中控件定位 ----
    def _right_edge(self):
        """右簇最左沿（布局里图标/标题以外的最左可见控件）。"""
        x = self.width()
        lay = self.layout()
        for i in range(lay.count()):
            w = lay.itemAt(i).widget()
            if (w is not None and w.isVisible()
                    and w not in (self._icon_label, self._title_label)):
                x = min(x, w.x())
        return x

    def _layout_center(self):
        w = getattr(self, "_center_widget", None)
        if w is None:
            return
        L = self._title_label.geometry().right() + 12
        R = self._right_edge() - 8
        gap = 8
        pref = self._center_pref
        minw = self._CENTER_MIN_WIDTH
        side = getattr(self, "_center_side", None)
        side_on = side is not None and side.isVisibleTo(self)
        bh = side.sizeHint().width() if side_on else 0
        avail = R - L

        if not side_on:
            # 无侧控件：居中 -> 左移 -> 收窄
            sw = pref
            x = (self.width() - sw) // 2
            if x + sw > R:
                x = R - sw
            if x < L:
                x = L
                sw = min(pref, max(60, R - L))
        elif avail >= pref + gap + bh:
            # 充足：原宽居中；放不下侧控件再整体左移（侧控件保持完整）
            sw = pref
            x = (self.width() - sw) // 2
            if x + sw + gap + bh > R:
                x = R - sw - gap - bh
            x = max(L, x)
        elif avail >= minw + gap + bh:
            # 左移到头：收窄搜索，侧控件仍保持完整
            sw = avail - gap - bh
            x = L
        else:
            # 搜索已到最窄：侧控件溢出省略；窗口再窄时为保住侧控件的
            # 最小（省略号）形态，搜索可继续收窄（60 兜底，绝不重叠）
            bmin = side.minimumSizeHint().width() if side is not None else 0
            sw = min(minw, max(60, avail - gap - bmin))
            x = L
        sw = max(sw, 60)
        h = w.sizeHint().height() or w.height()
        w.resize(sw, h)
        w.move(x, (self.height() - h) // 2)
        if side is not None and side_on:
            avail_side = max(0, R - (x + sw + gap))
            hint = side.sizeHint()
            side.resize(min(hint.width(), avail_side), hint.height())
            side.move(x + sw + gap,
                      (self.height() - hint.height()) // 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_center()

    # ---- 更新 ----
    def eventFilter(self, watched, event):
        if watched == self._window:
            if event.type() == QEvent.Type.WindowIconChange:
                self.updateIcon()
            elif event.type() == QEvent.Type.WindowTitleChange:
                self.updateTitle()
            elif event.type() == QEvent.Type.WindowStateChange:
                self.updateMaxButton()
        elif watched is getattr(self, "_center_side", None):
            if event.type() in (QEvent.Type.ShowToParent,
                                QEvent.Type.HideToParent):
                self._layout_center()
            elif event.type() in (QEvent.Type.ChildAdded,
                                  QEvent.Type.ChildRemoved):
                # 面包屑重建按钮（items 变化）后 sizeHint 已变——下一拍重定位
                QTimer.singleShot(0, self._layout_center)
        elif event.type() in (QEvent.Type.ShowToParent,
                              QEvent.Type.HideToParent):
            # 尾部控件显隐（右簇宽度变化）-> 居中控件重定位
            self._layout_center()
        return super().eventFilter(watched, event)

    def updateTitle(self):
        self._title_label.setText(self._window.windowTitle())

    def updateIcon(self):
        icon = self._window.windowIcon()
        if icon.isNull():
            icon = QApplication.windowIcon()
        if icon.isNull():
            self._icon_label.clear()
            return
        self._icon_label.setPixmap(icon.pixmap(QSize(16, 16)))

    def updateMaxButton(self):
        maximized = self._window.isMaximized()
        self._max_button.setText(ICON_RESTORE if maximized else ICON_MAXIMIZE)
