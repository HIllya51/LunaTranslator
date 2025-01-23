from translator.basetranslator import basetrans
import ctypes
import os, time
import windows, winsharedutils
from myutils.config import _TR
from language import Languages


class TS(basetrans):
    def inittranslator(self):

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
            paths = set()
            for _dir, _, _fs in os.walk(self.path):
                for _f in _fs:
                    path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
                    base, _ = os.path.splitext(os.path.basename(_f))
                    if base == "Jcuser":
                        paths.add(os.path.dirname(path))

            self.dllpath = os.path.abspath(os.path.join(self.path, "JBJCT.dll"))
            dictpath = ""
            for d in sorted(list(paths), key=lambda x: -len(x))[:3]:
                d = os.path.abspath(os.path.join(d, "Jcuser"))
                dictpath += ' "{}" '.format(d)

            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\jbj7_" + t
            waitsignal = "jbjwaitload_" + t

            self.engine = winsharedutils.AutoKillProcess(
                './files/plugins/shareddllproxy32.exe jbj7 "{}" {} {}'.format(
                    self.dllpath, pipename, waitsignal
                )
                + dictpath,
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
        if self.tgtlang not in ["936", "950"]:
            return ""
        if self.checkpath() == False:
            raise Exception(_TR("翻译器加载失败"))
        content = content.replace("\r", "\n")
        lines = content.split("\n")
        ress = []
        for line in lines:
            if len(line) == 0:
                continue
            code1 = line.encode("utf-16-le")
            windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(int(self.tgtlang))))
            windows.WriteFile(self.hPipe, code1)
            xx = windows.ReadFile(self.hPipe, 65535)
            xx = xx.decode("utf-16-le", errors="ignore")
            ress.append(xx)
        return "\n".join(ress)

    def langmap(self):
        return {Languages.Chinese: "936", Languages.TradChinese: "950"}
