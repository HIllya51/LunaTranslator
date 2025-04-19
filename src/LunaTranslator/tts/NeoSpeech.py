import uuid
import os
import windows, NativeUtils, threading
from tts.basettsclass import TTSbase, SpeechParam
import ctypes, subprocess, gobject
from ctypes import c_int32


class TTS(TTSbase):
    def init(self):
        self.lock = threading.Lock()
        exepath = os.path.join(os.getcwd(), "files/plugins/shareddllproxy32.exe")
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        mapname = str(uuid.uuid4())
        cmd = '"{}" neospeech {} {} {}'.format(exepath, pipename, waitsignal, mapname)

        self.engine = NativeUtils.AutoKillProcess(cmd)

        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)

        self.mappedFile2 = windows.OpenFileMapping(mapname)
        self.mem = windows.MapViewOfFile(self.mappedFile2)

    def getvoicelist(self):
        cachefname = gobject.gettempdir("{}.txt".format(uuid.uuid4()))
        exe = os.path.abspath("files/plugins/shareddllproxy32.exe")
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

    def speak(self, content: str, voice, param: SpeechParam):
        hkey, idx = voice
        with self.lock:
            windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(param.speed)))
            windows.WriteFile(self.hPipe, content.encode("utf-16-le"))
            windows.WriteFile(self.hPipe, hkey.encode("utf-16-le"))
            windows.WriteFile(self.hPipe, bytes(ctypes.c_uint(int(idx))))
            size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value

            return self.mem[:size]
