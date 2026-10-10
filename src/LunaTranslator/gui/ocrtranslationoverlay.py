"""OCR translation display, source provenance, and capture exclusion.

No changes to translation engines or user credentials are required.
"""

import ctypes
import math
import sys
import threading
import weakref
from contextlib import contextmanager
from ctypes.wintypes import HWND, DWORD, BOOL
from typing import NamedTuple

from qtsymbols import *
import windows, gobject
from myutils.config import globalconfig

if isqt5:
    from PyQt5.QtCore import QThread
else:
    from PyQt6.QtCore import QThread


class OCRCaptureSnapshot(NamedTuple):
    """Selection revision and physical rectangle at the start of recognition."""

    revision: int
    rect: tuple


class OCRRegionText(str):
    """Plain text at existing API/storage boundaries, with transient provenance.

    OCR managers attach this source to the parsed result at recognition commit.
    Dispatch must reuse it, rather than relabeling the result with a later revision.
    block_index 携带块级来源（原地按位置绘制）：None = 整个选框一条译文。
    """

    def __new__(cls, text, target, revision, owner=None, block_index=None):
        obj = super().__new__(cls, text)
        obj.ocr_overlay_context = (weakref.ref(target), revision)
        obj.ocr_overlay_owner = weakref.ref(owner) if owner is not None else None
        obj.ocr_block_index = block_index
        return obj


class OCRRegionBatch(str):
    def __new__(cls, sources):
        sources = tuple(sources)
        obj = super().__new__(cls, "\n".join(sources))
        obj.ocr_region_sources = sources
        return obj


def overlay_source_is_current(source):
    context = getattr(source, "ocr_overlay_context", None)
    if context is None:
        return False
    target, revision = context
    target = target()
    if target is None or target._ocr_overlay_revision != revision:
        return False
    owner_ref = getattr(source, "ocr_overlay_owner", None)
    if owner_ref is not None:
        owner = owner_ref()
        if owner is None or getattr(owner, "ending", False):
            return False
        if not any(r.range_ui is target for r in owner.ranges):
            return False
    return True


class OCRRegionTask:
    # The translator queue treats this as a protected request. Its validity is
    # per region, so a newer request from another region cannot cancel it.
    ocr_overlay_task = True

    def __init__(self, source):
        self.source = source

    def is_current(self):
        return globalconfig.get(
            "ocr_translation_overlay", False
        ) and overlay_source_is_current(self.source)


def route_overlay_translation(source, engine, text):
    if not overlay_source_is_current(source):
        return
    target, revision = source.ocr_overlay_context
    target = target()
    try:
        target.overlaytranslationsignal.emit(
            (revision, engine, text, getattr(source, "ocr_block_index", None))
        )
    except RuntimeError:
        # The region may have been closed while an engine was finishing.
        pass


_overlays = weakref.WeakSet()
_capture_guard = None
_capture_suspensions = 0
_capture_epoch = 0

# 原地显示翻译的对齐方式（设置页 combobox 的 internal 值 -> Qt 旗标）。
# 用 int 组合：TextFlag | (Alignment 旗标对象) 在 PyQt5 下会 TypeError，
# 且 paintEvent 内的异常会直接 qFatal 整个进程。
_OVERLAY_ALIGN_FLAGS = {
    "topleft": int(Qt.AlignmentFlag.AlignLeft) | int(Qt.AlignmentFlag.AlignTop),
    "topright": int(Qt.AlignmentFlag.AlignRight) | int(Qt.AlignmentFlag.AlignTop),
    "topcenter": int(Qt.AlignmentFlag.AlignHCenter) | int(Qt.AlignmentFlag.AlignTop),
    "center": int(Qt.AlignmentFlag.AlignHCenter) | int(Qt.AlignmentFlag.AlignVCenter),
}
_OVERLAY_ALIGN_DEFAULT = "topleft"
# 适配/扩展共用的测量旗标（左对齐换行测量所需宽高）
_OVERLAY_MEASURE_FLAGS = int(Qt.TextFlag.TextWordWrap) | int(
    Qt.AlignmentFlag.AlignLeft
)


