from translator.basetranslator import basetrans
from myutils.config import _TR
import os, time
import windows, winsharedutils, threading
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
        if self.config["path"] == "":
            return False
        if os.path.exists(self.config["path"]) == False:
            return False
        pairs = (self.srclang, self.tgtlang)
        if self.config["path"] != self.path or pairs != self.pair:
            self.path = self.config["path"]

            self.pair = pairs
            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\dreye_" + t
            waitsignal = "dreyewaitload_" + t
            mp = {("zh", "en"): 2, ("en", "zh"): 1, ("zh", "ja"): 3, ("ja", "zh"): 10}
            path = os.path.abspath(os.path.join(self.path, "DreyeMT\\SDK\\bin"))
            if mp[pairs] in [3, 10]:
                path2 = os.path.join(path, "TransCOM.dll")
            else:
                path2 = os.path.join(path, "TransCOMEC.dll")

            self.engine = winsharedutils.AutoKillProcess(
                './files/plugins/shareddllproxy32.exe dreye "{}" "{}" {} {} {}'.format(
                    path, path2, str(mp[pairs]), pipename, waitsignal
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

    def translate(self, content: str):

        if not self.checkpath():
            raise Exception(_TR("翻译器加载失败"))
        codes = {
            Languages.Chinese: "gbk",
            Languages.Japanese: "shift-jis",
            Languages.English: "utf8",
        }
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            with self.lock:
                windows.WriteFile(self.hPipe, line.encode(codes[self.srclang]))
                ress.append(
                    windows.ReadFile(self.hPipe, 4096).decode(codes[self.tgtlang])
                )
        return "\n".join(ress)
