from translator.basetranslator import basetrans
from myutils.config import _TR
import os, uuid
import windows, NativeUtils, threading
from language import Languages


class TS(basetrans):
    def init(self):
        self.lock = threading.Lock()
        self.path11 = None
        self.pair = None
        self.checkpath()

    def checkpath(self):

        pairs = (self.srclang, self.tgtlang)
        if self.config["path"] != self.path11 or pairs != self.pair:

            self.path11 = self.config["path"]
            base = os.path.abspath(
                os.path.join(self.config["path"], "GTS/" + self.srclang + self.tgtlang)
            )
            if not os.path.isdir(base):
                return False
            dll = None
            for f in os.listdir(base):
                if f.split(".")[-1] == "dll":
                    dll = f
                    break
            if dll is None:
                return False
            self.pair = pairs
            self.path = os.path.join(base, dll)
            self.path2 = os.path.join(base, "DCT")

            pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
            waitsignal = str(uuid.uuid4())
            self.engine = NativeUtils.AutoKillProcess(
                'files/plugins/shareddllproxy32.exe kingsoft "{}" "{}" {} {}'.format(
                    self.path, self.path2, pipename, waitsignal
                ),
            )

            windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
            windows.WaitNamedPipe(pipename)
            self.hPipe = windows.CreateFile(pipename)
        return True

    def translate(self, content: str):
        if not self.checkpath():
            raise Exception(_TR("翻译器加载失败"))
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            with self.lock:
                windows.WriteFile(self.hPipe, line.encode("utf-16-le"))
                x = windows.ReadFile(self.hPipe, 4096)
            ress.append(x.decode("utf-16-le"))

        return "\n".join(ress)

    def langmap(self):
        return {
            Languages.Chinese: "SChinese",
            Languages.TradChinese: "TChinese",
            Languages.English: "English",
            Languages.Japanese: "Japanese",
            Languages.Auto: "Japanese",
        }
