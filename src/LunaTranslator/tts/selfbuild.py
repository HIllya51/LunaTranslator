from myutils.utils import checkmd5reloadmodule
import gobject
from tts.basettsclass import TTSbase, SpeechParam, TTSResult
import types
from requests import Response


class TTS(TTSbase):
    def __init__(self, *a):
        self.internal = None
        self.__lastm = None
        super().__init__(*a)

    def mayreinit(self):
        module = checkmd5reloadmodule(
            gobject.getconfig("selfbuild_tts.py"), "selfbuild_tts"
        )
        if module and (module.TTS != self.__lastm):
            self.__lastm = module.TTS
            self.internal: TTSbase = module.TTS("selfbuild")
            self.internal.init()

    def speak(
        self, content, voice, param: SpeechParam
    ) -> "bytes|Response|TTSResult|types.GeneratorType":
        self.mayreinit()
        if not self.internal:
            return None
        return self.internal.speak(content, voice, param)

    def getvoicelist(self) -> "tuple[list[str], list[str]]":
        self.mayreinit()
        if not self.internal:
            return None
        return self.internal.getvoicelist()
