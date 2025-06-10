import time
from traceback import print_exc
from myutils.config import globalconfig
from myutils.wrapper import threader
import threading, functools
import gobject
from ctypes.wintypes import BOOL, DWORD, HWND
from ctypes import (
    WinDLL,
    WINFUNCTYPE,
    c_int,
    c_float,
    c_int64,
    c_void_p,
    c_char_p,
    POINTER,
    c_void_p,
    create_string_buffer,
    c_wchar_p,
    c_char,
)

HENCODE = DWORD
HMUSIC = DWORD  # MOD music handle
HSAMPLE = DWORD  # sample handle
HPLUGIN = DWORD  # Plugin handle
QWORD = c_int64
HSTREAM = DWORD  # sample stream handle
BASS_SAMPLE_FLOAT = 0x100
BASS_STREAM_DECODE = 0x200000
BASS_UNICODE = 0x80000000  # -2147483648
BASS_ATTRIB_VOL = 2
BASS_ATTRIB_FREQ = 1
BASS_SAMPLE_8BITS = 1
BASS_POS_BYTE = 0  # byte position
bass = WinDLL(gobject.GetDllpath("bass.dll"))

BASS_ChannelSetAttribute = WINFUNCTYPE(BOOL, DWORD, DWORD, c_float)(
    ("BASS_ChannelSetAttribute", bass)
)

BASS_ChannelGetLength = WINFUNCTYPE(QWORD, DWORD, DWORD)(
    ("BASS_ChannelGetLength", bass)
)
BASS_ChannelGetPosition = WINFUNCTYPE(QWORD, DWORD, DWORD)(
    ("BASS_ChannelGetPosition", bass)
)
BASS_ChannelPlay = WINFUNCTYPE(BOOL, DWORD, BOOL)(("BASS_ChannelPlay", bass))
BASS_StreamFree = WINFUNCTYPE(BOOL, HSTREAM)(("BASS_StreamFree", bass))
BASS_Init = WINFUNCTYPE(BOOL, c_int, DWORD, DWORD, HWND, c_void_p)(("BASS_Init", bass))
BASS_StreamCreateFile = WINFUNCTYPE(HSTREAM, BOOL, c_void_p, QWORD, QWORD, DWORD)(
    ("BASS_StreamCreateFile", bass)
)
BASS_Free = WINFUNCTYPE(BOOL)(("BASS_Free", bass))
BASS_PluginLoad = WINFUNCTYPE(HPLUGIN, c_char_p, DWORD)(("BASS_PluginLoad", bass))

bassenc = WinDLL(gobject.GetDllpath("bassenc.dll"))

BASS_Encode_IsActive = WINFUNCTYPE(DWORD, DWORD)(("BASS_Encode_IsActive", bassenc))
BASS_Encode_Stop = WINFUNCTYPE(BOOL, DWORD)(("BASS_Encode_Stop", bassenc))

BASS_ChannelIsActive = WINFUNCTYPE(DWORD, DWORD)(("BASS_ChannelIsActive", bass))
BASS_ChannelGetData = WINFUNCTYPE(DWORD, DWORD, c_void_p, DWORD)(
    ("BASS_ChannelGetData", bass)
)


class playonce:
    def __init__(self, fileormem, volume) -> None:
        self.handle = None
        self.channel_length = 0
        self.__play(fileormem, volume)

    def __del__(self):
        self.__stop()

    @property
    def isplaying(self):
        if not self.handle:
            return False
        if not self.channel_length:
            return False
        if self.channel_length == -1:
            return False
        channel_position = BASS_ChannelGetPosition(self.handle, BASS_POS_BYTE)
        if channel_position == -1:
            return False
        return channel_position < self.channel_length

    def __play(self, fileormem, volume):
        if isinstance(fileormem, bytes):
            handle = BASS_StreamCreateFile(True, fileormem, 0, len(fileormem), 0)
        else:
            handle = BASS_StreamCreateFile(False, fileormem, 0, 0, BASS_UNICODE)
        if not handle:
            return

        BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, volume / 100)
        if not BASS_ChannelPlay(handle, False):
            return
        channel_length = BASS_ChannelGetLength(handle, BASS_POS_BYTE)
        self.channel_length = channel_length
        self.handle = handle

    def __stop(self):
        _ = self.handle
        if not _:
            return
        self.handle = None
        BASS_StreamFree(_)


BASS_Init(-1, 44100, 0, 0, 0)
# https://www.un4seen.com/
plugins = ["bass_spx.dll", "bass_aac.dll", "bassopus.dll"]
for _ in plugins:
    BASS_PluginLoad(gobject.GetDllpath(_).encode("utf8"), 0)


def ENCODEPROCEXF(ret: list, _, _1, buffer, size, _2, _3):
    ret.append(buffer[:size])


def ENCODEPROCF(ret: list, _, _1, buffer, size, _2):
    ret.append(buffer[:size])


ENCODEPROC = WINFUNCTYPE(None, HENCODE, DWORD, POINTER(c_char), DWORD, c_void_p)
ENCODEPROCEX = WINFUNCTYPE(None, HENCODE, DWORD, POINTER(c_char), DWORD, QWORD, c_void_p)
encoders = {
    "mp3": [
        "bassenc_mp3.dll",
        "BASS_Encode_MP3_Start",
        "mp3",
        ENCODEPROCEXF,
        ENCODEPROCEX,
    ],
    "opus": [
        "bassenc_opus.dll",
        "BASS_Encode_OPUS_Start",
        "ogg",
        ENCODEPROCF,
        ENCODEPROC,
    ],
}
BASS_Encode_Start_T = WINFUNCTYPE(HENCODE, DWORD, c_wchar_p, DWORD, c_void_p, c_void_p)


def load_enc_func(ext):
    _ = encoders.get(ext)
    if not _:
        return None
    dll, fun = _[0], _[1]
    if isinstance(dll, str):
        dll = WinDLL(gobject.GetDllpath(dll))
        _[0] = dll
    if isinstance(fun, str):
        fun = BASS_Encode_Start_T((fun, dll))
        _[1] = fun
    return _


def bass_code_cast(bs, fr="mp3"):
    # fr没啥用，仅用来给出编码失败时的用来占位的后缀，以少写代码
    to = globalconfig["audioformat"]
    _ = load_enc_func(to)
    if not _:
        return bs, fr
    _, start, ext, func, funct = _
    stream = BASS_StreamCreateFile(True, bs, 0, len(bs), BASS_STREAM_DECODE)
    if not stream:
        return bs, fr
    ret = []
    func = funct(functools.partial(func, ret))
    if to == "mp3":
        opts = "-b{}".format(globalconfig["mp3kbps"])
    elif to == "opus":
        opts = "--bitrate {}".format(globalconfig["opusbitrate"])
    encoder = start(stream, opts, BASS_UNICODE, func, None)
    if not encoder:
        BASS_StreamFree(stream)
        return bs, fr
    buff = create_string_buffer(0x10000)  # wav，仅用于激活getdata
    while BASS_ChannelIsActive(stream):
        if not BASS_Encode_IsActive(stream):
            break
        _ = BASS_ChannelGetData(stream, buff, 0x10000)
    BASS_Encode_Stop(stream)
    BASS_StreamFree(stream)
    return b"".join(ret), ext


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