def ocr_popup_is_visible():
    # Readable from the main window's topmost check without querying widgets.
    return bool(
        _capture_suspensions
        or (_capture_guard is not None and _capture_guard._visible_popup)
    )


@contextmanager
def suspend_ocr_capture():
    """Keep OCR from capturing selection menus, including in-flight captures."""
    global _capture_suspensions, _capture_epoch
    _capture_epoch += 1
    _capture_suspensions += 1
    try:
        yield
    finally:
        # The popup has closed; wait for its pixels to leave the composed frame.
        try:
            ctypes.windll.dwmapi.DwmFlush()
        except (AttributeError, OSError):
            pass
        _capture_epoch += 1
        _capture_suspensions -= 1


def _windows_build():
    # The embedded launcher may lack a supportedOS manifest. GetVersionEx (and
    # sys.getwindowsversion().build) can then report 9200 on a modern Windows OS.
    class VersionInfo(ctypes.Structure):
        _fields_ = [
            ("size", DWORD),
            ("major", DWORD),
            ("minor", DWORD),
            ("build", DWORD),
            ("platform", DWORD),
            ("service_pack", ctypes.c_wchar * 128),
        ]

    try:
        version = VersionInfo()
        version.size = ctypes.sizeof(version)
        api = ctypes.windll.ntdll.RtlGetVersion
        api.argtypes = (ctypes.POINTER(VersionInfo),)
        api.restype = ctypes.c_long
        if api(ctypes.byref(version)) == 0:
            return version.build
    except (AttributeError, OSError):
        pass
    return sys.getwindowsversion().build


def _exclude_from_capture(hwnd):
    # Older systems interpret 0x11 as a black rectangle, which would hide OCR text.
    if _windows_build() < 19041:
        return False
    try:
        api = ctypes.windll.user32.SetWindowDisplayAffinity
        api.argtypes = (HWND, DWORD)
        api.restype = BOOL
        return bool(api(int(hwnd), 0x11))
    except (AttributeError, OSError):
        return False


class _CaptureRequest:
    def __init__(self, capture):
        self.capture = capture
        self.finished = threading.Event()
        self.result = None
        self.error = None
        self.cancelled = False


