# OCR translation overlay checks

Run these checks on Windows with Python 3.13 and a built LunaTranslator distribution. The distribution supplies Qt and native DLLs; the code under test comes from this checkout. The real UI check uses an isolated temporary configuration and disables OCR engines, translators, speech, automatic recognition, TCP services, and automatic updates. It does not read the user's saved accounts or configuration.

From the repository root in PowerShell:

```powershell
$env:LUNA_TRANSLATOR_DIR = 'C:\path\to\LunaTranslator'
$env:LUNA_TEST_RUNTIME = 'runtime3.13-64'
python -B tests/test_ocr_translation_overlay.py
python -B tests/check_ocr_overlay_ui.py
```

Use an unlocked interactive Windows desktop for the capture tests. The suite loads Qt from the selected distribution. Native capture tests are skipped if its DLLs are unavailable or the desktop does not expose the synthetic test window to GDI. Native window flags and the capture fallback are checked separately. It saves synthetic preview images to the system temporary directory.

The regression suite covers region provenance, stale and out-of-order results, duplicate text in different regions, streaming and engine selection, real translator queue dispatch, multi-region additions, disabled-mode compatibility, click-through windows, capture exclusion and its fallback, selection-menu capture suspension and in-flight cancellation, repeated geometry updates, cross-monitor DPI transitions and negative coordinates, adaptive backgrounds, and toolbar transitions. Menu checks exercise the actual selection-menu method with a real Qt popup, including cleanup after exceptions and nested suspension. Native Windows Z order checks verify that menus and submenus stay above overlays when another region's translation arrives. Qt DPI initialization matches the application's startup settings. Selected OCR/dispatch/UI methods are executed from their source AST with external services replaced, so tests do not initiate translation requests. The separate real UI check constructs the complete `TranslatorWindow` using the Qt text-browser renderer, opens the actual OCR settings page, clicks the main-window switch, and verifies both saved states and Qt callback errors. It also opens the actual selection-style dialog and verifies capture suspension and resumption for both settings and style windows.

For manual testing, enable the overlay under OCR Settings → Other Settings → Translation Overlay, then select two regions and add a third. Only the new region should immediately submit translation. Right-click a selection while automatic OCR is running: existing translations should remain, menu text should not be recognized, and capture should resume after the menu closes. Also check changing text, moving/removing/hiding selections, switching the main window, and disabling the feature. Actual game engines, translation providers, legacy Windows versions, and Qt6 still need separate testing.

Selection-race checks delay recognition while moving the frame, exercise manual, periodic, and image-analysis paths, and verify that old results cannot change caches or acquire a newer revision during batch assembly. Native selection movement, resizing, and moving back to the original coordinates are checked separately. Ordinary Qt dialogs and settings windows block only overlapping regions; show/hide transitions invalidate in-flight captures. Menus and combo dropdowns briefly pause all captures while visible. The combo test shows its actual Qt popup container directly because the test desktop can remove foreground focus after `showPopup()`. Test text and translations are synthetic.

Menu ordering is also checked with OCR frames owned by a main window. The real main-window topmost method is invoked while a selection menu is open, including after another region's overlay appears and after native frame movement. Popups temporarily defer main-window topmost promotion because Windows would also raise its owned OCR frames over the menu. Closing the popup leaves the configured topmost behavior available again.

`OCRCaptureSnapshot` freezes the revision and physical rectangle before capture. The selection's `ocr_source_lock` makes snapshot validation, OCR cache commit, and revision assignment atomic with geometry edits. Each parsed OCR result carries an `ocr_overlay_source` assigned at commit; dispatch reuses that source. `OCRRegionText` remains a plain string to translation providers, JSON, and SQLite. Its extra attributes are transient routing metadata and are not persisted. The legacy translator queue's third slot carries either an external synchronous callback or an `OCRRegionTask`; the worker recognizes the latter by `ocr_overlay_task` and checks region validity without calling it.
