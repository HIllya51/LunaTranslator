import os, uuid, subprocess, threading
from ctypes import (
    c_int32,
    c_float,
    c_int,
    c_uint,
    c_longlong,
    c_int64,
    Structure,
    memmove,
)
import windows, NativeUtils, gobject
from xml.sax.saxutils import escape
from myutils.utils import subprochiderun


def _exepath(bit64):
    return os.path.abspath("files/LunaSubProcess{}.exe".format(64 if bit64 else 32))


class _StatefulSubprocess:

    def __init__(self, command, bit64, *, args=(), use_map=True, cwd=None):
        self.lock = threading.Lock()
        self.pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        self.waitsignal = str(uuid.uuid4())
        argv = [_exepath(bit64), command, self.pipename, self.waitsignal]
        if use_map:
            self.mapname = str(uuid.uuid4())
            argv.append(self.mapname)
        argv += args
        self.engine = NativeUtils.AutoKillProcess(argv, cwd)
        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(self.waitsignal))
        windows.WaitNamedPipe(self.pipename)
        self.hPipe = windows.CreateFile(self.pipename)
        if use_map:
            self.mappedFile = windows.OpenFileMapping(self.mapname)
            self.mem = windows.MapViewOfFile(self.mappedFile, 32 * 1024 * 1024)

    def _write_string(self, content: str):
        l = content.encode("utf-16-le")
        windows.WriteFile(self.hPipe, bytes(c_int(len(l))))
        windows.WriteFile(self.hPipe, l)

    def _read_string(self):
        size = self._read_size()
        if not size:
            return
        return windows.ReadFile(self.hPipe, size).decode("utf-16-le")

    def _read_size(self):
        return c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value

    def _exchange(self, *chunks):
        with self.lock:
            try:
                for c in chunks:
                    windows.WriteFile(self.hPipe, c)
                return self._read_size()
            except:
                return 0


class _Vad(_StatefulSubprocess):

    def _find_vad_assets(self):
        dlldir = ""
        model = ""
        for root, _, files in os.walk("."):
            if not dlldir and "sherpa-onnx-cxx-api.dll" in files:
                p = os.path.abspath(os.path.join(root, "sherpa-onnx-cxx-api.dll"))
                dlldir = os.path.dirname(p)
            if not model and "silero_vad.onnx" in files:
                model = os.path.abspath(os.path.join(root, "silero_vad.onnx"))
            if dlldir and model:
                break
        return dlldir, model

    def __init__(self, threshold, min_silence_duration, min_speech_duration):
        dlldir, model = self._find_vad_assets()
        if not dlldir or not model:
            raise LookupError((dlldir, model))
        bit64 = NativeUtils.IsDLLBit64(
            os.path.abspath(os.path.join(dlldir, "sherpa-onnx-cxx-api.dll"))
        )
        super().__init__(
            "vad",
            bit64,
            args=(
                str(os.getpid()),
                dlldir,
                model,
                str(threshold),
                str(min_silence_duration),
                str(min_speech_duration),
            ),
        )

    def get(self):
        size = self._exchange(b"\0")
        if size <= 0:
            return None
        return self.mem[:size]


class _voiceroid_aivoice(_StatefulSubprocess):
    def __init__(self, dllpath, voicedir, dialect):
        super().__init__(
            "voiceroid_aivoice",
            NativeUtils.IsDLLBit64(dllpath),
            args=(dllpath, voicedir, dialect),
        )

    def speak(self, content: str, voicedir: str, dialect: str, speed, pitch):
        size = self._exchange(
            voicedir.encode(),
            dialect.encode(),
            bytes(c_float(speed)),
            bytes(c_float(pitch)),
            content.encode("utf8"),
        )
        if not size:
            raise Exception()
        return self.mem[:size]


class _NeoSpeech(_StatefulSubprocess):
    def __init__(self):
        super().__init__("neospeech", False)

    def speak(self, content, voice: str, speed, pitch):
        size = self._exchange(
            bytes(c_int32(int(speed))),
            bytes(c_int32(int(pitch))),
            escape(content).encode("utf-16-le"),
            voice.encode("utf-16-le"),
        )
        if not size:
            raise Exception()
        return self.mem[:size]


class _Msnaturalvoice(_StatefulSubprocess):
    def __init__(self, path, dllp, lic):
        super().__init__("msnaturalvoice", True, args=(path, dllp, lic))

    def speak(self, ssml: str):
        size = self._exchange(ssml.encode("utf-16-le"))
        if not size:
            raise Exception()
        if size < 0:
            raise Exception(self.mem[:-size].decode())
        return self.mem[:size]


