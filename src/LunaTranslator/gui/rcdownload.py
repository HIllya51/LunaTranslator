import os
from myutils.config import globalconfig
import requests, zipfile, gobject
from gui.usefulwidget import VisLFormLayout, getboxlayout, NQGroupBox, LinkLabel
from myutils.utils import makehtml, stringfyerror, format_bytes
from myutils.config import _TR, mayberelpath, dynamiclink
from myutils.wrapper import threader
from myutils.proxy import getproxy
from qtsymbols import *
from gui.dynalang import LPushButton


class resourcewidget(NQGroupBox):
    installsucc = pyqtSignal(bool, str)

    def _installsucc(self, succ, failreason):
        self.formLayout.setRowVisible(2, False)
        self.btninstall.setVisible(not succ)
        self.btninstall.setEnabled(True)
        if succ:
            QMessageBox.information(self, _TR("成功"), _TR("添加成功"))
        else:
            QMessageBox.critical(self, _TR("添加失败"), _TR("错误") + "\n" + failreason)

    @property
    def oldlink(self):
        return dynamiclink("Resource/dictionary/unidic-mecab-2.1.2_bin.zip")

    checkdirname = "unidic-mecab-2.1.2_bin"
    oldlinkfnname = "unidic-mecab-2.1.2_bin.zip"

    def downloadofficial(self):
        url = self.oldlink
        file_size = 0
        req = requests.get(url, stream=True, proxies=getproxy())
        size = int(req.headers["Content-Length"])
        target = gobject.gettempdir(self.oldlinkfnname)
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
        with zipfile.ZipFile(target) as ff:
            ff.extractall(gobject.getcachedir())
        tgt = gobject.getcachedir(self.checkdirname)
        globalconfig["hirasetting"]["mecab"]["args"]["path"] = mayberelpath(tgt)
        gobject.base.startmecab()

    @threader
    def downloadxSafe(self, url):
        try:
            self.progresssetval.emit("……", 0)
            self.downloadofficial()
            self.installsucc.emit(True, "")
        except Exception as e:
            self.installsucc.emit(False, stringfyerror(e))

    def downloadauto(self):
        self.downloadxSafe(self.oldlink)
        self.btninstall.setEnabled(False)
        self.formLayout.setRowVisible(2, True)

    def progresssetval_(self, text, val):
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)

    progresssetval = pyqtSignal(str, int)

    def __findithasinstalled(self):
        checkvalid = lambda d: (
            os.path.basename(d) == self.checkdirname
        ) and os.path.isfile(os.path.join(d, "dicrc"))
        for ___ in (
            globalconfig["hirasetting"]["mecab"]["args"]["path"],
            ".",
            r"C:\Program Files\MeCab\dic",
            r"C:\Program Files (x86)\MeCab\dic",
        ):
            if not os.path.isdir(___):
                continue
            if checkvalid(___):
                return True
            for _dir, _, __ in os.walk(___):
                if checkvalid(_dir):
                    return True
        return False

    def __init__(self, *argc, **kw):
        super().__init__(*argc, **kw)
        self.installsucc.connect(self._installsucc)
        formLayout = VisLFormLayout(self)
        formLayout.addRow(
            "unidic", LinkLabel(makehtml("https://clrd.ninjal.ac.jp/unidic/"))
        )
        self.formLayout = formLayout
        btninstall = LPushButton("下载")
        btninstall.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        if self.__findithasinstalled():
            btninstall.setVisible(False)
        self.btninstall = btninstall
        btninstall.clicked.connect(self.downloadauto)
        __maybebtn = getboxlayout(
            [
                LinkLabel(makehtml(self.oldlink, self.oldlinkfnname)),
                "",
                btninstall,
            ]
        )
        formLayout.addRow("unidic-2.1.2", __maybebtn)

        downloadprogress = QProgressBar()

        downloadprogress.setRange(0, 10000)
        downloadprogress.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        formLayout.addRow(downloadprogress)
        self.progresssetval.connect(self.progresssetval_)
        self.downloadprogress = downloadprogress
        formLayout.setRowVisible(2, False)


