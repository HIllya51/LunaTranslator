import ast
import ctypes
from ctypes import c_void_p, c_int, c_bool, c_char, c_size_t, POINTER, CFUNCTYPE
import importlib.util
import os
from pathlib import Path
import sys
import threading
import time
import types
import unittest
import functools
import traceback
import heapq
import uuid
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/LunaTranslator"
DIST = Path(os.environ.get("LUNA_TRANSLATOR_DIR", str(ROOT / "src")))
APP = DIST / "LunaTranslator"
OUTPUT = Path(tempfile.gettempdir()) / "lunatranslator-ocr-overlay-tests"
OUTPUT.mkdir(exist_ok=True)
sys.path.insert(0, str(SOURCE))
if os.environ.get("LUNA_TEST_RUNTIME"):
    runtime = APP.parent / "files" / os.environ["LUNA_TEST_RUNTIME"]
    sys.path.insert(0, str(runtime))
    sys.path.insert(0, str(runtime / "pylibs.zip"))
    dll_handle = os.add_dll_directory(str(runtime))
    qt_dll_handle = os.add_dll_directory(str(runtime / "PyQt5/Qt5/bin"))
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(
        runtime / "PyQt5/Qt5/plugins/platforms"
    )
from qtsymbols import *

if isqt5:
    from PyQt5.QtCore import QAbstractAnimation
else:
    from PyQt6.QtCore import QAbstractAnimation
import windows

config = {
    "ocr_translation_overlay": True,
    "ocr_translation_overlay_fontsize": 22,
    "fix_translate_rank_rank": ["slow", "fast"],
}
mock_config = types.ModuleType("myutils.config")
mock_config.globalconfig = config
sys.modules["myutils.config"] = mock_config
spec = importlib.util.spec_from_file_location(
    "overlay", SOURCE / "gui/ocrtranslationoverlay.py"
)
overlay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overlay)
app = QApplication.instance()
if app is None:
    # Match main.prepareqtenv: without these attributes, Qt can resize native
    # windows incorrectly when tests cross monitors with different DPI.
    if isqt5:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication([])
app.setQuitOnLastWindowClosed(False)
qt_callback_errors = []


def record_qt_exception(kind, error, trace):
    qt_callback_errors.append(str(error))
    traceback.print_exception(kind, error, trace)


sys.excepthook = record_qt_exception


def load_methods(path, classname, names, env, qtbase=None):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    cls = next(
        c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == classname
    )
    cls.body = [
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    cls.bases = [ast.Name(id="_test_base", ctx=ast.Load())] if qtbase else []
    if qtbase:
        env["_test_base"] = qtbase
    ast.fix_missing_locations(cls)
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(path), "exec"), env)
    return env[classname]


def translation_subject():
    events, history, sql = [], [], []
    signal = types.SimpleNamespace(emit=lambda *args: events.append(args))
    env = {
        "functools": functools,
        "partial": functools.partial,
        "uuid": uuid,
        "globalconfig": config,
        "route_overlay_translation": overlay.route_overlay_translation,
        "overlay_source_is_current": overlay.overlay_source_is_current,
        "OCRRegionTask": overlay.OCRRegionTask,
        "TranslateResult": lambda *args: args,
        "TranslateColor": lambda c: c,
        "dynamicapiname": lambda c: c,
        "_TR": lambda t: t,
        "POSTSOLVE": lambda text, **kw: text,
        "gobject": types.SimpleNamespace(
            base=types.SimpleNamespace(
                dispatch_translate=signal, showandsolvesig=signal
            )
        ),
    }
    cls = load_methods(
        SOURCE / "LunaTranslator.py",
        "BASEOBJECT",
        {
            "textgetmethod",
            "textgetmethod_1",
            "create_translate_task",
            "GetTranslationCallback",
            "__safecallback",
            "__erroroutput",
            "_delayshowraw",
        },
        env,
    )
    subject = cls()
    subject.gettranslatelock = threading.Lock()
    subject.solvegottextlock = threading.Lock()
    subject.currentsignature = "current"
    subject.currenttext_raw = ""
    subject.currenttext = ""
    subject.statusok = True
    subject.currenttranslate = ""
    subject.refresh_on_get_trans_signature = None
    subject.history = types.SimpleNamespace(
        viewptr=-1,
        appendtrans=lambda *a: history.append(a),
        appendtext=lambda *a: history.append(a),
    )
    subject.translation_ui = types.SimpleNamespace(
        displayres=signal, displayraw1=signal
    )
    subject.transhis = types.SimpleNamespace(
        getnewtranssignal=signal, getnewsentencesignal=signal
    )
    subject.textsource = types.SimpleNamespace(sqlqueueput=lambda *a: sql.append(a))
    subject.solveaftertrans = lambda result, params: result
    subject.solvebeforetrans = lambda text: (text, [])
    subject.dispatchoutputer = lambda *a: None
    subject.maybesetedittext = lambda *a: None
    return subject, events, history, sql


def translation_engine():
    tree = ast.parse((SOURCE / "myutils/utils.py").read_text(encoding="utf-8"))
    queue_class = next(
        c
        for c in tree.body
        if isinstance(c, ast.ClassDef) and c.name == "PriorityQueue"
    )
    env = {
        "threading": threading,
        "heapq": heapq,
        "functools": functools,
        "ArgsEmptyExc": type("ArgsEmptyExc", (Exception,), {}),
        "stringfyerror": str,
        "print_exc": lambda: None,
    }
    exec(
        compile(
            ast.Module(body=[queue_class], type_ignores=[]),
            "<real priority queue>",
            "exec",
        ),
        env,
    )
    # Run the actual worker/thread wait implementation, without network calls.
    engine_tree = ast.parse(
        (SOURCE / "translator/basetranslator.py").read_text(encoding="utf-8")
    )
    support = [
        n
        for n in engine_tree.body
        if getattr(n, "name", None)
        in {"Interrupted", "Threadwithresult", "timeoutfunction"}
    ]
    env["Thread"] = threading.Thread
    exec(
        compile(
            ast.Module(body=support, type_ignores=[]),
            "<real translation timeout>",
            "exec",
        ),
        env,
    )
    cls = load_methods(
        SOURCE / "translator/basetranslator.py",
        "basetrans",
        {"gettask", "_fythread"},
        env,
    )
    engine = cls()
    real_queue = env["PriorityQueue"]()
    engine.queue = types.SimpleNamespace(
        put=real_queue.put,
        empty=real_queue.empty,
        get=lambda: None if real_queue.empty() else real_queue.get(),
    )
    engine.using = True
    engine.onlymanual = False
    engine.srclang_1, engine.tgtlang_1 = "en", "zh"
    engine.using_gpt_dict = False
    engine.transtype = "api"
    engine.maybeneedreinit = lambda: None
    return engine


def selection_subject(regions):
    pending, reads, delivered = [], [], []
    available = iter(regions)
    base = types.SimpleNamespace(settin_ui=None)

    def region_factory(*args):
        region = next(available)
        region.isfocus = False
        region._ocr_overlay_original = None
        region.setrect = lambda rect: region.setGeometry(rect)
        region.update_overlay_background = lambda *args: None
        region.setmousetransp = lambda value: None
        region.ocr_source_lock = threading.RLock()
        region.capture_snapshot = lambda: overlay.OCRCaptureSnapshot(
            region._ocr_overlay_revision, region.getrect().getRect()
        )

        def remember(text, snapshot=None):
            if snapshot is not None and snapshot != region.capture_snapshot():
                return None
            if text != region._ocr_overlay_original:
                region._ocr_overlay_original = text
                region._ocr_overlay_revision += 1
                region.overlaytranslationsignal.emit(
                    (region._ocr_overlay_revision, None, "")
                )
            return region._ocr_overlay_revision

        region.remember_overlay_source = remember
        return region

    def capture(hwnd, rect, callback):
        reads.append(rect.getRect())
        return types.SimpleNamespace(isNull=lambda: False)

    manager = load_methods(
        SOURCE / "textio/textsource/ocrtext.py",
        "rangemanger",
        {"__init__", "getresmanual", "_commit_ocr_result"},
        {
            "rangeadjust": region_factory,
            "QRect": QRect,
            "OCRRegionText": overlay.OCRRegionText,
            "gobject": types.SimpleNamespace(base=base),
            "imageCutEx": capture,
            "cvMat": lambda image: object(),
            "time": time,
            "ocr_run": lambda image: types.SimpleNamespace(
                textonly="same source",
                error=False,
                result=types.SimpleNamespace(isocrtranslate=False),
            ),
        },
    )
    source = load_methods(
        SOURCE / "textio/textsource/ocrtext.py",
        "ocrtext",
        {
            "newrangeadjustor",
            "setrect",
            "clearrange",
            "showhiderangeui",
            "getuseranges",
            "getallres",
            "gettextonce",
        },
        {
            "globalconfig": config,
            "rangemanger": manager,
            "QRect": QRect,
            "OCRRegionText": overlay.OCRRegionText,
            "OCRRegionBatch": overlay.OCRRegionBatch,
            "overlay_source_is_current": overlay.overlay_source_is_current,
        },
    )
    owner = source()
    owner.ranges, owner.ending, owner.hwnd = [], False, None
    base.textsource = owner
    base.textgetmethod = lambda text, auto: delivered.append((text, auto))
    ui_class = load_methods(
        SOURCE / "gui/translatorUI.py",
        "TranslatorWindow",
        {"afterrange"},
        {
            "tryprint": lambda fn: fn,
            "globalconfig": config,
            "ocrtext": source,
            "gobject": types.SimpleNamespace(base=base),
            "threader": lambda fn: lambda: pending.append(fn),
        },
    )
    ui = ui_class()
    ui.showhidestateFirst, ui.showhidestate = False, True
    ui.refreshtoolicon = lambda: None
    return owner, ui, base, pending, reads, delivered