class _Img(Structure):
    _fields_ = [
        ("t", c_int32),
        ("col", c_int32),
        ("row", c_int32),
        ("_unk", c_int32),
        ("step", c_int64),
        ("data_ptr", c_int64),
    ]


class _OcrLineBoundingBox(Structure):
    _fields_ = [
        ("x1", c_float),
        ("y1", c_float),
        ("x2", c_float),
        ("y2", c_float),
        ("x3", c_float),
        ("y3", c_float),
        ("x4", c_float),
        ("y4", c_float),
    ]


class _SnippingTool(_StatefulSubprocess):
    def __init__(self, cachedir):
        super().__init__("SnippingTool", True, cwd=cachedir)

    def ocr(self, bits, width, height, bytesPerLine, sizeInBytes):
        img = _Img(t=3, col=width, row=height, _unk=0, step=bytesPerLine)
        with self.lock:
            memmove(self.mem, bits, sizeInBytes)
            windows.WriteFile(self.hPipe, bytes(img))
            cnt = c_longlong.from_buffer_copy(windows.ReadFile(self.hPipe, 8)).value
            if not cnt:
                return None
            boxs = []
            texts = []
            for _ in range(cnt):
                size = c_int.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                if not size:
                    continue
                texts.append(windows.ReadFile(self.hPipe, size).decode())
                box = _OcrLineBoundingBox.from_buffer_copy(
                    windows.ReadFile(self.hPipe, 32)
                )
                boxs.append(
                    (box.x1, box.y1, box.x2, box.y2, box.x3, box.y3, box.x4, box.y4)
                )
            return boxs, texts


class _Mssr:
    def __init__(self, path, source, dll, lic):
        self.pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        self.pipename2 = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        self.waitsignal = str(uuid.uuid4())
        self.notify = str(uuid.uuid4())
        self.notify2 = str(uuid.uuid4())
        self.notifyrun = NativeUtils.SimpleCreateEvent(self.notify)
        self.notifystop = NativeUtils.SimpleCreateEvent(self.notify2)
        args = [
            _exepath(True),
            "mssr",
            self.pipename,
            self.waitsignal,
            self.notify,
            path,
            source,
            dll,
            lic,
            self.pipename2,
            self.notify2,
        ]
        self.engine = NativeUtils.AutoKillProcess(args)
        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(self.waitsignal))
        windows.WaitNamedPipe(self.pipename)
        windows.WaitNamedPipe(self.pipename2)
        self.hPipe = windows.CreateFile(self.pipename)
        self.hPipe2 = windows.CreateFile(self.pipename2)

    def write_pid(self, pid):
        windows.WriteFile(self.hPipe2, bytes(c_int(pid)))

    def runornot(self, run):
        windows.SetEvent(self.notifyrun if run else self.notifystop)

    def _read4(self):
        b = windows.ReadFile(self.hPipe, 4)
        if len(b) < 4:
            raise BrokenPipeError
        return c_int.from_buffer_copy(b).value

    def read_record(self):
        iserr = self._read4()
        if iserr:
            sz = self._read4()
            text = windows.ReadFile(self.hPipe, sz).decode()
            return ("error", text)
        t = self._read4()
        if t == 0:
            ok = self._read4()
            offset = self._read4()
            duration = self._read4()
            sz = self._read4()
            text = windows.ReadFile(self.hPipe, sz).decode()
            return ("result", ok, offset, duration, text)
        return ("status", t)


class _Atlas(_StatefulSubprocess):
    def __init__(self):
        super().__init__("atlaswmain", False, use_map=False)

    def translate(self, content):
        with self.lock:
            self._write_string(content)
            return self._read_string()


class _Lec(_StatefulSubprocess):
    def __init__(self, srclang, tgtlang):
        super().__init__("lec", False, args=(srclang, tgtlang), use_map=False)

    def translate(self, content):
        with self.lock:
            self._write_string(content)
            return self._read_string()


class _Eztrans(_StatefulSubprocess):
    def __init__(self, dirname):
        super().__init__("eztrans", False, args=(dirname,), use_map=False)

    def translate(self, content: str):
        with self.lock:
            self._write_string(content.replace("\r", "\n"))
            return self._read_string()


class _Dreye(_StatefulSubprocess):
    def __init__(self, path, path2, mp):
        super().__init__("dreye", False, args=(path, path2, str(mp)), use_map=False)

    def translate(self, content: str, src_codec, tgt_codec):
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            with self.lock:
                windows.WriteFile(self.hPipe, line.encode(src_codec))
                ress.append(windows.ReadFile(self.hPipe, 4096).decode(tgt_codec))
        return "\n".join(ress)


