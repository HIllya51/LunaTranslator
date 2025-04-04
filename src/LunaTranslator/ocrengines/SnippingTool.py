import threading, time, winsharedutils, windows
from qtsymbols import *
from ctypes import Structure, memmove, c_longlong, c_int, c_float, c_int32, c_int64
from ocrengines.baseocrclass import baseocr
import os, zipfile, shutil
from myutils.utils import dynamiclink, stringfyerror
from myutils.config import _TR
import gobject, requests
from traceback import print_exc
from myutils.wrapper import threader
from myutils.proxy import getproxy
import winreg, re
from gui.dynalang import LPushButton, LLabel
from gui.usefulwidget import VisLFormLayout


def trygetsysst():
    hk = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, r"Software\RegisteredApplications\PackagedApps"
    )
    va = winreg.QueryValueEx(hk, "Microsoft.ScreenSketch_8wekyb3d8bbwe!App")[0]
    winreg.CloseKey(hk)
    return re.search("(Microsoft\\.ScreenSketch.*?)\\\\", va).groups()[0]


flist = ["oneocr.dll", "oneocr.onemodel", "onnxruntime.dll"]
testdirs = ["cache/SnippingTool"]


def selectdir():
    check = lambda d: os.path.isdir(d) and all(
        (os.path.isfile(os.path.join(d, _)) for _ in flist)
    )
    if check(testdirs[0]):
        return testdirs[0]
    if len(testdirs) == 1:
        try:
            path = trygetsysst()
            testdirs.append(
                os.path.join(
                    os.environ["PROGRAMFILES"],
                    "WindowsApps",
                    path,
                    "SnippingTool",
                )
            )
        except:
            testdirs.append("")
    if check(testdirs[1]):
        return testdirs[1]
    return None


class question(QWidget):
    installsucc = pyqtSignal(bool, str)
    url = dynamiclink("{main_server}") + "/Resource/SnippingTool"

    def downloadauto(self):
        self.downloadxSafe(self.url)
        self.formLayout.setRowVisible(1, False)
        self.formLayout.setRowVisible(2, True)

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
        target = gobject.getcachedir("ocrmodel/" + url.split("/")[-1])
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
            zipf.extractall("cache")

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
                os.startfile(self.url)
                f = QFileDialog.getOpenFileName(
                    self,
                    filter="SnippingTool.zip",
                )
                fn = f[0]
                if fn:
                    try:
                        with zipfile.ZipFile(fn) as zipf:
                            zipf.extractall("cache")
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

    def init(self):

        dir_ = selectdir()
        if not dir_:
            raise Exception(_TR("未安装"))
        if dir_ != testdirs[0]:
            shutil.copytree(dir_, testdirs[0])
        self.lock = threading.Lock()
        t = time.time()
        t = str(t)
        pipename = "\\\\.\\Pipe\\voiceroid2_" + t
        waitsignal = "voiceroid2waitload_" + t
        mapname = "voiceroid2filemap" + t
        exepath = os.path.abspath("files/plugins/shareddllproxy64.exe")
        self.engine = winsharedutils.AutoKillProcess(
            '"{}" SnippingTool {} {} {}'.format(
                exepath,
                pipename,
                waitsignal,
                mapname,
            ),
            testdirs[0],
        )
        windows.WaitForSingleObject(
            windows.AutoHandle(windows.CreateEvent(False, False, waitsignal)),
            windows.INFINITE,
        )
        windows.WaitNamedPipe(pipename, windows.NMPWAIT_WAIT_FOREVER)
        self.hPipe = windows.AutoHandle(
            windows.CreateFile(
                pipename,
                windows.GENERIC_READ | windows.GENERIC_WRITE,
                0,
                None,
                windows.OPEN_EXISTING,
                windows.FILE_ATTRIBUTE_NORMAL,
                None,
            )
        )
        self.mappedFile2 = windows.AutoHandle(
            windows.OpenFileMapping(
                windows.FILE_MAP_READ | windows.FILE_MAP_WRITE, False, mapname
            )
        )
        self.mem = windows.MapViewOfFile(
            self.mappedFile2,
            windows.FILE_MAP_READ | windows.FILE_MAP_WRITE,
            0,
            0,
            1024 * 1024 * 16,
        )

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
                boxs.append(
                    (box.x1, box.y1, box.x2, box.y2, box.x3, box.y3, box.x4, box.y4)
                )
            return {"box": boxs, "text": texts}
