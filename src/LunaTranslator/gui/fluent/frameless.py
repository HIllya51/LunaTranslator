"""FluentFramelessWindowMixin —— 无边框圆角窗口 mixin。

移植自 FluentUIStyle/PyQt5Examples/gallerywindow.py（qwindowkit 技法）：
保留 WS_THICKFRAME，用 WM_NCCALCSIZE 去掉原生标题栏占位（先 DefWindowProc
保留 L/R/B 系统边框 -> DWM 阴影 + 1px 边框 + Win11 圆角），WM_NCHITTEST 提供
拖动 / 8 向缩放 / 双击最大化 / Snap Layouts。

用法：混入 QMainWindow 子类（MRO 中放在窗口基类之前），在安装 FluentTitleBar
后所有钩子自动生效；未安装时 nativeEvent/showEvent 直通 super()，零开销。
仅支持 PyQt5（插件为 Qt5 构建）。
"""

import ctypes
import ctypes.wintypes as wt

from qtsymbols import QEvent, QPoint, QRect, Qt, QTimer

# Win32 常量
WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
WM_NCRBUTTONUP = 0x00A5
WM_SYSCOMMAND = 0x0112
WM_NCLBUTTONDOWN = 0x00A1
WM_NCDESTROY = 0x0082
WM_UAHDESTROYWINDOW = 0x0090        # 未公开消息
WM_UNREGISTER_WINDOW_SERVICES = 0x0272  # 未公开消息
HTCAPTION = 2
HTLEFT, HTRIGHT, HTTOP, HTTOPLEFT, HTTOPRIGHT = 10, 11, 12, 13, 14
HTBOTTOM, HTBOTTOMLEFT, HTBOTTOMRIGHT = 15, 16, 17
SM_CXSIZEFRAME = 32
SM_CXPADDEDBORDER = 92
SWP_FRAMECHANGED = 0x0020
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2
# 系统菜单
SC_SIZE, SC_MOVE, SC_MINIMIZE, SC_MAXIMIZE = 0xF000, 0xF010, 0xF020, 0xF030
SC_CLOSE, SC_RESTORE = 0xF060, 0xF120
MF_BYCOMMAND, MF_ENABLED, MF_GRAYED = 0x0, 0x0, 0x1
TPM_RETURNCALCMD = 0x0100
TPM_RIGHTBUTTON = 0x0002

user32 = ctypes.windll.user32
user32.GetSystemMenu.restype = ctypes.c_void_p
user32.GetSystemMenu.argtypes = [wt.HWND, wt.BOOL]
user32.TrackPopupMenu.restype = wt.BOOL
user32.TrackPopupMenu.argtypes = [wt.HWND, wt.UINT,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  wt.HWND, ctypes.c_void_p]


class _MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wt.HWND),
        ("message", wt.UINT),
        ("wParam", wt.WPARAM),
        ("lParam", wt.LPARAM),
        ("time", wt.DWORD),
        ("pt", wt.POINT),
        ("lPrivate", wt.DWORD),
    ]


