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
    c_uint64,
)
from qtsymbols import *
import gobject
import functools
import locale


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
        if self:
            self.deleter(self)


class cvMat(_unique_ptr):
    def __init__(self, image: QImage):
        if (image is None) or image.isNull() or (image.bits() is None):
            super().__init__(None, cvMatDestroy)
            return
        _CVUtils = _DelayLoadCVUtils()
        cvMatDestroy = _CVUtils.cvMatDestroy
        cvMatDestroy.argtypes = (c_void_p,)
        cvMatFromRGB888 = _CVUtils.cvMatFromRGB888
        cvMatFromRGB888.argtypes = c_void_p, c_int, c_int, c_int
        cvMatFromRGB888.restype = c_void_p
        if image.format() != QImage.Format.Format_RGB888:
            image = image.convertToFormat(QImage.Format.Format_RGB888)
        ptr = cvMatFromRGB888(
            int(image.bits()), image.width(), image.height(), image.bytesPerLine()
        )
        if not ptr:
            raise InvalidImage()
        super().__init__(ptr, cvMatDestroy)

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
_error = CFUNCTYPE(None, c_char_p)


def OcrIsProviderAvailable(provider="DML"):
    _CVUtils = _DelayLoadCVUtils()
    OcrIsProviderAvailable = _CVUtils.OcrIsProviderAvailable
    OcrIsProviderAvailable.restype = c_bool
    OcrIsProviderAvailable.argtypes = (c_wchar_p,)
    return OcrIsProviderAvailable(provider)


def GetOpenVINODeviceTypes():
    _CVUtils = _DelayLoadCVUtils()
    GetOpenVINODeviceTypes = _CVUtils.GetOpenVINODeviceTypes
    GetOpenVINODeviceTypescb = CFUNCTYPE(None, c_char_p)
    GetOpenVINODeviceTypes.argtypes = (GetOpenVINODeviceTypescb,)
    ret: "list[bytes]" = []
    GetOpenVINODeviceTypes(GetOpenVINODeviceTypescb(ret.append))
    return [_.decode() for _ in ret]


def GetDeviceInfoD3D12():
    _CVUtils = _DelayLoadCVUtils()
    GetDeviceInfoD3D12 = _CVUtils.GetDeviceInfoD3D12
    GetDeviceInfoD3D12_CB = CFUNCTYPE(None, c_uint64, c_wchar_p)
    GetDeviceInfoD3D12.argtypes = (GetDeviceInfoD3D12_CB,)

    ret = []

    def __cb(ret: list, luid, name):
        ret.append([luid, name])

    GetDeviceInfoD3D12(GetDeviceInfoD3D12_CB(functools.partial(__cb, ret)))
    return ret


class LocalOCR(_unique_ptr):

    def __init__(
        self, det, rec, key, thread: int, gpu: bool, luid, device_type: str
    ) -> None:
        _CVUtils = _DelayLoadCVUtils()
        OcrLoadRuntime = _CVUtils.OcrLoadRuntime
        OcrLoadRuntime.restype = c_bool
        if not OcrLoadRuntime():
            raise SysNotSupport()

        OcrInit = _CVUtils.OcrInit
        OcrInit.restype = c_void_p
        OcrInit.argtypes = (
            c_wchar_p,
            c_wchar_p,
            c_wchar_p,
            c_int32,
            c_bool,
            c_uint64,
            c_char_p,
            _error,
        )

        OcrDestroy = _CVUtils.OcrDestroy
        OcrDestroy.argtypes = (c_void_p,)

        error: "list[bytes]" = []

        super().__init__(
            OcrInit(
                det,
                rec,
                key,
                thread,
                gpu,
                luid,
                device_type.encode(),
                _error(error.append),
            ),
            OcrDestroy,
        )
        if error:
            raise Exception(
                error[0].decode(locale.getpreferredencoding(), errors="ignore")
            )
        if not self:
            raise ModelLoadFailed()

    def OcrDetect(self, image: QImage, mode: int):

        texts = []
        pss = []

        def cb(x1, y1, x2, y2, x3, y3, x4, y4, text: bytes):
            pss.append((x1, y1, x2, y2, x3, y3, x4, y4))
            texts.append(text.decode("utf8"))

        mat = cvMat(image)
        error: "list[bytes]" = []
        _CVUtils = _DelayLoadCVUtils()
        OcrDetect = _CVUtils.OcrDetect
        OcrDetect.argtypes = (
            c_void_p,
            cvMat,
            c_int32,
            _OcrDetectCallback,
            _error,
        )
        OcrDetect(self, mat, mode, _OcrDetectCallback(cb), _error(error.append))
        if error:
            raise Exception(
                error[0].decode(locale.getpreferredencoding(), errors="ignore")
            )
        return pss, texts
