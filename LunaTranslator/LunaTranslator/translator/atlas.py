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
          
            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\dreye_" + t
            waitsignal = "dreyewaitload_" + t 
            self.engine = autoproc(
                subproc_w(
                    './files/plugins/shareddllproxy32.exe atlaswmain   {} {} '.format(
                        pipename, waitsignal
                    ),
                    name="atlaswmain",
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
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            windows.WriteFile(self.hPipe, content.encode('utf-16-le'))
            ress.append(
                windows.ReadFile(self.hPipe, 4096).decode('utf-16-le')
            )
        return "\n".join(ress)

    def translate(self, content):
        return self.x64(content)
