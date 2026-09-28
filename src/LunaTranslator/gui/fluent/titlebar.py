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
    QWidget,
    pyqtSignal,
)

# Segoe Fluent Icons 码点
ICON_GLOBAL_NAV = "\ue700"
ICON_MINIMIZE = "\ue921"
ICON_MAXIMIZE = "\ue922"
ICON_RESTORE = "\ue923"
ICON_CLOSE = "\ue8bb"


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


class FluentTitleBar(QWidget):
    navToggleRequested = pyqtSignal()

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
        layout.setSpacing(0)
        layout.addWidget(self._nav_button)
        layout.addSpacing(8)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._title_label)
        layout.addStretch()
        layout.addWidget(self._min_button)
        layout.addWidget(self._max_button)
        layout.addWidget(self._close_button)

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

    # ---- 更新 ----
    def eventFilter(self, watched, event):
        if watched == self._window:
            if event.type() == QEvent.Type.WindowIconChange:
                self.updateIcon()
            elif event.type() == QEvent.Type.WindowTitleChange:
                self.updateTitle()
            elif event.type() == QEvent.Type.WindowStateChange:
                self.updateMaxButton()
        return super().eventFilter(watched, event)

    def updateTitle(self):
        self._title_label.setText(self._window.windowTitle())

    def updateIcon(self):
        from qtsymbols import QApplication

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