class _CaptureGuard(QObject):
    requested = pyqtSignal(object)

    def __init__(self):
        super().__init__(QApplication.instance())
        self.requested.connect(self.run)
        # Keep wrappers alive only while visible; Hide/destroy removes them.
        # Otherwise a Qt-owned dialog can lose its Python wrapper mid-capture.
        self._windows = {}
        self._window_rectangles = ()
        self._tracked = weakref.WeakSet()
        self._popups = set()
        self._visible_popup = False
        self._tracking = False
        self._flushed_epoch = _capture_epoch
        QApplication.instance().installEventFilter(self)
        # Settings can already be open when the first OCR region is created.
        for window in QApplication.topLevelWidgets():
            if self._is_popup(window):
                self._track_popup(window, window.isVisible())
            else:
                self._track_window(window)

    @staticmethod
    def _is_popup(window):
        # 任何 Qt::Popup 顶层都按可见性暂停截图：菜单、PopupWidget 飞层
        # （样式/取色器等——它们可能正好盖在 OCR 选区上）。
        # 事件过滤器会看到非控件 QObject，须先判 QWidget
        return isinstance(window, QMenu) or (
            isinstance(window, QWidget)
            and window.isWindow()
            and window.windowType() == Qt.WindowType.Popup
        )

    def _track_popup(self, popup, visible):
        global _capture_epoch
        if visible == (popup in self._popups):
            return
        if visible:
            self._popups.add(popup)
        else:
            self._popups.discard(popup)
        self._visible_popup = bool(self._popups)
        _capture_epoch += 1

    def _remove_window(self, ref):
        global _capture_epoch
        window = ref()
        if window in self._windows:
            self._windows.pop(window, None)
            self._window_rectangles = tuple(
                (weakref.ref(window), rect) for window, rect in self._windows.items()
            )
            _capture_epoch += 1

    @staticmethod
    def _flush_frame():
        try:
            ctypes.windll.dwmapi.DwmFlush()
        except (AttributeError, OSError):
            pass

    def flush_pending_frame(self):
        epoch = _capture_epoch
        if epoch != self._flushed_epoch:
            # Never wait for composition inside Qt show/move event delivery:
            # the GUI must finish processing that event before it can paint.
            self._flush_frame()
            self._flushed_epoch = epoch

    def _track_window(self, window):
        global _capture_epoch
        # Qt also creates private top-level widgets for popup animations.
        # Observe main windows and dialogs, not those internal helpers. Menus
        # suspend capture by visibility without inspecting native popup handles.
        if (
            self._tracking
            or not isinstance(window, (QMainWindow, QDialog))
            or not window.isWindow()
        ):
            return
        # The selection and its overlay are handled separately. The main
        # translation window keeps imageCutEx's existing capture behavior.
        if any(window is o or window is o.region for o in list(_overlays)):
            self._remove_window(weakref.ref(window))
            return
        base = getattr(gobject, "base", None)
        if window is getattr(base, "translation_ui", None):
            self._remove_window(weakref.ref(window))
            return
        self._tracking = True
        try:
            rectangle = None
            if window.isVisible() and not window.isMinimized():
                # Observe an existing handle; winId() can create a native
                # popup reentrantly while Qt is still delivering Show.
                hwnd = int(window.effectiveWinId())
                if not hwnd:
                    return
                rectangle = tuple(windows.GetWindowRect(hwnd))
                if window not in self._tracked:
                    self._tracked.add(window)
                    ref = weakref.ref(window)
                    window.destroyed.connect(lambda: self._remove_window(ref))
            if rectangle == self._windows.get(window):
                return
            if rectangle is None:
                self._windows.pop(window, None)
            else:
                self._windows[window] = rectangle
            self._window_rectangles = tuple(
                (weakref.ref(window), rect) for window, rect in self._windows.items()
            )
            # Reject captures spanning a popup show/hide/move, including ABA.
            _capture_epoch += 1
        finally:
            self._tracking = False

    def eventFilter(self, window, event):
        if self._is_popup(window):
            if event.type() in (
                QEvent.Type.Show,
                QEvent.Type.Hide,
                QEvent.Type.DeferredDelete,
            ):
                self._track_popup(window, event.type() == QEvent.Type.Show)
            return False
        if event.type() in (
            QEvent.Type.Show,
            QEvent.Type.Hide,
            QEvent.Type.Move,
            QEvent.Type.Resize,
            QEvent.Type.WindowStateChange,
            QEvent.Type.WinIdChange,
        ):
            self._track_window(window)
        return False

    def blocks_capture(self, rect):
        # Only cached Python geometry is read from OCR workers, never widgets.
        if self._visible_popup:
            return True
        main = getattr(getattr(gobject, "base", None), "translation_ui", None)
        rectangles = tuple(
            rect for window, rect in self._window_rectangles if window() is not main
        )
        if rect is None:
            return bool(rectangles)
        x, y, width, height = rect.getRect()
        return any(
            x < right and x + width > left and y < bottom and y + height > top
            for left, top, right, bottom in rectangles
        )

    def run(self, request):
        hidden = []
        try:
            if request.cancelled or _capture_suspensions:
                return
            for overlay in list(_overlays):
                if not overlay.capture_excluded and overlay.isVisible():
                    overlay.hide()
                    hidden.append(overlay)
            if hidden:
                # Wait for composition before capturing; no QWidget access in workers.
                try:
                    ctypes.windll.dwmapi.DwmFlush()
                except (AttributeError, OSError):
                    pass
            request.result = request.capture()
        except Exception as error:
            request.error = error
        finally:
            for overlay in hidden:
                overlay.sync()
            request.finished.set()


