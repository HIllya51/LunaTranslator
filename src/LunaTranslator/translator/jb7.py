from translator.basetranslator import basetrans
import ctypes
import os, uuid
import windows, NativeUtils, threading
from myutils.config import _TR
from language import Languages


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

            pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
            waitsignal = str(uuid.uuid4())

            self.engine = NativeUtils.AutoKillProcess(
                'files/plugins/shareddllproxy32.exe jbj7 "{}" {} {}'.format(
                    self.dllpath, pipename, waitsignal
                )
                + dictpath,
            )
            windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
            windows.WaitNamedPipe(pipename)
            self.hPipe = windows.CreateFile(pipename)
        return True

    def translate(self, content: str):
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
            with self.lock:
                windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(int(self.tgtlang))))
                windows.WriteFile(self.hPipe, code1)
                xx = windows.ReadFile(self.hPipe, 65535)
            xx = xx.decode("utf-16-le", errors="ignore")
            ress.append(xx)
        return "\n".join(ress)

    def langmap(self):
        return {Languages.Chinese: "936", Languages.TradChinese: "950"}
