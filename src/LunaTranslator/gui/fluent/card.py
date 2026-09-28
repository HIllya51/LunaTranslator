"""FluentUI 设置卡片工具（Gallery settings_page.py 的 make_* 系列移植）。

- FluentCard          —— isCard 卡片（图标 + 标题/描述 + 尾部控件）
- make_card           —— FluentCard 的便捷工厂（Gallery make_card）
- make_trailing_combo —— 把已有下拉框包装成卡片尾部控件（固定 170×32，零边距）
"""

from qtsymbols import (
    QEvent,
    QColor,
    Qt,
    QFont,
    QHBoxLayout,
    QLabel,
    QListView,
    QPalette,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.fluent.icons import (
    ICON_COLOR,
    ICON_GLOBE,
    ICON_SYNC,
    ICON_PICTURE,
    ICON_TASK_VIEW,
    ICON_SETTINGS_DISPLAY_SOUND,
)


class FluentCard(QWidget):
    """WinUI3 设置卡片（Gallery make_card 的 make_card_contents 等价物）。"""

    def __init__(self, icon_code, title, description="", trailing=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("isCard", True)
        self.setMinimumHeight(72)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        # 图标
        if icon_code:
            icon_label = QLabel(self)
            icon_font = QFont("Segoe Fluent Icons")
            icon_font.setPixelSize(22)
            icon_label.setFont(icon_font)
            icon_label.setText(icon_code)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedWidth(36)
            layout.addWidget(icon_label)

        # 标题 + 描述
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
            desc_label = QLabel(description, text_widget)
            desc_font = desc_label.font()
            desc_font.setPixelSize(13)
            desc_label.setFont(desc_font)
            desc_label.setWordWrap(True)
            text_layout.addWidget(desc_label)

        layout.addWidget(text_widget, 1)

        # 尾部控件
        if trailing is not None:
            if callable(trailing):
                trailing = trailing()
            if trailing is not None:
                layout.addSpacing(16)
                layout.addWidget(trailing, 0, Qt.AlignVCenter)


def make_card(icon_code, title, description="", trailing=None, parent=None):
    """Gallery make_card 同款。"""
    return FluentCard(icon_code, title, description, trailing, parent)


def make_trailing_combo(combo, width=170, height=32):
    """把已有下拉框包装成卡片尾部控件（固定尺寸，零边距容器）。"""
    from qtsymbols import QComboBox

    if isinstance(combo, QComboBox):
        combo.setMinimumWidth(width)
        combo.setMinimumHeight(height)
    holder = QWidget()
    lay = QHBoxLayout(holder)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(combo)
    return holder
