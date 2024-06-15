import os
from myutils.utils import getlangsrc
from myutils.config import globalconfig, _TR
from ocrengines.baseocrclass import baseocr
from ctypes import (
    CDLL,
    c_char_p,
    c_size_t,
    c_void_p,
    c_int32,
    POINTER,
    Structure,
    pointer,
    c_char_p,
)
import os
import gobject
from traceback import print_exc


class ocrpoints(Structure):
    _fields_ = [
        ("x1", c_int32),
        ("y1", c_int32),
        ("x2", c_int32),
        ("y2", c_int32),
        ("x3", c_int32),
        ("y3", c_int32),
        ("x4", c_int32),
        ("y4", c_int32),
    ]


class ocrwrapper:
    def __init__(self) -> None:
        self.dll = CDLL(gobject.GetDllpath(("LunaOCR32.dll", "LunaOCR64.dll")))

    def _OcrInit(self, szDetModel, szRecModel, szKeyPath, szClsModel="", nThreads=4):

        _OcrInit = self.dll.OcrInit
        _OcrInit.restype = c_void_p
        self.pOcrObj = _OcrInit(
            c_char_p(szDetModel.encode("utf8")),
            c_char_p(szClsModel.encode("utf8")),
            c_char_p(szRecModel.encode("utf8")),
            c_char_p(szKeyPath.encode("utf8")),
            nThreads,
        )

    def _OcrDetect(self, data: bytes, angle):
        _OcrDetect = self.dll.OcrDetect
        _OcrDetect.argtypes = (
            c_void_p,
            c_void_p,
            c_size_t,
            c_int32,
            POINTER(c_int32),
            POINTER(POINTER(ocrpoints)),
            POINTER(POINTER(c_char_p)),
        )

        _OcrFreeptr = self.dll.OcrFreeptr
        _OcrFreeptr.argtypes = c_int32, c_void_p, c_void_p

        num = c_int32()
        ps = POINTER(ocrpoints)()
        chars = POINTER(c_char_p)()
        res = _OcrDetect(
            self.pOcrObj,
            data,
            len(data),
            c_int32(angle),
            pointer(num),
            pointer(ps),
            pointer(chars),
        )
        if not res:
            return [], []
        texts = []
        pss = []
        for i in range((num.value)):
            texts.append(chars[i].decode("utf8"))
            pss.append(
                (
                    ps[i].x1,
                    ps[i].y1,
                    ps[i].x2,
                    ps[i].y2,
                    ps[i].x3,
                    ps[i].y3,
                    ps[i].x4,
                    ps[i].y4,
                )
            )
        _OcrFreeptr(num, ps, chars)
        return pss, texts

    def _OcrDestroy(self):
        _OcrDestroy = self.dll.OcrDestroy
        _OcrDestroy(self.pOcrObj)

    def init(self, det, rec, key):
        self._OcrInit(det, rec, key)

    def ocr(self, data, angle=0):
        try:
            return self._OcrDetect(data, angle)
        except:
            print_exc()
            return [], []

    def trydestroy(self):
        try:
            self._OcrDestroy()
        except:
            pass


class OCR(baseocr):
    def end(self):
        self._ocr.trydestroy()

    def initocr(self):
        self._ocr = ocrwrapper()
        self._savelang = None
        self.checkchange()

    def checkchange(self):
        if self._savelang == self.srclang:
            return
        self._ocr.trydestroy()

        path = "./files/ocr/{}".format(getlangsrc())
        if not (
            os.path.exists(path + "/det.onnx")
            and os.path.exists(path + "/rec.onnx")
            and os.path.exists(path + "/dict.txt")
        ):
            raise Exception(
                _TR(
                    "未下载该语言的OCR模型,请在[其他设置]->[资源下载]->[OCR语言包]下载模型解压到files/ocr路径后使用"
                )
            )
        self._ocr.init(path + "/det.onnx", path + "/rec.onnx", path + "/dict.txt")
        self._savelang = self.srclang

    def ocr(self, imagebinary):
        self.checkchange()

        pss, texts = self._ocr.ocr(
            imagebinary,
            globalconfig["verticalocr"],
        )

        return self.common_solve_text_orientation(pss, texts)
