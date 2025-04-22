from translator.basetranslator import basetrans
import ctypes, uuid
from myutils.config import _TR
import windows, NativeUtils, threading


class TS(basetrans):
    def init(self):
        self.lock = threading.Lock()
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        self.engine = NativeUtils.AutoKillProcess(
            "files/plugins/shareddllproxy32.exe atlaswmain {} {}".format(
                pipename, waitsignal
            ),
        )

        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)

    def translate(self, content: str):
        l = content.encode("utf-16-le")
        with self.lock:
            windows.WriteFile(self.hPipe, bytes(ctypes.c_int(len(l))))
            windows.WriteFile(self.hPipe, l)
            size = ctypes.c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
            if not size:
                raise Exception(_TR("未安装"))
            return windows.ReadFile(self.hPipe, size).decode("utf-16-le")
