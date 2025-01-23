from translator.basetranslator import basetrans
from myutils.config import _TR
import os, time
import windows, winsharedutils
from language import Languages


class TS(basetrans):
    def inittranslator(self):
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
            if os.path.exists(base) == False:
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

            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\ks_" + t
            waitsignal = "kswaitload_" + t
            self.engine = winsharedutils.AutoKillProcess(
                './files/plugins/shareddllproxy32.exe kingsoft "{}" "{}" {} {}'.format(
                    self.path, self.path2, pipename, waitsignal
                ),
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
        return True

    def translate(self, content):
        if self.checkpath() == False:
            raise Exception(_TR("翻译器加载失败"))
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
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
