import windows
import os, importlib
from myutils.config import globalconfig, _TR
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray, QBuffer
from myutils.commonbase import ArgsEmptyExc
from myutils.hwnd import dynamic_rate
from myutils.utils import stringfyerror
from traceback import print_exc
import gobject, winsharedutils


def togray(image):
    gray_image = image.convertToFormat(QImage.Format_Grayscale8)
    return gray_image


def otsu_threshold_fast(image: QImage, thresh):

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QBuffer.WriteOnly)
    image.save(buffer, "BMP")
    buffer.close()
    image_data = byte_array.data()

    solved = winsharedutils.otsu_binary(image_data, thresh)
    image = QImage()
    image.loadFromData(solved)
    return image


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


def imageCut(hwnd, x1, y1, x2, y2, viscompare=True):
    screen = QApplication.primaryScreen()
    for _ in range(2):

        if _ % 2 == 0:
            try:
                if hwnd == 0:
                    continue
                rect = windows.GetWindowRect(hwnd)
                if rect is None:
                    continue

                rate = dynamic_rate(hwnd, rect)
                hwndrate = windows.GetDpiForWindow(hwnd) / 96
                x1, y1 = windows.ScreenToClient(
                    hwnd, x1 * rate * hwndrate, y1 * rate * hwndrate
                )
                x2, y2 = windows.ScreenToClient(
                    hwnd, x2 * rate * hwndrate, y2 * rate * hwndrate
                )
                pix = screen.grabWindow(
                    hwnd,
                    int(x1 / rate / rate / hwndrate),
                    int(y1 / rate / rate / hwndrate),
                    int((x2 - x1) / rate / rate / hwndrate),
                    int((y2 - y1) / rate / rate / hwndrate),
                )
                if pix.toImage().allGray():
                    continue
                break
            except:
                print_exc()
        else:
            pix = screen.grabWindow(
                QApplication.desktop().winId(), x1, y1, x2 - x1, y2 - y1
            )

    image = pix.toImage()
    image2 = imagesolve(image)
    if viscompare:
        gobject.baseobject.showocrimage.setimage.emit([image, image2])
    return image2


_nowuseocr = None
_ocrengine = None


def ocr_end():
    global _ocrengine, _nowuseocr
    try:
        _ocrengine.end()
    except:
        pass
    _nowuseocr = None
    _ocrengine = None


def ocr_run(img):
    global _nowuseocr, _ocrengine

    use = None
    for k in globalconfig["ocr"]:
        if globalconfig["ocr"][k]["use"] == True and os.path.exists(
            ("./LunaTranslator/ocrengines/" + k + ".py")
        ):
            use = k
            break
    if use is None:
        return ""

    try:
        if _nowuseocr != use:
            try:
                _ocrengine.end()
            except:
                pass
            aclass = importlib.import_module("ocrengines." + use).OCR
            _ocrengine = aclass(use)
            _nowuseocr = use
        text = _ocrengine._private_ocr(img)
    except Exception as e:
        if isinstance(e, ArgsEmptyExc):
            msg = str(e)
        else:
            print_exc()
            msg = stringfyerror(e)
        msg = "<msg_error_refresh>" + _TR(globalconfig["ocr"][use]["name"]) + " " + msg
        text = msg
    return text
