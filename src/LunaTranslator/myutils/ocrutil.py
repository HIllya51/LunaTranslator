import os, importlib
from myutils.config import globalconfig, _TR
from qtsymbols import *
from myutils.commonbase import ArgsEmptyExc
from myutils.hwnd import safepixmap
from myutils.utils import stringfyerror
from traceback import print_exc
import threading, gobject, NativeUtils
from ocrengines.baseocrclass import baseocr, OCRResultParsed


def imageCut(hwnd, x1, y1, x2, y2) -> QImage:
    succ, pix = NativeUtils.GdiCropImage(x1, y1, x2, y2, hwnd)
    pix = safepixmap(pix).toImage()
    if hwnd:
        return succ, pix
    return pix


_nowuseocrx = None
_nowuseocr = None
_ocrengine: baseocr = None
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
            ("LunaTranslator/ocrengines/" + k + ".py")
        ):
            use = k
            break
    _nowuseocrx = use
    if use is None:
        raise Exception(_TR("未选择OCR引擎"))
    if _nowuseocr == use:
        return
    _ocrengine = None
    _nowuseocr = None
    aclass = importlib.import_module("ocrengines." + use).OCR
    _ocrengine = aclass(use)
    _nowuseocr = use


def ocr_run(qimage: QImage):
    gobject.base.setimage.emit(qimage)
    if qimage.isNull():
        return OCRResultParsed()
    global _nowuseocrx, _ocrengine
    thisocrtype = _nowuseocrx
    try:
        ocr_init()
        thisocrtype: str = _ocrengine.typename
        res = _ocrengine._private_ocr(qimage)
        gobject.base.setresult.emit(res)
        return res
    except Exception as e:
        if isinstance(e, ArgsEmptyExc):
            msg = str(e)
        else:
            print_exc()
            msg = stringfyerror(e)
        return OCRResultParsed(error=msg, engine=thisocrtype)
