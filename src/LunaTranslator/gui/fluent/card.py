"""FluentCard —— WinUI3 设置卡片（Gallery settings_page.py 的 make_card 等价物）。

每张卡片：Segoe Fluent 图标(22px) + 标题(15px) + 描述(13px, Mid 色) + 尾部控件。
isCard 属性由 FluentUI3 插件渲染为 WinUI 圆角卡片。
描述文字颜色在主题切换时自动跟随调色板（修复 Gallery 中暗色下不可见的问题）。
"""

from qtsymbols import (
    QEvent,
    Qt,
    QFont,
    QHBoxLayout,
    QLabel,
    QPalette,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class FluentCard(QWidget):
    """WinUI3 设置卡片。"""

    def __init__(self, icon_code, title, description="", trailing=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("isCard", True)
        self.setMinimumHeight(72)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._desc_label = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        # 图标（同 Gallery：Segoe Fluent Icons 22px，固定宽 36）
        if icon_code:
            icon_label = QLabel(self)
            icon_font = QFont("Segoe Fluent Icons")
            icon_font.setPixelSize(22)
            icon_label.setFont(icon_font)
            icon_label.setText(icon_code)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedWidth(36)
            layout.addWidget(icon_label)

        # 标题 + 描述（同 Gallery：15px / 13px，间距 1）
        text_widget = QWidget(self)
        text_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        title_label = QLabel(title, text_widget)
        title_font = title_label.font()
        title_font.setPixelSize(15)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)

        if description:
            self._desc_label = QLabel(description, text_widget)
            desc_font = self._desc_label.font()
            desc_font.setPixelSize(13)
            self._desc_label.setFont(desc_font)
            self._desc_label.setWordWrap(True)
            text_layout.addWidget(self._desc_label)

        layout.addWidget(text_widget, 1)

        # 尾部控件（开关/下拉框等）
        if trailing is not None:
            if callable(trailing):
                trailing = trailing()
            if trailing is not None:
                layout.addSpacing(16)
                layout.addWidget(trailing, 0, Qt.AlignVCenter)

        self._update_desc_color()

    def _update_desc_color(self):
        """从当前应用调色板读 Mid 色设为描述文字颜色（主题切换时跟随）。"""
        if self._desc_label is None:
            return
        from qtsymbols import QApplication

        app_pal = QApplication.instance().palette()
        mid = app_pal.color(QPalette.Mid)
        pal = self._desc_label.palette()
        pal.setColor(QPalette.WindowText, mid)
        self._desc_label.setPalette(pal)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (
            QEvent.Type.PaletteChange,
            QEvent.Type.StyleChange,
            QEvent.Type.ApplicationPaletteChange,
        ):
            self._update_desc_color()


def create_card(icon_code, title, description="", trailing=None, parent=None):
    """便捷工厂：返回 FluentCard 实例。"""
    return FluentCard(icon_code, title, description, trailing, parent)
