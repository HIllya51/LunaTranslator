import os, zipfile
from myutils.utils import dynamiclink, stringfyerror
from myutils.config import _TR, globalconfig
from language import Languages
from ocrengines.baseocrclass import baseocr, OCRResult
from CVUtils import LocalOCR, SysNotSupport, ModelLoadFailed, OcrIsDMLAvailable
import gobject, requests, json, shutil, hashlib
from traceback import print_exc
from qtsymbols import *
from myutils.wrapper import threader
from myutils.proxy import getproxy
from gui.usefulwidget import SuperCombo, getboxwidget, getspinbox, getsimpleswitch
from gui.dynalang import LPushButton, LLabel
from gui.usefulwidget import VisLFormLayout
from myutils.wrapper import Singleton
from gui.dynalang import LDialog, LFormLayout


@Singleton
class customwidget(LDialog):
    def __init__(self, parent, config: dict, title) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        config__ = config.copy()
        self.setWindowTitle(title)
        self.resize(QSize(400, 10))
        lform = LFormLayout(self)
        lform.addRow("优先使用更高精度的模型", getsimpleswitch(config__, "accfirst"))
        lform.addRow("线程数", getspinbox(1, 16, config__, "thread"))
        if OcrIsDMLAvailable():
            d = getspinbox(0, 16, config__, "device")
            d.setEnabled(config__["gpu"])
            lform.addRow(
                "使用GPU", getsimpleswitch(config__, "gpu", callback=d.setEnabled)
            )
            lform.addRow("GPU序号", d)
        else:
            lform.addRow("当前软件或操作系统版本不支持使用GPU", None)
        lineW = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        lineW.rejected.connect(self.close)
        lineW.accepted.connect(lambda: (config.update(config__), self.close()))

        lineW.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
        lineW.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
        lform.addRow(lineW)
        self.show()


class localmodels:
    def __repr__(self):
        return str(dict(path=self.path, languages=self.languages, scale=self.scale))

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
        self.scale = js.get("scale", 0)
        __ = js.get("languages", [os.path.basename(d)])
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
    def findall():
        __: "list[localmodels]" = []
        for path in ["files/ocrmodel", "cache/ocrmodel"]:
            if not os.path.isdir(path):
                continue
            for p in os.listdir(path):
                try:
                    __.append(localmodels(os.path.join(path, p)))
                except:
                    print_exc()
        return __

    @staticmethod
    def findmodel(ms: "list[localmodels]", lang, accfirst):
        if not ms:
            return None
        mss = None
        if lang == "auto":
            if len(ms) == 1:
                return ms[0]
            for m in ms:
                if not mss:
                    mss = m
                elif len(m.languages) > len(mss.languages):
                    mss = m
                elif len(m.languages) == len(mss.languages):
                    if accfirst == (m.scale > mss.scale):
                        mss = m
        else:
            for m in ms:
                if lang in m.languages:
                    if not mss:
                        mss = m
                    elif accfirst == (m.scale > mss.scale):
                        mss = m
        return mss

    @staticmethod
    def collectlangs(ms: "list[localmodels]") -> "list[str]":
        langs = []
        for _ in ms:
            for f in _.languages:
                try:
                    _ = Languages.fromcode(f)
                except:
                    continue
                if _.zhsname in langs:
                    continue
                langs.append(_.zhsname)
        return langs


class question(QWidget):
    installsucc = pyqtSignal(bool, str)

    def downloadauto(self):
        data, support = self.combo.getIndexData(self.combo.currentIndex())
        if support:
            reply = QMessageBox.question(
                self,
                _TR("确认"),
                _TR("确认移除"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return
            try:
                shutil.rmtree(support.path)
            except:
                print_exc()
            self.loadcombos(self.result)
            self.loadhassupport()
        else:
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
        req = requests.get(url, verify=False, proxies=getproxy(), stream=True)
        size = int(req.headers["Content-Length"])
        target = gobject.gettempdir("ocrmodel/" + hashlib.md5(url.encode()).hexdigest())
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
        self.writeinfos(data, target)

    def writeinfos(self, data, target, encodeby=None):
        url: str = encodeby if encodeby else data["link"]
        tgt = "cache/ocrmodel/" + hashlib.md5(url.encode()).hexdigest()
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
        self.loadhassupport()
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
        _, support = self.combo.getIndexData(i)
        self.btninstall.setText(("添加", "移除")[bool(support)])

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
        self.combo.setCurrentText("loading...")
        self.combo.currentIndexChanged.connect(self.combochanged)
        btninstall = LPushButton("添加")
        btninstall.clicked.connect(self.downloadauto)
        self.btninstall = btninstall
        self.lineX = getboxwidget([self.combo, btninstall])
        l: QHBoxLayout = self.lineX.layout()
        l.setStretch(0, 2)
        l.setStretch(1, 1)
        self.lineX.setEnabled(False)
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
        self.loadhassupport()
        self.laodlangscallback.connect(self.loadcombos)
        self.result = []
        threader(self.__loadlangs)()

    def loadhassupport(self):
        self.supportlang.setText(
            "_,_".join(
                ([_TR(f) for f in localmodels.collectlangs(localmodels.findall())])
            )
        )

    laodlangscallback = pyqtSignal(list)

    def __loadlangs(self):
        try:
            result = requests.get(
                dynamiclink("/Resource/ocr_models_list"),
                verify=False,
                proxies=getproxy(),
            ).json()
        except:
            self.combo.setCurrentText("load failed")
            return
        print(result)
        self.result = result
        self.laodlangscallback.emit(result)

    def loadcombos(self, result: "list[dict]"):

        links = []
        vis = []
        ms = localmodels.findall()
        for _ in result:
            scale = _.get("scale", 0)
            tips = _.get("tips")
            langs = _["languages"]
            v = "_,_".join([Languages.fromcode(f).zhsname for f in langs])
            if tips:
                v += "_({})".format(tips)
            support = False
            for m in ms:
                if (
                    tuple(sorted(langs)) == tuple(sorted(m.languages))
                    and m.scale == scale
                ):
                    v = "√_" + v
                    support = m
                    break

            vis.append(v)
            links.append((_, support))

        idx = self.combo.currentIndex()
        self.combo.clear()
        self.combo.addItems(vis, links)
        if self.combo.count():
            idx = max(idx, 0)
        self.combo.setCurrentIndex(idx)


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
            self.config["device"] if self.config["gpu"] else None
        )
        if self.tgi != tgi:
            self.tgi = tgi
            self._models = None
            self._ocr = None
        checks = localmodels.checks()
        if checks != self.checks:
            self.checks = checks
            self.models = localmodels.findall()
        findm = localmodels.findmodel(
            self.models, self.srclang, self.config["accfirst"]
        )
        if self._models == findm:
            return
        if not findm:
            if self.is_src_auto:
                raise Exception(_TR("无可用模型"))
            else:
                raise Exception(
                    _TR("未添加“{currlang}”的OCR模型\n当前支持的语言：{langs}").format(
                        currlang=_TR(self.srclang_1.zhsname),
                        langs=", ".join(
                            [_TR(f) for f in localmodels.collectlangs(self.models)]
                        ),
                    )
                )
        print(findm.path)
        try:
            self._ocr = LocalOCR(
                findm.path + "/det.onnx",
                findm.path + "/rec.onnx",
                findm.path + "/dict.txt",
                self.config["thread"],
                self.config["gpu"],
                self.config["device"],
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
            globalconfig["verticalocr"],
        )
        return OCRResult(boxs=pss, texts=texts)
