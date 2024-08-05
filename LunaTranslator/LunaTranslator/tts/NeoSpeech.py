import time
import os
import windows
from tts.basettsclass import TTSbase
import ctypes, subprocess, gobject
from myutils.subproc import subproc_w, autoproc
from ctypes import cast, POINTER, c_char, c_int32


class TTS(TTSbase):
    def init(self):
        exepath = os.path.join(os.getcwd(), "files/plugins/shareddllproxy32.exe")
        t = time.time()
        t = str(t)
        pipename = "\\\\.\\Pipe\\voiceroid2_" + t
        waitsignal = "voiceroid2waitload_" + t
        mapname = "voiceroid2filemap" + t

        cmd = '"{}" neospeech  {} {} {}'.format(exepath, pipename, waitsignal, mapname)

        self.engine = autoproc(subproc_w(cmd, name=str(time.time())))

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

        self.mappedFile2 = windows.AutoHandle(
            windows.OpenFileMapping(
                windows.FILE_MAP_READ | windows.FILE_MAP_WRITE, False, mapname
            )
        )
        self.mem = windows.MapViewOfFile(
            self.mappedFile2,
            windows.FILE_MAP_READ | windows.FILE_MAP_WRITE,
            0,
            0,
            1024 * 1024 * 10,
        )

    def getvoicelist(self):
        cachefname = gobject.gettempdir(f"{time.time()}.txt")
        exe = os.path.abspath("./files/plugins/shareddllproxy32.exe")
        subprocess.run('"{}"  neospeechlist "{}"'.format(exe, cachefname))

        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()
        print(readf)
        os.remove(cachefname)
        datas = (readf.split("\n"))[:-1]
        internal = []
        vis = []
        for i in range(len(datas) // 3):
            internal.append((datas[i * 3 + 1], datas[i * 3 + 2]))
            vis.append(datas[i * 3])
        return internal, vis

    def speak(self, content, rate, voice):
        hkey, idx = voice
        windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(rate)))
        windows.WriteFile(self.hPipe, content.encode("utf-16-le"))
        windows.WriteFile(self.hPipe, hkey.encode("utf-16-le"))
        windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(int(idx))))
        size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value

        return cast(self.mem, POINTER(c_char))[:size]
