import time
from traceback import print_exc
from myutils.config import globalconfig
from myutils.wrapper import threader
import threading, types
import NativeUtils


class playonce:
    @threader
    def ___push_data_thread(self, handle, data: "types.GeneratorType[bytes]"):
        for d in data:
            if not NativeUtils.bass_stream_push_data(handle, d, len(d)):
                break
        NativeUtils.bass_stream_push_data(handle, None, 0)

    def __init__(self, fileormem, volume) -> None:
        self.handle = 0
        self.__play(fileormem, volume)

    def __del__(self):
        self.__stop()

    @property
    def isplaying(self):
        return NativeUtils.bass_handle_isplaying(self.handle)

    def __play(self, data: "bytes | str | types.GeneratorType[bytes]", volume):
        if isinstance(data, (bytes, str)):
            handle = NativeUtils.bass_handle_create(
                data, len(data), isinstance(data, bytes)
            )
        elif isinstance(data, types.GeneratorType):
            d = next(data)
            handle = NativeUtils.bass_stream_handle_create(d, len(d))
            self.___push_data_thread(handle, data)

        if not NativeUtils.bass_handle_play(handle, volume):
            return
        self.handle = handle

    def __stop(self):
        _ = self.handle
        self.handle = 0
        NativeUtils.bass_handle_free(_)


def bass_code_cast(bs, fr="mp3"):
    # fr没啥用，仅用来给出编码失败时的用来占位的后缀，以少写代码
    to = globalconfig["audioformat"]
    ret = NativeUtils.bass_code_cast(
        bs, to, globalconfig["mp3kbps"], globalconfig["opusbitrate"]
    )
    if not ret:
        return bs, fr
    ext = {"mp3": "mp3", "opus": "ogg"}[to]
    return ret, ext


class series_audioplayer:
    def __init__(self, playovercallback=None):
        self.i = 0
        self.playovercallback = playovercallback
        self.lastfile = None
        self.tasks = None
        self.lock = threading.Lock()
        self.lock.acquire()
        self.timestamp = None
        self.lastcontext = None
        self.__dotasks()

    def stop(self):
        self.timestamp = None
        try:
            self.tasks = (None, 0, True)
            self.lock.release()
        except:
            pass

    def play(self, binary, volume=100, force=False, timestamp=None):
        if timestamp and (timestamp != self.timestamp):
            return
        self.timestamp = timestamp
        try:
            self.tasks = (binary, volume, force)
            self.lock.release()
        except:
            pass

    @threader
    def __dotasks(self):
        try:
            while True:
                self.lock.acquire()
                task = self.tasks
                self.tasks = None
                if task is None:
                    continue
                binary, volume, force = task
                _playonce = None
                if not binary:
                    continue
                _playonce = playonce(binary, volume)
                while _playonce.isplaying:
                    time.sleep(0.1)
                    if self.tasks and not (
                        globalconfig["ttsnointerrupt"] and (not self.tasks[-1])
                    ):
                        break
                else:
                    if self.playovercallback:
                        self.playovercallback()
        except:
            print_exc()
