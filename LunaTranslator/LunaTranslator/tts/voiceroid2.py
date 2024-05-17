import time
import os
import windows
from tts.basettsclass import TTSbase
from ctypes import cast, POINTER, c_char, c_int32
from myutils.subproc import subproc_w, autoproc
import threading


class TTS(TTSbase):

    def init(self):
        self.status = None

        self.voicelist = self.getvoicelist()
        threading.Thread(target=self.checkpath).start()

    def getvoicelist(self):
        voicelist = []
        if os.path.exists(self.config["path"]) == False:
            return []
        l = os.listdir(os.path.join(self.config["path"], "Voice"))

        for _ in l:
            if "_" in _:
                _l = _.split("_")
                if len(_l) >= 2:
                    if _l[-1] == "44" or _l[-1] == "22":
                        voicelist.append(_)
        return voicelist

    def voiceshowmap(self, voice):
        name = voice.split("_")[0]
        jpname = {
            "yukari": "結月ゆかり",
            "akari": "紲星あかり",
            "kiritan": "東北きりたん",
            "itako": "東北イタコ",
            "zunko": "東北ずん子",
            "yuzuru": "伊織弓鶴",
            "tsuina": "ついなちゃん",
            "akane": "琴葉茜",
            "aoi": "琴葉葵",
            "kou": "水奈瀬コウ",
            "sora": "桜乃そら",
            "tamiyasu": "民安ともえ",
            "ai": "月読アイ",
            "shouta": "月読ショウタ",
            "seika": "京町セイカ",
            "una": "音街ウナ",
            "yoshidakun": "鷹の爪吉田",
            "galaco": "ギャラ子",
        }
        vv = jpname[name]
        if "west" in voice:
            vv += "（関西弁）"
        return vv

    def checkpath(self):
        if self.config["path"] == "":
            return False
        if os.path.exists(self.config["path"]) == False:
            return False
        if (
            self.config["path"],
            self.privateconfig["voice"],
            self.publicconfig["rate"],
        ) != self.status:
            dllpath = os.path.join(self.config["path"], "aitalked.dll")
            ##dllpath=r'C:\Users\wcy\Downloads\zunko\aitalked.dll'
            exepath = os.path.join(os.getcwd(), "files/plugins/shareddllproxy32.exe")

            t = time.time()
            t = str(t)
            pipename = "\\\\.\\Pipe\\voiceroid2_" + t
            waitsignal = "voiceroid2waitload_" + t
            mapname = "voiceroid2filemap" + t

            def linear_map(x):
                if x >= 0:
                    x = 0.1 * x + 1.0
                else:
                    x = 0.05 * x + 1.0
                return x

            "".endswith
            if self.privateconfig["voice"].endswith("_44"):
                _1 = 44100
                _2 = linear_map(self.publicconfig["rate"])
            elif self.privateconfig["voice"].endswith("_22"):
                _1 = 22050
                _2 = 0
            self.engine = autoproc(
                subproc_w(
                    '"{}" voiceroid2 "{}" "{}" {} {} {} {} {} {}'.format(
                        exepath,
                        self.config["path"],
                        dllpath,
                        self.privateconfig["voice"],
                        _1,
                        _2,
                        pipename,
                        waitsignal,
                        mapname,
                    ),
                    name="voicevoid2",
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
                1024 * 1024 * 10,
            )

            self.status = (
                self.config["path"],
                self.privateconfig["voice"],
                self.publicconfig["rate"],
            )

    def speak(self, content, rate, voice, voice_idx):
        self.checkpath()

        try:
            code1 = content.encode("shift-jis")
        except:
            return
        windows.WriteFile(self.hPipe, code1)

        size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
        if size == 0:
            return None
        return cast(self.mem, POINTER(c_char))[:size]
