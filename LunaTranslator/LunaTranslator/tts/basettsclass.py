from myutils.config import globalconfig
import functools, threading
from myutils.wrapper import threader
from traceback import print_exc
from myutils.proxy import getproxy
from myutils.utils import LRUCache


class TTSbase:
    typename = None

    def init(self): ...
    def getvoicelist(self):
        # 分别返回内部标识名,显示
        return [], []

    def speak(self, content, rate, voice):
        return None  # fname ,若为None则是不需要文件直接朗读

    ####################
    # 一些可能需要的属性
    @property
    def proxy(self):
        return getproxy(("reader", self.typename))

    @property
    def config(self):
        return globalconfig["reader"][self.typename]["args"]

    @property
    def volume(self):
        return globalconfig["ttscommon"]["volume"]

    @property
    def rate(self):
        return globalconfig["ttscommon"]["rate"]

    @property
    def voice(self):
        _v = self.privateconfig["voice"]
        if _v not in self.voicelist:
            _v = self.voicelist[0]
        return _v

    @voice.setter
    def voice(self, v):
        self.privateconfig["voice"] = v

    ########################

    def __init__(
        self, typename, playaudiofunction, privateconfig=None, init=True, uid=None
    ) -> None:
        self.typename = typename
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

    def read(self, content, force=False):

        def _(force, volume, data):
            self.playaudiofunction(data, volume, force)

        self.ttscallback(content, functools.partial(_, force, self.volume))

    @threader
    def ttscallback(self, content, callback):

        if len(content) == 0:
            return
        if len(self.voicelist) == 0:
            return
        try:
            key = content, self.rate, self.voice
            data = self.LRUCache.get(key)
            if data:
                return callback(data)
            data = self.speak(content, self.rate, self.voice)
            if data:
                callback(data)
                self.LRUCache.put(key, data)
        except:
            print_exc()
            return
