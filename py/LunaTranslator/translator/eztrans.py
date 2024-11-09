from translator.basetranslator import basetrans
from myutils.config import _TR
import os, time
import windows
from myutils.subproc import subproc_w, autoproc


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

            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\xxx_" + t
            waitsignal = "waitload_" + t

            self.engine = autoproc(
                subproc_w(
                    './files/plugins/shareddllproxy32.exe eztrans "{}" {} {} '.format(
                        os.path.normpath(os.path.dirname(self.path)),
                        pipename,
                        waitsignal,
                    ),
                    name="eztrans",
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

    def x64(self, content: str):

        if self.checkpath() == False:
            raise Exception(_TR("翻译器加载失败"))
        content = content.replace("\r", "\n")

        code1 = content.encode("utf-16-le")
        windows.WriteFile(self.hPipe, code1)
        xx = windows.ReadFile(self.hPipe, 65535)
        xx = xx.decode("utf-16-le", errors="ignore")

        return xx

    def translate(self, content):

        return self.x64(content)

    def langmap(self):
        return {"zh": "936", "cht": "950"}
