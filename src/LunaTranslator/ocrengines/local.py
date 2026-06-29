import os, zipfile
from myutils.utils import stringfyerror
from myutils.config import _TR, globalconfig, dynamiclink
from language import Languages
from qtsymbols import *
from ocrengines.baseocrclass import baseocr, OCRResult
from CVUtils import (
    LocalOCR,
    SysNotSupport,
    ModelLoadFailed,
    GetDeviceInfoD3D12,
    OcrIsProviderAvailable,
    GetOpenVINODeviceTypes,
)
import gobject, requests, json, hashlib
from traceback import print_exc
from qtsymbols import *
from myutils.wrapper import threader
from myutils.proxy import getproxy
from myutils.utils import format_bytes
from gui.usefulwidget import (
    SuperCombo,
    getboxwidget,
    getboxlayout,
    getspinbox,
    getsimpleswitch,
    D_getdoclink,
    getsimplecombobox,
)
import functools
from gui.dynalang import LPushButton, LLabel
from gui.usefulwidget import VisLFormLayout, SplitLine
from myutils.wrapper import Singleton
from gui.dynalang import LDialog, LFormLayout


class question(QWidget):
    installsucc = pyqtSignal(bool, str)

    def downloadauto(self):
        data, __, _ = self.combo.getIndexData(self.combo.currentIndex())

        self.downloadxSafe(data)
        self.formLayout.setRowVisible(self.row, True)
        self.lineX.setEnabled(False)

    progresssetval = pyqtSignal(str, int)

    @threader
    def downloadxSafe(self, data):
        try:
            self.downloadx(data)
            self.installsucc.emit(True, "")
        except Exception as e:
            self.installsucc.emit(False, stringfyerror(e))

    def downloadx(self, data: str):
        url: str = data["link"]
        self.progresssetval.emit("……", 0)
        file_size = 0
        req = requests.get(url, proxies=getproxy(), stream=True)
        size = int(req.headers["Content-Length"])
        target = gobject.gettempdir("ocrmodel/" + hashlib.md5(url.encode()).hexdigest())
        md5 = hashlib.md5()
        with open(target, "wb") as ff:
            asize = format_bytes(size)
            for _ in req.iter_content(chunk_size=1024 * 32):
                ff.write(_)
                md5.update(_)
                file_size += len(_)
                prg = int(10000 * file_size / size)
                self.progresssetval.emit(
                    _TR("{}/{} _进度_{:0.2f}%").format(
                        format_bytes(file_size), asize, prg / 100
                    ),
                    prg,
                )
        if file_size != size:
            raise Exception()
        self.progresssetval.emit(_TR("正在解压"), 10000)
        self.writeinfos(data, target, md5.hexdigest())

    def writeinfos(self, data, target, hd):
        tgt = "cache/ocrmodel/" + hd
        with zipfile.ZipFile(target) as zipf:
            zipf.extractall(tgt)
        try:
            with open(
                os.path.join(localmodels.findtarget(tgt), "info.json"),
                "r",
                encoding="utf8",
            ) as ff:
                js = json.loads(ff.read())
        except:
            js = {}
        with open(
            os.path.join(localmodels.findtarget(tgt), "info.json"), "w", encoding="utf8"
        ) as ff:
            js.update(data)
            ff.write(json.dumps(js))

    def _installsucc(self, succ, failreason):
        self.formLayout.setRowVisible(self.row, False)
        self.lineX.setEnabled(True)
        self.loadcombos(self.result)
        if not succ:
            QMessageBox.critical(
                self,
                _TR("添加失败"),
                _TR("错误") + "\n" + failreason,
            )

    def progresssetval_(self, text, val):
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)

    def combochanged(self, i):
        if i == -1:
            self.lineX.setEnabled(False)
            return
        self.lineX.setEnabled(True)
        print(self.combo.getIndexData(i))
        data, support, langs = self.combo.getIndexData(i)
        self.infolabel.setText(langs)
        self.btninstall.setHidden(support)
        if support:
            self.config__["model"] = data.get("name")

    def __init__(self, config__: dict, *argc, **kw):
        super().__init__(*argc, **kw)
        self.config__ = config__
        self.installsucc.connect(self._installsucc)
        self.progresssetval.connect(self.progresssetval_)
        formLayout = VisLFormLayout(self)
        formLayout.setContentsMargins(0, 0, 0, 0)
        self.combo = SuperCombo(static=True)
        self.combo.currentIndexChanged.connect(self.combochanged)
        btninstall = LPushButton("下载")
        btninstall.clicked.connect(self.downloadauto)
        btninstall.hide()
        self.btninstall = btninstall
        self.lineX = getboxwidget([self.combo, btninstall])
        l: QHBoxLayout = self.lineX.layout()
        l.setStretch(0, 2)
        l.setStretch(1, 1)
        self.lineX.setEnabled(False)
        formLayout.addRow(
            getboxwidget(
                [D_getdoclink("useapis/ocrapi.html#anchor-offline"), self.lineX]
            )
        )
        self.infolabel = LLabel()
        self.infolabel.setWordWrap(True)
        formLayout.addRow("支持的语言", self.infolabel)
        formLayout.setRowVisible(1, False)

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
        self.laodlangscallback.connect(functools.partial(self.loadcombos, init=True))
        threader(self.__loadlangs)()

    laodlangscallback = pyqtSignal(list)

    def __loadlangs(self):
        try:
            result = requests.get(
                dynamiclink("Resource/ocr_models"),
                proxies=getproxy(),
            ).json()
        except:
            result = localmodels.findall()
        self.result = result
        self.laodlangscallback.emit(result)

    def loadcombos(self, result: "list[dict]", init=False):

        self.formLayout.setRowVisible(1, True)
        links = []
        vis = []
        ms = localmodels.findall()
        idx = self.combo.currentIndex()
        for i, _ in enumerate(result):
            v = _.get("name")
            langs = _.get("languages")
            langs = (
                "_,_".join([Languages.fromcode(f).zhsname for f in langs])
                if langs
                else "任意"
            )
            support = False
            for m in ms:
                __ = {}
                for ___ in m:
                    __[___] = _.get(___)
                if m == __:
                    v = "√ " + v
                    if m.get("name") == self.config__["model"]:
                        if init:
                            idx = i
                    support = True
                    break

            vis.append(v)
            links.append((_, support, langs))

        self.combo.clear()
        self.combo.addItems(vis, links)
        if self.combo.count():
            idx = max(idx, 0)
        self.combo.setCurrentIndex(idx)


