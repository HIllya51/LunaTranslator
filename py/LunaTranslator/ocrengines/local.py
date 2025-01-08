import os, zipfile
from myutils.utils import dynamiclink
from myutils.config import _TR, getlang_inner2show, globalconfig
from ocrengines.baseocrclass import baseocr
from ctypes import (
    CDLL,
    c_char_p,
    c_size_t,
    c_void_p,
    c_int32,
    Structure,
    c_char_p,
    c_wchar_p,
    CFUNCTYPE,
)
import os
from language import Languages
import gobject, functools
from traceback import print_exc
from qtsymbols import *
from gui.usefulwidget import SuperCombo, getboxlayout, getQMessageBox
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
        self.dll = CDLL(gobject.GetDllpath("LunaOCR.dll"))
        self.pOcrObj = None
        self.__OcrInit(det, rec, key)

    def __OcrInit(self, szDetModel, szRecModel, szKeyPath, nThreads=4):

        _OcrInit = self.dll.OcrInit
        _OcrInit.restype = c_void_p
        _OcrInit.argtypes = c_wchar_p, c_wchar_p, c_wchar_p, c_int32
        self.pOcrObj = _OcrInit(szDetModel, szRecModel, szKeyPath, nThreads)

    def __OcrDetect(self, data: bytes, mode: int):

        texts = []
        pss = []

        def cb(ps: ocrpoints, text: bytes):
            pss.append((ps.x1, ps.y1, ps.x2, ps.y2, ps.x3, ps.y3, ps.x4, ps.y4))
            texts.append(text.decode("utf8"))

        _OcrDetect = self.dll.OcrDetect
        _OcrDetect.argtypes = (
            c_void_p,
            c_void_p,
            c_size_t,
            c_int32,
            c_void_p,
        )
        _OcrDetect(
            self.pOcrObj,
            data,
            len(data),
            mode,
            CFUNCTYPE(None, ocrpoints, c_char_p)(cb),
        )
        return pss, texts

    def ocr(self, data, mode):
        try:
            return self.__OcrDetect(data, mode)
        except:
            print_exc()
            return [], []

    def __del__(self):
        if not self.pOcrObj:
            return
        _OcrDestroy = self.dll.OcrDestroy
        _OcrDestroy.argtypes = (c_void_p,)
        _OcrDestroy(self.pOcrObj)


def findmodel(langcode):

    check = lambda path: (
        os.path.exists(path + "/det.onnx")
        and os.path.exists(path + "/rec.onnx")
        and os.path.exists(path + "/dict.txt")
    )
    for path in [
        "./files/ocrmodel/{}".format(langcode),
        "cache/ocrmodel/{}".format(langcode),
    ]:
        if check(path):
            return path


def getallsupports():
    validlangs = []
    for d in ["./files/ocrmodel", "cache/ocrmodel"]:
        if os.path.exists(d):
            for lang in os.listdir(d):
                if findmodel(lang):
                    validlangs.append(lang)
    return validlangs


def dodownload(combo: QComboBox, allsupports: list):
    if not allsupports:
        return
    lang = allsupports[combo.currentIndex()]
    gobject.baseobject.openlink(
        dynamiclink("{main_server}") + "/Resource/ocr_models/{}.zip".format(lang)
    )


def doinstall(self, allsupports: list, parent, callback):
    if not allsupports:
        return
    f = QFileDialog.getOpenFileName(
        parent, filter="model ({})".format(" ".join(["{}.zip".format(_) for _ in allsupports]))
    )
    fn = f[0]
    if not fn:
        return
    try:
        with zipfile.ZipFile(fn) as zipf:
            zipf.extractall("cache/ocrmodel")
        getQMessageBox(self, "成功", "添加成功")
        callback()
    except:
        print_exc()


def question():
    dialog = QWidget()
    formLayout = LFormLayout()
    formLayout.setContentsMargins(0, 0, 0, 0)
    dialog.setLayout(formLayout)
    supportlang = LLabel()
    supportlang.setWordWrap(True)
    formLayout.addRow("当前支持的语言", supportlang)
    combo = SuperCombo()
    allsupports = []

    def callback():
        langs = getallsupports()
        supportlang.setText("_,_".join([getlang_inner2show(f) for f in langs]))
        _allsupports = [
            Languages.Japanese,
            Languages.English,
            Languages.Chinese,
            Languages.TradChinese,
            Languages.Korean,
            Languages.Russian,
            Languages.Arabic,
            Languages.Ukrainian,
        ]
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
        functools.partial(doinstall, combo, allsupports, dialog, callback)
    )
    formLayout.addRow(
        "添加语言包",
        getboxlayout([combo, btndownload, btninstall], makewidget=True, margin0=True),
    )
    return dialog


class OCR(baseocr):

    def langmap(self):
        return {Languages.TradChinese: "cht"}

    def initocr(self):
        self._ocr = None
        self._savelang = None
        self.checkchange()

    def checkchange(self):
        if self._savelang == self.srclang:
            return
        if self.srclang == Languages.Auto:
            validlangs = getallsupports()
            if len(validlangs) == 1:
                uselang = validlangs[0]
            elif len(validlangs) == 0:
                raise Exception(_TR("无可用模型"))
            else:
                self.raise_cant_be_auto_lang()
        else:
            if findmodel(self.srclang):
                uselang = self.srclang
            else:
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

        self._ocr = None
        path = findmodel(uselang)
        self._ocr = ocrwrapper(
            path + "/det.onnx", path + "/rec.onnx", path + "/dict.txt"
        )
        self._savelang = uselang

    def ocr(self, imagebinary):
        self.checkchange()

        pss, texts = self._ocr.ocr(
            imagebinary,
            globalconfig["verticalocr"],
        )
        return {"box": pss, "text": texts}
