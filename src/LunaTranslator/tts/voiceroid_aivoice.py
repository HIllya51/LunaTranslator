import os, io
import NativeUtils
from LunaSubProcess import LunaSubProcess
from tts.basettsclass import TTSbase, SpeechParam
import xml.etree.ElementTree as ET
import hashlib, zlib, threading
from traceback import print_exc
from myutils.regedit import LOCAL_MACHINE

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


class _methods:

    @staticmethod
    def _voiceroid2_decrypt(stream: io.FileIO):
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

        result = inflate(NativeUtils.AES_decrypt(key, iv, bs)).decode()
        print(result)
        return result

    @staticmethod
    def readinfobin(voicedir):
        try:
            # voiceroid2 & AIVoice -> info.bin
            # AIVoice2 -> infox.bin
            for f in ["info.bin", "infox.bin"]:
                f = os.path.join(voicedir, f)
                if not os.path.isfile(f):
                    continue
                try:
                    with open(f, "rb") as ff:
                        root = ET.fromstring(_methods._voiceroid2_decrypt(ff))
                        return dict(
                            name=root.find("Name").text,
                            dialect=root.find("Dialect").text,
                        )
                except:
                    print_exc()

            # voiceroid+
            with open(os.path.join(voicedir, "dbconf.xml"), "r", encoding="utf8") as ff:
                root = ET.fromstring(ff.read())
                return dict(name=root.find("profile").attrib.get("name"), dialect="")
        except:
            print_exc()
            return {}

    @staticmethod
    def finddll(d, dll):
        if not d or not os.path.isdir(d):
            raise Exception()
        for _dir, _, __ in os.walk(d):
            for d, b64 in dll:
                _dll = os.path.join(_dir, d)
                if os.path.isfile(_dll) and (b64 == NativeUtils.IsDLLBit64(_dll)):
                    return os.path.normpath(os.path.abspath(_dll))

    @staticmethod
    def findinstalled(ver):
        try:
            path = r"SOFTWARE\AI\AIVoice{}\AIVoice{}Editor\{}.0".format(
                "" if ver == 1 else ver, "" if ver == 1 else ver, ver
            )
            k = LOCAL_MACHINE.open(path, query=True)
            _dir = k.query("InstallDir")
            dll = _methods.finddll(
                _dir, [("AITalk_SDK.dll" if ver == 1 else "aitalk_engine.dll", True)]
            )
            path = r"SOFTWARE\AI\AIVoice{}\Voice\{}.0".format(
                "" if ver == 1 else ver, ver
            )
            k = LOCAL_MACHINE.open(path, read=True)
            voices = []
            for sub in k.enum():
                subkey = k.open(sub, query=True)
                _dir_1 = subkey.query("InstallDir")
                if not _dir_1 or not os.path.isdir(_dir_1):
                    continue
                voices.append(os.path.normpath(_dir_1))
            return dll, voices
        except:
            print_exc()
            return None, None

    @staticmethod
    def findinpath(skip, path):
        try:
            dll = _methods.finddll(
                path,
                [
                    ("aitalked.dll", False),  # voiceroid+ & voiceroid2
                    ("AITalk_SDK.dll", True),  # aivoice
                    ("aitalk_engine.dll", True),  # aivoice2
                ],
            )
            if dll in skip:
                raise Exception()
            if not dll:
                raise Exception()
            path = os.path.dirname(dll)
            voicelist = []
            for l in [
                os.path.join(path, "Voice"),  # voiceroid+ & voiceroid2
                os.path.join(os.path.dirname(path), "Voice"),  # aivoice
                os.path.join(
                    os.path.dirname(os.path.dirname(path)), "Voice"
                ),  # aivoice2
            ]:
                if not os.path.isdir(l):
                    continue
                for _ in os.listdir(l):
                    _ = os.path.join(l, _)
                    if not os.path.isdir(_):
                        continue
                    voicelist.append(os.path.normpath(_))
            return dll, voicelist
        except:
            return None, None

    @staticmethod
    def findall(path):
        dll1, voicelist1 = _methods.findinstalled(1)
        dll2, voicelist2 = _methods.findinstalled(2)
        dll3, voicelist3 = _methods.findinpath((dll1, dll2), path)
        join = lambda dll, lit: [(dll, _) for _ in lit] if lit else []
        voicelists = (
            join(dll2, voicelist2) + join(dll1, voicelist1) + join(dll3, voicelist3)
        )
        valids: "list[dict[str, str]]" = []
        for dll, voicedir in voicelists:
            ret = _methods.readinfobin(voicedir)
            if not ret:
                continue
            ret["dll"] = dll
            ret["voicedir"] = voicedir
            ret["voice"] = os.path.basename(voicedir)
            valids.append(ret)
        return valids


class TTS(TTSbase):

    def getvoicelist(self):
        self.saveinfos = _methods.findall(self.config["path"])
        print(self.saveinfos)
        return (
            [_["voice"] for _ in self.saveinfos],
            [_["name"] for _ in self.saveinfos],
        )

    def findinfo(self, voice):
        for _ in self.saveinfos:
            if _["voice"] == voice:
                return _
        return self.saveinfos[0]

    def init(self):
        self.lock = threading.Lock()
        if not self.saveinfos:
            raise Exception()
        which = self.findinfo(self.voice)
        self.runtime = None
        self.invokeruntime(which)

    def invokeruntime(self, which):
        if which["dll"] == self.runtime:
            return
        self.runtime = which["dll"]
        self._proc = LunaSubProcess.voiceroid_aivoice(
            which["dll"],
            which["voicedir"],
            which["dialect"],
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
        with self.lock:
            which = self.findinfo(voice)
            self.invokeruntime(which)
            return self._proc.speak(
                content,
                which["voicedir"],
                which["dialect"],
                self.linear_map(speed.speed),
                self.linear_map2(speed.pitch),
            )