class _Jb7(_StatefulSubprocess):
    def __init__(self, dllpath, dicts):
        super().__init__("jbj7", False, args=[dllpath] + list(dicts), use_map=False)

    def translate(self, content: str, codepage):
        content = content.replace("\r", "\n")
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            code1 = line.encode("utf-16-le")
            with self.lock:
                windows.WriteFile(self.hPipe, bytes(c_uint(codepage)))
                windows.WriteFile(self.hPipe, code1)
                xx = windows.ReadFile(self.hPipe, 65535)
            ress.append(xx.decode("utf-16-le", errors="ignore"))
        return "\n".join(ress)


class _Kingsoft(_StatefulSubprocess):
    def __init__(self, path, path2):
        super().__init__("kingsoft", False, args=(path, path2), use_map=False)

    def translate(self, content: str):
        ress = []
        for line in content.split("\n"):
            if len(line) == 0:
                continue
            with self.lock:
                windows.WriteFile(self.hPipe, line.encode("utf-16-le"))
                x = windows.ReadFile(self.hPipe, 4096)
            ress.append(x.decode("utf-16-le"))
        return "\n".join(ress)


class LunaSubProcess:
    @staticmethod
    def vad(threshold, min_silence_duration, min_speech_duration):
        return _Vad(threshold, min_silence_duration, min_speech_duration)

    @staticmethod
    def voiceroid_aivoice(dllpath, voicedir, dialect):
        return _voiceroid_aivoice(dllpath, voicedir, dialect)

    @staticmethod
    def neospeech():
        return _NeoSpeech()

    @staticmethod
    def msnaturalvoice(path, dllp, lic):
        return _Msnaturalvoice(path, dllp, lic)

    @staticmethod
    def SnippingTool(cachedir):
        return _SnippingTool(cachedir)

    @staticmethod
    def mssr(path, source, dll, lic):
        return _Mssr(path, source, dll, lic)

    @staticmethod
    def atlas():
        return _Atlas()

    @staticmethod
    def lec(srclang, tgtlang):
        return _Lec(srclang, tgtlang)

    @staticmethod
    def dreye(path, path2, mp):
        return _Dreye(path, path2, mp)

    @staticmethod
    def eztrans(dirname):
        return _Eztrans(dirname)

    @staticmethod
    def jb7(dllpath, dicts):
        return _Jb7(dllpath, dicts)

    @staticmethod
    def kingsoft(path, path2):
        return _Kingsoft(path, path2)

    @staticmethod
    def listpm(pids, bit64):
        exe = _exepath(bit64)
        cachefname = gobject.gettempdir("{}.txt".format(uuid.uuid4()))
        subprocess.run([exe, "listpm", cachefname] + [str(_) for _ in pids])
        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()
        try:
            os.remove(cachefname)
        except:
            pass
        return readf.split("\n")

    @staticmethod
    def dllinject_run(pids, bit64, dll):
        exe = _exepath(bit64)
        return subprocess.run(
            [exe, "dllinject"] + [str(_) for _ in pids] + [dll]
        ).returncode

    @staticmethod
    def dllinject_elevated(pids, bit64, dll):
        exe = _exepath(bit64)
        return windows.ShellExecute(
            0,
            "runas",
            exe,
            subprocess.list2cmdline(["dllinject"] + [str(_) for _ in pids] + [dll]),
            None,
            windows.SW_HIDE,
        )

    @staticmethod
    def shellexecutehelper(op, exe, args, dirpath, bshow):
        subprochiderun(
            [
                _exepath(gobject.runtime_bit_64),
                "shellexecutehelper",
                op,
                exe,
                args,
                dirpath,
                str(bshow),
            ],
            run=False,
        )

    @staticmethod
    def createprocesshelper(cmd, dirpath):
        subprochiderun(
            [_exepath(gobject.runtime_bit_64), "createprocesshelper", cmd, dirpath],
            run=False,
        )

    @staticmethod
    def update(exe1, istriggertoupdate, found, pid, b64):
        subprocess.Popen(
            r"{} update {} {} {} {}".format(
                exe1, int(istriggertoupdate), found, pid, b64
            )
        )

    @staticmethod
    def neospeechlist():
        exe = _exepath(False)
        cachefname = gobject.gettempdir("{}.txt".format(uuid.uuid4()))
        subprocess.run([exe, "neospeechlist", cachefname])
        with open(cachefname, "r", encoding="utf-16-le") as ff:
            readf = ff.read()
        try:
            os.remove(cachefname)
        except:
            pass
        datas = readf.split("\n")[:-1]
        internal = []
        vis = []
        for i in range(len(datas) // 2):
            internal.append(datas[i * 2])
            vis.append(datas[i * 2 + 1])
        return internal, vis
