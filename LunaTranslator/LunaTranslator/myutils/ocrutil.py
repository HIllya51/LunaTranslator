import windows
import os, importlib
from myutils.config import globalconfig, _TR
from qtsymbols import *
from myutils.commonbase import ArgsEmptyExc
from myutils.hwnd import screenshot
from myutils.utils import stringfyerror
from traceback import print_exc
import threading, gobject


def qimage2binary(qimage: QImage, fmt="BMP"):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.WriteOnly)
    qimage.save(buffer, fmt)
    buffer.close()
    image_data = byte_array.data()
    return image_data


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
                pix = screenshot(_x1, _y1, _x2, _y2, hwnd)
                if pix.toImage().allGray():
                    continue
                break
            except:
                print_exc()
        else:
            pix = screenshot(x1, y1, x2, y2)

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
        return ""
    global _nowuseocrx, _ocrengine
    try:
        ocr_init()
        text = _ocrengine._private_ocr(image)
        isocrtranslate = _ocrengine.isocrtranslate
        if isocrtranslate:
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
