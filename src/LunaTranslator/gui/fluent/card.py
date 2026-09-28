"""create_card —— FluentUI 设置卡片（同 Gallery settings_page.py 的 make_card）。

每张卡片：图标 + 标题/描述 + 尾部控件（开关/下拉框等），isCard 属性由
FluentUI3 插件渲染为 WinUI 圆角卡片（#fdfdfd 底 + #e9e9e9 描边）。
"""

from qtsymbols import (
    Qt,
    QFont,
    QHBoxLayout,
    QLabel,
    QPalette,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def create_card(icon_code, title, description="", trailing=None, parent=None):
    """创建一张 FluentUI 设置卡片。

    icon_code:  Segoe Fluent Icons 码点（空字符串则不显示图标）
    title:      标题
    description: 描述文字（空则不显示）
    trailing:   尾部控件（QWidget 或返回 QWidget 的 callable）
    """
    card = QWidget(parent)
    card.setAttribute(Qt.WA_StyledBackground, True)
    card.setProperty("isCard", True)
    card.setMinimumHeight(72)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    layout = QHBoxLayout(card)
    layout.setContentsMargins(18, 12, 18, 12)
    layout.setSpacing(14)

    # 图标
    if icon_code:
        icon_label = QLabel(card)
        icon_font = QFont("Segoe Fluent Icons")
        icon_font.setPixelSize(22)
        icon_label.setFont(icon_font)
        icon_label.setText(icon_code)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedWidth(36)
        layout.addWidget(icon_label)

    # 标题 + 描述
    text_widget = QWidget(card)
    text_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    text_layout = QVBoxLayout(text_widget)
    text_layout.setContentsMargins(0, 0, 0, 0)
    text_layout.setSpacing(1)

    title_label = QLabel(title, text_widget)
    title_font = title_label.font()
    title_font.setPointSizeF(title_font.pointSizeF() + 1)
    title_label.setFont(title_font)
    text_layout.addWidget(title_label)

    if description:
        desc_label = QLabel(description, text_widget)
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

    return card
