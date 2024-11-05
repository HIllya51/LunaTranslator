import winsharedutils
from tts.basettsclass import TTSbase


class TTS(TTSbase):
    def makemap(self, lsit):
        _ = {}
        for i in range(len(lsit)):
            _[lsit[i]] = i
        return _

    def getvoicelist(self):
        self._7 = winsharedutils.SAPI_List(7)
        self._7m = self.makemap(self._7)
        self._10 = winsharedutils.SAPI_List(10)
        self._10m = self.makemap(self._10)
        if len(self._10):
            needremove = []
            for _ in self._7:
                for _1 in self._10:
                    _s = _1.split("-")
                    if len(_s) and _s[0] == _[: len(_s[0])]:
                        needremove.append(_)

            for _ in needremove:
                self._7.remove(_)
        return (self._7 + self._10), (self._7 + self._10)

    def speak(self, content, rate, voice):
        if voice in self._10m:
            version = 10
            voice_idx = self._10m[voice]
        else:
            version = 7
            voice_idx = self._7m[voice]

        data = winsharedutils.SAPI_Speak(content, version, voice_idx, rate, 100)
        return data
