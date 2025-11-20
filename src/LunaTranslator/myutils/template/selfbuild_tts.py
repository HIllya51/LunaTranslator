from tts.basettsclass import TTSbase, SpeechParam, TTSResult
import types
from requests import Response


class TTS(TTSbase):

    def init(self): ...

    def getvoicelist(self) -> "tuple[list[str], list[str]]":
        # 分别返回内部标识名,显示名
        ...

    def speak(
        self, content, voice, param: SpeechParam
    ) -> "bytes|Response|TTSResult|types.GeneratorType": ...
