from ctypes import (
    CDLL,
    c_int,
    c_void_p,
    c_double,
    c_int32,
    c_float,
    c_char_p,
    c_bool,
    c_wchar_p,
    CFUNCTYPE,
)
from qtsymbols import *
import gobject


class InvalidImage(Exception):
    pass


_CVUtils = None


def _DelayLoadCVUtils():

    global _CVUtils
    if not _CVUtils:
        _CVUtils = CDLL(gobject.GetDllpath("CVUtils.dll"))
    return _CVUtils


class _unique_ptr(c_void_p):
    def __init__(self, ptr, deleter):
        super().__init__(ptr)
        self.deleter = deleter

    def __del__(self):
        self.deleter(self)


class cvMat(c_void_p):
    @staticmethod
    def fromQImage(image: QImage):
        _CVUtils = _DelayLoadCVUtils()
        cvMatFromBGR888 = _CVUtils.cvMatFromBGR888
        cvMatFromBGR888.argtypes = c_void_p, c_int, c_int, c_int
        cvMatFromBGR888.restype = cvMat

        if image.format() != QImage.Format.Format_BGR888:
            image = image.convertToFormat(QImage.Format.Format_BGR888)
        ptr: cvMat = cvMatFromBGR888(
            int(image.bits()), image.width(), image.height(), image.bytesPerLine()
        )

        if not ptr:
            raise InvalidImage()
        return ptr

    def __del__(self):
        if self:
            cvMatDestroy = _DelayLoadCVUtils().cvMatDestroy
            cvMatDestroy.argtypes = (cvMat,)
            cvMatDestroy(self)

    def MSSIM(self, mat: "cvMat"):
        cvMatMSSIM = _DelayLoadCVUtils().cvMatMSSIM
        cvMatMSSIM.argtypes = cvMat, cvMat
        cvMatMSSIM.restype = c_double
        return cvMatMSSIM(self, mat)


class SysNotSupport(Exception):
    pass


class ModelLoadFailed(Exception):
    pass


_OcrDetectCallback = CFUNCTYPE(
    None,
    c_float,
    c_float,
    c_float,
    c_float,
    c_float,
    c_float,
    c_float,
    c_float,
    c_char_p,
)


class LocalOCR:

    def __init__(self, det, rec, key) -> None:

        _CVUtils = _DelayLoadCVUtils()
        OcrLoadRuntime = _CVUtils.OcrLoadRuntime
        OcrLoadRuntime.restype = c_bool
        if not OcrLoadRuntime():
            raise SysNotSupport()

        self._OcrInit = _CVUtils.OcrInit
        self._OcrInit.restype = c_void_p
        self._OcrInit.argtypes = c_wchar_p, c_wchar_p, c_wchar_p, c_int32

        self._OcrDetect = _CVUtils.OcrDetect
        self._OcrDetect.argtypes = (c_void_p, cvMat, c_int32, _OcrDetectCallback)

        OcrDestroy = _CVUtils.OcrDestroy
        OcrDestroy.argtypes = (c_void_p,)

        self.pOcrObj = _unique_ptr(self._OcrInit(det, rec, key, 4), OcrDestroy)
        if not self.pOcrObj:
            raise ModelLoadFailed()

    def OcrDetect(self, image: QImage, mode: int):

        texts = []
        pss = []

        def cb(x1, y1, x2, y2, x3, y3, x4, y4, text: bytes):
            pss.append((x1, y1, x2, y2, x3, y3, x4, y4))
            texts.append(text.decode("utf8"))

        mat = cvMat.fromQImage(image)
        self._OcrDetect(self.pOcrObj, mat, mode, _OcrDetectCallback(cb))
        return pss, texts
