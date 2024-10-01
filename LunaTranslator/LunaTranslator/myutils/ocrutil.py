import windows
import os, importlib
from myutils.config import globalconfig, _TR
from qtsymbols import *
from myutils.commonbase import ArgsEmptyExc
from myutils.hwnd import gdi_screenshot
from myutils.utils import stringfyerror, qimage2binary
from traceback import print_exc
import threading, gobject



def binary2qimage(binary):
    image = QImage()
    image.loadFromData(binary)
    return image


def imageCut(hwnd, x1, y1, x2, y2) -> QImage:

    for _ in range(2):

        if _ % 2 == 0:
            try:
                if hwnd == 0:
                    continue
                rect = windows.GetWindowRect(hwnd)
                if rect is None:
                    continue

                _x1, _y1 = windows.ScreenToClient(hwnd, x1, y1)
                _x2, _y2 = windows.ScreenToClient(hwnd, x2, y2)

                if not QRect(0, 0, rect[2] - rect[0], rect[3] - rect[1]).contains(
                    QRect(_x1, _y1, _x2 - _x1, _y2 - _y1)
                ):
                    continue
                pix = gdi_screenshot(_x1, _y1, _x2, _y2, hwnd)
                if pix.isNull():
                    continue
                break
            except:
                print_exc()
        else:
            pix = gdi_screenshot(x1, y1, x2, y2)

    image = pix.toImage()
    gobject.baseobject.maybesetimage(image)
    return image


_nowuseocrx = None
_nowuseocr = None
_ocrengine = None
_initlock = threading.Lock()


def ocr_end():
    global _ocrengine, _nowuseocr, _nowuseocrx
    with _initlock:
        _nowuseocr = None
        _nowuseocrx = None
        _ocrengine = None


def ocr_init():
    with _initlock:
        __ocr_init()


def __ocr_init():
    global _nowuseocr, _ocrengine, _nowuseocrx
    use = None
    for k in globalconfig["ocr"]:
        if globalconfig["ocr"][k]["use"] == True and os.path.exists(
            ("./LunaTranslator/ocrengines/" + k + ".py")
        ):
            use = k
            break
    _nowuseocrx = use
    if use is None:
        raise Exception("no engine")
    if _nowuseocr == use:
        return
    _ocrengine = None
    _nowuseocr = None
    aclass = importlib.import_module("ocrengines." + use).OCR
    _ocrengine = aclass(use)
    _nowuseocr = use


def ocr_run(qimage: QImage):
    image = qimage2binary(qimage, "PNG")
    if not image:
        return "", None
    global _nowuseocrx, _ocrengine
    try:
        ocr_init()
        res = _ocrengine._private_ocr(image)
        gobject.baseobject.maybesetocrresult(res)
        text = res["textonly"]
        if res["isocrtranslate"]:
            return text, "<notrans>"
        else:
            return text, None
    except Exception as e:
        if isinstance(e, ArgsEmptyExc):
            msg = str(e)
        else:
            print_exc()
            msg = stringfyerror(e)
        text = (
            (_TR(globalconfig["ocr"][_nowuseocrx]["name"]) if _nowuseocrx else "")
            + " "
            + msg
        )
        return text, "<msg_error_refresh>"
