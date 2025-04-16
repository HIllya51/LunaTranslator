import uuid
import os, io
import windows, winsharedutils
from tts.basettsclass import TTSbase, SpeechParam
from ctypes import cast, POINTER, c_char, c_int32, c_float
import xml.etree.ElementTree as ET
import hashlib, zlib, threading
from traceback import print_exc


class TTS(TTSbase):
    def getvoicelist(self):
        self.cacheDialect = {}
        voicelist = []
        vis = []
        path = os.path.dirname(self.findtarget(self.config["path"]))
        # AIVoice试用版语音路径在上一层
        for l in [
            os.path.join(path, "Voice"),
            os.path.join(os.path.dirname(path), "Voice"),
        ]:
            if not os.path.isdir(l):
                continue
            for _ in os.listdir(l):
                v = self.getvoicename(l, _)
                if not v:
                    continue
                vis.append(v)
                voicelist.append(_)
        return voicelist, vis

    def voiceroid2_decrypt(self, stream: io.FileIO):
        a = b"jD5yPFM63olaOWC5fiGpLL5LJnpwTlsK"
        d = 16
        salt = stream.read(d)
        iv = stream.read(d)
        key = hashlib.pbkdf2_hmac("sha1", a, salt, 1000, d)
        bs: bytes = stream.read()

        def inflate(data):
            decompress = zlib.decompressobj(-zlib.MAX_WBITS)  # see above
            inflated = decompress.decompress(data)
            inflated += decompress.flush()
            return inflated

        return inflate(winsharedutils.AES_decrypt(key, iv, bs)).decode()

    def readinfobin(self, voicedir, voice):

        voicedir = os.path.join(voicedir, voice)
        # voiceroid2 & AIVoice -> info.bin
        # AIVoice2 -> infox.bin
        for f in ["info.bin", "infox.bin"]:
            f = os.path.join(voicedir, f)
            if not os.path.isfile(f):
                continue
            try:
                with open(f, "rb") as ff:
                    root = ET.fromstring(self.voiceroid2_decrypt(ff))
                    self.cacheDialect[voice] = root.find("Dialect").text
                    return root.find("Name").text
            except:
                print_exc()

    def getvoicename(self, voicedir, voice):
        Name = self.readinfobin(voicedir, voice)
        if Name:
            return Name
        try:
            # voiceroid+
            with open(
                os.path.join(voicedir, voice, "dbconf.xml"), "r", encoding="utf8"
            ) as ff:
                root = ET.fromstring(ff.read())
                self.cacheDialect[voice] = "standard"
                return root.find("profile").attrib.get("name")
        except:
            pass
        return None

    def findtarget(self, path):
        for _dir, _, __ in os.walk(path):
            dll = os.path.join(_dir, "aitalked.dll")
            if os.path.isfile(dll):
                return os.path.abspath(dll)

    def init(self):
        self.lock = threading.Lock()
        # voiceroid+ & voiceroid2 & AIVoice -> aitalked.dll
        # AIVoice2 -> aitalk_engine.dll
        dllpath = self.findtarget(self.config["path"])
        if not os.path.isfile(dllpath):
            raise Exception()

        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        mapname = str(uuid.uuid4())
        is64 = winsharedutils.IsDLLBit64(dllpath)
        # AIVoice & AIVoice2 -> 64位
        exepath = os.path.abspath(
            "files/plugins/shareddllproxy{}.exe".format([32, 64][is64])
        )
        self.engine = winsharedutils.AutoKillProcess(
            '"{}" voiceroid2 "{}" "{}" {} {} {} {} {}'.format(
                exepath,
                os.path.dirname(dllpath),
                dllpath,
                pipename,
                waitsignal,
                mapname,
                self.voice,
                self.cacheDialect[self.voice],
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
            1024 * 1024 * 16,
        )

    def linear_map(self, x):
        # 0.5-4
        if x >= 0:
            x = 0.3 * x + 1.0
        else:
            x = 0.05 * x + 1.0
        return x

    def linear_map2(self, x):
        # 0.5-2
        if x >= 0:
            x = 0.1 * x + 1.0
        else:
            x = 0.05 * x + 1.0
        return x

    def speak(self, content: str, voice: str, speed: SpeechParam):
        __ = []
        for c in content:
            try:
                __.append(c.encode("shift-jis"))
            except:
                pass
        code1 = b"".join(__)
        if not code1:
            return
        with self.lock:
            windows.WriteFile(self.hPipe, voice.encode())
            windows.WriteFile(self.hPipe, self.cacheDialect[self.voice].encode())
            windows.WriteFile(self.hPipe, bytes(c_float(self.linear_map(speed.speed))))
            windows.WriteFile(self.hPipe, bytes(c_float(self.linear_map2(speed.pitch))))
            windows.WriteFile(self.hPipe, code1)

            size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
            if size == 0:
                return None
            return cast(self.mem, POINTER(c_char))[:size]
