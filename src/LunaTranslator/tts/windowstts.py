import NativeUtils, os, threading, uuid, windows
from tts.basettsclass import TTSbase, SpeechParam
import xml.etree.ElementTree as ET
from ctypes import c_int32
from myutils.config import globalconfig, isascii, _TR


class TTS(TTSbase):
    @property
    def extralicense(self):
        return globalconfig.get("MicrosoftWindows.Voice.License", "")

    def getname(self, path):
        Name = None
        LicenseVersion = "0"
        try:
            with open(os.path.join(path, "Tokens.xml"), "r", encoding="utf8") as ff:
                root = ET.fromstring(ff.read())
            try:
                Name = root.findall(".//Attribute[@name='Name']")[0].get("value")
            except:
                pass
            try:
                LicenseVersion = root.findall(".//Attribute[@name='LicenseVersion']")[
                    0
                ].get("value")
            except:
                pass
        except:
            pass
        if LicenseVersion != "0" and not self.extralicense:
            Name = None
        if not isascii(Name):
            Name = _TR("请勿使用非英文路径")
        return Name, LicenseVersion

    def get_paths(self):
        paths = []
        names = []
        for _, path in NativeUtils.FindPackages("MicrosoftWindows.Voice."):
            name = self.getname(path)[0]
            if not name:
                continue
            names.append(name)
            paths.append(path)
        for path, _, __ in os.walk("."):
            base = os.path.basename(path)
            if not base.startswith("MicrosoftWindows.Voice."):
                continue
            name = self.getname(path)[0]
            if not name:
                continue
            ok = False
            for i in range(len(names)):
                if names[i] == name:
                    paths[i] = path
                    ok = True
                    break
            if not ok:
                paths.append(path)
                names.append(name)
        return zip(names, paths)

    def getvoicelist(self):
        self._7 = NativeUtils.SAPI.List(7)
        self._10 = NativeUtils.SAPI.List(10)
        names = []
        vals = []
        for name, path in self.get_paths():
            names.append(name)
            vals.append((1, path))
        for token, name in self._10 + self._7:
            names.append(name)
            vals.append((0, token))
        return vals, names

    cogdll = "Microsoft.CognitiveServices.Speech.extension.embedded.tts.dll"
    def finddlldirectory(self):
        checkdir = lambda d: d and os.path.isfile(os.path.join(d, self.cogdll))
        dllp = r"C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\SpeechSynthesizer"
        if checkdir(dllp):
            return dllp
        for _dir, _, __ in os.walk("."):
            if checkdir(_dir):
                return os.path.abspath(_dir)

        for _dir, _, __ in os.walk(r"C:\Windows\SystemApps"):
            if checkdir(_dir):
                return os.path.abspath(_dir)

    def checkifnatural(self, voice):
        t, path = voice
        if t != 1:
            return
        if self.lastvoice == path:
            return
        dllp = self.finddlldirectory()
        print(path, dllp, NativeUtils.QueryVersion(os.path.join(dllp, self.cogdll)))
        exepath = os.path.join(os.getcwd(), "files/shareddllproxy64.exe")
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        mapname = str(uuid.uuid4())
        lv = self.getname(path)[1]
        cmd = '"{}" msnaturalvoice {} {} {} "{}" "{}" "{}"'.format(
            exepath,
            pipename,
            waitsignal,
            mapname,
            path,
            dllp,
            self.extralicense if (lv != "0") else "",
        )
        self.engine = NativeUtils.AutoKillProcess(cmd)

        windows.WaitForSingleObject(NativeUtils.SimpleCreateEvent(waitsignal))
        windows.WaitNamedPipe(pipename)
        self.hPipe = windows.CreateFile(pipename)
        self.mappedFile2 = windows.OpenFileMapping(mapname)
        self.mem = windows.MapViewOfFile(self.mappedFile2)
        self.lastvoice = path

    def init(self):
        self.lock = threading.Lock()
        self.lastvoice = None

    def speak(self, content: str, voice_1: "tuple[int, str]", param: SpeechParam):
        t, voice = voice_1
        if t == 0:
            return NativeUtils.SAPI.Speak(content, voice, param.speed, param.pitch)
        elif t == 1:
            with self.lock:
                content = self.createSSML(content, voice, param)
                self.checkifnatural(voice_1)
                windows.WriteFile(self.hPipe, content.encode("utf-16-le"))
                size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
                if size < 0:
                    error: bytes = self.mem[:-size]
                    raise Exception(error.decode())
                return self.mem[:size]
