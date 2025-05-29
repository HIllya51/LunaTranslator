import uuid
import os
import windows, NativeUtils, threading
from xml.sax.saxutils import escape
from tts.basettsclass import TTSbase, SpeechParam
import subprocess, gobject
from ctypes import c_int32


class TTS(TTSbase):
    def init(self):
        self.lock = threading.Lock()
        exepath = os.path.join(os.getcwd(), "files/shareddllproxy32.exe")
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
        exe = os.path.abspath("files/shareddllproxy32.exe")
        subprocess.run('"{}"  neospeechlist "{}"'.format(exe, cachefname))

        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()
        print(readf)
        os.remove(cachefname)
        datas = (readf.split("\n"))[:-1]
        internal = []
        vis = []
        for i in range(len(datas) // 2):
            internal.append((datas[i * 2]))
            vis.append(datas[i * 2 + 1])
        return internal, vis

    def speak(self, content: str, voice: str, param: SpeechParam):
        with self.lock:
            windows.WriteFile(self.hPipe, bytes(c_int32(int(param.speed))))
            windows.WriteFile(self.hPipe, bytes(c_int32(int(param.pitch))))
            windows.WriteFile(self.hPipe, escape(content).encode("utf-16-le"))
            windows.WriteFile(self.hPipe, voice.encode("utf-16-le"))
            size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value

            return self.mem[:size]
