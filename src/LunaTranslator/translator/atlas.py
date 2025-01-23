from translator.basetranslator import basetrans
import ctypes, time
import windows, winsharedutils


class TS(basetrans):
    def inittranslator(self):

        t = time.time()
        t = str(t)
        pipename = "\\\\.\\Pipe\\dreye_" + t
        waitsignal = "dreyewaitload_" + t
        self.engine = winsharedutils.AutoKillProcess(
            "./files/plugins/shareddllproxy32.exe atlaswmain {} {}".format(
                pipename, waitsignal
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

    def translate(self, content):

        l = content.encode("utf-16-le")
        windows.WriteFile(self.hPipe, bytes(ctypes.c_int(len(l))))
        windows.WriteFile(self.hPipe, l)
        size = ctypes.c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
        if not size:
            raise Exception("not installed")
        return windows.ReadFile(self.hPipe, size).decode("utf-16-le")