@Singleton
class customwidget(LDialog):
    delayload = pyqtSignal(int, list)

    def __delayload(self, config__, lform: LFormLayout, t, devices):
        lform.removeRow(lform.rowCount() - 2)
        if devices:
            print(devices)
            if t == 0:
                for i, _ in enumerate(devices):
                    if i == 0:
                        _[-1] = "默认_[[({})]]".format(_[-1])
                    else:
                        _[-1] = "[[{}]]".format(_[-1])
                d = getsimplecombobox(
                    [_[1] for _ in devices],
                    config__,
                    "luid",
                    internal=[_[0] for _ in devices],
                )
                d.setEnabled(config__["gpu"])
                lform.insertRow(
                    lform.rowCount() - 1,
                    "使用GPU",
                    getboxlayout(
                        [getsimpleswitch(config__, "gpu", callback=d.setEnabled), d]
                    ),
                )
            elif t == 1:
                d = getsimplecombobox(
                    devices,
                    config__,
                    "device_type",
                    internal=devices,
                )
                lform.insertRow(lform.rowCount() - 1, "Device", d)

        else:
            lform.insertRow(
                lform.rowCount() - 1, "当前软件或操作系统版本不支持使用GPU", None
            )

    @threader
    def __load(self):
        devices = GetDeviceInfoD3D12()
        self.delayload.emit(0, devices)

    def __init__(self, parent, config: dict, title) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        config__ = config.copy()
        self.setWindowTitle(title)
        self.resize(QSize(400, 10))
        lform = LFormLayout(self)
        lform.addRow("选择模型", question(config__))
        lform.addRow(SplitLine())
        lform.addRow("线程数", getspinbox(1, 16, config__, "thread"))
        self.delayload.connect(functools.partial(self.__delayload, config__, lform))
        lineW = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        lineW.rejected.connect(self.close)
        lineW.accepted.connect(lambda: (config.update(config__), self.close()))

        lineW.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
        lineW.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
        lform.addRow(lineW)
        if OcrIsProviderAvailable("DML"):
            lform.insertRow(lform.rowCount() - 1, "正在加载可用GPU", None)
            self.__load()
        elif OcrIsProviderAvailable("OpenVINO"):
            lform.insertRow(lform.rowCount() - 1, "正在加载可用GPU", None)
            devices = GetOpenVINODeviceTypes()
            self.delayload.emit(1, devices)
        else:
            lform.insertRow(
                lform.rowCount() - 1, "当前软件或操作系统版本不支持使用GPU", None
            )
        self.resize(600, 1)
        self.show()


