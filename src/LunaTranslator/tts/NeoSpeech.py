from tts.basettsclass import TTSbase, SpeechParam
from LunaSubProcess import LunaSubProcess


class TTS(TTSbase):
    def init(self):
        self._proc = LunaSubProcess.neospeech()

    def getvoicelist(self):
        return LunaSubProcess.neospeechlist()

    def speak(self, content: str, voice: str, param: SpeechParam):
        return self._proc.speak(content, voice, param.speed, param.pitch)