def toolbar_window():
    saved_geometry = []

    class GeometryWidget(QWidget):
        def resizeEvent(self, event):
            if getattr(self, "possave", None):
                self.possave(self.geometry().getRect())
            super().resizeEvent(event)

        def moveEvent(self, event):
            if getattr(self, "possave", None):
                self.possave(self.geometry().getRect())
            super().moveEvent(event)

    class Bar(QFrame):
        cntbtn = 10

        def setDirection(self, vertical):
            self.vertical = vertical

        def adjustminwidth(self):
            if config.get("verticalhorizontal", False):
                self.parent().setMinimumSize(24, 300)
            else:
                self.parent().setMinimumSize(500, 30)

    class Text(QWidget):
        cleared = False

        def __init__(self, parent):
            super().__init__(parent)
            self.textbrowser = QLabel("main translation", self)

        def verticalhorizontal(self, vertical):
            pass

        def scrolltoend(self):
            pass

    env = {
        "QSize": QSize,
        "QPoint": QPoint,
        "QResizeEvent": QResizeEvent,
        "threading": threading,
        "time": time,
        "QTimer": QTimer,
        "globalconfig": config,
        "IconLabelX": types.SimpleNamespace(w=lambda: 24, h=lambda: 30),
    }
    cls = load_methods(
        SOURCE / "gui/translatorUI.py",
        "TranslatorWindow",
        {
            "ocr_overlay_collapsed",
            "set_ocr_overlay_mode",
            "initvalues",
            "enterfunction",
            "toolbarhidedelay",
            "changeextendstated",
            "textAreaChanged",
            "resizeEvent",
            "dynamicextraheight",
            "autodisappear",
            "autohidedelaythread",
            "verticalhorizontal",
            "smooth_resizing",
        },
        env,
        qtbase=GeometryWidget,
    )
    window = cls()
    window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    window.initvalues()
    window.possave = lambda rect: saved_geometry.append(rect)
    window.titlebar = Bar(window)
    window.titlebar.setFixedHeight(30)
    window.translate_text = Text(window)
    window.resizeFuck = window.resize
    window.smooth_resizer = QVariantAnimation(window)
    window.smooth_resizer2 = QVariantAnimation(window)
    window.smooth_resizer4 = QVariantAnimation(window)
    window.smooth_resizer.valueChanged.connect(window.smooth_resizing)
    window.isMouseHover = False
    window.set_color_transparency = lambda: None
    window.dodelayhide = lambda *args, **kwargs: None
    window.radiu_valid = False
    window.setMinimumSize(500, 30)
    window.setGeometry(50, 50, 600, 240)
    window.ocr_toolbar_mode = overlay.OCRToolbarMode(
        window, lambda vertical: 24 if vertical else 30
    )
    window.show()
    pump(0.03)
    return window, saved_geometry


def pump(seconds=0.15):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)


class Region(QWidget):
    overlaytranslationsignal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self._ocr_overlay_revision = 1
        self.setGeometry(100, 100, 520, 160)
        self.panel = overlay.OCRTranslationOverlay(self)
        self.overlaytranslationsignal.connect(self.panel.receive)

    def getrect(self):
        r = windows.GetWindowRect(int(self.winId()))
        return QRect(r[0], r[1], r[2] - r[0], r[3] - r[1])

    def paintEvent(self, event):
        # Paint explicitly: a QWidget subclass need not draw its stylesheet
        # background, which can otherwise leave the desktop visible in GDI.
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#11aadd"))
        painter.end()


def gdi_crop(rect):
    dll_dir = str(DIST / "files/DLL64")
    if not (Path(dll_dir) / "NativeUtils.dll").exists():
        raise unittest.SkipTest(
            "Set LUNA_TRANSLATOR_DIR to a built Windows distribution for real GDI capture"
        )
    with os.add_dll_directory(dll_dir):
        dll = ctypes.CDLL(str(Path(dll_dir) / "NativeUtils.dll"))
    api = dll.GdiCropImage
    api.argtypes = c_void_p, c_int, c_int, c_int, c_int, c_void_p
    api.restype = c_bool
    data = []
    cb = CFUNCTYPE(None, POINTER(c_char), c_size_t)(lambda p, n: data.append(p[:n]))
    api(None, rect.x(), rect.y(), rect.right(), rect.bottom(), cb)
    img = QImage()
    if data:
        img.loadFromData(data[0])
    return img


