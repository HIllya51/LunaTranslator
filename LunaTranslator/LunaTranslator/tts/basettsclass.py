from myutils.config import globalconfig
import functools, threading
from myutils.wrapper import threader
from traceback import print_exc
from myutils.proxy import getproxy


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
        if len(self.voicelist) == 0:
            return None
        if _v not in self.voicelist:
            _v = self.voicelist[0]
        return _v

    ########################

    def __init__(
        self,
        typename,
        voicelistsignal,
        playaudiofunction,
        privateconfig=None,
        init=True,
    ) -> None:
        self.typename = typename
        self.voicelistsignal = voicelistsignal
        self.playaudiofunction = playaudiofunction

        if privateconfig is None:
            self.privateconfig = globalconfig["reader"][self.typename]
        else:
            self.privateconfig = privateconfig
        self.voicelist, self.voiceshowlist = self.getvoicelist()
        voicelistsignal.emit(self)
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
            data = self.speak(content, self.rate, self.voice)
            if data and len(data):
                callback(data)
        except:
            print_exc()
            return


def getvisidx(obj: TTSbase):
    if obj is None:
        vl = []
        idx = -1
    else:
        vl = obj.voiceshowlist
        if obj.voice:
            idx = obj.voicelist.index(obj.voice)
        else:
            idx = -1
    return vl, idx
