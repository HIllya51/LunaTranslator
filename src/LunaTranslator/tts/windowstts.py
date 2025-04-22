import NativeUtils
from tts.basettsclass import TTSbase, SpeechParam


class TTS(TTSbase):

    def getvoicelist(self):
        self._7 = NativeUtils.SAPI.List(7)
        self._10 = NativeUtils.SAPI.List(10)
        __ = []
        for _ in range(len(self._7)):
            __.append((7, _))
        for _ in range(len(self._10)):
            __.append((10, _))
        return __, (self._7 + self._10)

    def speak(self, content, voice, param: SpeechParam):
        version, voice_idx = voice

        data = NativeUtils.SAPI.Speak(content, version, voice_idx, param.speed, 100)
        return data
