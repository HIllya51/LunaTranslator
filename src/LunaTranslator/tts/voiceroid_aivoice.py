import uuid
import os, io
import windows, NativeUtils
from tts.basettsclass import TTSbase, SpeechParam
from ctypes import c_int32, c_float
import xml.etree.ElementTree as ET
import hashlib, zlib, threading
from traceback import print_exc

try:
    # 煞笔python3.12把pbkdf2_hmac放到openssl里去了，导致无法import
    from hashlib import pbkdf2_hmac
except Exception:
    _trans_5C = bytes((x ^ 0x5C) for x in range(256))
    _trans_36 = bytes((x ^ 0x36) for x in range(256))

    def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
        """Password based key derivation function 2 (PKCS #5 v2.0)

        This Python implementations based on the hmac module about as fast
        as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
        for long passwords.
        """
        if not isinstance(hash_name, str):
            raise TypeError(hash_name)

        if not isinstance(password, (bytes, bytearray)):
            password = bytes(memoryview(password))
        if not isinstance(salt, (bytes, bytearray)):
            salt = bytes(memoryview(salt))
        # Fast inline HMAC implementation
        inner = hashlib.sha1()
        outer = hashlib.sha1()
        blocksize = getattr(inner, "block_size", 64)
        if len(password) > blocksize:
            password = hashlib.sha1(hash_name, password).digest()
        password = password + b"\x00" * (blocksize - len(password))
        inner.update(password.translate(_trans_36))
        outer.update(password.translate(_trans_5C))

        def prf(msg, inner=inner, outer=outer):
            # PBKDF2_HMAC uses the password as key. We can re-use the same
            # digest objects and just update copies to skip initialization.
            icpy = inner.copy()
            ocpy = outer.copy()
            icpy.update(msg)
            ocpy.update(icpy.digest())
            return ocpy.digest()

        if iterations < 1:
            raise ValueError(iterations)
        if dklen is None:
            dklen = outer.digest_size
        if dklen < 1:
            raise ValueError(dklen)

        dkey = b""
        loop = 1
        from_bytes = int.from_bytes
        while len(dkey) < dklen:
            prev = prf(salt + loop.to_bytes(4, "big"))
            # endianness doesn't matter here as long to / from use the same
            rkey = int.from_bytes(prev, "big")
            for i in range(iterations - 1):
                prev = prf(prev)
                # rkey = rkey ^ prev
                rkey ^= from_bytes(prev, "big")
            loop += 1
            dkey += rkey.to_bytes(inner.digest_size, "big")

        return dkey[:dklen]


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
        key = pbkdf2_hmac("sha1", a, salt, 1000, d)
        bs: bytes = stream.read()

        def inflate(data):
            decompress = zlib.decompressobj(-zlib.MAX_WBITS)  # see above
            inflated = decompress.decompress(data)
            inflated += decompress.flush()
            return inflated

        return inflate(NativeUtils.AES_decrypt(key, iv, bs)).decode()

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
        is64 = NativeUtils.IsDLLBit64(dllpath)
        # AIVoice & AIVoice2 -> 64位
        exepath = os.path.abspath("files/shareddllproxy{}.exe".format([32, 64][is64]))
        self.engine = NativeUtils.AutoKillProcess(
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
        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)
        self.mappedFile2 = windows.OpenFileMapping(mapname)
        self.mem = windows.MapViewOfFile(self.mappedFile2)

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
            return self.mem[:size]