def capture_without_overlays(capture, rect=None):
    guard = _capture_guard
    if _capture_suspensions or (guard is not None and guard.blocks_capture(rect)):
        return None
    epoch = _capture_epoch

    def guarded_capture():
        if _capture_suspensions or epoch != _capture_epoch:
            return None
        if guard is not None:
            guard.flush_pending_frame()
        if _capture_suspensions or epoch != _capture_epoch:
            return None
        result = capture()
        # A menu may have opened/closed while native capture released the GIL.
        return result if not _capture_suspensions and epoch == _capture_epoch else None

    # Excluded overlays are omitted by Windows without hiding or flickering.
    # The fallback runs captures on the GUI thread and temporarily hides overlays.
    if guard is None or not any(
        o._capture_visible and not o.capture_excluded for o in list(_overlays)
    ):
        return guarded_capture()
    request = _CaptureRequest(guarded_capture)
    if QThread.currentThread() == guard.thread():
        guard.run(request)
    else:
        guard.requested.emit(request)
        if not request.finished.wait(2):
            request.cancelled = True
            return None
    if request.error is not None:
        raise request.error
    return request.result


def refresh_overlays():
    """显示设置变化（译文跟随字号/字体/居中显示等）后重算覆盖层。

    sync 幂等：paint_key 变化才触发重绘。"""
    for overlay in list(_overlays):
        try:
            overlay.sync()
        except RuntimeError:
            pass


