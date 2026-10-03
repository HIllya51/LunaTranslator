"""Exercise the real UI and OCR settings with isolated config and checkout sources."""

import ast
import ctypes
import importlib
import json
import os
from pathlib import Path
import sys
import time
import traceback
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if not os.environ.get("LUNA_TRANSLATOR_DIR"):
    raise SystemExit("Set LUNA_TRANSLATOR_DIR to a built Windows distribution.")
APP = Path(os.environ["LUNA_TRANSLATOR_DIR"]).resolve()
SOURCE = ROOT / "src/LunaTranslator"
RUNTIME = APP / "files" / os.environ.get("LUNA_TEST_RUNTIME", "runtime3.13-64")
TEST_CONFIG = Path(tempfile.mkdtemp(prefix="lunatranslator-ocr-ui-"))
PATCH_SOURCE = SOURCE
base_config = json.loads(
    (SOURCE / "defaultconfig/config.json").read_text(encoding="utf-8")
)
safe_config = {
    "languageuse2": "zh",
    "ocr_translation_overlay": True,
    "ocr_translation_overlay_adaptive_background": True,
    "ocr_translation_overlay_show_main": False,
    "ocrregions2": [],
    "transuigeo": [100, 100, 780, 200],
    "showintab": False,
    "keepontop": False,
    "networktcpenable": False,
    "read_raw": False,
    "read_trans": False,
    "autorun": False,
    "autoupdate": False,
    "rendertext_using": "textbrowser",
    "sourcestatus2": {
        key: dict(value, use=(key == "ocr"))
        for key, value in base_config["sourcestatus2"].items()
    },
    "fanyi": {key: {"use": False} for key in base_config["fanyi"]},
}
(TEST_CONFIG / "config.json").write_text(json.dumps(safe_config), encoding="utf-8")
os.chdir(APP)
sys.path[:0] = [str(SOURCE), str(RUNTIME), str(RUNTIME / "pylibs.zip")]
dll_handles = [
    os.add_dll_directory(str(path))
    for path in (RUNTIME, RUNTIME / "PyQt5/Qt5/bin", APP / "files/DLL64")
]
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(RUNTIME / "PyQt5/Qt5/plugins/platforms")
import gobject

gobject.thisuserconfig = str(TEST_CONFIG)
import main

main.prepareqtenv(None)
for name, path in [
    ("gui", PATCH_SOURCE / "gui"),
    ("gui.setting", PATCH_SOURCE / "gui/setting"),
    ("textio.textsource", PATCH_SOURCE / "textio/textsource"),
    ("translator", PATCH_SOURCE / "translator"),
]:
    package = importlib.import_module(name)
    package.__path__ = [str(path)] + list(package.__path__)
sys.path.insert(0, str(PATCH_SOURCE))
from qtsymbols import *

app = QApplication.instance() or QApplication([])
app.setQuitOnLastWindowClosed(False)
callback_errors = []


def record_error(kind, error, trace):
    callback_errors.append(error)
    traceback.print_exception(kind, error, trace)


sys.excepthook = record_error
from LunaTranslator import BASEOBJECT
from gui.translatorUI import TranslatorWindow
from gui.rangeselect import yangshisetting
from gui.ocrtranslationoverlay import capture_without_overlays
import windows

gobject.base = BASEOBJECT()
gobject.base.parsedefaultfont()
print("Constructing the real TranslatorWindow...", flush=True)
window = TranslatorWindow()
gobject.base.translation_ui = window
gobject.base.commonstylebase = QWidget(window)
app.processEvents()
if callback_errors:
    raise RuntimeError(
        "UI construction raised %d Qt callback error(s)" % len(callback_errors)
    )
print("Real UI construction succeeded.", flush=True)
window.set_ocr_overlay_mode(True)
app.processEvents()
print("Folded dimensions:", window.width(), window.height(), flush=True)
window.set_ocr_overlay_mode(False)
app.processEvents()
print("Expanded dimensions:", window.width(), window.height(), flush=True)
# Open the actual OCR settings page and click its actual persisted switch.
from gui.setting.textinput_ocr import internal
from textio.textsource.ocrtext import ocrtext
from myutils.config import globalconfig, saveallconfig

source = ocrtext.__new__(ocrtext)
source.ranges, source.ending, source._overlay_enabled = [], False, True
gobject.base.textsource = source
settings = QMainWindow()
settings.ocrswitchs = {}
page, create_page = internal(settings)
create_page()
page.setCurrentIndex(1)
app.processEvents()
switch = settings.ocrshowmainswitch
assert not switch.isChecked()
assert window.ocr_overlay_collapsed
switch.click()
app.processEvents()
assert globalconfig["ocr_translation_overlay_show_main"] is True
assert not window.ocr_overlay_collapsed
assert not window.translate_text.isHidden()
assert window.height() > 30
print("Actual settings switch shows the full main window.", flush=True)
saveallconfig(test=True)
saved = json.loads((TEST_CONFIG / "config.json").read_text(encoding="utf-8"))
assert saved["ocr_translation_overlay_show_main"] is True
switch.click()
app.processEvents()
assert globalconfig["ocr_translation_overlay_show_main"] is False
assert window.ocr_overlay_collapsed
assert window.translate_text.isHidden()
saveallconfig(test=True)
saved = json.loads((TEST_CONFIG / "config.json").read_text(encoding="utf-8"))
assert saved["ocr_translation_overlay_show_main"] is False
print(
    "Actual settings switch folds the main window and persists both states.", flush=True
)
# Exercise popup protection with the actual style dialog and OCR settings page.
gobject.base.settin_ui = settings
source.hwnd = None
manager = source.newrangeadjustor()
region = manager.range_ui
settings.setCentralWidget(page)
settings.resize(600, 450)
settings.show()
app.processEvents()
rect = windows.GetWindowRect(int(settings.winId()))
region.setrect(QRect(rect[0] + 20, rect[1] + 50, 250, 120))
assert capture_without_overlays(lambda: "settings pixels", region.getrect()) is None
settings.hide()
app.processEvents()
assert capture_without_overlays(lambda: "uncovered", region.getrect()) == "uncovered"
style = yangshisetting(region)
assert style is not None
app.processEvents()
rect = windows.GetWindowRect(int(style.winId()))
region.setrect(QRect(rect[0] + 20, rect[1] + 50, 180, 80))
assert capture_without_overlays(lambda: "style pixels", region.getrect()) is None
style.close()
app.processEvents()
assert capture_without_overlays(lambda: "resumed", region.getrect()) == "resumed"
print(
    "Actual OCR settings and style dialogs pause covered capture and resume after hiding.",
    flush=True,
)
region.close()
source.ranges.clear()
del manager
if callback_errors:
    raise RuntimeError("UI mode changes raised Qt callback errors")
for timer in window.findChildren(QTimer):
    timer.stop()
page.hide()
page.deleteLater()
settings.deleteLater()
# This test window never starts translation engines or the app's services.
# Do not call TranslatorWindow.closeEvent(), which is the application's exit path.
window.hide()
window.deleteLater()
QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
print("Real startup constructor and mode transitions passed.", flush=True)
