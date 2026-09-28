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
_plugin_path_done = False


def _ensure_plugin_path():
    global _plugin_path_done
    if _plugin_path_done:
        return
    _plugin_path_done = True
    path = os.path.abspath("files/plugins")
    if os.path.isdir(path):
        QCoreApplication.addLibraryPath(path)


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
    global _applied_key
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
    app.setStyle("FluentUI3")

    # setStyle 的 re-polish 会把控件字体重置；setcommonstylesheet 末尾的
    # 无条件 setFont 会恢复 app 字体，但弹出容器内的视图与常驻菜单不跟随——额外恢复
    QTimer.singleShot(0, _restore_combo_view_fonts)
    _install_menu_font_gate()
    _applied_key = key


_menu_font_gate = None


def _install_menu_font_gate():
    """应用级事件过滤：QMenu 显示时统一 12px 字号（菜单不跟随 12pt
    应用字体——那样偏大）。QApplication.setFont(f, "QMenu") 类字体
    在 app.setFont 之后对新建控件失效，事件过滤是可靠途径；
    先判 ev.type() 再判 isinstance，逐事件开销极小。"""
    global _menu_font_gate
    if _menu_font_gate is not None:
        return
    from qtsymbols import QEvent, QObject, QMenu

    class _Gate(QObject):
        def eventFilter(self, obj, ev):
            if ev.type() == QEvent.Show and isinstance(obj, QMenu):
                f = obj.font()
                if f.pointSize() > 0:
                    nf = QFont(f.family())
                    nf.setPixelSize(12)
                    obj.setFont(nf)
            return False

    _app = QApplication.instance()
    _menu_font_gate = _Gate(_app)
    _app.installEventFilter(_menu_font_gate)


def _restore_combo_view_fonts():
    """setStyle 重扫描（延迟生效）会把 combo 弹出视图的字体重置为系统
    默认(9pt)。对受害控件无条件设显式字体——显式字体能在后续的延迟重置
    中存活。构造式 QFont(family, size)：拷贝式带空 resolve mask，
    setFont 等于清除显式字体，无效。"""
    from qtsymbols import QComboBox

    app = QApplication.instance()
    if app is None:
        return
    appf = app.font()
    if appf.pointSize() > 0:
        newf = QFont(appf.family(), appf.pointSize())
    else:
        newf = QFont(appf.family())
        newf.setPixelSize(max(1, appf.pixelSize()))
    for w in QApplication.allWidgets():
        if isinstance(w, QComboBox):
            try:
                w.view().setFont(QFont(newf))
            except RuntimeError:
                pass