class localmodels:
    def __repr__(self):
        return str(dict(path=self.path, info=self.info))

    def __eq__(self, value: "localmodels"):
        if not isinstance(value, localmodels):
            return False
        return self.path == value.path

    @staticmethod
    def findtarget(d):
        for _dir, _, __fs in os.walk(d):
            for ff in __fs:
                if ff == "det.onnx":
                    return _dir

    def __init__(self, d):
        self.path = self.findtarget(d)
        if not all(
            os.path.isfile(os.path.join(self.path, _))
            for _ in ("det.onnx", "rec.onnx", "dict.txt")
        ):
            raise Exception()
        try:
            with open(os.path.join(d, "info.json"), "r", encoding="utf8") as ff:
                js = json.load(ff)
        except:
            js = {}
        self.info = js
        __ = js.get("languages", [])
        self.languages = list(Languages.fromcode(_).code for _ in __)

    @staticmethod
    def checks():
        __ = []
        for path in ["files/ocrmodel", "cache/ocrmodel"]:
            if not os.path.isdir(path):
                continue
            __ += [os.path.join(path, _) for _ in os.listdir(path)]
        return tuple(__)

    @staticmethod
    def findmodel(ms: "list[localmodels]", model: str):
        if not ms:
            return None

        for m in ms:
            if m.info.get("name") == model:
                return m
        return None

    @staticmethod
    def findall(infoonly=True):
        __: "list[dict|localmodels]" = []
        for path in ["files/ocrmodel", "cache/ocrmodel"]:
            if not os.path.isdir(path):
                continue
            for p in os.listdir(path):
                try:
                    _ = localmodels(os.path.join(path, p))
                    if infoonly:
                        _ = _.info
                    __.append(_)
                except:
                    print_exc()
        return __


class OCR(baseocr):
    required_image_format = QImage

    def init(self):
        self.tgi = None
        self.models: list[localmodels] = []
        self.checks = None
        self._models = 1
        self.checkchange()

    def checkchange(self):
        tgi = self.config["thread"], (
            self.config["luid"] if self.config["gpu"] else None
        )
        if self.tgi != tgi:
            self.tgi = tgi
            self._models = None
            self._ocr = None
        checks = localmodels.checks()
        if checks != self.checks:
            self.checks = checks
            self.models = localmodels.findall(infoonly=False)
        if not self.models:
            raise Exception(_TR("无可用模型"))
        findm = localmodels.findmodel(self.models, self.config["model"])
        if not findm:
            findm = self.models[0]
        if self._models == findm:
            return
        print(findm)
        try:
            self._ocr = LocalOCR(
                findm.path + "/det.onnx",
                findm.path + "/rec.onnx",
                findm.path + "/dict.txt",
                self.config["thread"],
                self.config["gpu"],
                self.config["luid"],
                self.config["device_type"],
            )
        except SysNotSupport:
            raise Exception(_TR("系统不支持"))
        except ModelLoadFailed:
            raise Exception(_TR("模型加载失败"))
        self._models = findm

    def ocr(self, image: QImage):
        self.checkchange()
        pss, texts = self._ocr.OcrDetect(
            image,
            globalconfig.get("verticalocr", 2),
        )
        return OCRResult(boxs=pss, texts=texts)
