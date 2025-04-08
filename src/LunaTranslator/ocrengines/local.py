import os, zipfile
from myutils.utils import dynamiclink, stringfyerror
from myutils.config import _TR, getlang_inner2show, globalconfig
from ocrengines.baseocrclass import baseocr, OCRResult
from ctypes import (
    CDLL,
    c_char_p,
    c_void_p,
    c_int32,
    Structure,
    c_char_p,
    c_wchar_p,
    CFUNCTYPE,
)
import os
from language import Languages
import gobject, requests, winsharedutils, windows
from traceback import print_exc
from qtsymbols import *
from myutils.wrapper import threader
from myutils.proxy import getproxy
from gui.usefulwidget import SuperCombo, getboxlayout
from gui.dynalang import LPushButton, LLabel
from gui.usefulwidget import VisLFormLayout


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


def usewhichonnxruntime():
    # 尝试加载系统onnxruntime，有directml优化，速度稍快一丢丢
    sysonnx = windows.SearchPath("onnxruntime.dll")
    ver = winsharedutils.queryversion(sysonnx)
    ver = ver if ver else (0,)
    myonnx = gobject.GetDllpath("onnxruntime.dll")
    vermy = winsharedutils.queryversion(myonnx)
    vermy = vermy if vermy else (0,)
    print(sysonnx, ver)
    print(myonnx, vermy)
    # 但最多尝试到v1.20.1版本，v1.21.0开始会不兼容。
    # https://github.com/microsoft/onnxruntime/releases/tag/v1.21.0
    # All the prebuilt Windows packages now require VC++ Runtime version >= 14.40(instead of 14.38). If your VC++ runtime version is lower than that, you may see a crash when ONNX Runtime was initializing. See https://github.com/microsoft/STL/wiki/Changelog#vs-2022-1710 for more details.
    # 不过实测在更古老py37(14.00)上是没问题的，但在py311(14.38)或pyqt(14.26)上确实会崩溃，保险起见不要加载。
    if (ver >= vermy) and (ver < (1, 21)):
        return sysonnx
    return myonnx


class ocrwrapper:

    def __init__(self, det, rec, key) -> None:
        usewhich = usewhichonnxruntime()
        print(usewhich)

        # msvcp140已被qt导入
        # onnxruntime v1.13.1 用于win7兼容
        self._onnxruntimedll = CDLL(usewhich)
        self._LunaOCR = CDLL(gobject.GetDllpath("LunaOCR.dll"))
        OcrListProviders = self._LunaOCR.OcrListProviders
        OcrListProviders()

        self._OcrInit = self._LunaOCR.OcrInit
        self._OcrInit.restype = c_void_p
        self._OcrInit.argtypes = c_wchar_p, c_wchar_p, c_wchar_p, c_int32

        self._OcrDetect = self._LunaOCR.OcrDetect
        self._OcrDetect.argtypes = (
            c_void_p,
            c_void_p,
            c_int32,
            c_int32,
            c_int32,
            c_int32,
            c_void_p,
        )

        self._OcrDestroy = self._LunaOCR.OcrDestroy
        self._OcrDestroy.argtypes = (c_void_p,)

        self.pOcrObj = self._OcrInit(det, rec, key, 4)

    def __OcrDetect(self, image: QImage, mode: int):

        texts = []
        pss = []

        def cb(ps: ocrpoints, text: bytes):
            pss.append((ps.x1, ps.y1, ps.x2, ps.y2, ps.x3, ps.y3, ps.x4, ps.y4))
            texts.append(text.decode("utf8"))

        if image.format() != QImage.Format.Format_RGB888:
            image = image.convertToFormat(QImage.Format.Format_RGB888)
        self._OcrDetect(
            self.pOcrObj,
            int(image.bits()),
            image.width(),
            image.height(),
            image.bytesPerLine(),
            mode,
            CFUNCTYPE(None, ocrpoints, c_char_p)(cb),
        )
        return pss, texts

    def ocr(self, image: QImage, mode):
        try:
            return self.__OcrDetect(image, mode)
        except:
            print_exc()
            return [], []

    def __del__(self):
        self._OcrDestroy(self.pOcrObj)


