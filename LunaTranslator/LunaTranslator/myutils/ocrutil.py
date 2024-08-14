import windows
import os, importlib
from myutils.config import globalconfig, _TR
from qtsymbols import *
from myutils.commonbase import ArgsEmptyExc
from myutils.hwnd import screenshot
from myutils.utils import stringfyerror
from traceback import print_exc
import gobject, winsharedutils, threading


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


def togray(image):
    gray_image = image.convertToFormat(QImage.Format_Grayscale8)
    return gray_image


def otsu_threshold_fast(image: QImage, thresh):
    image_data = qimage2binary(image)
    solved = winsharedutils.otsu_binary(image_data, thresh)
    return binary2qimage(solved)


def imagesolve(image):
    if globalconfig["ocr_presolve_method"] == 0:
        image2 = image
    elif globalconfig["ocr_presolve_method"] == 1:
        image2 = togray(image)
    elif globalconfig["ocr_presolve_method"] == 2:
        image2 = otsu_threshold_fast(image, globalconfig["binary_thresh"])
    elif globalconfig["ocr_presolve_method"] == 3:
        image2 = otsu_threshold_fast(image, -1)
    return image2


def imageCut(hwnd, x1, y1, x2, y2, viscompare=True, rawimage=False) -> QImage:

    for _ in range(2):

        if _ % 2 == 0:
            try:
                if hwnd == 0:
                    continue
                rect = windows.GetWindowRect(hwnd)
                if rect is None:
                    continue

                x1, y1 = windows.ScreenToClient(hwnd, x1, y1)
                x2, y2 = windows.ScreenToClient(hwnd, x2, y2)
                pix = screenshot(x1, y1, x2, y2, hwnd)
                if pix.toImage().allGray():
                    continue
                break
            except:
                print_exc()
        else:
            pix = screenshot(x1, y1, x2, y2)

    image = pix.toImage()
    if rawimage:
        return image
    image2 = imagesolve(image)
    if viscompare:
        gobject.baseobject.maybesetimage([image, image2])
    return image2


_nowuseocr = None
_ocrengine = None
_initlock = threading.Lock()


def ocr_end():
    global _ocrengine, _nowuseocr
    with _initlock:
        _nowuseocr = None
        _ocrengine = None


def ocr_init():
    with _initlock:
        __ocr_init()


def __ocr_init():
    global _nowuseocr, _ocrengine
    use = None
    for k in globalconfig["ocr"]:
        if globalconfig["ocr"][k]["use"] == True and os.path.exists(
            ("./LunaTranslator/ocrengines/" + k + ".py")
        ):
            use = k
            break
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
    global _nowuseocr, _ocrengine
    try:
        ocr_init()
        text = _ocrengine._private_ocr(image)
    except Exception as e:
        if isinstance(e, ArgsEmptyExc):
            msg = str(e)
        else:
            print_exc()
            msg = stringfyerror(e)
        msg = (
            "<msg_error_refresh>"
            + _TR(globalconfig["ocr"][_nowuseocr]["name"])
            + " "
            + msg
        )
        text = msg
    return text


def ocr_run_2(qimage: QImage):
    text = ocr_run(qimage)

    msgs = [
        "<notrans>",
        "<msg_info_not_refresh>",
        "<msg_info_refresh>",
        "<msg_error_not_refresh>",
        "<msg_error_refresh>",
    ]
    for msg in msgs:
        if text.startswith(msg):
            return text[len(msg) :]
    return text