class _NCCALCSIZE_PARAMS(ctypes.Structure):
    class _RECT3(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    _fields_ = [("rgrc", _RECT3 * 3), ("lppos", ctypes.c_void_p)]


# DefWindowProcW 需要显式的 64 位签名（LPARAM 是指针宽度，默认 c_int 会溢出）
_DefWindowProcW = ctypes.windll.user32.DefWindowProcW
_DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
_DefWindowProcW.restype = ctypes.c_ssize_t


class FluentFramelessWindowMixin:
    """叠加在 QMainWindow 子类链上的无边框外壳。

    需要窗口自身提供：self._fluent_title_bar（FluentTitleBar 实例）与
    self.hitTestWidgets()（标题栏内需要接收鼠标事件的控件列表）。
    """

    def _fluent_frameless_active(self):
        return getattr(self, "_fluent_title_bar", None) is not None

    # ---- 事件链 ----
    def showEvent(self, event):
        super().showEvent(event)
        if self._fluent_frameless_active() and not getattr(
            self, "_fluent_frameless_initialized", False
        ):
            self._fluent_frameless_initialized = True
            self._setup_frameless_native()
            # 标题栏原生化监控（见 eventFilter）
            self._fluent_title_bar.installEventFilter(self)

    def closeEvent(self, event):
        # 停掉仍在运行的动画（导航宽度动画等），避免销毁期间定时器触发已删对象
        try:
            from qtsymbols import QVariantAnimation

            for anim in self.findChildren(QVariantAnimation):
                anim.stop()
        except:
            pass
        super().closeEvent(event)

    def eventFilter(self, watched, event):
        if watched is self and event.type() in (
            QEvent.Type.WindowActivate,
            QEvent.Type.WindowDeactivate,
        ):
            bar = getattr(self, "_fluent_title_bar", None)
            if bar is not None:
                bar.setProperty(
                    "bar-active", event.type() == QEvent.Type.WindowActivate
                )
                try:
                    self.style().polish(bar)
                except:
                    pass
        elif (
            watched is getattr(self, "_fluent_title_bar", None)
            and event.type() == QEvent.Type.WinIdChange
        ):
            # 根本修复：有原生子窗口注入本窗口时（如弹窗容器残留），Qt 会把
            # 重叠的子控件（标题栏）提升为原生窗口——其自身 HWND 会盖住自己、
            # 吞掉全部鼠标命中（无 WM_NCHITTEST，只剩转发的
            # SETCURSOR/MOUSEACTIVATE/PARENTNOTIFY）。检测到即重新内嵌。
            QTimer.singleShot(0, self._fluent_reembed_titlebar)
        return super().eventFilter(watched, event)

    def _fluent_reembed_titlebar(self):
        bar = getattr(self, "_fluent_title_bar", None)
        if bar is not None and bar.testAttribute(Qt.WA_NativeWindow):
            bar.setAttribute(Qt.WA_NativeWindow, False)
            bar.hide()
            bar.show()

    # ---- 原生层 ----
    def _setup_frameless_native(self):
        """窗口首次显示后的原生层微调（同 qwindowkit winIdChanged）。"""
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32

            # 保留 WS_SYSMENU：HTCAPTION 右键/Alt+Space 由 DefWindowProc 弹出
            # 原生系统菜单（WM_NCCALCSIZE 已去掉标题栏区，不会透出原生按钮）
            # Win11：显式启用系统圆角（Luna 的 cornerornot 会把顶层窗口
            # 设成直角，这里在每次显示时重新声明）
            value = wt.DWORD(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wt.HWND(hwnd), wt.DWORD(DWMWA_WINDOW_CORNER_PREFERENCE),
                ctypes.byref(value), ctypes.sizeof(value))

            # 触发一次边框重建，让上述修改立即生效
            user32.SetWindowPos(
                wt.HWND(hwnd), None, 0, 0, 0, 0,
                SWP_FRAMECHANGED | 0x0001 | 0x0002 | 0x0004 | 0x0010)  # NOMOVE|NOSIZE|NOZORDER|NOACTIVATE
        except:
            pass

    def _frame_thickness(self):
        user32 = ctypes.windll.user32
        return (user32.GetSystemMetrics(SM_CXSIZEFRAME)
                + user32.GetSystemMetrics(SM_CXPADDEDBORDER))

    def nativeEvent(self, eventType, message):
        try:
            return self._native_event_impl(eventType, message)
        except Exception:
            # 窗口销毁过程中子控件可能已被删除，任何异常都不能向外抛
            # （否则会引发消息风暴，表现为退出时鼠标忙圈转个不停）
            try:
                return super().nativeEvent(eventType, message)
            except Exception:
                return False, 0

    def _native_event_impl(self, eventType, message):
        if eventType == b"windows_generic_MSG" and self._fluent_frameless_active():
            try:
                msg = _MSG.from_address(int(message))
            except Exception:
                return super().nativeEvent(eventType, message)

            # 销毁链路上的消息直接跳过（同 qwindowkit windowProc 的前置过滤）
            if msg.message in (WM_DESTROY, WM_CLOSE, WM_NCDESTROY,
                               WM_UAHDESTROYWINDOW, WM_UNREGISTER_WINDOW_SERVICES):
                return super().nativeEvent(eventType, message)

            if msg.message == WM_NCCALCSIZE and msg.wParam:
                # qwindowkit 的做法：先让 DefWindowProc 计算默认边框（保留
                # L/R/B 系统边框 -> DWM 阴影、1px 边框与 Win11 圆角），
                # 再把整个顶部框架（标题栏+上边框）去掉
                params = _NCCALCSIZE_PARAMS.from_address(int(msg.lParam))
                rect = params.rgrc[0]
                original_top = rect.top

                default_result = _DefWindowProcW(
                    wt.HWND(int(msg.hwnd)), WM_NCCALCSIZE, msg.wParam, msg.lParam)
                if default_result != 0:
                    return True, default_result
                rect.top = original_top

                if self.isMaximized() and not self.isFullScreen():
                    # 最大化时窗口比工作区大一圈缩放边框，把顶部缩回工作区
                    rect.top += self._frame_thickness()
                return True, 0

            if msg.message == WM_NCHITTEST:
                result = self._hit_test(int(msg.lParam))
                if result is not None:
                    return True, result

            if msg.message == WM_NCLBUTTONDOWN:
                # 非客户区（标题栏/边框）按下——Qt::Popup 的鼠标抓取收不到
                # 非客户区点击，颜色取色飞层会残留，在这里手动关闭
                from gui.fluent.colorpicker import close_color_flyouts

                close_color_flyouts()

            if msg.message == WM_NCRBUTTONUP:
                # Qt 会把 WM_NCRBUTTONUP 转成 QContextMenuEvent（DefWindowProc
                # 收不到，原生系统菜单不会自己弹出）——这里用 GetSystemMenu +
                # TrackPopupMenu 弹出真正的系统菜单（qwindowkit 同款做法）
                if self._show_title_bar_system_menu(int(msg.lParam)):
                    return True, 0

        return super().nativeEvent(eventType, message)

    def _show_title_bar_system_menu(self, l_param):
        """标题栏右键 → 原生系统菜单（GetSystemMenu + TrackPopupMenu）。"""
        bar = self._fluent_title_bar
        dpr = self.devicePixelRatioF() or 1.0
        x = ctypes.c_short(l_param & 0xFFFF).value
        y = ctypes.c_short((l_param >> 16) & 0xFFFF).value
        local = self.mapFromGlobal(QPoint(int(x / dpr), int(y / dpr)))
        bar_rect = QRect(bar.mapTo(self, QPoint(0, 0)), bar.size())
        if not bar_rect.contains(local):
            return False

        hwnd = wt.HWND(int(self.winId()))
        menu = user32.GetSystemMenu(hwnd, False)
        if not menu:
            return False

        maximized = self.isMaximized()
        minimized = self.isMinimized()
        states = (
            (SC_RESTORE, minimized or maximized),
            (SC_MOVE, not minimized and not maximized),
            (SC_SIZE, not minimized and not maximized),
            (SC_MINIMIZE, not maximized),
            (SC_MAXIMIZE, not maximized),
        )
        for cmd, enable in states:
            user32.EnableMenuItem(
                menu, cmd, MF_BYCOMMAND | (MF_ENABLED if enable else MF_GRAYED))

        # TrackPopupMenu 内部跑模态循环直到选择/取消；TPM_RETURNCALCMD 返回命令 id
        cmd = user32.TrackPopupMenu(
            menu, TPM_RETURNCALCMD | TPM_RIGHTBUTTON, x, y, 0, hwnd, None)
        if cmd:
            user32.PostMessageW(hwnd, WM_SYSCOMMAND, cmd, 0)
        return True

    def _hit_test(self, l_param):
        # lParam 为屏幕坐标（有符号 16 位打包，物理像素）；
        # Qt 的 mapFromGlobal / width / height 都是逻辑坐标，需按 DPR 换算
        dpr = self.devicePixelRatioF() or 1.0
        x = ctypes.c_short(l_param & 0xFFFF).value
        y = ctypes.c_short((l_param >> 16) & 0xFFFF).value
        local = self.mapFromGlobal(QPoint(int(x / dpr), int(y / dpr)))

        border = 0 if self.isMaximized() else int(self._frame_thickness() / dpr)
        width = self.width()
        height = self.height()

        if border > 0:
            on_left = local.x() < border
            on_right = local.x() >= width - border
            on_top = local.y() < border
            on_bottom = local.y() >= height - border
            if on_top and on_left:
                return HTTOPLEFT
            if on_top and on_right:
                return HTTOPRIGHT
            if on_bottom and on_left:
                return HTBOTTOMLEFT
            if on_bottom and on_right:
                return HTBOTTOMRIGHT
            if on_left:
                return HTLEFT
            if on_right:
                return HTRIGHT
            if on_top:
                return HTTOP
            if on_bottom:
                return HTBOTTOM

        # 标题栏背景 = 拖动区；标题栏里的交互控件 = 客户区
        bar = self._fluent_title_bar
        bar_rect = QRect(bar.mapTo(self, QPoint(0, 0)), bar.size())
        if bar_rect.contains(local):
            for widget in self.hitTestWidgets():
                wr = QRect(widget.mapTo(self, QPoint(0, 0)), widget.size())
                if wr.contains(local):
                    return None  # 交给 Qt 处理（HTCLIENT）
            # 命中标题栏空白区域或纯展示的图标/文字标签 -> 拖动
            child = bar.childAt(bar.mapFrom(self, local))
            if (child is None or child is bar
                    or child in (bar.iconLabel(), bar.titleLabel())):
                return HTCAPTION
            return None  # 未知子控件，交给 Qt

        return None
