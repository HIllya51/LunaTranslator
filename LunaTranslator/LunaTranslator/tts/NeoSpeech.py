import time
import os
import windows
from tts.basettsclass import TTSbase
import ctypes, subprocess
from myutils.subproc import subproc_w, autoproc
from ctypes import cast, POINTER, c_char, c_int32


class TTS(TTSbase):
    def checkchange(self):
        fname = str(time.time())
        os.makedirs("./cache/tts/", exist_ok=True)
        exepath = os.path.join(os.getcwd(), "files/plugins/shareddllproxy32.exe")
        t = time.time()
        t = str(t)
        pipename = "\\\\.\\Pipe\\voiceroid2_" + t
        waitsignal = "voiceroid2waitload_" + t
        mapname = "voiceroid2filemap" + t
        idx = self.privateconfig["voice"].split("_")[-1]
        hkey = self.privateconfig["voice"][: -len(idx) - 1]

        if self.voicexx != (hkey, idx):
            self.voicexx = (hkey, idx)
            cmd = '"{}" neospeech  {} {} {} {} {} '.format(
                exepath, pipename, waitsignal, mapname, hkey, idx
            )

            self.engine = autoproc(subproc_w(cmd, name="neospeech"))

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

    def init(self):

        self.voicexx = (0, 0)
        self.voicelist = self.getvoicelist()

    def voiceshowmap(self, voice):

        idx = voice.split("_")[-1]
        hk = voice[: -len(idx) - 1]

        return self.mapx[(hk, idx)]

    def getvoicelist(self):
        cachefname = os.path.abspath("./cache/{}.txt".format(time.time()))
        exe = os.path.abspath("./files/plugins/shareddllproxy32.exe")
        subprocess.run('"{}"  neospeechlist "{}"'.format(exe, cachefname))

        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()

        os.remove(cachefname)
        datas = (readf.split("\n"))[:-1]

        self.mapx = {}
        xx = []
        for i in range(len(datas) // 3):
            self.mapx[(datas[i * 3 + 1], datas[i * 3 + 2])] = datas[i * 3]
            xx.append("{}_{}".format(datas[i * 3 + 1], datas[i * 3 + 2]))

        return xx

    def speak(self, content, rate, voice, voice_idx):
        self.checkchange()
        windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(rate)))
        buf = ctypes.create_unicode_buffer(content, 10000)
        windows.WriteFile(self.hPipe, bytes(buf))
        size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
        
        return cast(self.mem, POINTER(c_char))[:size]