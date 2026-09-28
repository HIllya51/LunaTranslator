"""QMenu 标准动作图标——移植 C++ Gallery 的 applyStandardMenuIcons
（Examples/Gallery/mainwindow.cpp：给 QLineEdit/QSpinBox 等标准右键
菜单装 Segoe Fluent 图标；Qt 原生不带）。含中英文动作名匹配。"""

from qtsymbols import QPalette, QApplication, QMenu

from gui.fluent.nav import create_fluent_icon

# Segoe Fluent Icons 码点（同 C++ Gallery）+ 中文动作名
_GLYPHS = (
    ("undo", 0xE7A7),
    ("撤销", 0xE7A7),
    ("redo", 0xE7A6),
    ("重做", 0xE7A6),
    ("cut", 0xE8C6),
    ("剪切", 0xE8C6),
    ("copy", 0xE8C8),
    ("复制", 0xE8C8),
    ("paste", 0xE77F),
    ("粘贴", 0xE77F),
    ("select all", 0xE8B3),
    ("selectall", 0xE8B3),
    ("全选", 0xE8B3),
    ("delete", 0xE74D),
    ("删除", 0xE74D),
    ("clear", 0xE74D),
    ("清除", 0xE74D),
    ("step up", 0xE70E),
    ("上调", 0xE70E),
    ("step down", 0xE70D),
    ("下调", 0xE70D),
)


def apply_standard_menu_icons(menu: QMenu, widget=None):
    if menu is None:
        return
    # 字号由 QApplication.setFont(font, "QMenu") 类级字体统一处理
    color = None
    if widget is not None:
        color = widget.palette().color(QPalette.Text)
    if color is None:
        app = QApplication.instance()
        if app is not None:
            color = app.palette().color(QPalette.Text)
    for action in menu.actions():
        if action.isSeparator():
            continue
        if action.menu() is not None:
            apply_standard_menu_icons(action.menu(), widget)
            continue
        if not action.icon().isNull():
            continue
        text = action.text().replace("&", "").lower()
        for key, glyph in _GLYPHS:
            if key in text:
                action.setIcon(create_fluent_icon(chr(glyph), color))
                break