class OCRTranslationOverlay(QWidget):
    def __init__(self, region):
        super().__init__(region)
        self._native_ready = False
        self._capture_visible = False
        self._applying_native_flags = False
        self._native_hwnd = None
        self._geometry_window_handle = None
        self._last_rect = None
        self._last_paint_key = None
        self.region = region
        self.results = {}
        self.text = ""
        self.revision = region._ocr_overlay_revision
        # 块级显示（原地按位置绘制）：块区域（选框图像物理像素）与
        # 每块各引擎的译文。无块区域（图片翻译/不输出坐标的 OCR）时
        # 走整框绘制（self.text）。
        self.block_rects = None
        self.block_results = {}
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.capture_excluded = False
        _overlays.add(self)
        global _capture_guard
        if _capture_guard is None:
            _capture_guard = _CaptureGuard()
        self._native_ready = True

    def _apply_native_flags(self):
        if not self._native_ready or self._applying_native_flags:
            return
        self._applying_native_flags = True
        try:
            hwnd = int(self.winId())
            if hwnd != self._native_hwnd:
                self._last_rect = None
                self._native_hwnd = hwnd
            handle = self.windowHandle()
            if handle is not None and handle is not self._geometry_window_handle:
                handle.screenChanged.connect(self._resync_screen_geometry)
                self._geometry_window_handle = handle
            windows.WindowFocus.giveup(hwnd)
            windows.MouseTrans.set(hwnd)
            self.capture_excluded = _exclude_from_capture(hwnd)
        finally:
            self._applying_native_flags = False

    def event(self, event):
        result = super().event(event)
        if (
            event.type() == QEvent.Type.WinIdChange
            and getattr(self, "_native_ready", False)
            and self.isVisible()
        ):
            self._apply_native_flags()
        return result

    def _resync_screen_geometry(self, *_):
        # Qt applies a suggested size when native movement crosses monitors
        # with different DPI. Restore the selection's physical rectangle
        # after that transition, even when no new OCR result arrives.
        self._last_rect = None
        QTimer.singleShot(0, self.sync)

    def showEvent(self, event):
        super().showEvent(event)
        self._capture_visible = True
        # Qt may replace the native handle or reset its flags on first show.
        self._last_rect = None
        self._apply_native_flags()

    def hideEvent(self, event):
        self._capture_visible = False
        super().hideEvent(event)

    @staticmethod
    def _preferred_text(results: dict):
        # 同主窗口的引擎优先级：首选引擎 > 排序列表 > 任意
        preferred = globalconfig.get("toppest_translator")
        if preferred in results:
            return results[preferred]
        for key in globalconfig.get("fix_translate_rank_rank", []):
            if key in results:
                return results[key]
        return next(iter(results.values()), "")

    def _blocktexts(self):
        """当前可绘制的块译文：[(块序号, 译文), ...]。"""
        if not self.block_rects:
            return []
        out = []
        for i in range(len(self.block_rects)):
            texts = self.block_results.get(i)
            if not texts:
                continue
            text = self._preferred_text(texts)
            if text:
                out.append((i, text))
        return out

    def receive(self, payload):
        revision, engine, text, blockidx = payload
        if revision != self.region._ocr_overlay_revision:
            return
        if revision != self.revision or engine is None:
            self.results.clear()
            self.text = ""
            self.block_results.clear()
            self.revision = revision
        if engine is not None and text:
            if blockidx is None:
                self.results[engine] = text
                self.text = self._preferred_text(self.results)
            else:
                self.block_results.setdefault(blockidx, {})[engine] = text
        self.sync()

    def receive_layout(self, payload):
        """识别提交时发布的块区域布局（信号从 OCR 工作线程排队而来）。

        rects：各块 box4（选框图像物理像素）；None = 本轮无坐标，退回
        整框绘制。布局先于块译文到达。"""
        revision, rects = payload
        if revision != self.region._ocr_overlay_revision:
            return
        if revision != self.revision:
            self.results.clear()
            self.text = ""
            self.block_results.clear()
            self.revision = revision
        self.block_rects = tuple(tuple(r) for r in rects) if rects else None
        self.sync()

    def background_color(self):
        color = QColor(
            globalconfig.get("ocr_translation_overlay_background", "#ffffffff")
        )
        if not color.isValid():
            color = QColor(Qt.GlobalColor.white)
        return color

    def text_color(self):
        color = QColor(globalconfig.get("ocr_translation_overlay_textcolor", "#000000"))
        if not color.isValid():
            color = QColor(Qt.GlobalColor.black)
        return color

    def sync(self):
        rect = self.region.getrect()
        if (
            not globalconfig.get("ocr_translation_overlay", False)
            or not (self.text or self._blocktexts())
            or not rect.isValid()
            or not self.region.isVisible()
        ):
            if self.isVisible():
                self.hide()
            return
        showing = not self.isVisible()
        if showing:
            self.show()
        geometry = (
            rect.x(),
            rect.y(),
            rect.width(),
            rect.height(),
            self.devicePixelRatioF(),
        )
        if geometry != self._last_rect:
            # Avoid MoveWindow(repaint=True) on every 10 ms follow-window tick.
            windows.MoveWindow(int(self.winId()), *geometry[:4], False)
            self._last_rect = geometry
        if showing:
            self.raise_()
            # A pending translation can show another overlay while a selection
            # menu's nested event loop is running. Keep its popup on top.
            popup = QApplication.activePopupWidget()
            if popup is not None:
                popup.raise_()
        paint_key = (
            self.text,
            self.block_rects,
            tuple(
                sorted(
                    (k, tuple(sorted(v.items())))
                    for k, v in self.block_results.items()
                )
            ),
            geometry,
            globalconfig.get("fonttype2", ""),
            globalconfig.get("fontsize", 16),
            globalconfig.get("showbold_trans", False),
            globalconfig.get(
                "ocr_translation_overlay_alignment", _OVERLAY_ALIGN_DEFAULT
            ),
            globalconfig.get("ocr_translation_overlay_background", "#ffffffff"),
            globalconfig.get("ocr_translation_overlay_textcolor", "#000000"),
        )
        if showing or paint_key != self._last_paint_key:
            self._last_paint_key = paint_key
            self.update()

    def _translation_font(self):
        """译文字体（字体/字号/加粗设置，同主窗口译文显示）。"""
        font = QFont(globalconfig.get("fonttype2", "") or "Microsoft YaHei")
        try:
            size = float(globalconfig.get("fontsize", 16))
        except (TypeError, ValueError):
            size = 16
        if size > 0:
            font.setPointSizeF(size)
        font.setBold(globalconfig.get("showbold_trans", False))
        return font

    def fitted_font(self, text_rect, text=None, maximum=100, minimum=12):
        """按区域尺寸二分适配字号；下限 minimum——分析出的字号不能过小，
        放不下时由调用方扩展绘制区域（见 _expanded_text_rect）。"""
        if text is None:
            text = self.text
        font = QFont(globalconfig.get("fonttype2", "") or "Microsoft YaHei")
        font.setBold(globalconfig.get("showbold_trans", False))
        flags = int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft)
        # Fit by pixel size so the requested size has the same meaning across Qt versions.
        low, high = min(minimum, maximum), maximum
        while low < high:
            size = (low + high + 1) // 2
            font.setPixelSize(size)
            bounds = QFontMetrics(font).boundingRect(text_rect, flags, text)
            if (
                bounds.height() <= text_rect.height()
                and bounds.width() <= text_rect.width()
            ):
                low = size
            else:
                high = size - 1
        font.setPixelSize(low)
        return font

    @staticmethod
    def _text_fits(font, text_rect, text):
        bounds = QFontMetrics(font).boundingRect(
            text_rect, _OVERLAY_MEASURE_FLAGS, text
        )
        return (
            bounds.width() <= text_rect.width()
            and bounds.height() <= text_rect.height()
        )

    def _expanded_text_rect(self, inner, font, text, bounds=None):
        """块内放不下时的扩展绘制区：按块宽换行所需的尺寸放大、按对齐
        锚点定位、再平移回绘制范围内——译文必须完整显示，不能被裁掉。
        bounds：当前坐标系的可用范围（水平块=选框，倾斜块=局部范围）。"""
        fm = QFontMetrics(font)
        needed = fm.boundingRect(
            QRect(0, 0, inner.width(), 1 << 20), _OVERLAY_MEASURE_FLAGS, text
        )
        w = max(inner.width(), needed.width())
        needed = fm.boundingRect(
            QRect(0, 0, w, 1 << 20), _OVERLAY_MEASURE_FLAGS, text
        )
        h = max(inner.height(), needed.height())
        align = globalconfig.get(
            "ocr_translation_overlay_alignment", _OVERLAY_ALIGN_DEFAULT
        )
        if align == "topright":
            top_left = QPoint(inner.right() - w + 1, inner.top())
        elif align == "topcenter":
            top_left = QPoint(inner.center().x() - w // 2, inner.top())
        elif align == "center":
            center = inner.center()
            top_left = QPoint(center.x() - w // 2, center.y() - h // 2)
        else:
            top_left = inner.topLeft()
        new = QRect(top_left, QSize(w, h))
        # 平移进绘制范围；范围本身放不下时才裁边
        if bounds is None:
            bounds = self.rect()
        if bounds.width() > 0 and bounds.height() > 0:
            if new.right() > bounds.right():
                new.moveRight(bounds.right())
            if new.left() < bounds.left():
                new.moveLeft(bounds.left())
            if new.bottom() > bounds.bottom():
                new.moveBottom(bounds.bottom())
            if new.top() < bounds.top():
                new.moveTop(bounds.top())
            new = new.intersected(bounds)
        return new

    def _alignment_flags(self):
        # 原地显示翻译自己的对齐设置（不共用文本设置的居中显示）
        return int(Qt.TextFlag.TextWordWrap) | _OVERLAY_ALIGN_FLAGS.get(
            globalconfig.get(
                "ocr_translation_overlay_alignment", _OVERLAY_ALIGN_DEFAULT
            ),
            _OVERLAY_ALIGN_FLAGS[_OVERLAY_ALIGN_DEFAULT],
        )

    def _local_widget_bounds(self, p0, ang):
        """选框（覆盖层）四角逆变换到旋转局部坐标的 AABB——倾斜块
        扩展/绘制时的可用范围。"""
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        W, H = self.width(), self.height()
        us, vs = [], []
        for x, y in ((0, 0), (W, 0), (W, H), (0, H)):
            dx, dy = x - p0.x(), y - p0.y()
            us.append(dx * ca + dy * sa)
            vs.append(-dx * sa + dy * ca)
        u1, u2, v1, v2 = min(us), max(us), min(vs), max(vs)
        if u2 <= u1 or v2 <= v1:
            return self.rect()
        return QRect(round(u1), round(v1), round(u2 - u1), round(v2 - v1))

    def _block_layout(self, i, text, cap, dpr):
        """单块绘制布局：返回 (transform, inner, outer, font)。

        transform=None 为近水平块（AABB 绘制，行为同旧版）；否则
        (p0, angle)——在 p0 平移、angle 旋转的坐标系中绘制，倾斜的
        OCR 结果让译文同样倾斜。块过小放不下时向外扩展保证完整。"""
        quad = self.block_rects[i]
        pts = [QPointF(quad[j] / dpr, quad[j + 1] / dpr) for j in (0, 2, 4, 6)]
        p0, p1, p2, p3 = pts
        ang = math.degrees(math.atan2(p1.y() - p0.y(), p1.x() - p0.x()))
        w = (
            math.hypot(p1.x() - p0.x(), p1.y() - p0.y())
            + math.hypot(p2.x() - p3.x(), p2.y() - p3.y())
        ) / 2
        h = (
            math.hypot(p3.x() - p0.x(), p3.y() - p0.y())
            + math.hypot(p2.x() - p1.x(), p2.y() - p1.y())
        ) / 2
        if abs(ang) < 0.3 or w <= 1 or h <= 1:
            # 近水平：AABB 绘制（避免变换取整带来的漂移）
            xs = [p.x() for p in pts]
            ys = [p.y() for p in pts]
            rect = QRectF(
                min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
            )
            transform = None
            bounds = self.rect()
        else:
            rect = QRectF(0, 0, w, h)
            transform = (p0, ang)
            bounds = self._local_widget_bounds(p0, ang)
        margin = min(4, max(1, int(min(rect.width(), rect.height()) // 12)))
        inner = rect.adjusted(margin, margin, -margin, -margin).toAlignedRect()
        if inner.isEmpty():
            # 极小块：不留边距，整块作绘制区
            margin = 0
            inner = rect.toAlignedRect()
        if inner.isEmpty():
            return None
        font = self.fitted_font(inner, text, cap)
        if not self._text_fits(font, inner, text):
            # 块过小放不下：字号保持（≥下限），向外扩展绘制区
            inner = self._expanded_text_rect(inner, font, text, bounds)
        outer = inner.adjusted(-margin, -margin, margin, margin)
        return transform, inner, outer, font

    def paintEvent(self, event):
        painter = QPainter(self)
        flags = self._alignment_flags()
        # 块级：各 OCR 结果区域按位置单独绘制；背景色只画在文字块上，
        # 不铺满整个选框；字号 = 译文字号与按区域尺寸适配字号中的较小者
        blocks = self._blocktexts()
        if blocks:
            dpr = self.devicePixelRatioF() or 1.0
            cap = max(6, min(100, QFontInfo(self._translation_font()).pixelSize()))
            bg = self.background_color()
            pen = self.text_color()
            layouts = []
            for i, text in blocks:
                layout = self._block_layout(i, text, cap, dpr)
                if layout is not None:
                    layouts.append((layout, text))
            # 先画所有背景、再画所有文字：相邻块的背景不会遮挡另一块的文字
            for (transform, inner, outer, font), text in layouts:
                painter.save()
                if transform is not None:
                    painter.translate(transform[0])
                    painter.rotate(transform[1])
                painter.setClipRect(outer)
                painter.fillRect(outer, bg)
                painter.restore()
            for (transform, inner, outer, font), text in layouts:
                painter.save()
                if transform is not None:
                    painter.translate(transform[0])
                    painter.rotate(transform[1])
                painter.setClipRect(outer)
                painter.setFont(font)
                painter.setPen(pen)
                painter.drawText(inner, flags, text)
                painter.restore()
            painter.end()
            return
        # 无坐标（图片翻译、不输出坐标的 OCR）：整框绘制（原行为）
        painter.fillRect(self.rect(), self.background_color())
        margin = min(8, max(1, min(self.width(), self.height()) // 12))
        text_rect = self.rect().adjusted(margin, margin, -margin, -margin)
        painter.setClipRect(text_rect)
        painter.setFont(self.fitted_font(text_rect))
        painter.setPen(self.text_color())
        painter.drawText(text_rect, flags, self.text)
        painter.end()
