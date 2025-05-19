from translator.basetranslator import basetrans
import ctypes, uuid
from myutils.config import _TR
import windows, NativeUtils, threading
from language import Languages


class TS(basetrans):
    def init(self):
        self.lock = threading.Lock()
        self.path = None
        self.pair = None
        self.checkpath()

    def langmap(self):
        return {Languages.Auto: "ja"}

    def checkpath(self):

        pairs = (self.srclang, self.tgtlang)
        if pairs == self.pair:
            return
        self.pair = pairs
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        self.engine = NativeUtils.AutoKillProcess(
            "files/shareddllproxy32.exe lec {} {} {} {}".format(
                pipename, waitsignal, self.srclang, self.tgtlang
            )
        )

        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)

    def translate(self, content: str):

        self.checkpath()
        l = content.encode("utf-16-le")
        with self.lock:
            windows.WriteFile(self.hPipe, bytes(ctypes.c_int(len(l))))
            windows.WriteFile(self.hPipe, l)
            size = ctypes.c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
            if not size:
                raise Exception(_TR("未安装"))
            return windows.ReadFile(self.hPipe, size).decode("utf-16-le")
