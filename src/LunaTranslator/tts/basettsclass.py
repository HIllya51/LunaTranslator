from myutils.config import globalconfig
import functools
from myutils.wrapper import threader
from xml.sax.saxutils import escape
from traceback import print_exc
from myutils.utils import LRUCache, stringfyerror
from myutils.commonbase import commonbase
from requests import Response
import types
from myutils.mimehelper import query_mime


class TTSResult:
    def __bool__(self):
        return bool((not self.error) and self.data)

    @property
    def ext(self):
        if "/" in self._type:
            return self._type.split("/")[1]
        return "wav"

    @property
    def mime(self):
        if "/" in self._type:
            return self._type
        return query_mime(self._type)

    def __init__(
        self,
        data: "bytes|Response|TTSResult|types.GeneratorType" = None,
        type: str = "audio/wav",
        error=None,
    ):
        if isinstance(data, TTSResult):
            self.data = data.data
            self.error = data.error
            self._type = data._type
        elif isinstance(data, Response):
            data.raise_for_status()
            self.data = data.content
            self._type = data.headers.get("content-type", type)
        else:
            self.data = data
            self._type = type
        self.error = error


class SpeechParam:
    def __init__(self, speed, pitch):
        self.speed = speed
        self.pitch = pitch

    def __hash__(self):
        return self._tuple_().__hash__()

    def __eq__(self, value: "SpeechParam"):
        return self._tuple_() == value._tuple_()

    def _tuple_(self):
        return tuple((self.speed, self.pitch))


class TTSbase(commonbase):
    def init(self): ...
    def getvoicelist(self):
        # 分别返回内部标识名,显示
        return [], []

    def speak(self, content, voice, param: SpeechParam):
        return None  # fname ,若为None则是不需要文件直接朗读

    ####################
    arg_support_pitch = True
    arg_support_speed = True

    @property
    def volume(self):
        return globalconfig["ttscommon"]["volume"]

    @property
    def param(self):
        return SpeechParam(
            globalconfig["ttscommon"]["rate"], globalconfig["ttscommon"]["pitch"]
        )

    @property
    def voice(self):
        _v = self.privateconfig.get("voice")
        if _v and isinstance(self.voicelist[0], tuple):
            # vits的tuple在json.load后变成list了
            _v = tuple(_v)
        if _v not in self.voicelist:
            _v = self.voicelist[0]
        return _v

    @voice.setter
    def voice(self, v):
        self.privateconfig["voice"] = v

    ########################

    _globalconfig_key = "reader"
    _setting_dict = globalconfig["reader"]

    def __init__(
        self, typename, playaudiofunction, privateconfig=None, init=True, uid=None
    ) -> None:
        super().__init__(typename)
        self.playaudiofunction = playaudiofunction
        self.uid = uid
        self.LRUCache = LRUCache(32)
        if privateconfig is None:
            self.privateconfig = globalconfig["reader"][self.typename]
        else:
            self.privateconfig = privateconfig
        self.voicelist, self.voiceshowlist = self.getvoicelist()
        if len(self.voicelist) != len(self.voiceshowlist):
            raise Exception()
        if len(self.voicelist) == 0:
            raise Exception()
        if init:
            self.init()

    def read(self, content, force=False, timestamp=None):

        def _(force, volume, timestamp, data: TTSResult):
            if not data:
                return
            self.playaudiofunction(data.data, volume, force, timestamp)

        self.ttscallback(content, functools.partial(_, force, self.volume, timestamp))

    @threader
    def ttscallback(self, content, callback):

        if len(content) == 0:
            return
        if len(self.voicelist) == 0:
            return
        try:
            key = self.ttscachekey(content, self.voice, self.param)
            data = self.LRUCache.get(key)
            if data:
                return callback(data)
            data = self.multiapikeywrapper(self.speak)(content, self.voice, self.param)
            if data:
                data = TTSResult(data)
                callback(data)
                self.LRUCache.put(key, data)
            else:
                callback(None)
        except Exception as e:
            print_exc()
            res = TTSResult(error=stringfyerror(e))
            print(res.error)
            callback(res)
            return

    def ttscachekey(self, content, voice, param):
        return content, voice, param

    def createSSML(self, content, voice, param: SpeechParam):
        # https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice
        # 按照微软文档，pitch应当取值-50%~50%，rate应该取值-50%~100%。虽然实测可以超出范围，但还是按他说的来吧。
        pitch = int(param.pitch * 5)
        rate = int(param.speed * 10) if param.speed > 0 else int(param.speed * 5)
        ssml = (
            "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
            "<voice name='{}'><prosody pitch='{}%' rate='{}%'>{}</prosody></voice></speak>".format(
                escape(voice), pitch, rate, escape(content)
            )
        )
        return ssml
