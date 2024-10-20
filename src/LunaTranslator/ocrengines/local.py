import os, zipfile
from myutils.utils import dynamiclink
from myutils.config import _TR, getlang_inner2show
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
import gobject, functools
from traceback import print_exc
from qtsymbols import *
from gui.usefulwidget import LFocusCombo, getboxlayout, getQMessageBox
from gui.dynalang import LPushButton, LFormLayout, LLabel


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
    def __init__(self, det, rec, key) -> None:
        self.dll = CDLL(gobject.GetDllpath(("LunaOCR32.dll", "LunaOCR64.dll")))
        self.pOcrObj = None
        self.__OcrInit(det, rec, key)

    def __OcrInit(self, szDetModel, szRecModel, szKeyPath, szClsModel="", nThreads=4):

        _OcrInit = self.dll.OcrInit
        _OcrInit.restype = c_void_p
        self.pOcrObj = _OcrInit(
            c_char_p(szDetModel.encode("utf8")),
            c_char_p(szClsModel.encode("utf8")),
            c_char_p(szRecModel.encode("utf8")),
            c_char_p(szKeyPath.encode("utf8")),
            nThreads,
        )

    def __OcrDetect(self, data: bytes, angle):
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

    def ocr(self, data, angle=0):
        try:
            return self.__OcrDetect(data, angle)
        except:
            print_exc()
            return [], []

    def __del__(self):
        if not self.pOcrObj:
            return
        _OcrDestroy = self.dll.OcrDestroy
        _OcrDestroy.argtypes = (c_void_p,)
        _OcrDestroy(self.pOcrObj)


def getallsupports():
    langs = []
    for f in os.listdir("./files/ocr"):
        path = "./files/ocr/{}".format(f)
        if not (
            os.path.exists(path + "/det.onnx")
            and os.path.exists(path + "/rec.onnx")
            and os.path.exists(path + "/dict.txt")
        ):
            continue
        langs.append(f)
    return langs


def dodownload(combo: QComboBox, allsupports: list):
    lang = allsupports[combo.currentIndex()]
    gobject.baseobject.openlink(
        dynamiclink("{main_server}/Resource/ocr_models/" + lang + ".zip")
    )


def doinstall(self, combo: QComboBox, allsupports: list, parent, callback):
    lang = allsupports[combo.currentIndex()]
    f = QFileDialog.getOpenFileName(parent, filter=lang + ".zip")
    fn = f[0]
    if not fn:
        return
    try:
        with zipfile.ZipFile(fn) as zipf:
            zipf.extractall("files/ocr")
        getQMessageBox(self, "成功", "安装成功")
        callback()
    except:
        print_exc()


def question(dialog: QDialog):
    formLayout = LFormLayout()
    dialog.setLayout(formLayout)
    supportlang = LLabel()
    formLayout.addRow("当前支持的语言", supportlang)
    combo = LFocusCombo()
    allsupports = []

    def callback():
        langs = getallsupports()
        supportlang.setText("_,_".join([getlang_inner2show(f) for f in langs]))
        _allsupports = ["ja", "en", "zh", "cht", "ko", "ru"]
        allsupports.clear()
        for l in _allsupports:
            if l not in langs:
                allsupports.append(l)
        vis = [getlang_inner2show(f) for f in allsupports]
        combo.clear()
        combo.addItems(vis)

    callback()
    btndownload = LPushButton("下载")
    btndownload.clicked.connect(functools.partial(dodownload, combo, allsupports))
    btninstall = LPushButton("添加")
    btninstall.clicked.connect(
        functools.partial(doinstall, dialog, combo, allsupports, dialog, callback)
    )
    formLayout.addRow(
        "添加语言包",
        getboxlayout([combo, btndownload, btninstall], makewidget=True),
    )


class OCR(baseocr):
    def langmap(self):
        return {"cht": "cht"}

    def initocr(self):
        self._ocr = None
        self._savelang = None
        self.checkchange()

    def checkchange(self):
        if self._savelang == self.srclang:
            return
        self._ocr = None
        path = "./files/ocr/{}".format(self.srclang)
        if not (
            os.path.exists(path + "/det.onnx")
            and os.path.exists(path + "/rec.onnx")
            and os.path.exists(path + "/dict.txt")
        ):
            raise Exception(
                _TR("未添加")
                + ' "'
                + _TR(getlang_inner2show(self.srclang))
                + '" '
                + _TR("的OCR模型")
                + "\n"
                + _TR("当前支持的语言")
                + ": "
                + ", ".join([_TR(getlang_inner2show(f)) for f in getallsupports()])
            )
        self._ocr = ocrwrapper(
            path + "/det.onnx", path + "/rec.onnx", path + "/dict.txt"
        )
        self._savelang = self.srclang

    def ocr(self, imagebinary):
        self.checkchange()

        pss, texts = self._ocr.ocr(
            imagebinary,
            0,
        )
        return {"box": pss, "text": texts}
