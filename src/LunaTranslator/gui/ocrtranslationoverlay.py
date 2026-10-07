"""OCR translation display, source provenance, and capture exclusion.

No changes to translation engines or user credentials are required.
"""

import ctypes
import sys
import threading
import uuid
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
    """

    def __new__(cls, text, target, revision, owner=None):
        obj = super().__new__(cls, text)
        obj.ocr_overlay_context = (weakref.ref(target), revision)
        obj.ocr_overlay_owner = weakref.ref(owner) if owner is not None else None
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
        target.overlaytranslationsignal.emit((revision, engine, text))
    except RuntimeError:
        # The region may have been closed while an engine was finishing.
        pass


_overlays = weakref.WeakSet()
_capture_guard = None
_capture_suspensions = 0
_capture_epoch = 0


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


def sample_background(image):
    """Estimate the inner background, tolerating borders and small selection overshoot."""
    if image.isNull():
        return None
    width, height = image.width(), image.height()
    # Selection borders and nearby panels should not decide the fill color.
    inset_x = int(width * 0.12) if width >= 8 else 0
    inset_y = int(height * 0.12) if height >= 8 else 0
    inner_width, inner_height = width - 2 * inset_x, height - 2 * inset_y
    nx, ny = min(24, inner_width), min(16, inner_height)
    radius = max(1, min(3, round(min(width, height) / 64)))
    all_bins, flat_bins = {}, {}
    for row in range(ny):
        fy = (row + 0.5) / ny
        y = inset_y + min(inner_height - 1, int(fy * inner_height))
        for col in range(nx):
            fx = (col + 0.5) / nx
            x = inset_x + min(inner_width - 1, int(fx * inner_width))
            color = image.pixelColor(x, y)
            if color.alpha() < 128:
                continue
            rgb = color.red(), color.green(), color.blue()
            # Give the middle more influence than the edge of the sampling area.
            weight = 1 + 2 * (1 - abs(2 * fx - 1)) * (1 - abs(2 * fy - 1))
            flat = True
            for dx, dy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
                neighbor = image.pixelColor(
                    max(0, min(width - 1, x + dx)), max(0, min(height - 1, y + dy))
                )
                if (
                    neighbor.alpha() >= 128
                    and max(abs(a - b) for a, b in zip(rgb, neighbor.getRgb()[:3])) > 24
                ):
                    flat = False
                    break
            bucket = tuple(channel // 32 for channel in rgb)
            for bins in (all_bins, flat_bins) if flat else (all_bins,):
                entry = bins.setdefault(bucket, [0, 0, 0, 0])
                entry[0] += weight
                for channel in range(3):
                    entry[channel + 1] += weight * rgb[channel]
    if not all_bins:
        return None
    # Text strokes and sharp transitions are poor background samples. For a
    # textured image with few flat points, keep the general weighted estimate.
    flat_weight = sum(entry[0] for entry in flat_bins.values())
    all_weight = sum(entry[0] for entry in all_bins.values())
    bins = flat_bins if flat_weight >= all_weight * 0.35 else all_bins
    colors = {
        key: tuple(value / entry[0] for value in entry[1:])
        for key, entry in bins.items()
    }
    best = None
    # Merge close shades across quantization boundaries, e.g. 223 and 224.
    # Otherwise one background can split into weaker bins than an outside panel.
    for key, rgb in colors.items():
        group = [0, 0, 0, 0]
        for dr in (-1, 0, 1):
            for dg in (-1, 0, 1):
                for db in (-1, 0, 1):
                    neighbor_key = key[0] + dr, key[1] + dg, key[2] + db
                    neighbor_rgb = colors.get(neighbor_key)
                    if (
                        neighbor_rgb is None
                        or max(abs(a - b) for a, b in zip(rgb, neighbor_rgb)) > 24
                    ):
                        continue
                    entry = bins[neighbor_key]
                    for channel in range(4):
                        group[channel] += entry[channel]
        if best is None or group[0] > best[0]:
            best = group
    return tuple(round(value / best[0]) for value in best[1:])


def contrasting_text_color(rgb):
    def linear(channel):
        value = channel / 255.0
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in rgb)
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    black_contrast = (luminance + 0.05) / 0.05
    white_contrast = 1.05 / (luminance + 0.05)
    return QColor("black" if black_contrast >= white_contrast else "white")


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
        return isinstance(window, QMenu) or (
            isinstance(window, QFrame)
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
        self.background_rgb = (20, 20, 24)
        self.region = region
        self.results = {}
        self.text = ""
        self.revision = region._ocr_overlay_revision
        self.font_size = 22
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

    def receive(self, payload):
        revision, engine, text = payload
        if revision != self.region._ocr_overlay_revision:
            return
        if revision != self.revision or engine is None:
            self.results.clear()
            self.text = ""
            self.revision = revision
        if engine is not None and text:
            self.results[engine] = text
            rank = list(globalconfig.get("fix_translate_rank_rank", []))
            preferred = globalconfig.get("toppest_translator")
            if preferred in self.results:
                chosen = preferred
            else:
                chosen = next(
                    (key for key in rank if key in self.results),
                    next(iter(self.results)),
                )
            self.text = self.results[chosen]
        self.sync()

    def receive_background(self, payload):
        rect, rgb = payload
        # A capture may finish after the selection has moved or been replaced.
        if rect != self.region.getrect().getRect():
            return
        # Ignore capture noise instead of repainting the panel every OCR tick.
        if max(abs(a - b) for a, b in zip(rgb, self.background_rgb)) <= 6:
            return
        self.background_rgb = tuple(rgb)
        self.sync()

    def background_colors(self):
        if globalconfig.get("ocr_translation_overlay_adaptive_background", True):
            return self.background_rgb, contrasting_text_color(self.background_rgb)
        return (20, 20, 24), QColor("white")

    def sync(self):
        rect = self.region.getrect()
        if (
            not globalconfig.get("ocr_translation_overlay", False)
            or not self.text
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
            geometry,
            globalconfig.get("fonttype2", ""),
            globalconfig.get("ocr_translation_overlay_fontsize", 22),
            globalconfig.get("ocr_translation_overlay_opacity", 0.95),
            self.background_colors()[0],
        )
        if showing or paint_key != self._last_paint_key:
            self._last_paint_key = paint_key
            self.update()

    def fitted_font(self, text_rect):
        font = QFont(globalconfig.get("fonttype2", "") or "Microsoft YaHei")
        maximum = max(
            6, min(100, int(globalconfig.get("ocr_translation_overlay_fontsize", 22)))
        )
        flags = int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft)
        # Fit by pixel size so the requested size has the same meaning across Qt versions.
        low, high = 6, maximum
        while low < high:
            size = (low + high + 1) // 2
            font.setPixelSize(size)
            bounds = QFontMetrics(font).boundingRect(text_rect, flags, self.text)
            if (
                bounds.height() <= text_rect.height()
                and bounds.width() <= text_rect.width()
            ):
                low = size
            else:
                high = size - 1
        font.setPixelSize(low)
        self.font_size = low
        return font

    def paintEvent(self, event):
        painter = QPainter(self)
        alpha = max(
            0.1,
            min(1.0, float(globalconfig.get("ocr_translation_overlay_opacity", 0.95))),
        )
        background, foreground = self.background_colors()
        painter.fillRect(self.rect(), QColor(*background, round(alpha * 255)))
        margin = min(8, max(1, min(self.width(), self.height()) // 12))
        text_rect = self.rect().adjusted(margin, margin, -margin, -margin)
        painter.setClipRect(text_rect)
        painter.setFont(self.fitted_font(text_rect))
        painter.setPen(foreground)
        flags = int(
            Qt.TextFlag.TextWordWrap
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        painter.drawText(text_rect, flags, self.text)
        painter.end()


class OCRToolbarMode(QObject):
    """Keep the main window as a usable toolbar while OCR overlays display text."""

    def __init__(self, window, icon_size):
        super().__init__(window)
        self.window = window
        self.icon_size = icon_size
        self.active = False
        self._syncing = False
        self._orientation = None

    def _stop_animations(self):
        for name in ("smooth_resizer", "smooth_resizer2", "smooth_resizer4"):
            animation = getattr(self.window, name, None)
            if animation is not None:
                animation.stop()

    def save_geometry(self, rect):
        # Persist the expanded dimensions, even if the app exits while folded.
        x, y, width, height = rect
        if self.active:
            if self._orientation:
                if not self._syncing:
                    self._expanded_size.setHeight(height)
                width = self._expanded_size.width()
            else:
                if not self._syncing:
                    self._expanded_size.setWidth(width)
                height = self._expanded_size.height()
        if self._save_geometry is not None:
            self._save_geometry((x, y, width, height))

    def set_active(self, active):
        active = bool(active)
        if active == self.active:
            if active:
                self.refresh()
            return
        window = self.window
        self._stop_animations()
        # Invalidate any pending toolbar-hide timer from the previous mode.
        window.enter_sig = uuid.uuid4()
        if active:
            self._expanded_size = QSize(window.size())
            self._expanded_minimum = QSize(window.minimumSize())
            self._expanded_maximum = QSize(window.maximumSize())
            self._text_was_hidden = window.translate_text.isHidden()
            self._save_geometry = getattr(window, "possave", None)
            window.possave = self.save_geometry
            self.active = True
            self.refresh()
        else:
            self.active = False
            window.setMaximumSize(self._expanded_maximum)
            window.setMinimumSize(self._expanded_minimum)
            window.possave = self._save_geometry
            window.translate_text.setVisible(not self._text_was_hidden)
            window.resizeFuck(self._expanded_size)
            self._orientation = None
            window.changeextendstated()
            window.enterfunction()

    def refresh(self):
        if not self.active or self._syncing:
            return
        self._syncing = True
        try:
            window = self.window
            self._stop_animations()
            window.translate_text.hide()
            window.titlebar.show()
            vertical = bool(globalconfig.get("verticalhorizontal", False))
            changed_direction = vertical != self._orientation
            self._orientation = vertical
            thickness = max(1, self.icon_size(vertical))
            minimum = QSize(self._expanded_minimum)
            maximum = QSize(self._expanded_maximum)
            size = QSize(self._expanded_size if changed_direction else window.size())
            if vertical:
                minimum.setWidth(thickness)
                maximum.setWidth(thickness)
                size.setWidth(thickness)
                # Match ButtonBar's minimum along the direction of its buttons.
                minimum.setHeight(
                    max(200, int(window.titlebar.cntbtn * self.icon_size(False)))
                )
            else:
                minimum.setHeight(thickness)
                maximum.setHeight(thickness)
                size.setHeight(thickness)
                minimum.setWidth(
                    max(200, int(window.titlebar.cntbtn * self.icon_size(True)))
                )
            if (
                window.minimumWidth() > maximum.width()
                or window.minimumHeight() > maximum.height()
            ):
                window.setMinimumSize(0, 0)
            if window.maximumSize() != maximum:
                window.setMaximumSize(maximum)
            if window.minimumSize() != minimum:
                window.setMinimumSize(minimum)
            if size != window.size():
                window.resizeFuck(size)
            if vertical:
                window.titlebar.setFixedWidth(thickness)
                window.titlebar.setFixedHeight(window.height())
            else:
                window.titlebar.setFixedHeight(thickness)
                window.titlebar.setFixedWidth(window.width())
            window.titlebar.move(0, 0)
        finally:
            self._syncing = False
        self.save_geometry(window.geometry().getRect())
