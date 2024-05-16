from myutils.config import globalconfig
import threading, os, functools
from myutils.wrapper import threader
from traceback import print_exc

class TTSbase:
    def init(self):
        pass

    def getvoicelist(self):
        return []

    def voiceshowmap(self, voice):
        return voice

    def speak(self, content, rate, volume, voice, voiceindex):
        return None  # fname ,若为None则是不需要文件直接朗读

    ####################
    # 一些可能需要的属性
    @property
    def config(self):
        return self.privateconfig["args"]

    @property
    def privateconfig(self):
        return globalconfig["reader"][self.typename]

    @property
    def publicconfig(self):
        return globalconfig["ttscommon"]

    ########################

    def __init__(self, typename, showlistsignal, mp3playsignal) -> None:
        self.typename = typename
        self.showlistsignal = showlistsignal
        self.mp3playsignal = mp3playsignal
        self.loadok = False

        def _():
            self.init()
            self.voicelist = self.getvoicelist()
            self.voiceshowlist = []
            for k in self.voicelist:
                try:
                    _v = self.voiceshowmap(k)
                except:
                    _v = k
                self.voiceshowlist.append(_v)
            if self.privateconfig["voice"] not in self.voicelist:
                self.privateconfig["voice"] = self.voicelist[0]

            showlistsignal.emit(
                self.voiceshowlist,
                self.voicelist.index(self.privateconfig["voice"]),
            )
            self.loadok = True

        threading.Thread(target=_).start()

    def read(self, content, force=False):
        def _(force, fname):
            volume = self.publicconfig["volume"]
            self.mp3playsignal.emit(fname, volume, force)

        self.ttscallback(content, functools.partial(_, force))

    @threader
    def ttscallback(self, content, callback):
        if self.loadok == False:
            return
        if len(content) == 0:
            return
        if len(self.voicelist) == 0:
            return

        rate = self.publicconfig["rate"]
        voice = self.privateconfig["voice"]
        voice_index = self.voicelist.index(voice)
        try:
            fname = self.speak(content, rate, voice, voice_index)
            if fname:
                callback(os.path.abspath(fname))
        except:
            print_exc()
            return
