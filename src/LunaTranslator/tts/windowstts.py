import NativeUtils, os, threading, uuid, windows
from tts.basettsclass import TTSbase, SpeechParam
import xml.etree.ElementTree as ET
from ctypes import c_int32


class TTS(TTSbase):

    def getvoicelist(self):
        self._7 = NativeUtils.SAPI.List(7)
        self._10 = NativeUtils.SAPI.List(10)
        self.natural = NativeUtils.FindPackages("MicrosoftWindows.Voice.")
        names = []
        vals = []
        for _, path in NativeUtils.FindPackages("MicrosoftWindows.Voice."):
            with open(os.path.join(path, "Tokens.xml"), "r", encoding="utf8") as ff:
                root = ET.fromstring(ff.read())
            target_attributes = root.findall(".//Attribute[@name='Name']")
            if not target_attributes:
                continue
            names.append(target_attributes[0].get("value"))
            vals.append((1, path))
        for token, name in self._10 + self._7:
            names.append(name)
            vals.append((0, token))
        return vals, names

    def finddlldirectory(self):
        dll = "Microsoft.CognitiveServices.Speech.extension.embedded.tts.dll"
        checkdir = lambda d: d and os.path.isfile(os.path.join(d, dll))
        dllp = r"C:\Windows\SystemApps\MicrosoftWindows.Client.Core_cw5n1h2txyewy\SpeechSynthesizer"
        if checkdir(dllp):
            return dllp
        dllp = "C:\\Windows\\SystemApps\\LKG\\MicrosoftWindows.LKG.SpeechRuntime_cw5n1h2txyewy"
        if checkdir(dllp):
            return dllp
        for _dir, _, __fs in os.walk(r"C:\Windows\SystemApps"):
            for _f in __fs:
                if _f == dll:
                    return os.path.abspath(_dir)

    def checkifnatural(self, voice):
        t, path = voice
        if t != 1:
            return
        if self.lastvoice == path:
            return
        dllp = self.finddlldirectory()
        print(dllp, path)
        exepath = os.path.join(os.getcwd(), "files/shareddllproxy64.exe")
        pipename = "\\\\.\\Pipe\\" + str(uuid.uuid4())
        waitsignal = str(uuid.uuid4())
        mapname = str(uuid.uuid4())
        cmd = '"{}" msnaturalvoice {} {} {} "{}" "{}"'.format(
            exepath, pipename, waitsignal, mapname, path, dllp
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