def findmodel(langcode):

    check = lambda path: (
        os.path.isfile(path + "/det.onnx")
        and os.path.isfile(path + "/rec.onnx")
        and os.path.isfile(path + "/dict.txt")
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
        if os.path.isdir(d):
            for lang in os.listdir(d):
                if findmodel(lang):
                    validlangs.append(lang)
    return validlangs


class question(QWidget):

    installsucc = pyqtSignal(bool, str)

    def loadcombo(self):

        langs = getallsupports()
        self.supportlang.setText("_,_".join([getlang_inner2show(f) for f in langs]))
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
        self.allsupports.clear()
        for l in _allsupports:
            if l not in langs:
                self.allsupports.append(l)
        vis = [getlang_inner2show(f) for f in self.allsupports]
        self.combo.clear()
        self.combo.addItems(vis)
        if not self.allsupports:
            self.btninstall.setEnabled(False)

    @property
    def cururl(self):
        if not self.allsupports:
            return
        lang = self.allsupports[self.combo.currentIndex()]
        return dynamiclink("{main_server}") + "/Resource/ocr_models/{}.zip".format(lang)

    def downloadauto(self):
        if not self.cururl:
            return
        self.downloadxSafe(self.cururl)
        self.formLayout.setRowVisible(self.row, True)
        self.lineX.setEnabled(False)

    progresssetval = pyqtSignal(str, int)

    @threader
    def downloadxSafe(self, url):
        try:
            self.downloadx(url)
            self.installsucc.emit(True, "")
        except Exception as e:
            self.installsucc.emit(False, stringfyerror(e))

    def downloadx(self, url: str):

        self.progresssetval.emit("……", 0)
        req = requests.head(url, verify=False, proxies=getproxy())
        size = int(req.headers["Content-Length"])
        file_size = 0
        req = requests.get(url, verify=False, proxies=getproxy(), stream=True)
        target = gobject.gettempdir("ocrmodel/" + url.split("/")[-1])
        with open(target, "wb") as ff:
            for _ in req.iter_content(chunk_size=1024 * 32):
                ff.write(_)
                file_size += len(_)
                prg = int(10000 * file_size / size)
                prg100 = prg / 100
                sz = int(1000 * (int(size / 1024) / 1024)) / 1000
                self.progresssetval.emit(
                    _TR("总大小_{} MB _进度_{:0.2f}%").format(sz, prg100),
                    prg,
                )
        self.progresssetval.emit(_TR("正在解压"), 10000)
        with zipfile.ZipFile(target) as zipf:
            zipf.extractall("cache/ocrmodel")

    def _installsucc(self, succ, failreason):
        if succ:
            self.progresssetval.emit(_TR("添加成功"), 10000)
            QMessageBox.information(self, _TR("成功"), _TR("添加成功"))
        else:
            self.progresssetval.emit(_TR("添加失败"), 0)
            res = QMessageBox.question(
                self,
                _TR("错误"),
                failreason + "\n\n" + _TR("自动添加失败，是否手动添加？"),
            )
            if res == QMessageBox.StandardButton.Yes:
                self.formLayout.setRowVisible(self.row, False)
                os.startfile(self.cururl)
                f = QFileDialog.getOpenFileName(
                    self,
                    filter=self.cururl.split("/")[-1],
                )
                fn = f[0]
                if fn:
                    try:
                        with zipfile.ZipFile(fn) as zipf:
                            zipf.extractall("cache/ocrmodel")
                        QMessageBox.information(self, _TR("成功"), _TR("添加成功"))
                    except:
                        QMessageBox.information(self, _TR("错误"), _TR("添加失败"))
                        print_exc()
        self.loadcombo()
        self.formLayout.setRowVisible(self.row, False)
        self.lineX.setEnabled(True)

    def progresssetval_(self, text, val):
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)

    def __init__(self, *argc, **kw):
        super().__init__(*argc, **kw)
        self.installsucc.connect(self._installsucc)
        self.progresssetval.connect(self.progresssetval_)
        formLayout = VisLFormLayout(self)
        formLayout.setContentsMargins(0, 0, 0, 0)
        self.supportlang = LLabel()
        self.supportlang.setWordWrap(True)
        formLayout.addRow("当前支持的语言", self.supportlang)
        self.combo = SuperCombo()
        self.allsupports = []

        btninstall = LPushButton("添加")
        btninstall.clicked.connect(self.downloadauto)
        self.btninstall = btninstall
        self.loadcombo()
        self.lineX = getboxlayout(
            [self.combo, btninstall], makewidget=True, margin0=True
        )
        formLayout.addRow("添加语言包", self.lineX)

        downloadprogress = QProgressBar()

        downloadprogress.setRange(0, 10000)
        downloadprogress.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        formLayout.addRow(downloadprogress)
        self.downloadprogress = downloadprogress
        self.row = formLayout.rowCount() - 1
        formLayout.setRowVisible(self.row, False)
        self.formLayout = formLayout


class OCR(baseocr):
    required_image_format = QImage

    def langmap(self):
        return {Languages.TradChinese: "cht"}

    def init(self):
        self._ocr = None
        self._savelang = None
        self._savelang1 = None
        self.checkchange()

    def checkchange(self):
        if (self._savelang == self.srclang) or (self._savelang1 == self.srclang):
            return
        if self.is_src_auto:
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
                    _TR("未添加“{currlang}”的OCR模型\n当前支持的语言：{langs}").format(
                        currlang=_TR(getlang_inner2show(self.srclang)),
                        langs=", ".join(
                            [_TR(getlang_inner2show(f)) for f in getallsupports()]
                        ),
                    )
                )

        self._ocr = None
        path = findmodel(uselang)
        self._ocr = ocrwrapper(
            path + "/det.onnx", path + "/rec.onnx", path + "/dict.txt"
        )
        self._savelang = uselang
        self._savelang1 = self.srclang

    def ocr(self, image: QImage):
        self.checkchange()

        pss, texts = self._ocr.ocr(
            image,
            globalconfig["verticalocr"],
        )
        return OCRResult(boxs=pss, texts=texts)
