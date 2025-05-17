import threading, NativeUtils, windows
from qtsymbols import *
from ctypes import Structure, memmove, c_longlong, c_int, c_float, c_int32, c_int64
from ocrengines.baseocrclass import baseocr, OCRResult
import os, zipfile, shutil
from myutils.utils import dynamiclink, stringfyerror
from myutils.config import _TR
import gobject, requests
from traceback import print_exc
from myutils.wrapper import threader
from myutils.proxy import getproxy
import re, uuid
from gui.dynalang import LPushButton, LLabel
from gui.usefulwidget import VisLFormLayout


flist = ["oneocr.dll", "oneocr.onemodel", "onnxruntime.dll"]
cachedir = "cache/SnippingTool"
packageFamilyName = "Microsoft.ScreenSketch_8wekyb3d8bbwe"


def checkdir(d):
    return os.path.isdir(d) and all((os.path.isfile(os.path.join(d, _)) for _ in flist))


def selectdir():
    if checkdir(cachedir):
        return cachedir
    path = NativeUtils.GetPackagePathByPackageFamily(packageFamilyName)
    if not path:
        return None
    path = os.path.join(path, "SnippingTool")
    if not checkdir(path):
        return None
    return path


class question(QWidget):
    def downloadofficial(self):
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,ru;q=0.8,ar;q=0.7,sq;q=0.6",
            "cache-control": "no-cache",
            "origin": "https://store.rg-adguard.net",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://store.rg-adguard.net/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }

        data = dict(type="PackageFamilyName", url=packageFamilyName)

        response = requests.post(
            "https://store.rg-adguard.net/api/GetFiles",
            headers=headers,
            data=data,
            proxies=getproxy(),
        )

        saves = []
        for link, package in re.findall('<a href="(.*?)".*?>(.*?)</a>', response.text):
            if not package.startswith("Microsoft.ScreenSketch"):
                continue
            if not package.endswith(".msixbundle"):
                continue
            version = re.search(r"\d+\.\d+\.\d+\.\d+", package)
            if not version:
                continue
            version = tuple(int(_) for _ in version.group().split("."))
            saves.append((version, link, package))
        saves.sort(key=lambda _: _[0])
        url = saves[-1][1]
        file_size = 0
        req = requests.get(url, stream=True, proxies=getproxy())
        size = int(req.headers["Content-Length"])
        self.failedlink = lambda: url
        self.skiplink2 = True
        target = gobject.gettempdir(saves[-1][2])
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
        self.unzipmsix(target)

    def unzipmsix(self, file):
        namemsix = None
        with zipfile.ZipFile(file) as ff:
            for name in ff.namelist():
                if name.startswith("SnippingTool") and name.endswith("_x64.msix"):
                    namemsix = name
                    break
            ff.extract(namemsix, gobject.gettempdir())
        if not namemsix:
            raise Exception()
        with zipfile.ZipFile(gobject.gettempdir(namemsix)) as ff:
            collect = []
            for name in ff.namelist():
                if name.startswith("SnippingTool/"):
                    collect.append(name)
            ff.extractall(gobject.getcachedir(), collect)
        if not checkdir(cachedir):
            raise Exception()

    installsucc = pyqtSignal(bool, str)

    def downloadauto(self):
        self.downloadxSafe(dynamiclink("/Resource/SnippingTool"))
        self.formLayout.setRowVisible(1, False)
        self.formLayout.setRowVisible(2, True)

    progresssetval = pyqtSignal(str, int)

    @threader
    def downloadxSafe(self, url):
        try:
            self.progresssetval.emit("……", 0)
            try:
                self.downloadofficial()
            except:
                if self.skiplink2:
                    raise Exception()
                self.downloadx(url)
                print_exc()
                self.progresssetval.emit("……", 0)
            self.installsucc.emit(True, "")
        except Exception as e:
            self.installsucc.emit(False, stringfyerror(e))

    def downloadx(self, url: str):

        file_size = 0
        req = requests.get(url, verify=False, proxies=getproxy(), stream=True)
        size = int(req.headers["Content-Length"])
        target = gobject.gettempdir(url.split("/")[-1])
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
            zipf.extractall(gobject.getcachedir())
        if not checkdir(cachedir):
            raise Exception()

    def _installsucc(self, succ, failreason):
        if succ:
            self.progresssetval.emit(_TR("添加成功"), 10000)
            QMessageBox.information(self, _TR("成功"), _TR("添加成功"))
            self.formLayout.setRowVisible(0, True)
            self.formLayout.setRowVisible(1, False)
            self.formLayout.setRowVisible(2, False)
        else:
            self.progresssetval.emit(_TR("添加失败"), 0)
            res = QMessageBox.question(
                self,
                _TR("错误"),
                failreason + "\n\n" + _TR("自动添加失败，是否手动添加？"),
            )
            if res == QMessageBox.StandardButton.Yes:
                os.startfile(self.failedlink())
                f = QFileDialog.getOpenFileName(
                    self,
                    filter="*.msixbundle" if self.skiplink2 else "SnippingTool.zip",
                )
                fn = f[0]
                if fn:
                    try:
                        if self.skiplink2:
                            self.unzipmsix(fn)
                        else:
                            with zipfile.ZipFile(fn) as zipf:
                                zipf.extractall(gobject.getcachedir())
                            if not checkdir(cachedir):
                                raise Exception()
                        QMessageBox.information(self, _TR("成功"), _TR("添加成功"))
                        self.formLayout.setRowVisible(0, True)
                        self.formLayout.setRowVisible(1, False)
                        self.formLayout.setRowVisible(2, False)
                        return
                    except:
                        QMessageBox.information(self, _TR("错误"), _TR("添加失败"))
                        print_exc()
            self.formLayout.setRowVisible(0, False)
            self.formLayout.setRowVisible(1, True)
            self.formLayout.setRowVisible(2, False)

    def progresssetval_(self, text, val):
        self.downloadprogress.setValue(val)
        self.downloadprogress.setFormat(text)

    def __init__(self, *argc, **kw):
        super().__init__(*argc, **kw)
        self.installsucc.connect(self._installsucc)
        self.failedlink = lambda: dynamiclink("/Resource/SnippingTool")
        self.skiplink2 = False
        formLayout = VisLFormLayout(self)
        formLayout.setContentsMargins(0, 0, 0, 0)
        lb = LLabel("已安装")
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formLayout.addRow(lb)
        if selectdir():
            return
        btninstall = LPushButton("下载")
        btninstall.clicked.connect(self.downloadauto)
        formLayout.addRow(btninstall)

        downloadprogress = QProgressBar()

        downloadprogress.setRange(0, 10000)
        downloadprogress.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        formLayout.addRow(downloadprogress)
        self.progresssetval.connect(self.progresssetval_)
        self.downloadprogress = downloadprogress
        formLayout.setRowVisible(0, False)
        formLayout.setRowVisible(2, False)
        self.formLayout = formLayout


