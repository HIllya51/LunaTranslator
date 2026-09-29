"""FluentUI3 样式接管（gui.fluent）。

采用 app 级 QApplication.setStyle("FluentUI3")（同 Gallery 的
refresh_fluent_style）。明暗切换通过 setstylesheetsignal 的
QueuedConnection 进入（不在组合框弹出的关闭序列中同步执行）。
"""

from qtsymbols import (
    QApplication, QColor, QFont, QTimer, isqt5,
    QEvent, QObject, QMenu, Qt, QWidget,
    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox,
)

if isqt5:
    from PyQt5.QtWidgets import QStyleFactory
    from PyQt5.QtCore import QCoreApplication

import ctypes
import os
from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER

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
    _install_exec_menu_gate()
    _applied_key = key


_menu_font_gate = None


def _disable_dwm_nc_chrome(widget):
    """提前创建原生窗口并关闭 DWM 非客户区渲染（系统边框+阴影）。

    DWM 在窗口**首次合成**时画上系统边框/阴影；若等 WinIdChange（首次
    显示过程中）再设属性，第一次显示仍带边框、第二次才干净——这正是
    "每个右键菜单首次唤出时有右/下边框"的根源。必须在显示前完成：
    先 winId() 强制创建窗口（尚未合成），再设 DWM 属性。"""
    try:
        hwnd = int(widget.winId())
        dwmapi = ctypes.windll.dwmapi
        policy = ctypes.c_uint(1)  # DWMNCRP_DISABLED（边框+阴影全关）
        dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(policy), 4)
        color = ctypes.c_uint(0xFFFFFFFE)  # DWMWA_COLOR_NONE
        dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(color), 4)
    except:
        pass


def _install_menu_font_gate():
    """应用级事件过滤：QMenu 显示时统一 13px 字号（同应用字体/Gallery；
    并治愈切换明暗后 setStyle 重扫描把菜单字体重置为默认的问题）。
    QApplication.setFont(f, "QMenu") 类字体在 app.setFont 之后对新建
    控件失效，事件过滤是可靠途径；先判 ev.type() 再判 isinstance，
    逐事件开销极小。"""
    global _menu_font_gate
    if _menu_font_gate is not None:
        return

    class _Gate(QObject):
        def eventFilter(self, obj, ev):
            if ev.type() == QEvent.Show and isinstance(obj, QMenu):
                f = obj.font()
                if f.pixelSize() != 13:
                    nf = QFont(f.family())
                    nf.setPixelSize(13)
                    obj.setFont(nf)
            return False

    _app = QApplication.instance()
    _menu_font_gate = _Gate(_app)
    _app.installEventFilter(_menu_font_gate)


_exec_menu_gate = None


def _install_exec_menu_gate():
    """QLineEdit/QPlainTextEdit/QComboBox 的标准右键菜单改走 exec()。

    同 PyQt5Examples 的 StandardContextMenuFilter（对应 C++ Gallery 重写的
    各 contextMenuEvent）：Qt 默认路径用 QMenu::popup()——窗口在 show 过程
    中创建，DWM 首次合成会给菜单画上系统边框（右/下侧，首个 hwnd 每次
    首次显示可见）；exec() 先 createWinId() 再显示，无此问题（spinbox 的
    菜单正是 exec 路径）。QSpinBox 不拦（本来就正常）。"""
    global _exec_menu_gate
    if _exec_menu_gate is not None:
        return

    class _Gate(QObject):
        def eventFilter(self, watched, ev):
            if ev.type() != QEvent.ContextMenu:
                return False
            target = watched
            # QPlainTextEdit/QTextEdit 是滚动区：真实右键事件落在其
            # viewport 子件上（viewport 的 parent 即编辑器本体）
            if isinstance(target, QWidget):
                parent = target.parentWidget()
                if isinstance(parent, (QPlainTextEdit, QTextEdit)):
                    target = parent
            if target.contextMenuPolicy() != Qt.ContextMenuPolicy.DefaultContextMenu:
                return False
            menu = None
            if isinstance(target, QLineEdit):
                menu = target.createStandardContextMenu()
            elif isinstance(target, (QPlainTextEdit, QTextEdit)):
                menu = target.createStandardContextMenu(ev.pos())
            elif isinstance(target, QComboBox) and target.lineEdit() is not None:
                menu = target.lineEdit().createStandardContextMenu()
            if menu is None:
                return False
            menu.setAttribute(Qt.WA_DeleteOnClose)
            menu.exec_(ev.globalPos())
            return True

    _app = QApplication.instance()
    _exec_menu_gate = _Gate(_app)
    _app.installEventFilter(_exec_menu_gate)


def _restore_combo_view_fonts():
    """setStyle 重扫描（延迟生效）会把 combo 弹出视图的字体重置为系统
    默认(9pt)。对受害控件无条件设显式字体——显式字体能在后续的延迟重置
    中存活。构造式 QFont(family, size)：拷贝式带空 resolve mask，
    setFont 等于清除显式字体，无效。"""
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
