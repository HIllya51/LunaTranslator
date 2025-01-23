import time
import os
import windows, winsharedutils
from tts.basettsclass import TTSbase, SpeechParam
from ctypes import cast, POINTER, c_char, c_int32, c_float


class TTS(TTSbase):
    def getvoicelist(self):
        voicelist = []
        _p = os.path.join(self.config["path"], "Voice")
        if os.path.exists(_p) == False:
            raise Exception("not exists " + _p)
        l = os.listdir(_p)

        for _ in l:
            if "_" in _:
                _l = _.split("_")
                if len(_l) >= 2:
                    if _l[-1] == "44" or _l[-1] == "22":
                        voicelist.append(_)
        return voicelist, [self.voiceshowmap(_) for _ in voicelist]

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

    def init(self):
        dllpath = os.path.abspath(os.path.join(self.config["path"], "aitalked.dll"))
        exepath = os.path.abspath("files/plugins/shareddllproxy32.exe")

        t = time.time()
        t = str(t)
        pipename = "\\\\.\\Pipe\\voiceroid2_" + t
        waitsignal = "voiceroid2waitload_" + t
        mapname = "voiceroid2filemap" + t

        self.engine = winsharedutils.AutoKillProcess(
            '"{}" voiceroid2 "{}" "{}" {} {} {}'.format(
                exepath,
                os.path.abspath(self.config["path"]),
                dllpath,
                pipename,
                waitsignal,
                mapname,
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

    def speak(self, content, voice, speed: SpeechParam):

        __ = []
        for c in content:
            try:
                __.append(c.encode("shift-jis"))
            except:
                pass
        code1 = b"".join(__)
        if not code1:
            return
        windows.WriteFile(self.hPipe, voice.encode())
        windows.WriteFile(self.hPipe, bytes(c_float(self.linear_map(speed.speed))))
        windows.WriteFile(self.hPipe, bytes(c_float(self.linear_map2(speed.pitch))))
        windows.WriteFile(self.hPipe, code1)

        size = c_int32.from_buffer_copy(windows.ReadFile(self.hPipe, 4)).value
        if size == 0:
            return None
        return cast(self.mem, POINTER(c_char))[:size]
