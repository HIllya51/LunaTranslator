import os, zipfile
from myutils.utils import dynamiclink, stringfyerror
from myutils.config import _TR, getlang_inner2show, globalconfig
from ocrengines.baseocrclass import baseocr, OCRResult
from CVUtils import LocalOCR, SysNotSupport, ModelLoadFailed
from language import Languages
import gobject, requests
from traceback import print_exc
from qtsymbols import *
from myutils.wrapper import threader
from myutils.proxy import getproxy
from gui.usefulwidget import SuperCombo, getboxwidget
from gui.dynalang import LPushButton, LLabel
from gui.usefulwidget import VisLFormLayout


def findmodel(langcode):

    check = lambda path: (
        os.path.isfile(path + "/det.onnx")
        and os.path.isfile(path + "/rec.onnx")
        and os.path.isfile(path + "/dict.txt")
    )
    for path in [
        "files/ocrmodel/{}".format(langcode),
        "cache/ocrmodel/{}".format(langcode),
    ]:
        if check(path):
            return path


def getallsupports():
    validlangs = []
    for d in ["files/ocrmodel", "cache/ocrmodel"]:
        if os.path.isdir(d):
            for lang in os.listdir(d):
                if findmodel(lang):
                    validlangs.append(lang)
    return validlangs


class question(QWidget):
    allsupports = [
        Languages.Japanese,
        Languages.English,
        Languages.Chinese,
        Languages.TradChinese,
        Languages.Korean,
        Languages.Russian,
        Languages.Arabic,
        Languages.Ukrainian,
        Languages.German,
        Languages.French,
    ]
    installsucc = pyqtSignal(bool, str)

    def loadcombo(self):

        data = self.combo.getCurrentData()
        langs = getallsupports()
        self.supportlang.setText("_,_".join([getlang_inner2show(f) for f in langs]))
        _allsupports = [l for l in self.allsupports if l not in langs]
        vis = [getlang_inner2show(f) for f in _allsupports]
        self.combo.clear()
        self.combo.addItems(vis, _allsupports)
        if data:
            self.combo.setCurrentData(data)
        if not _allsupports:
            self.btninstall.setEnabled(False)

    @property
    def cururl(self):
        lang = self.combo.getCurrentData()
        if not lang:
            return
        return dynamiclink("/Resource/ocr_models/{}.zip".format(lang))

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

        btninstall = LPushButton("添加")
        btninstall.clicked.connect(self.downloadauto)
        self.btninstall = btninstall
        self.loadcombo()
        self.lineX = getboxwidget([self.combo, btninstall])
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

    def init(self):
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

        path = findmodel(uselang)
        try:
            self._ocr = LocalOCR(
                path + "/det.onnx", path + "/rec.onnx", path + "/dict.txt"
            )
        except SysNotSupport:
            raise Exception(_TR("系统不支持"))
        except ModelLoadFailed:
            raise Exception(_TR("模型加载失败"))
        self._savelang = uselang
        self._savelang1 = self.srclang

    def ocr(self, image: QImage):
        self.checkchange()

        pss, texts = self._ocr.OcrDetect(
            image,
            globalconfig["verticalocr"],
        )
        return OCRResult(boxs=pss, texts=texts)