class OverlayTests(unittest.TestCase):
    def setUp(self):
        config["ocr_translation_overlay"] = True
        config["ocr_translation_overlay_show_main"] = False
        config["ocr_translation_overlay_adaptive_background"] = True
        config["toppest_translator"] = None
        config["verticalhorizontal"] = False
        self.region = Region()
        self.region.show()
        pump()
        self.source = overlay.OCRRegionText("OCR source", self.region, 1)

    def tearDown(self):
        self.region.panel.hide()
        self.region.close()
        self.region.deleteLater()
        app.processEvents()
        overlay._overlays.discard(self.region.panel)
        errors = list(qt_callback_errors)
        qt_callback_errors.clear()
        self.assertEqual(errors, [], "Unhandled Qt callback exception")

    def test_source_provenance_and_stale_result(self):
        overlay.route_overlay_translation("clipboard source", "fast", "wrong")
        self.assertEqual(self.region.panel.text, "")
        overlay.route_overlay_translation(self.source, "fast", "translated")
        self.assertEqual(self.region.panel.text, "translated")
        self.region._ocr_overlay_revision = 2
        self.region.panel.receive((2, None, ""))
        overlay.route_overlay_translation(self.source, "slow", "stale")
        self.assertEqual(self.region.panel.text, "")
        self.region.panel.receive((1, "slow", "queued stale"))
        self.assertEqual(self.region.panel.text, "")

    def test_streaming_and_engine_priority(self):
        overlay.route_overlay_translation(self.source, "fast", "early")
        overlay.route_overlay_translation(self.source, "slow", "优先引擎：第一段")
        overlay.route_overlay_translation(self.source, "fast", "late lower priority")
        self.assertEqual(self.region.panel.text, "优先引擎：第一段")
        overlay.route_overlay_translation(
            self.source, "slow", "优先引擎：完整的流式译文"
        )
        self.assertEqual(self.region.panel.text, "优先引擎：完整的流式译文")
        config["toppest_translator"] = "fast"
        overlay.route_overlay_translation(self.source, "fast", "preferred")
        self.assertEqual(self.region.panel.text, "preferred")

    def test_dominant_background_ignores_original_text(self):
        for background, foreground in [
            ("#fffaf0", "black"),
            ("#20252e", "white"),
            ("#11aadd", "black"),
            ("#b4cfb0", "black"),
        ]:
            image = QImage(320, 100, QImage.Format.Format_ARGB32)
            image.fill(QColor(background))
            painter = QPainter(image)
            font = QFont("Microsoft YaHei")
            font.setPixelSize(24)
            painter.setFont(font)
            painter.setPen(QColor(foreground))
            painter.drawText(
                QRect(10, 10, 300, 80),
                int(Qt.AlignmentFlag.AlignCenter),
                "Original text 原文 123",
            )
            painter.end()
            sampled = overlay.sample_background(image)
            expected = QColor(background).getRgb()[:3]
            for actual, wanted in zip(sampled, expected):
                self.assertLessEqual(abs(actual - wanted), 2)
        self.assertIsNone(overlay.sample_background(QImage()))
        transparent = QImage(10, 10, QImage.Format.Format_ARGB32)
        transparent.fill(Qt.GlobalColor.transparent)
        self.assertIsNone(overlay.sample_background(transparent))

    def test_background_overshoot_with_two_shades_beats_outside_color(self):
        image = QImage(240, 120, QImage.Format.Format_ARGB32)
        image.fill(QColor("#00ff55"))
        painter = QPainter(image)
        painter.fillRect(QRect(24, 12, 96, 96), QColor(203, 219, 227))
        painter.fillRect(QRect(120, 12, 96, 96), QColor(223, 237, 247))
        painter.end()
        result = overlay.sample_background(image)
        for actual, expected in zip(result, (213, 228, 237)):
            self.assertLessEqual(abs(actual - expected), 2)

    def test_background_one_sided_overshoot_and_borders(self):
        for rgb, outside in [
            ((70, 88, 110), (255, 255, 255)),
            ((248, 243, 227), (10, 10, 10)),
        ]:
            image = QImage(240, 120, QImage.Format.Format_ARGB32)
            image.fill(QColor(*rgb))
            painter = QPainter(image)
            painter.fillRect(QRect(0, 0, 43, 120), QColor(*outside))
            painter.setPen(QPen(QColor(*outside), 4))
            painter.drawRect(image.rect().adjusted(1, 1, -2, -2))
            painter.setPen(QColor("white" if rgb[0] < 128 else "black"))
            font = QFont("Microsoft YaHei")
            font.setPixelSize(22)
            painter.setFont(font)
            painter.drawText(
                QRect(50, 10, 180, 100),
                int(Qt.TextFlag.TextWordWrap),
                "Original text\n原文内容",
            )
            painter.end()
            for actual, expected in zip(overlay.sample_background(image), rgb):
                self.assertLessEqual(abs(actual - expected), 2)

    def test_background_small_crop_changes_do_not_flip_to_surrounding_panel(self):
        results = []
        for fraction in (0.05, 0.08, 0.10, 0.12, 0.15, 0.18):
            image = QImage(240, 120, QImage.Format.Format_ARGB32)
            image.fill(QColor("#00ff55"))
            x, y = round(240 * fraction), round(120 * fraction)
            painter = QPainter(image)
            painter.fillRect(QRect(x, y, 120 - x, 120 - 2 * y), QColor(203, 219, 227))
            painter.fillRect(QRect(120, y, 120 - x, 120 - 2 * y), QColor(223, 237, 247))
            painter.end()
            result = overlay.sample_background(image)
            results.append(result)
            for actual, expected in zip(result, (213, 228, 237)):
                self.assertLessEqual(abs(actual - expected), 2)
        for channel in range(3):
            self.assertLessEqual(
                max(rgb[channel] for rgb in results)
                - min(rgb[channel] for rgb in results),
                2,
            )

    def test_background_small_images_and_transparency(self):
        for width, height in [(1, 1), (3, 3), (4, 40), (40, 4)]:
            image = QImage(width, height, QImage.Format.Format_ARGB32)
            image.fill(QColor(17, 170, 221))
            self.assertEqual(overlay.sample_background(image), (17, 170, 221))

    def test_adaptive_background_rendering_and_text_contrast(self):
        overlay.route_overlay_translation(self.source, "fast", "自适应背景")
        pump()
        rect = self.region.getrect().getRect()
        self.assertLessEqual(
            abs(
                self.region.panel.width() * self.region.panel.devicePixelRatioF()
                - rect[2]
            ),
            2,
        )
        for rgb, foreground, name in [
            ((255, 250, 240), "black", "light"),
            ((20, 25, 35), "white", "dark"),
            ((17, 170, 221), "black", "blue"),
        ]:
            self.region.panel.receive_background((rect, rgb))
            pump(0.03)
            colors = self.region.panel.background_colors()
            self.assertEqual(colors[0], rgb)
            self.assertEqual(colors[1].name(), QColor(foreground).name())
            image = self.region.panel.grab().toImage()
            image.save(str(OUTPUT / ("adaptive-background-" + name + ".png")))
            for actual, expected in zip(image.pixelColor(2, 2).getRgb()[:3], rgb):
                self.assertLessEqual(abs(actual - expected), 2)
        config["ocr_translation_overlay_adaptive_background"] = False
        self.assertEqual(self.region.panel.background_colors()[0], (20, 20, 24))
        self.assertEqual(
            self.region.panel.background_colors()[1].name(), QColor("white").name()
        )

    def test_palette_noise_and_stale_captures_do_not_repaint(self):
        class Paints(QObject):
            def __init__(self):
                super().__init__()
                self.count = 0

            def eventFilter(self, watched, event):
                if event.type() == QEvent.Type.Paint:
                    self.count += 1
                return False

        overlay.route_overlay_translation(self.source, "fast", "稳定的背景色")
        rect = self.region.getrect().getRect()
        self.region.panel.receive_background((rect, (240, 240, 240)))
        pump()
        paints = Paints()
        self.region.panel.installEventFilter(paints)
        for _ in range(100):
            self.region.panel.receive_background((rect, (242, 239, 241)))
            app.processEvents()
        self.region.panel.receive_background(((0, 0, 1, 1), (10, 10, 10)))
        pump()
        self.assertEqual(self.region.panel.background_rgb, (240, 240, 240))
        self.assertEqual(paints.count, 0)
        self.region.panel.receive_background((rect, (40, 40, 40)))
        pump()
        self.assertGreater(paints.count, 0)

    def test_background_sampling_precedes_ocr_preprocessing(self):
        tree = ast.parse(
            (SOURCE / "textio/textsource/ocrtext.py").read_text(encoding="utf-8")
        )
        method = next(
            n
            for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "imageCutEx"
        )
        raw = QImage(30, 30, QImage.Format.Format_ARGB32)
        raw.fill(QColor("#11aadd"))
        processed = QImage(30, 30, QImage.Format.Format_ARGB32)
        processed.fill(QColor("#777777"))
        captured = []
        env = {
            "QImage": QImage,
            "QRect": QRect,
            "capture_without_overlays": lambda capture, rect: capture(),
            "imageCut": lambda hwnd, rect: (True, raw),
            "globalconfig": {"use_ocr_preprocess": True},
            "gobject": types.SimpleNamespace(getconfig=lambda name: name),
            "checkmd5reloadmodule": lambda *a: types.SimpleNamespace(
                Process=lambda image: processed
            ),
        }
        exec(
            compile(
                ast.Module(body=[method], type_ignores=[]),
                "<background capture>",
                "exec",
            ),
            env,
        )
        image = env["imageCutEx"](
            1,
            QRect(0, 0, 30, 30),
            lambda image, rect: captured.append(overlay.sample_background(image)),
        )
        self.assertEqual(captured, [(17, 170, 221)])
        self.assertEqual(image.pixelColor(0, 0).name(), "#777777")

    def test_unchanged_follow_ticks_and_stream_chunks_do_not_repaint(self):
        class Events(QObject):
            def __init__(self):
                super().__init__()
                self.counts = {}

            def eventFilter(self, watched, event):
                kind = event.type()
                if kind in (
                    QEvent.Type.Paint,
                    QEvent.Type.Move,
                    QEvent.Type.Resize,
                    QEvent.Type.Show,
                    QEvent.Type.Hide,
                ):
                    self.counts[kind] = self.counts.get(kind, 0) + 1
                return False

        overlay.route_overlay_translation(self.source, "fast", "稳定译文")
        pump()
        events = Events()
        self.region.panel.installEventFilter(events)
        for _ in range(100):
            self.region.panel.sync()
            overlay.route_overlay_translation(self.source, "fast", "稳定译文")
            app.processEvents()
        pump()
        self.assertEqual(events.counts, {})
        overlay.route_overlay_translation(self.source, "fast", "更新后的译文")
        pump()
        self.assertGreater(events.counts.get(QEvent.Type.Paint, 0), 0)
        self.assertEqual(events.counts.get(QEvent.Type.Show, 0), 0)
        self.assertEqual(events.counts.get(QEvent.Type.Hide, 0), 0)

    def test_capture_affinity_after_native_window_recreation(self):
        def affinity():
            value = ctypes.wintypes.DWORD()
            api = ctypes.windll.user32.GetWindowDisplayAffinity
            api.argtypes = c_void_p, ctypes.POINTER(ctypes.wintypes.DWORD)
            self.assertTrue(api(int(self.region.panel.winId()), ctypes.byref(value)))
            return value.value

        overlay.route_overlay_translation(self.source, "fast", "稳定译文")
        pump()
        self.assertEqual(affinity(), 0x11)
        self.region.panel.hide()
        self.region.panel.destroy()
        self.region.panel.sync()
        pump()
        self.assertTrue(self.region.panel.capture_excluded)
        self.assertEqual(affinity(), 0x11)

    def test_unmanifested_launcher_build_does_not_disable_exclusion(self):
        getversion = overlay.sys.getwindowsversion
        try:
            overlay.sys.getwindowsversion = lambda: types.SimpleNamespace(build=9200)
            self.assertGreaterEqual(overlay._windows_build(), 19041)
            self.region.panel.receive((1, "fast", "launcher compatibility"))
            self.assertTrue(self.region.panel.capture_excluded)
        finally:
            overlay.sys.getwindowsversion = getversion

    def test_geometry_visibility_font_and_preview(self):
        text = "你好，这是直接显示在 OCR 选区中的译文。\n区域可以移动和缩放，文字会自动换行。"
        overlay.route_overlay_translation(self.source, "fast", text)
        app.processEvents()
        self.assertTrue(self.region.panel.isVisible())
        self.assert_geometry_matches()
        self.region.setGeometry(150, 150, 350, 120)
        self.region.panel.sync()
        app.processEvents()
        self.assert_geometry_matches()
        config["ocr_translation_overlay_fontsize"] = 60
        self.region.panel.grab().save(str(OUTPUT / "overlay-preview.png"))
        self.assertLess(self.region.panel.font_size, 60)
        self.assertGreaterEqual(self.region.panel.font_size, 6)
        config["ocr_translation_overlay_fontsize"] = 22
        config["ocr_translation_overlay"] = False
        self.region.panel.sync()
        self.assertFalse(self.region.panel.isVisible())
        config["ocr_translation_overlay"] = True
        self.region.panel.sync()
        self.assertTrue(self.region.panel.isVisible())
        self.region.hide()
        self.region.panel.sync()
        self.assertFalse(self.region.panel.isVisible())

    def assert_geometry_matches(self):
        actual = windows.GetWindowRect(int(self.region.panel.winId()))
        expected = windows.GetWindowRect(int(self.region.winId()))
        # Qt rounds logical dimensions at 175% DPI; allow one logical pixel.
        for a, e in zip(actual, expected):
            self.assertLessEqual(
                abs(a - e), max(1, round(self.region.panel.devicePixelRatioF()))
            )

    def test_overlay_resyncs_after_cross_monitor_dpi_change(self):
        overlay.route_overlay_translation(self.source, "fast", "Translation")
        for coordinates in [
            (-700, 140, 520, 160),
            (160, -350, 420, 130),
            (220, 180, 320, 100),
        ]:
            windows.MoveWindow(int(self.region.winId()), *coordinates, True)
            pump(0.05)
            self.region.panel.sync()
            pump(0.05)
            # No second manual sync: a DPI transition must correct itself.
            self.assert_geometry_matches()

    def extra_region(self, x=700, y=100):
        region = Region()
        region.setGeometry(x, y, 520, 160)
        region.show()

        def cleanup():
            overlay._overlays.discard(region.panel)
            region.close()
            region.deleteLater()
            app.processEvents()

        self.addCleanup(cleanup)
        return region

    def make_toolbar_window(self):
        window, saved = toolbar_window()

        def cleanup():
            for timer in window.findChildren(QTimer):
                timer.stop()
            window.ocr_toolbar_mode.set_active(False)
            window.close()
            window.deleteLater()
            app.processEvents()
            QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

        self.addCleanup(cleanup)
        return window, saved

    def test_toolbar_collapse_stays_folded_when_content_and_hover_update(self):
        window, saved = self.make_toolbar_window()
        window.set_ocr_overlay_mode(True)
        pump(0.03)
        self.assertEqual(window.size(), QSize(600, 30))
        self.assertEqual(window.maximumHeight(), 30)
        self.assertTrue(window.translate_text.isHidden())
        self.assertTrue(window.titlebar.isVisible())

        class Events(QObject):
            def __init__(self):
                super().__init__()
                self.changes = []

            def eventFilter(self, watched, event):
                if event.type() in (
                    QEvent.Type.Resize,
                    QEvent.Type.Show,
                    QEvent.Type.Hide,
                ):
                    self.changes.append(event.type())
                return False

        events = Events()
        window.installEventFilter(events)
        for _ in range(100):
            window.textAreaChanged(QSize(600, 800))
            window.enterfunction()
            window.toolbarhidedelay()
            window.autodisappear()
            app.processEvents()
        self.assertEqual(events.changes, [])
        window.resize(700, 800)
        pump(0.03)
        self.assertEqual(window.size(), QSize(700, 30))
        self.assertEqual(saved[-1][2:], (700, 240))
        self.assertTrue(window.translate_text.isHidden())
        self.assertTrue(window.titlebar.isVisible())

    def test_toolbar_restore_dimensions_constraints_and_manual_visibility(self):
        window, saved = self.make_toolbar_window()
        initial_size = window.size()
        initial_minimum, initial_maximum = window.minimumSize(), window.maximumSize()
        for _ in range(3):
            window.set_ocr_overlay_mode(True)
            window.set_ocr_overlay_mode(True)
            window.set_ocr_overlay_mode(False)
            self.assertEqual(window.size(), initial_size)
            self.assertEqual(window.minimumSize(), initial_minimum)
            self.assertEqual(window.maximumSize(), initial_maximum)
            self.assertTrue(window.translate_text.isVisible())
        window.set_ocr_overlay_mode(True)
        window.hide()
        window.set_ocr_overlay_mode(False)
        self.assertTrue(window.isHidden())
        self.assertFalse(window.translate_text.isHidden())
        self.assertEqual(saved[-1][2:], (600, 240))

    def test_toolbar_fold_stops_animation_and_automatic_window_hide(self):
        window, saved = self.make_toolbar_window()
        # Real enterfunction/dodelayhide replaces the initial integer with a UUID.
        window.enter_sig = uuid.uuid4()
        window.smooth_resizer.setStartValue(240)
        window.smooth_resizer.setEndValue(800)
        window.smooth_resizer.setDuration(1000)
        window.smooth_resizer.start()
        window.set_ocr_overlay_mode(True)
        self.assertEqual(
            window.smooth_resizer.state(), QAbstractAnimation.State.Stopped
        )
        window.smooth_resizing(1000)
        self.assertEqual(window.height(), 30)
        old = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(old)))
        config.update(autodisappear=True, autodisappear_which=0, disappear_delay=0)
        window.lastrefreshtime = 0
        window.autohidestart = True
        window.autohidedelaythread()
        pump(0.6)
        self.assertTrue(window.isVisible())
        self.assertTrue(window.titlebar.isVisible())

    def test_toolbar_orientation_and_button_size_changes(self):
        window, saved = self.make_toolbar_window()
        window.set_ocr_overlay_mode(True)
        config["verticalhorizontal"] = True
        window.verticalhorizontal(True)
        pump(0.03)
        self.assertEqual(window.width(), 24)
        self.assertEqual(window.maximumWidth(), 24)
        self.assertEqual(window.titlebar.geometry(), window.rect())
        config["verticalhorizontal"] = False
        window.verticalhorizontal(False)
        self.assertEqual(window.height(), 30)
        window.ocr_toolbar_mode.icon_size = lambda vertical: 28 if vertical else 36
        window.ocr_toolbar_mode.refresh()
        self.assertEqual(window.height(), 36)
        self.assertEqual(window.titlebar.geometry(), window.rect())
        window.set_ocr_overlay_mode(False)
        self.assertGreater(window.height(), 36)
        self.assertGreater(window.width(), 28)

    def test_source_switch_folds_only_ocr_with_overlay_enabled(self):
        class OCR:
            def endX(self):
                pass

        class OtherSource:
            def endX(self):
                pass

        modes = []
        env = {"ocrtext": OCR, "globalconfig": config}
        cls = load_methods(
            SOURCE / "LunaTranslator.py", "BASEOBJECT", {"textsource"}, env
        )
        subject = cls()
        subject.textsource_p = None
        subject.translation_ui = types.SimpleNamespace(
            ocroverlaymodesignal=types.SimpleNamespace(emit=modes.append)
        )
        subject.textsource = OCR()
        subject.textsource = None
        subject.textsource = OtherSource()
        config["ocr_translation_overlay"] = False
        subject.textsource = None
        subject.textsource = OCR()
        self.assertEqual(modes, [True, False, False, False, False])

    def test_overlay_setting_signal_folds_and_restores_main_window(self):
        class ModeSignals(QObject):
            ocroverlaymodesignal = pyqtSignal(bool)

        window, saved = self.make_toolbar_window()
        signals = ModeSignals()
        signals.ocroverlaymodesignal.connect(window.set_ocr_overlay_mode)
        env = {
            "globalconfig": config,
            "gobject": types.SimpleNamespace(
                base=types.SimpleNamespace(translation_ui=signals)
            ),
        }
        cls = load_methods(
            SOURCE / "textio/textsource/ocrtext.py", "ocrtext", {"setstyle"}, env
        )
        owner = cls()
        styles = []
        manager = types.SimpleNamespace(
            range_ui=types.SimpleNamespace(setstyle=lambda: styles.append(True)),
            savelasttext="existing OCR",
            lastocrtime=12,
            savelastimg=object(),
            savelastrecimg=object(),
        )
        owner.ranges, owner.ending, owner._overlay_enabled = [manager], False, True
        cached = (
            manager.savelasttext,
            manager.lastocrtime,
            manager.savelastimg,
            manager.savelastrecimg,
        )
        owner.setstyle()
        self.assertEqual(window.height(), 30)
        for _ in range(3):
            config["ocr_translation_overlay_show_main"] = True
            owner.setstyle()
            self.assertEqual(window.size(), QSize(600, 240))
            self.assertTrue(window.translate_text.isVisible())
            self.assertFalse(window.ocr_overlay_collapsed)
            config["ocr_translation_overlay_show_main"] = False
            owner.setstyle()
            self.assertEqual(window.size(), QSize(600, 30))
            self.assertTrue(window.translate_text.isHidden())
            self.assertEqual(
                cached,
                (
                    manager.savelasttext,
                    manager.lastocrtime,
                    manager.savelastimg,
                    manager.savelastrecimg,
                ),
            )
        config["ocr_translation_overlay"] = False
        owner.setstyle()
        self.assertEqual(window.height(), 240)
        config["ocr_translation_overlay"] = True
        owner._overlay_enabled = True
        owner.ending = True
        owner.setstyle()
        self.assertEqual(window.height(), 240)

    def test_multi_region_real_dispatch_queue_and_thread_callbacks(self):
        regions = [self.region, self.extra_region(), self.extra_region(100, 350)]
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(
            minlength=1,
            maxlength=10000,
            read_raw=False,
            fix_translate_rank=False,
            fix_translate_rank_rank=["fast"],
            fanyi={"fast": {}},
            showfanyi=True,
        )
        result_texts = ["same source", "second source", "same source"]
        managers = []
        for region, text in zip(regions, result_texts):
            result = types.SimpleNamespace(
                textonly=text,
                error=False,
                result=types.SimpleNamespace(isocrtranslate=False),
                ocr_overlay_source=overlay.OCRRegionText(
                    text, region, region._ocr_overlay_revision
                ),
            )
            managers.append(
                types.SimpleNamespace(
                    range_ui=region,
                    getresauto=lambda value=result: value,
                    getresmanual=lambda value=result: value,
                )
            )
        cls = load_methods(
            SOURCE / "textio/textsource/ocrtext.py",
            "ocrtext",
            {"getallres"},
            {
                "OCRRegionText": overlay.OCRRegionText,
                "OCRRegionBatch": overlay.OCRRegionBatch,
                "overlay_source_is_current": overlay.overlay_source_is_current,
                "globalconfig": config,
            },
        )
        owner = cls()
        owner.ranges, owner.ending = managers, False
        owner.getuseranges = lambda: owner.ranges
        batch = owner.getallres(True)
        subject, events, history, sql = translation_subject()
        engine = translation_engine()
        processed = []

        def translate(lang, text, auto, callback):
            processed.append(text)
            callback("译文：" + text[:4], 1)
            callback("译文：" + text, 2)

        engine.translate_and_collect = translate
        subject.translators = {"fast": engine}
        subject.textgetmethod(batch)
        self.assertEqual(len([h for h in history if len(h) == 2]), 3)
        engine._fythread()
        pump()
        self.assertEqual(processed, result_texts)
        self.assertEqual(
            [r.panel.text for r in regions], ["译文：" + t for t in result_texts]
        )
        self.assertTrue(all(r.panel.isVisible() for r in regions))
        self.assertEqual(len([h for h in history if len(h) == 3]), 3)
        self.assertEqual(len([row for row in sql if len(row[0]) == 3]), 3)
        # Each frame retains its own sampled palette, alongside its own result.
        for region, rgb in zip(
            regions, [(250, 245, 230), (40, 50, 60), (17, 170, 221)]
        ):
            region.panel.receive_background((region.getrect().getRect(), rgb))
            self.assertEqual(region.panel.background_rgb, rgb)

    def test_add_region_only_recognizes_new_frame_and_manual_refresh_still_all(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(
            multiregion=True,
            keepontop=True,
            minlength=1,
            maxlength=10000,
            read_raw=False,
            fix_translate_rank=False,
            fix_translate_rank_rank=["fast"],
            fanyi={"fast": {}},
            showfanyi=True,
        )
        regions = [
            self.region,
            self.extra_region(100, 350),
            self.extra_region(700, 350),
        ]
        owner, ui, base, pending, reads, delivered = selection_subject(regions)
        for region in regions[:2]:
            manager = owner.newrangeadjustor()
            source = owner.gettextonce(manager)
            overlay.route_overlay_translation(source, "fast", "existing translation")
        cached = [
            (
                r.savelastimg,
                r.savelastrecimg,
                r.lastocrtime,
                r.savelasttext,
                r.range_ui._ocr_overlay_revision,
            )
            for r in owner.ranges
        ]
        reads.clear()
        # An old focused frame must not redirect the new frame's initial OCR.
        owner.ranges[0].range_ui.isfocus = True
        ui.afterrange(False, QRect(700, 350, 520, 160))
        self.assertEqual(len(pending), 1)
        pending.pop()()
        self.assertEqual(reads, [regions[2].getrect().getRect()])
        self.assertEqual(len(delivered), 1)
        self.assertIs(delivered[0][0].ocr_overlay_context[0](), regions[2])
        self.assertEqual(
            cached,
            [
                (
                    r.savelastimg,
                    r.savelastrecimg,
                    r.lastocrtime,
                    r.savelasttext,
                    r.range_ui._ocr_overlay_revision,
                )
                for r in owner.ranges[:2]
            ],
        )
        subject, _, _, _ = translation_subject()
        engine = translation_engine()
        processed = []
        engine.translate_and_collect = lambda lang, text, auto, callback: (
            processed.append(text),
            callback("new translation", 0),
        )
        subject.translators = {"fast": engine}
        subject.textgetmethod(delivered[0][0], is_auto_run=False)
        engine._fythread()
        pump()
        self.assertEqual(processed, ["same source"])
        self.assertEqual(
            [r.panel.text for r in regions],
            ["existing translation", "existing translation", "new translation"],
        )
        owner.ranges[0].range_ui.isfocus = False
        reads.clear()
        refreshed = owner.gettextonce()
        self.assertEqual(len(reads), 3)
        self.assertEqual(len(refreshed.ocr_region_sources), 3)

    def test_consecutive_additions_capture_their_own_region(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(multiregion=True, keepontop=True)
        regions = [self.region, self.extra_region(700, 350)]
        owner, ui, base, pending, reads, delivered = selection_subject(regions)
        ui.afterrange(False, QRect(100, 100, 520, 160))
        ui.afterrange(False, QRect(700, 350, 520, 160))
        # Deliberately finish in reverse order after both selections exist.
        pending[1]()
        pending[0]()
        self.assertEqual(
            reads, [regions[1].getrect().getRect(), regions[0].getrect().getRect()]
        )
        self.assertEqual(
            [value.ocr_overlay_context[0]() for value, _ in delivered],
            [regions[1], regions[0]],
        )

    def test_cancel_remove_or_change_source_does_not_refresh_other_regions(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(multiregion=True, keepontop=True)
        owner, ui, base, pending, reads, delivered = selection_subject([self.region])
        ui.afterrange(False, QRect(100, 100, 520, 160))
        ui.afterrange(True, QRect())
        self.assertEqual(len(owner.ranges), 1)
        self.assertEqual(len(pending), 1)
        manager = owner.ranges.pop()
        pending[0]()
        self.assertEqual(reads, [])
        owner.ranges.append(manager)
        base.textsource = object()
        pending[0]()
        self.assertEqual(reads, [])
        base.textsource = owner
        owner.ending = True
        pending[0]()
        self.assertEqual(delivered, [])

    def test_adding_region_with_overlay_disabled_preserves_combined_ocr(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(multiregion=True, keepontop=True, ocr_translation_overlay=False)
        regions = [self.region, self.extra_region(700, 350)]
        owner, ui, base, pending, reads, delivered = selection_subject(regions)
        owner.newrangeadjustor()
        ui.afterrange(False, QRect(700, 350, 520, 160))
        pending[0]()
        self.assertEqual(reads, [region.getrect().getRect() for region in regions])
        self.assertEqual(str(delivered[0][0]), "same source\nsame source")
        self.assertFalse(hasattr(delivered[0][0], "ocr_region_sources"))

    def test_hidden_overlays_do_not_move_capture_to_gui_thread(self):
        self.assertFalse(self.region.panel.isVisible())
        self.assertFalse(self.region.panel.capture_excluded)
        captures = []
        worker_ids = []

        def capture():
            captures.append(threading.get_ident())
            return "captured"

        def worker():
            worker_ids.append(threading.get_ident())
            self.assertEqual(overlay.capture_without_overlays(capture), "captured")

        thread = threading.Thread(target=worker)
        thread.start()
        # A hidden overlay should not require any GUI event processing.
        thread.join(0.5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(captures, worker_ids)

    def test_real_selection_context_menu_blocks_capture_then_resumes(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config["multiregion"] = False
        self.region._mousetransp = False
        overlay.route_overlay_translation(self.source, "fast", "existing translation")
        captured, during, errors = [], [], []
        menu = QMenu(self.region)
        env = {
            "QMenu": lambda parent: menu,
            "Qt": Qt,
            "LAction": QAction,
            "QCursor": QCursor,
            "globalconfig": config,
            "suspend_ocr_capture": overlay.suspend_ocr_capture,
        }
        cls = load_methods(
            SOURCE / "gui/rangeselect.py", "rangeadjust", {"showmenu"}, env
        )

        def inspect_open_menu():
            try:
                self.assertTrue(menu.isVisible())
                worker = threading.Thread(
                    target=lambda: during.append(
                        overlay.capture_without_overlays(lambda: captured.append(True))
                    )
                )
                worker.start()
                worker.join(0.5)
                self.assertFalse(worker.is_alive())
                self.assertEqual(during, [None])
                self.assertEqual(captured, [])
                self.assertEqual(self.region.panel.text, "existing translation")
            except Exception as error:
                errors.append(error)
            finally:
                menu.close()

        QTimer.singleShot(50, inspect_open_menu)
        cls.showmenu(self.region, None)
        self.assertEqual(errors, [])
        self.assertEqual(overlay.capture_without_overlays(lambda: "resumed"), "resumed")
        self.assertEqual(self.region.panel.text, "existing translation")
        menu.deleteLater()

    def test_selection_menu_stays_above_overlays_and_new_results(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config["multiregion"] = False
        self.region._mousetransp = False
        windows.WindowFocus.giveup(self.region.winId())
        overlay.route_overlay_translation(self.source, "fast", "existing translation")
        other = self.extra_region(self.region.x(), self.region.y())
        menu = QMenu(self.region)
        submenu = menu.addMenu("Nested menu")
        submenu.addAction("Nested action")
        env = {
            "QMenu": lambda parent: menu,
            "Qt": Qt,
            "LAction": QAction,
            "QCursor": types.SimpleNamespace(
                pos=lambda: self.region.mapToGlobal(QPoint(40, 40))
            ),
            "globalconfig": config,
            "suspend_ocr_capture": overlay.suspend_ocr_capture,
        }
        cls = load_methods(
            SOURCE / "gui/rangeselect.py", "rangeadjust", {"showmenu"}, env
        )
        enum_callback = ctypes.WINFUNCTYPE(c_bool, c_void_p, c_void_p)
        enum_windows = ctypes.windll.user32.EnumWindows
        enum_windows.argtypes = (enum_callback, c_void_p)
        enum_windows.restype = c_bool
        errors = []

        def assert_above(popup, panel):
            order = []
            callback = enum_callback(lambda hwnd, _: (order.append(hwnd), True)[1])
            self.assertTrue(enum_windows(callback, None))
            self.assertIn(int(popup.winId()), order)
            self.assertIn(int(panel.winId()), order)
            self.assertLess(
                order.index(int(popup.winId())),
                order.index(int(panel.winId())),
                "The OCR overlay is above the selection menu",
            )

        def inspect_open_menu():
            try:
                self.assertTrue(menu.isVisible())
                assert_above(menu, self.region.panel)
                # A different region can finish translating inside QMenu.exec's
                # nested event loop, even though new OCR captures are suspended.
                other.panel.receive((1, "fast", "new region translation"))
                pump(0.03)
                assert_above(menu, other.panel)
                submenu.popup(menu.mapToGlobal(QPoint(menu.width(), 0)))
                pump(0.03)
                self.assertTrue(submenu.isVisible())
                self.assertIs(QApplication.activePopupWidget(), submenu)
                other.panel.hide()
                other.panel.sync()
                pump(0.03)
                assert_above(submenu, other.panel)
                self.assertIsNone(overlay.capture_without_overlays(lambda: 123))
            except Exception as error:
                errors.append(error)
            finally:
                submenu.close()
                menu.close()

        QTimer.singleShot(50, inspect_open_menu)
        cls.showmenu(self.region, None)
        self.assertEqual(errors, [])
        self.assertEqual(overlay.capture_without_overlays(lambda: 123), 123)
        self.assertEqual(self.region.panel.text, "existing translation")
        self.assertEqual(other.panel.text, "new region translation")
        menu.deleteLater()

    def test_selection_menu_survives_main_window_topmost_checks(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(multiregion=False, keepontop=True, focusnotop=False)
        self.region._mousetransp = False
        owner = QMainWindow()
        owner.setGeometry(120, 100, 600, 220)
        owner.show()
        self.addCleanup(owner.deleteLater)
        self.region.setParent(owner, self.region.windowFlags() | Qt.WindowType.Tool)
        self.region.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.region.show()
        windows.WindowFocus.giveup(self.region.winId())
        overlay.route_overlay_translation(self.source, "fast", "existing translation")
        other = self.extra_region(self.region.x(), self.region.y())
        other.setParent(owner, other.windowFlags() | Qt.WindowType.Tool)
        other.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        other.show()
        windows.WindowFocus.giveup(other.winId())
        overlay.route_overlay_translation(
            overlay.OCRRegionText("other source", other, 1), "fast", "other translation"
        )
        top_methods = load_methods(
            SOURCE / "gui/translatorUI.py",
            "TranslatorWindow",
            {"settop", "checksettop", "istopmost", "canceltop"},
            {
                "windows": windows,
                "globalconfig": config,
                "os": os,
                "ocr_popup_is_visible": overlay.ocr_popup_is_visible,
            },
        )
        main = top_methods()
        main.winid = int(owner.winId())
        main.setontopthread_lock = threading.Lock()
        main.settop()
        menu = QMenu(self.region)
        env = {
            "QMenu": lambda parent: menu,
            "Qt": Qt,
            "LAction": QAction,
            "QCursor": types.SimpleNamespace(
                pos=lambda: self.region.mapToGlobal(QPoint(40, 40))
            ),
            "globalconfig": config,
            "suspend_ocr_capture": overlay.suspend_ocr_capture,
        }
        cls = load_methods(
            SOURCE / "gui/rangeselect.py", "rangeadjust", {"showmenu"}, env
        )
        enum_callback = ctypes.WINFUNCTYPE(c_bool, c_void_p, c_void_p)
        enum_windows = ctypes.windll.user32.EnumWindows
        enum_windows.argtypes = (enum_callback, c_void_p)
        enum_windows.restype = c_bool
        errors = []

        def assert_menu_above_regions(stage):
            self.assertTrue(menu.isVisible(), stage + ": menu closed unexpectedly")
            self.assertIs(QApplication.activePopupWidget(), menu, stage)
            order = []
            callback = enum_callback(lambda hwnd, _: (order.append(hwnd), True)[1])
            self.assertTrue(enum_windows(callback, None))
            for window in (self.region, self.region.panel, other, other.panel, owner):
                self.assertLess(
                    order.index(int(menu.winId())),
                    order.index(int(window.winId())),
                    stage + ": " + type(window).__name__ + " obscures the menu",
                )

        def inspect():
            try:
                self.assertTrue(menu.isVisible())
                assert_menu_above_regions("menu opened")
                # Exercise the real main-window topmost method, which also runs
                # periodically in the application while the game has focus.
                main.settop()
                assert_menu_above_regions("owner raised")
                # A new overlay result must retain this order with the actual
                # top-level owner chain, rather than only unowned test frames.
                other.panel.receive((1, None, ""))
                other.panel.receive((1, "fast", "new other translation"))
                main.settop()
                assert_menu_above_regions("new translation received")
                # Follow-window movement updates native geometry without
                # dismissing the popup as QWidget.show() would do.
                rect = other.getrect()
                windows.MoveWindow(
                    int(other.winId()),
                    rect.x() + 5,
                    rect.y(),
                    rect.width(),
                    rect.height(),
                    False,
                )
                other.panel.sync()
                main.settop()
                assert_menu_above_regions("frame moved")
            except Exception as error:
                errors.append(error)
            finally:
                menu.close()
                owner.hide()

        QTimer.singleShot(50, inspect)
        cls.showmenu(self.region, None)
        self.assertEqual(errors, [])
        self.assertEqual(self.region.panel.text, "existing translation")
        main.canceltop()
        self.assertFalse(main.istopmost())
        main.settop()
        self.assertTrue(
            main.istopmost(), "Topmost behavior did not resume after closing"
        )
        menu.deleteLater()

    def test_context_menu_exception_and_nested_suspensions_restore_capture(self):
        saved = config.copy()
        self.addCleanup(lambda: (config.clear(), config.update(saved)))
        config.update(multiregion=False, ocr_translation_overlay=False)
        self.region._mousetransp = False

        class FailingMenu(QMenu):
            def exec(self, *_):
                raise ValueError("menu failure")

        menu = FailingMenu(self.region)
        cls = load_methods(
            SOURCE / "gui/rangeselect.py",
            "rangeadjust",
            {"showmenu"},
            {
                "QMenu": lambda parent: menu,
                "Qt": Qt,
                "LAction": QAction,
                "QCursor": QCursor,
                "globalconfig": config,
                "suspend_ocr_capture": overlay.suspend_ocr_capture,
            },
        )
        with self.assertRaisesRegex(ValueError, "menu failure"):
            cls.showmenu(self.region, None)
        self.assertEqual(overlay.capture_without_overlays(lambda: 123), 123)
        with overlay.suspend_ocr_capture():
            with overlay.suspend_ocr_capture():
                self.assertIsNone(overlay.capture_without_overlays(lambda: 123))
            self.assertIsNone(overlay.capture_without_overlays(lambda: 123))
        self.assertEqual(overlay.capture_without_overlays(lambda: 123), 123)
        menu.deleteLater()

    def test_capture_spanning_menu_open_and_close_is_discarded(self):
        started, release = threading.Event(), threading.Event()
        results = []

        def capture():
            started.set()
            if not release.wait(1):
                raise RuntimeError("test capture timed out")
            return "frame potentially containing the menu"

        worker = threading.Thread(
            target=lambda: results.append(overlay.capture_without_overlays(capture))
        )
        worker.start()
        try:
            self.assertTrue(started.wait(0.5))
            with overlay.suspend_ocr_capture():
                pass
            release.set()
            worker.join(0.5)
            self.assertFalse(worker.is_alive())
            self.assertEqual(results, [None])
            self.assertEqual(
                overlay.capture_without_overlays(lambda: "clean frame"), "clean frame"
            )
        finally:
            release.set()
            worker.join(1)

    def test_stability_wait_skips_suspended_menu_capture(self):
        samples = []
        cls = load_methods(
            SOURCE / "textio/textsource/ocrtext.py",
            "rangemanger",
            {"waitforstable"},
            {
                "imageCutEx": lambda *args: QImage(),
                "QRect": QRect,
                "cvMat": lambda image: samples.append(image),
            },
        )
        manager = cls()
        manager.range_ui = types.SimpleNamespace(
            capture_snapshot=lambda: overlay.OCRCaptureSnapshot(
                1, self.region.getrect().getRect()
            ),
            update_overlay_background=lambda *args: None,
        )
        manager.ref = types.SimpleNamespace(hwnd=None)
        self.assertFalse(manager.waitforstable())
        self.assertEqual(samples, [])

    def test_moving_selection_during_manual_or_auto_ocr_discards_result(self):
        for auto, mode in ((False, "period"), (True, "period"), (True, "analysis")):
            with self.subTest(auto=auto, mode=mode):
                ui_class = load_methods(
                    SOURCE / "gui/rangeselect.py",
                    "rangeadjust",
                    {
                        "capture_snapshot",
                        "getrect",
                        "remember_overlay_source",
                        "invalidate_overlay",
                    },
                    {
                        "QRect": QRect,
                        "OCRCaptureSnapshot": getattr(
                            overlay, "OCRCaptureSnapshot", None
                        ),
                    },
                )
                ui = ui_class()
                ui.ocr_source_lock = threading.RLock()
                ui._rect = QRect(100, 100, 300, 100)
                ui._ocr_overlay_revision, ui._ocr_overlay_original = 1, None
                ui.overlaytranslationsignal = types.SimpleNamespace(
                    emit=lambda payload: None
                )
                owner = type("Owner", (), {})()
                owner.hwnd, owner.ending, owner.ranges = None, False, []
                moved = [False]

                def recognize(image):
                    if not moved[0]:
                        ui._rect = QRect(500, 200, 300, 100)
                        ui.invalidate_overlay()
                        moved[0] = True
                    return types.SimpleNamespace(
                        textonly=(
                            "old-position text" if not image else "new-position text"
                        ),
                        error=False,
                        result=types.SimpleNamespace(isocrtranslate=False),
                    )

                images = [False, True]
                cls = load_methods(
                    SOURCE / "textio/textsource/ocrtext.py",
                    "rangemanger",
                    {"getresmanual", "getresauto", "_commit_ocr_result"},
                    {
                        "globalconfig": config,
                        "QRect": QRect,
                        "OCRRegionText": overlay.OCRRegionText,
                        "imageCutEx": lambda *args: types.SimpleNamespace(
                            isNull=lambda: False, index=images.pop(0)
                        ),
                        "ocr_run": lambda img: recognize(img.index),
                        "cvMat": lambda image: types.SimpleNamespace(
                            MSSIM=lambda other: 1
                        ),
                        "gobject": types.SimpleNamespace(
                            base=types.SimpleNamespace(
                                thresholdsett1=types.SimpleNamespace(
                                    emit=lambda value: None
                                ),
                                thresholdsett2=types.SimpleNamespace(
                                    emit=lambda value: None
                                ),
                            )
                        ),
                        "time": time,
                        "NativeUtils": types.SimpleNamespace(distance=lambda a, b: 100),
                    },
                )
                manager = cls()
                manager.range_ui, manager.ref = ui, owner
                manager.savelastimg, manager.savelastrecimg = (
                    "old image",
                    "old recognition image",
                )
                manager.savelasttext, manager.lastocrtime = "old cache", 0
                manager._last_capture_rect = None
                ui.update_overlay_background = lambda *args: None
                owner.ranges = [manager]
                saved = config.copy()
                try:
                    config.update(ocr_auto_method_v2=mode, ocr_interval=0)
                    method = manager.getresauto if auto else manager.getresmanual
                    self.assertIsNone(method())
                    self.assertEqual(manager.savelasttext, "old cache")
                    self.assertEqual(manager.lastocrtime, 0)
                    self.assertEqual(manager.savelastimg, "old image")
                    self.assertEqual(manager.savelastrecimg, "old recognition image")
                    self.assertIsNone(ui._ocr_overlay_original)
                    fresh = method()
                    self.assertEqual(fresh.textonly, "new-position text")
                    self.assertTrue(
                        overlay.overlay_source_is_current(fresh.ocr_overlay_source)
                    )
                finally:
                    config.clear()
                    config.update(saved)

    def test_result_moved_before_batch_assembly_does_not_take_new_revision(self):
        second = self.extra_region()
        first_result = types.SimpleNamespace(
            textonly="old A",
            error=False,
            result=types.SimpleNamespace(isocrtranslate=False),
            ocr_overlay_source=self.source,
        )
        second_result = types.SimpleNamespace(
            textonly="current B",
            error=False,
            result=types.SimpleNamespace(isocrtranslate=False),
            ocr_overlay_source=overlay.OCRRegionText("current B", second, 1),
        )

        def recognize_second():
            self.region._ocr_overlay_revision += 1
            return second_result

        managers = [
            types.SimpleNamespace(
                range_ui=self.region, getresmanual=lambda: first_result
            ),
            types.SimpleNamespace(range_ui=second, getresmanual=recognize_second),
        ]
        cls = load_methods(
            SOURCE / "textio/textsource/ocrtext.py",
            "ocrtext",
            {"getallres"},
            {
                "globalconfig": config,
                "OCRRegionText": overlay.OCRRegionText,
                "OCRRegionBatch": overlay.OCRRegionBatch,
                "overlay_source_is_current": overlay.overlay_source_is_current,
            },
        )
        owner = cls()
        owner.ranges, owner.ending = managers, False
        owner.getuseranges = lambda: managers
        result = owner.getallres(False)
        self.assertEqual([str(s) for s in result.ocr_region_sources], ["current B"])

    def test_ordinary_dialog_blocks_capture_until_hidden(self):
        dialog = QDialog()
        dialog.setGeometry(self.region.geometry())
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        pump(0.03)
        captured = []
        try:
            self.assertIsNone(
                overlay.capture_without_overlays(lambda: captured.append(True))
            )
            self.assertEqual(captured, [])
        finally:
            dialog.hide()
        self.assertEqual(
            overlay.capture_without_overlays(lambda: "clean frame"), "clean frame"
        )

    def test_settings_and_dialogs_block_only_overlapping_regions(self):
        second = self.extra_region(900, 100)
        rect_a, rect_b = self.region.getrect(), second.getrect()
        for window_type in (QMainWindow, QDialog):
            with self.subTest(window_type=window_type.__name__):
                window = window_type()
                self.addCleanup(window.deleteLater)
                try:
                    window.setGeometry(self.region.geometry())
                    window.show()
                    pump(0.03)
                    self.assertIsNone(
                        overlay.capture_without_overlays(lambda: "covered A", rect_a)
                    )
                    self.assertEqual(
                        overlay.capture_without_overlays(lambda: "uncovered B", rect_b),
                        "uncovered B",
                    )
                    window.setGeometry(second.geometry())
                    pump(0.03)
                    self.assertEqual(
                        overlay.capture_without_overlays(lambda: "uncovered A", rect_a),
                        "uncovered A",
                    )
                    self.assertIsNone(
                        overlay.capture_without_overlays(lambda: "covered B", rect_b)
                    )
                finally:
                    window.hide()
                self.assertEqual(
                    overlay.capture_without_overlays(lambda: "resumed B", rect_b),
                    "resumed B",
                )

    def test_capture_spanning_ordinary_popup_show_and_hide_is_discarded(self):
        started, release = threading.Event(), threading.Event()
        results = []
        rectangle = self.region.getrect()
        window = QDialog()
        window.setGeometry(self.region.geometry())
        self.addCleanup(window.deleteLater)

        def capture():
            started.set()
            if not release.wait(1):
                raise RuntimeError("test capture timed out")
            return "frame potentially containing dialog text"

        worker = threading.Thread(
            target=lambda: results.append(
                overlay.capture_without_overlays(capture, rectangle)
            )
        )
        worker.start()
        try:
            self.assertTrue(started.wait(0.5))
            window.show()
            window.hide()
            release.set()
            worker.join(1)
            self.assertFalse(worker.is_alive())
            self.assertEqual(results, [None])
            self.assertEqual(
                overlay.capture_without_overlays(lambda: "resumed", rectangle),
                "resumed",
            )
        finally:
            window.hide()
            release.set()
            worker.join(1)

    def test_other_application_menu_pauses_capture_then_resumes(self):
        menu = QMenu()
        menu.addAction("Application menu text")
        self.addCleanup(menu.deleteLater)
        try:
            menu.popup(self.region.mapToGlobal(QPoint(20, 20)))
            pump(0.03)
            self.assertTrue(menu.isVisible())
            self.assertIsNone(
                overlay.capture_without_overlays(
                    lambda: "menu pixels", self.region.getrect()
                )
            )
        finally:
            menu.hide()
        self.assertEqual(
            overlay.capture_without_overlays(lambda: "resumed", self.region.getrect()),
            "resumed",
        )

    def test_combo_popup_pauses_capture_then_resumes(self):
        combo = QComboBox()
        combo.addItems(["Choice A", "Choice B", "Choice C"])
        combo.move(self.region.mapToGlobal(QPoint(20, 20)))
        combo.show()
        self.addCleanup(combo.deleteLater)
        # Exercise Qt's actual dropdown container without relying on foreground
        # focus, which this desktop may remove immediately after showPopup().
        popup = combo.view().window()
        try:
            self.assertEqual(popup.windowType(), Qt.WindowType.Popup)
            popup.show()
            self.assertTrue(popup.isVisible())
            self.assertIsNone(
                overlay.capture_without_overlays(
                    lambda: "dropdown text", self.region.getrect()
                )
            )
            popup.hide()
            self.assertEqual(
                overlay.capture_without_overlays(
                    lambda: "resumed", self.region.getrect()
                ),
                "resumed",
            )
        finally:
            popup.hide()
            combo.hide()

    def test_out_of_order_region_results_and_independent_invalidation(self):
        second = self.extra_region()
        source_b = overlay.OCRRegionText("source B", second, 1)
        subject, events, history, sql = translation_subject()
        subject.currenttext_raw = source_b

        def send(source, text, signature="old", state=0):
            subject.GetTranslationCallback(
                {"fast"},
                None,
                "fast",
                signature,
                [],
                None,
                str(source),
                [],
                None,
                text,
                state,
                ocr_overlay_source=source,
            )

        send(source_b, "B first", signature="current", state=1)
        send(self.source, "A late", state=1)
        send(source_b, "B complete", signature="current", state=2)
        send(self.source, "A complete", state=2)
        self.assertEqual(self.region.panel.text, "A complete")
        self.assertEqual(second.panel.text, "B complete")
        self.region._ocr_overlay_revision = 2
        self.region.panel.receive((2, None, ""))
        send(self.source, "A stale after update")
        send(source_b, "B still current", signature="current")
        self.assertEqual(self.region.panel.text, "")
        self.assertEqual(second.panel.text, "B still current")
        # Viewing history does not redirect live frame results to another region.
        subject.history.viewptr = 0
        send(source_b, "B live while viewing history", signature="current")
        self.assertEqual(second.panel.text, "B live while viewing history")

    def test_region_queue_skips_only_superseded_region_and_keeps_api_behavior(self):
        second = self.extra_region()
        old_a = overlay.OCRRegionTask(self.source)
        current_b = overlay.OCRRegionTask(overlay.OCRRegionText("B", second, 1))
        self.region._ocr_overlay_revision = 2
        current_a = overlay.OCRRegionTask(
            overlay.OCRRegionText("A new", self.region, 2)
        )
        engine = translation_engine()
        processed = []
        engine.translate_and_collect = (
            lambda lang, text, auto, callback: processed.append(text)
        )
        for text, marker in [
            ("A old", old_a),
            ("B current", current_b),
            ("A current", current_a),
        ]:
            engine.gettask((lambda *a: None, text, marker, True, []))
        engine._fythread()
        self.assertEqual(processed, ["B current", "A current"])
        processed.clear()
        for text in ["ordinary old", "ordinary latest"]:
            engine.gettask((lambda *a: None, text, None, True, []))
        engine._fythread()
        self.assertEqual(processed, ["ordinary latest"])
        processed.clear()
        for text in ["API first", "API second"]:
            engine.gettask((lambda *a: None, text, lambda *a: None, True, []))
        engine._fythread()
        self.assertEqual(processed, ["API first", "API second"])

    def test_removed_region_source_end_and_toggle_cancel_owned_tasks(self):
        class Owner:
            pass

        second = self.extra_region()
        owner = Owner()
        owner.ending = False
        owner.ranges = [
            types.SimpleNamespace(range_ui=self.region),
            types.SimpleNamespace(range_ui=second),
        ]
        a = overlay.OCRRegionText("A", self.region, 1, owner=owner)
        b = overlay.OCRRegionText("B", second, 1, owner=owner)
        task_a, task_b = overlay.OCRRegionTask(a), overlay.OCRRegionTask(b)
        self.assertTrue(task_a.is_current())
        owner.ranges.pop(0)
        self.assertFalse(task_a.is_current())
        self.assertTrue(task_b.is_current())
        overlay.route_overlay_translation(a, "fast", "removed region")
        self.assertEqual(self.region.panel.text, "")
        config["ocr_translation_overlay"] = False
        self.assertFalse(task_b.is_current())
        config["ocr_translation_overlay"] = True
        owner.ending = True
        self.assertFalse(task_b.is_current())
        overlay.route_overlay_translation(b, "fast", "previous source")
        self.assertEqual(second.panel.text, "")

    def test_batch_dispatch_direct_ocr_translation_and_external_callback(self):
        second = self.extra_region()
        direct = overlay.OCRRegionText("already translated", second, 1)
        direct.ocr_direct_translation = True
        batch = overlay.OCRRegionBatch([self.source, direct])
        subject, _, _, _ = translation_subject()
        normal, direct_calls = [], []
        subject.textgetmethod_1 = (
            lambda text, **kwargs: normal.append((text, kwargs)) or True
        )
        subject.displayinfomessage = lambda text, kind: (
            direct_calls.append((text, kind)),
            overlay.route_overlay_translation(text, "ocr", text),
        )
        subject.textgetmethod(batch)
        self.assertEqual([v[0] for v in normal], [self.source])
        self.assertEqual(direct_calls, [(direct, "<notrans>")])
        self.assertEqual(second.panel.text, "already translated")
        normal.clear()
        subject.textgetmethod(batch, waitforresultcallback=lambda *a: None)
        self.assertEqual(len(normal), 1)
        self.assertIs(normal[0][0], batch)
        self.assertEqual(len(direct_calls), 1)

    def test_multi_ocr_errors_unchanged_regions_and_overlay_enable_reset(self):
        second = self.extra_region()
        errors, resets, styles = [], [], []
        good = types.SimpleNamespace(
            textonly="B changed",
            error=False,
            result=types.SimpleNamespace(isocrtranslate=False),
            ocr_overlay_source=overlay.OCRRegionText("B changed", second, 1),
        )
        bad = types.SimpleNamespace(
            error=True,
            displayerror=lambda: errors.append("A OCR error"),
            ocr_overlay_source=overlay.OCRRegionText("", self.region, 1),
        )
        values = [bad, good]
        managers = []
        for idx, region in enumerate([self.region, second]):
            region.invalidate_overlay = lambda n=idx: resets.append(n)
            region.setstyle = lambda n=idx: styles.append(n)
            managers.append(
                types.SimpleNamespace(
                    range_ui=region,
                    lastocrtime=12,
                    savelasttext="old",
                    savelastrecimg="image",
                    getresauto=lambda n=idx: values[n],
                    getresmanual=lambda n=idx: values[n],
                )
            )
        cls = load_methods(
            SOURCE / "textio/textsource/ocrtext.py",
            "ocrtext",
            {"getallres", "setstyle"},
            {
                "OCRRegionText": overlay.OCRRegionText,
                "OCRRegionBatch": overlay.OCRRegionBatch,
                "globalconfig": config,
                "gobject": types.SimpleNamespace(base=types.SimpleNamespace()),
                "overlay_source_is_current": overlay.overlay_source_is_current,
            },
        )
        owner = cls()
        owner.ranges, owner.ending, owner._overlay_enabled = managers, False, False
        owner.getuseranges = lambda: owner.ranges
        batch = owner.getallres(True)
        self.assertEqual(errors, ["A OCR error"])
        self.assertEqual(len(batch.ocr_region_sources), 1)
        self.assertIs(batch.ocr_region_sources[0].ocr_overlay_context[0](), second)
        values[0] = None
        batch = owner.getallres(True)
        self.assertEqual(len(batch.ocr_region_sources), 1)
        owner.setstyle()
        self.assertEqual(resets, [0, 1])
        self.assertTrue(
            all(
                m.lastocrtime == 0
                and m.savelasttext is None
                and m.savelastrecimg is None
                for m in managers
            )
        )
        owner.setstyle()
        self.assertEqual(resets, [0, 1])
        config["ocr_translation_overlay"] = False
        values[:] = [good, good]
        combined = owner.getallres(True)
        self.assertEqual(str(combined), "B changed\nB changed")
        self.assertFalse(hasattr(combined, "ocr_region_sources"))

    def test_real_range_ui_lifecycle_and_frame_passthrough(self):
        modules = {
            "NativeUtils": {},
            "gobject": {"base": types.SimpleNamespace(hwnd=None)},
            "myutils.hwnd": {"safepixmap": lambda data: QPixmap()},
            "gui.dynalang": {
                "LAction": QAction,
                "LDialog": QDialog,
                "LFormLayout": QFormLayout,
            },
            "gui.usefulwidget": {
                "getspinbox": lambda *a, **k: None,
                "ColorButton": lambda *a, **k: None,
                "getsimpleswitch": lambda *a, **k: None,
            },
            "myutils.wrapper": {"Singleton_activate": lambda cls: cls},
        }
        previous = {key: sys.modules.get(key) for key in modules}
        previous["gui.ocrtranslationoverlay"] = sys.modules.get(
            "gui.ocrtranslationoverlay"
        )
        for key, attrs in modules.items():
            mod = types.ModuleType(key)
            mod.__dict__.update(attrs)
            sys.modules[key] = mod
        sys.modules["gui.ocrtranslationoverlay"] = overlay
        target = None
        try:
            rangespec = importlib.util.spec_from_file_location(
                "range_ui", SOURCE / "gui/rangeselect.py"
            )
            range_module = importlib.util.module_from_spec(rangespec)
            rangespec.loader.exec_module(range_module)
            target = range_module.rangeadjust(None, [])
            target.setrect(QRect(200, 200, 500, 150))
            revision = target.remember_overlay_source("a sentence")
            source = overlay.OCRRegionText("a sentence", target, revision)
            overlay.route_overlay_translation(source, "fast", "这是一段覆盖译文。")
            pump()
            self.assertTrue(target.translation_overlay.isVisible())
            raw = QImage(120, 60, QImage.Format.Format_ARGB32)
            raw.fill(QColor("#fffaf0"))
            target.update_overlay_background(raw, target.getrect())
            self.assertEqual(target.translation_overlay.background_rgb, (255, 250, 240))
            move_calls = []
            native_move = windows.MoveWindow
            try:
                windows.MoveWindow = lambda *args: (
                    move_calls.append(args),
                    native_move(*args),
                )[1]
                for _ in range(100):
                    target.setGeometry(target.geometry())
                self.assertEqual(move_calls, [])
            finally:
                windows.MoveWindow = native_move
            snapshot = target.capture_snapshot()
            geometry = target.geometry()
            moved = QRect(geometry)
            moved.translate(35, 20)
            target.setGeometry(moved)
            pump(0.03)
            self.assertFalse(overlay.overlay_source_is_current(source))
            self.assertEqual(target.translation_overlay.text, "")
            target.setGeometry(geometry)
            pump(0.03)
            self.assertEqual(target.capture_snapshot().rect, snapshot.rect)
            self.assertIsNone(
                target.remember_overlay_source("stale after move and return", snapshot)
            )
            snapshot = target.capture_snapshot()
            resized = QRect(geometry)
            resized.setWidth(resized.width() + 50)
            target.setGeometry(resized)
            pump(0.03)
            self.assertIsNone(
                target.remember_overlay_source("stale after resize", snapshot)
            )
            target.setGeometry(geometry)
            target.setmousetransp(True)
            region_handle = ctypes.windll.gdi32.CreateRectRgn(0, 0, 0, 0)
            ctypes.windll.user32.GetWindowRgn.argtypes = c_void_p, c_void_p
            ctypes.windll.user32.GetWindowRgn(int(target.winId()), region_handle)
            self.assertFalse(ctypes.windll.gdi32.PtInRegion(region_handle, 200, 80))
            self.assertTrue(ctypes.windll.gdi32.PtInRegion(region_handle, 1, 1))
            ctypes.windll.gdi32.DeleteObject(region_handle)
            target.setrect(QRect(220, 210, 400, 130))
            self.assertEqual(target.translation_overlay.text, "")
            overlay.route_overlay_translation(source, "fast", "stale after selection")
            self.assertEqual(target.translation_overlay.text, "")
            source = overlay.OCRRegionText(
                "new sentence", target, target.remember_overlay_source("new sentence")
            )
            overlay.route_overlay_translation(source, "fast", "新的译文")
            target.hide()
            self.assertFalse(target.translation_overlay.isVisible())
            target.show()
            self.assertTrue(target.translation_overlay.isVisible())
            target.close()
            self.assertFalse(target.translation_overlay.isVisible())
        finally:
            if target is not None:
                overlay._overlays.discard(target.translation_overlay)
                target.close()
                target.deleteLater()
            for key, mod in previous.items():
                if mod is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = mod

    def test_mouse_passthrough_and_native_capture_affinity(self):
        overlay.route_overlay_translation(self.source, "fast", "覆盖译文")
        pump()
        exstyle = windows.GetWindowLong(
            int(self.region.panel.winId()), windows.GWL_EXSTYLE
        )
        self.assertTrue(exstyle & windows.WS_EX_TRANSPARENT)
        self.assertTrue(exstyle & windows.WS_EX_NOACTIVATE)
        if overlay._windows_build() >= 19041:
            self.assertTrue(self.region.panel.capture_excluded)

    def test_real_gdi_exclusion(self):
        # A locked/noninteractive desktop may return only the wallpaper even
        # when the synthetic window is visible to Qt. Detect this *before*
        # displaying the overlay; matching wallpaper is not an exclusion test.
        ctypes.windll.dwmapi.DwmFlush()
        baseline = gdi_crop(self.region.getrect())
        self.assertFalse(baseline.isNull())
        baseline_color = baseline.pixelColor(
            baseline.width() // 2, baseline.height() // 2
        )
        if any(
            abs(actual - expected) > 5
            for actual, expected in zip(baseline_color.getRgb()[:3], (17, 170, 221))
        ):
            self.skipTest(
                "The current desktop does not expose the synthetic window to GDI; "
                "rerun on an unlocked interactive desktop"
            )
        overlay.route_overlay_translation(self.source, "fast", "覆盖译文")
        pump()
        if not self.region.panel.capture_excluded:
            self.skipTest(
                "Native capture exclusion is unavailable; fallback is tested separately"
            )
        ctypes.windll.dwmapi.DwmFlush()
        captured = gdi_crop(self.region.getrect())
        self.assertFalse(captured.isNull())
        # Sample the center, away from the test window's title bar and resize border.
        color = captured.pixelColor(captured.width() // 2, captured.height() // 2)
        captured.save(str(OUTPUT / "gdi-capture-under-overlay.png"))
        print(
            "Capture center RGB:", color.getRgb(), "baseline:", baseline_color.getRgb()
        )
        for a, b in zip(color.getRgb()[:3], baseline_color.getRgb()[:3]):
            self.assertLessEqual(abs(a - b), 5)

    def test_fallback_worker_hides_and_restores(self):
        overlay.route_overlay_translation(self.source, "fast", "fallback")
        self.region.panel.capture_excluded = False
        observed = []
        result = []

        def capture():
            observed.append(self.region.panel.isVisible())
            return 123

        worker = threading.Thread(
            target=lambda: result.append(overlay.capture_without_overlays(capture))
        )
        worker.start()
        deadline = time.monotonic() + 3
        while worker.is_alive() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        worker.join(0.1)
        self.assertEqual(result, [123])
        self.assertEqual(observed, [False])
        self.assertTrue(self.region.panel.isVisible())

        def fail():
            raise ValueError("test error")

        with self.assertRaises(ValueError):
            overlay.capture_without_overlays(fail)
        self.assertTrue(self.region.panel.isVisible())

    def test_python37_syntax(self):
        for p in SOURCE.rglob("*.py"):
            ast.parse(
                p.read_text(encoding="utf-8"), filename=str(p), feature_version=(3, 7)
            )

    def test_actual_translation_callback_routing(self):
        tree = ast.parse((SOURCE / "LunaTranslator.py").read_text(encoding="utf-8"))
        base = next(
            c
            for c in tree.body
            if isinstance(c, ast.ClassDef) and c.name == "BASEOBJECT"
        )
        names = {
            "GetTranslationCallback",
            "__safecallback",
            "__erroroutput",
            "_delayshowraw",
        }
        base.body = [
            n for n in base.body if isinstance(n, ast.FunctionDef) and n.name in names
        ]
        base.bases = []
        emitted = []
        signal = types.SimpleNamespace(emit=lambda *args: emitted.append(args))
        env = {
            "functools": functools,
            "globalconfig": config,
            "route_overlay_translation": overlay.route_overlay_translation,
            "overlay_source_is_current": overlay.overlay_source_is_current,
            "TranslateResult": lambda *args: args,
            "TranslateColor": lambda c: c,
            "dynamicapiname": lambda c: c,
            "_TR": lambda t: t,
            "gobject": types.SimpleNamespace(
                base=types.SimpleNamespace(dispatch_translate=signal)
            ),
        }
        exec(
            compile(
                ast.Module(body=[base], type_ignores=[]),
                "<translation callback>",
                "exec",
            ),
            env,
        )
        subject = env["BASEOBJECT"]()
        subject.gettranslatelock = threading.Lock()
        subject.currentsignature = "current"
        subject.currenttext_raw = self.source
        subject.currenttranslate = ""
        subject.refresh_on_get_trans_signature = None
        subject.history = types.SimpleNamespace(viewptr=-1, appendtrans=lambda *a: None)
        subject.translation_ui = types.SimpleNamespace(displayres=signal)
        subject.transhis = types.SimpleNamespace(getnewtranssignal=signal)
        subject.textsource = types.SimpleNamespace(sqlqueueput=lambda *a: None)
        subject.solveaftertrans = lambda result, params: result
        subject.dispatchoutputer = lambda *a: None

        def send(text, state, signature="current", callback=None):
            subject.GetTranslationCallback(
                {"fast"},
                callback,
                "fast",
                signature,
                [],
                None,
                "raw",
                [],
                None,
                text,
                state,
            )

        send("old signature", 0, signature="old")
        self.assertEqual(self.region.panel.text, "")
        send("流式第一段", 1)
        self.assertEqual(self.region.panel.text, "流式第一段")
        send("流式完成", 2)
        self.assertEqual(self.region.panel.text, "流式完成")
        subject.currenttext_raw = "clipboard text"
        send("foreign translation", 0)
        self.assertEqual(self.region.panel.text, "流式完成")
        subject.currenttext_raw = self.source
        send("API-only translation", 0, callback=lambda result: None)
        self.assertEqual(self.region.panel.text, "流式完成")
        subject.history.viewptr = 0
        send("history view", 0)
        self.assertEqual(self.region.panel.text, "流式完成")

    def test_actual_ocr_single_and_combined_region_routing(self):
        tree = ast.parse(
            (SOURCE / "textio/textsource/ocrtext.py").read_text(encoding="utf-8")
        )
        cls = next(
            c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == "ocrtext"
        )
        cls.body = [
            n
            for n in cls.body
            if isinstance(n, ast.FunctionDef) and n.name == "getallres"
        ]
        cls.bases = []
        env = {
            "OCRRegionText": overlay.OCRRegionText,
            "OCRRegionBatch": overlay.OCRRegionBatch,
            "globalconfig": config,
            "overlay_source_is_current": overlay.overlay_source_is_current,
        }
        exec(
            compile(ast.Module(body=[cls], type_ignores=[]), "<OCR routing>", "exec"),
            env,
        )
        result = types.SimpleNamespace(
            textonly="raw source",
            error=False,
            result=types.SimpleNamespace(isocrtranslate=False),
            ocr_overlay_source=overlay.OCRRegionText("raw source", self.region, 1),
        )
        region_manager = types.SimpleNamespace(
            range_ui=self.region, getresauto=lambda: result, getresmanual=lambda: result
        )
        subject = env["ocrtext"]()
        subject.ranges = [region_manager]
        subject.ending = False
        subject.getuseranges = lambda: [region_manager]
        single = subject.getallres(False)
        self.assertEqual(str(single), "raw source")
        self.assertEqual(single.ocr_overlay_context[1], 1)
        overlay.route_overlay_translation(single, "fast", "单区域译文")
        self.assertEqual(self.region.panel.text, "单区域译文")
        subject.getuseranges = lambda: [region_manager, region_manager]
        combined = subject.getallres(False)
        self.assertFalse(hasattr(combined, "ocr_overlay_context"))
        self.assertEqual(str(combined), "raw source\nraw source")
        self.assertEqual(len(combined.ocr_region_sources), 2)
        self.assertEqual(self.region.panel.text, "单区域译文")
        # Disabled mode uses the original plain-string path, including source
        # deduplication in the main translation dispatcher.
        config["ocr_translation_overlay"] = False
        subject.getuseranges = lambda: [region_manager]
        self.assertIs(type(subject.getallres(False)), str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
