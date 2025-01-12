from myutils.config import globalconfig
import functools, threading
from myutils.wrapper import threader
from traceback import print_exc
from myutils.proxy import getproxy
from myutils.utils import LRUCache
from myutils.commonbase import commonbase



class SpeechParam:
    def __init__(self, speed, pitch):
        self.speed = speed
        self.pitch = pitch


class TTSbase(commonbase):
    def init(self): ...
    def getvoicelist(self):
        # 分别返回内部标识名,显示
        return [], []

    def speak(self, content, voice, param: SpeechParam):
        return None  # fname ,若为None则是不需要文件直接朗读

    ####################
    @property
    def arg_not_sup(self):
        return globalconfig["reader"][self.typename].get("arg_not_sup", [])

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
        _v = self.privateconfig["voice"]
        if isinstance(self.voicelist[0], tuple):
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
        self.LRUCache = LRUCache(3)
        if privateconfig is None:
            self.privateconfig = globalconfig["reader"][self.typename]
        else:
            self.privateconfig = privateconfig
        self.voicelist, self.voiceshowlist = self.getvoicelist()
        if len(self.voicelist) != len(self.voiceshowlist):
            raise
        if len(self.voicelist) == 0:
            raise
        if init:
            self.init()

    def read(self, content, force=False, timestamp=None):

        def _(force, volume, timestamp, data):
            self.playaudiofunction(data, volume, force, timestamp)

        self.ttscallback(content, functools.partial(_, force, self.volume, timestamp))

    @threader
    def ttscallback(self, content, callback):

        if len(content) == 0:
            return
        if len(self.voicelist) == 0:
            return
        try:
            key = content, self.voice, self.param
            data = self.LRUCache.get(key)
            if data:
                return callback(data)
            data = self.speak(content, self.voice, self.param)
            if data:
                callback(data)
                self.LRUCache.put(key, data)
        except:
            print_exc()
            return
