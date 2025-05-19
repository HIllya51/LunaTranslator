from translator.basetranslator import basetrans
from myutils.config import _TR
import os, uuid, threading
import windows, ctypes, NativeUtils


class TS(basetrans):
    def init(self):
        self.lock = threading.Lock()
        self.path = None
        self.userdict = None
        self.checkpath()

    def checkpath(self):
        if self.config["path"] == "":
            return False
        if os.path.exists(self.config["path"]) == False:
            return False
        if self.config["path"] != self.path:
            self.path = self.config["path"]

            pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
            waitsignal = str(uuid.uuid4())

            self.engine = NativeUtils.AutoKillProcess(
                'files/shareddllproxy32.exe eztrans "{}" {} {}'.format(
                    os.path.normpath(os.path.dirname(os.path.abspath(self.path))),
                    pipename,
                    waitsignal,
                ),
            )

            windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
            windows.WaitNamedPipe(pipename)
            self.hPipe = windows.CreateFile(pipename)
        return True

    def translate(self, content: str):

        if not self.checkpath():
            raise Exception(_TR("翻译器加载失败"))
        content = content.replace("\r", "\n")

        code1 = content.encode("utf-16-le")
        with self.lock:
            windows.WriteFile(self.hPipe, code1)
            size = ctypes.c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
            if not size:
                raise Exception(_TR("未安装"))
            return windows.ReadFile(self.hPipe, size).decode("utf-16-le")