class Img(Structure):
    _fields_ = [
        ("t", c_int32),
        ("col", c_int32),
        ("row", c_int32),
        ("_unk", c_int32),
        ("step", c_int64),
        ("data_ptr", c_int64),
    ]


class OcrLineBoundingBox(Structure):
    _fields_ = [
        ("x1", c_float),
        ("y1", c_float),
        ("x2", c_float),
        ("y2", c_float),
        ("x3", c_float),
        ("y3", c_float),
        ("x4", c_float),
        ("y4", c_float),
    ]


class OCR(baseocr):
    required_image_format = QImage
    required_mini_height = 50

    def init(self):

        dir_ = selectdir()
        if not dir_:
            raise Exception(_TR("未安装"))
        if dir_ != cachedir:
            shutil.copytree(dir_, cachedir)
        self.lock = threading.Lock()
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        mapname = str(uuid.uuid4())
        exepath = os.path.abspath("files/plugins/shareddllproxy64.exe")
        self.engine = NativeUtils.AutoKillProcess(
            '"{}" SnippingTool {} {} {}'.format(
                exepath,
                pipename,
                waitsignal,
                mapname,
            ),
            cachedir,
        )
        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)
        self.mappedFile2 = windows.OpenFileMapping(mapname)
        self.mem = windows.MapViewOfFile(self.mappedFile2)

    def ocr(self, qimage: QImage):
        if qimage.format() != QImage.Format.Format_RGBA8888:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        with self.lock:
            img_struct = Img(
                t=3,
                col=qimage.width(),
                row=qimage.height(),
                _unk=0,
                step=qimage.bytesPerLine(),
            )
            memmove(self.mem, int(qimage.bits()), qimage.byteCount())
            windows.WriteFile(self.hPipe, bytes(img_struct))
            cnt = c_longlong.from_buffer_copy(windows.ReadFile(self.hPipe, 8)).value

            if not cnt:
                return
            boxs = []
            texts = []
            for i in range(cnt):
                size = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                if not size:
                    continue
                texts.append(windows.ReadFile(self.hPipe, size).decode())
                box = OcrLineBoundingBox.from_buffer_copy(
                    windows.ReadFile(self.hPipe, 32)
                )
                box = (box.x1, box.y1, box.x2, box.y2, box.x3, box.y3, box.x4, box.y4)
                boxs.append(box)
            return OCRResult(boxs=boxs, texts=texts)
