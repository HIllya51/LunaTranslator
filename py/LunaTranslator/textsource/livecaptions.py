from textsource.textsourcebase import basetext
import winrtutils, threading, time, os
from myutils.config import globalconfig


class livecaptions(basetext):

    def end(self):
        winrtutils.livecaption_stop(self.sem)

    def init(self) -> None:
        if not winrtutils.livecaption_isrunning():
            threading.Thread(target=os.system, args=("livecaptions.exe",)).start()
        self.curr = ""
        self.lastshow = ""
        self._kep = winrtutils.CFUNCTYPE(winrtutils.c_void_p, winrtutils.c_wchar_p)(
            self.callback
        )
        self.sem = winrtutils.livecaption_start(self._kep)
        self.lasttime = time.time()
        self.flashtime = time.time()
        self.lastflashstr = ""
        threading.Thread(target=self.delay).start()

    def xdispath(self, xx):
        if self.lastflashstr == xx:
            return
        self.lastflashstr = xx
        self.dispatchtext(xx)
        self.lasttime = self.flashtime = time.time()

    def delay(self):
        while not self.ending:
            time.sleep(0.01)
            if (
                time.time() - self.lasttime
                > globalconfig["livecaptions_maxwait"] / 1000
            ) or (
                time.time() - self.flashtime > globalconfig["livecaptions_delay"] / 1000
            ):
                self.xdispath(self.getlast(self.curr))

    def getlast(self, xx: str):
        return "\n".join(xx.splitlines()[-globalconfig["livecaptions_cachesentence"] :])

    def ___getlast(self, xx: str):
        savexx = xx
        __ = ""
        sheng = globalconfig["livecaptions_cachesentence"]
        while len(xx) and sheng:
            maxend = -1
            ck = None
            for _ in globalconfig["livecaptions_checkers"] + ["\n"]:
                rf = xx.rfind(_)
                if maxend < rf:
                    maxend = rf
                    ck = _
            if len(xx) > len(_) + maxend:
                sheng -= 1
            if ck:
                xx = xx[:maxend]
                __ = _
        return savexx[len(xx + __) :]

    def callback(self, xx: str):
        self.flashtime = time.time()
        self.curr = xx

    def gettextonce(self):
        self.lasttime = self.flashtime = time.time()
        xx = self.getlast(self.curr)
        self.lastflashstr = xx
        return xx
