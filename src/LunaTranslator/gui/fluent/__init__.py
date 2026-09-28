"""FluentUI3 样式接管（gui.fluent）。

采用 app 级 QApplication.setStyle("FluentUI3")（同 Gallery 的
refresh_fluent_style）。明暗切换通过 setstylesheetsignal 的
QueuedConnection 进入（不在组合框弹出的关闭序列中同步执行）。
"""

from qtsymbols import QApplication, QColor, QFont, QTimer, isqt5

if isqt5:
    from PyQt5.QtWidgets import QStyleFactory
    from PyQt5.QtCore import QCoreApplication

import os

_applied_key = None
_legacy_style_key = None
_plugin_path_done = False


def _ensure_plugin_path():
    global _plugin_path_done
    if _plugin_path_done:
        return
    _plugin_path_done = True
    path = os.path.abspath("files/plugins")
    if os.path.isdir(path):
        QCoreApplication.addLibraryPath(path)


def is_fluent_theme():
    """当前是否处于 FluentUI3 主题（theme3 == FluentUI3）。"""
    from myutils.config import ui_settings

    return ui_settings.get("theme3") == "FluentUI3"


def get_windows_accent_color():
    """读取 Windows 系统强调色。失败返回无效 QColor。"""
    from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER

    registry = ConnectRegistry(None, HKEY_CURRENT_USER)
    key = OpenKey(
        registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent"
    )
    accent_int = QueryValueEx(key, "AccentColorMenu")[0]  # 0xAABBGGRR
    bb = (accent_int >> 16) & 0xFF
    gg = (accent_int >> 8) & 0xFF
    rr = accent_int & 0xFF
    return QColor(rr, gg, bb)


def apply_fluent_style(dark):
    """app 级应用 FluentUI3 样式。同 Gallery 的 refresh_fluent_style。"""
    global _applied_key, _legacy_style_key
    app = QApplication.instance()

    app.setProperty("_q_scrollHint_center", False)
    app.setProperty("_q_themestyle", 0)
    app.setProperty("_q_widget_mode", 0)
    accent = get_windows_accent_color()
    if accent.isValid():
        app.setProperty("_q_accent_color", accent)

    key = (bool(dark), accent.name() if accent.isValid() else "")
    if _applied_key == key:
        return

    _ensure_plugin_path()
    app.setProperty("_q_colorscheme", 1 if dark else 0)
    if _legacy_style_key is None:
        _legacy_style_key = app.style().objectName()
    app.setStyle("FluentUI3")

    # setStyle 的 re-polish 会把控件字体重置；setcommonstylesheet 末尾的
    # 无条件 setFont 会恢复 app 字体，但弹出容器内的视图不跟随——额外恢复
    QTimer.singleShot(0, _restore_combo_view_fonts)
    _applied_key = key


def _restore_combo_view_fonts():
    from qtsymbols import QComboBox

    app = QApplication.instance()
    if app is None:
        return
    font = QFont(app.font())
    for w in QApplication.allWidgets():
        if isinstance(w, QComboBox):
            try:
                w.view().setFont(QFont(font))
            except RuntimeError:
                pass


def clear_fluent_style():
    """切回传统主题时还原 app 样式。"""
    global _applied_key
    if _applied_key is None:
        return
    app = QApplication.instance()
    if _legacy_style_key is not None:
        app.setStyle(_legacy_style_key)
    _applied_key = None
