from myutils.subproc import subproc_w, autoproc
from translator.basetranslator import basetrans
import os, time
import windows


class TS(basetrans):
    def inittranslator(self):
        self.path = None
        self.pair = None
        self.checkpath()

    def checkpath(self):
        if self.config["路径"] == "":
            return False
        if os.path.exists(self.config["路径"]) == False:
            return False
        pairs = (self.srclang, self.tgtlang)
        if self.config["路径"] != self.path or pairs != self.pair:
            self.path = self.config["路径"]

            self.pair = pairs
            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\dreye_" + t
            waitsignal = "dreyewaitload_" + t
            mp = {("zh", "en"): 2, ("en", "zh"): 1, ("zh", "ja"): 3, ("ja", "zh"): 10}
            path = os.path.join(self.path, "DreyeMT\\SDK\\bin")
            if mp[pairs] in [3, 10]:
                path2 = os.path.join(path, "TransCOM.dll")
            else:
                path2 = os.path.join(path, "TransCOMEC.dll")

            self.engine = autoproc(
                subproc_w(
                    './files/plugins/shareddllproxy32.exe dreye "{}"  "{}" {} {} {} '.format(
                        path, path2, str(mp[pairs]), pipename, waitsignal
                    ),
                    name="dreye",
                )
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

    def x64(self, content):

        if self.checkpath() == False:
            return "error"
        codes = {"zh": "gbk", "ja": "shift-jis", "en": "utf8"}
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            windows.WriteFile(self.hPipe, line.encode(codes[self.srclang]))
            ress.append(
                windows.ReadFile(self.hPipe, 4096).decode(codes[self.tgtlang])
            )
        return "\n".join(ress)

    def translate(self, content):
        return self.x64(content)
