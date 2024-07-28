import windows
import os, time
import gobject, uuid
from traceback import print_exc
from myutils.config import globalconfig, static_data
import threading
import winsharedutils
from ctypes import c_float, pointer, c_void_p

# miniaudio似乎有的时候会莫名崩溃，但我没遇到过。没办法只好恢复之前的mci了
# 但miniaudio的好处是不需要写硬盘，可以直接在内存里播放，mci必须写到文件里才能播放


class player_miniaudio:
    def stop(self, context):
        winsharedutils.PlayAudioInMem_Stop(context[0], context[1])

    def play(self, binary, volume):
        duration = c_float()
        device = c_void_p()
        decoder = c_void_p()
        succ = winsharedutils.PlayAudioInMem(
            binary,
            len(binary),
            volume / 100,
            pointer(decoder),
            pointer(device),
            pointer(duration),
        )
        if succ != 0:
            return 0
        context = decoder, device
        durationms = duration.value * 1000
        return durationms, context


class player_mci:
    def stop(self, context):
        i, lastfile, remove = context
        windows.mciSendString(("stop lunatranslator_mci_{}".format(i)))
        windows.mciSendString(("close lunatranslator_mci_{}".format(i)))
        if remove:
            os.remove(lastfile)

    def play(self, binaryorfile, volume):
        i = str(uuid.uuid4())
        if isinstance(binaryorfile, bytes):
            tgt = gobject.gettempdir(f"tts/{i}.wav")
            with open(tgt, "wb") as ff:
                ff.write(binaryorfile)
            remove = True
        elif isinstance(binaryorfile, str):
            tgt = binaryorfile
            remove = False
        context = (i, tgt, remove)
        windows.mciSendString(
            'open "{}" type mpegvideo  alias lunatranslator_mci_{}'.format(tgt, i)
        )
        durationms = int(
            windows.mciSendString("status lunatranslator_mci_{} length".format(i))
        )
        windows.mciSendString(
            "setaudio lunatranslator_mci_{} volume to {}".format(i, volume * 10)
        )
        windows.mciSendString(("play lunatranslator_mci_{}".format(i)))
        return durationms, context


class series_audioplayer:
    def __init__(self):
        self.i = 0
        self.lastfile = None
        self.tasks = None
        self.lock = threading.Lock()
        self.lock.acquire()
        self.lastplayer = None
        self.lastengine = None

        self.lastcontext = None
        threading.Thread(target=self.__dotasks).start()

    def play(self, binary, volume, force):
        try:
            self.tasks = (binary, volume, force)
            self.lock.release()
        except:
            pass

    def __maybeinitengine(self):
        using = globalconfig["audioengine"]
        supports = static_data["audioengine"]
        if using not in supports:
            using = supports[0]
        if using == self.lastengine:
            return
        self.lastplayer = {"mci": player_mci, "miniaudio": player_miniaudio}.get(
            using
        )()
        self.lastengine = using

    def __maybestoplast(self):
        if self.lastplayer and self.lastcontext:
            try:
                self.lastplayer.stop(self.lastcontext)
            except:
                print_exc()
        self.lastcontext = None

    def __playthis(self, binary, volume):
        try:
            durationms, self.lastcontext = self.lastplayer.play(binary, volume)
        except:
            durationms = 0
            self.lastcontext = None
        return durationms

    def __dotasks(self):
        durationms = 0
        try:
            while True:
                self.lock.acquire()
                task = self.tasks
                self.tasks = None
                if task is None:
                    continue
                binary, volume, force = task
                self.__maybestoplast()
                self.__maybeinitengine()
                durationms = self.__playthis(binary, volume)
                if durationms and globalconfig["ttsnointerrupt"]:
                    while durationms > 0:
                        durationms -= 100
                        time.sleep(0.1)
                        if self.tasks and self.tasks[-1]:
                            break
        except:
            print_exc()