class resourcewidget2(NQGroupBox):
    installsucc = pyqtSignal(bool, str)

    def _installsucc(self, succ, failreason):
        self.formLayout.setRowVisible(3, False)
        self.btninstall.setVisible(not succ)
        self.btninstall.setEnabled(True)
        if succ:
            QMessageBox.information(self, _TR("成功"), _TR("添加成功"))
        else:
            QMessageBox.critical(self, _TR("添加失败"), _TR("错误") + "\n" + failreason)

    @property
    def oldlink(self):
        return dynamiclink("Resource/dictionary/jitendex-mdict.zip")

    def downloadofficial(self):
        tgt = gobject.getcachedir("mdict/jitendex/jitendex.mdx")
        if not os.path.isfile(tgt):
            url = self.oldlink
            file_size = 0
            req = requests.get(url, stream=True, proxies=getproxy())
            size = int(req.headers["Content-Length"])
            target = gobject.gettempdir(url.split("/")[-1])
            with open(target, "wb") as ff:
                asize = format_bytes(size)
                for _ in req.iter_content(chunk_size=1024 * 32):
                    ff.write(_)
                    file_size += len(_)
                    prg = int(10000 * file_size / size)
                    prg100 = prg / 100
                    self.progresssetval.emit(
                        _TR("总大小_{} _进度_{:0.2f}%").format(asize, prg100),
                        prg,
                    )

            self.progresssetval.emit(_TR("正在解压"), 10000)
            with zipfile.ZipFile(target) as ff:
                ff.extractall(gobject.getcachedir("mdict"))
        globalconfig["cishu"]["mdict"]["args"]["paths"].append(mayberelpath(tgt))
        gobject.base.startxiaoxueguan("mdict")

    @threader
    def downloadxSafe(self, url):
        try:
            self.progresssetval.emit("……", 0)
            self.downloadofficial()
            self.installsucc.emit(True, "")
        except Exception as e:
            self.installsucc.emit(False, stringfyerror(e))

    def downloadauto(self):
        self.downloadxSafe(self.oldlink)
        self.btninstall.setEnabled(False)
        self.formLayout.setRowVisible(3, True)

    def progresssetval_(self, text, val):
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)

    progresssetval = pyqtSignal(str, int)

    def __findithasinstalled(self):
        checkvalid = lambda f: os.path.basename(f) == "jitendex.mdx"
        for f in globalconfig["cishu"]["mdict"]["args"]["paths"]:
            if not f.strip():
                continue
            if not os.path.exists(f):
                continue
            if os.path.isfile(f):
                if checkvalid(f):
                    return True
            for _dir, _, _fs in os.walk(f):
                for _f in _fs:
                    if checkvalid(_f):
                        return True
        return False

    def __init__(self, *argc, **kw):
        super().__init__(*argc, **kw)
        self.installsucc.connect(self._installsucc)
        formLayout = VisLFormLayout(self)
        self.formLayout = formLayout
        formLayout.addRow("论坛", LinkLabel(makehtml("https://forum.freemdict.com/")))
        formLayout.addRow(
            "freemdict", LinkLabel(makehtml("https://search.freemdict.com/"))
        )
        btninstall = LPushButton("下载")
        btninstall.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        if self.__findithasinstalled():
            btninstall.setVisible(False)
        self.btninstall = btninstall
        btninstall.clicked.connect(self.downloadauto)
        __maybebtn = getboxlayout([LinkLabel(makehtml(self.oldlink)), "", btninstall])
        formLayout.addRow("Jitendex", __maybebtn)

        downloadprogress = QProgressBar()

        downloadprogress.setRange(0, 10000)
        downloadprogress.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        formLayout.addRow(downloadprogress)
        self.progresssetval.connect(self.progresssetval_)
        self.downloadprogress = downloadprogress

        formLayout.setRowVisible(3, False)
