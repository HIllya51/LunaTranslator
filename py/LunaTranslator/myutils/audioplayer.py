import time
from traceback import print_exc
from myutils.config import globalconfig
import threading
import gobject, winsharedutils
from ctypes.wintypes import BOOL, DWORD, HWND, WORD
from ctypes import (
    WinDLL,
    WINFUNCTYPE,
    c_int,
    c_ulong,
    c_float,
    c_int64,
    c_void_p,
    c_char_p,
    Structure,
    POINTER,
    pointer,
    c_void_p,
    create_string_buffer,
    sizeof,
)


HMUSIC = c_ulong  # MOD music handle
HSAMPLE = c_ulong  # sample handle
HPLUGIN = c_ulong  # Plugin handle
QWORD = c_int64
HSTREAM = c_ulong  # sample stream handle
BASS_SAMPLE_FLOAT = 0x100
BASS_STREAM_DECODE = 0x200000
BASS_UNICODE = 0x80000000  # -2147483648
BASS_ATTRIB_VOL = 2
BASS_ATTRIB_FREQ = 1
BASS_SAMPLE_8BITS = 1
BASS_POS_BYTE = 0  # byte position
bass_module = WinDLL(gobject.GetDllpath("bass.dll"))

BASS_ChannelSetAttribute = WINFUNCTYPE(BOOL, DWORD, DWORD, c_float)(
    ("BASS_ChannelSetAttribute", bass_module)
)

BASS_ChannelGetLength = WINFUNCTYPE(QWORD, DWORD, DWORD)(
    ("BASS_ChannelGetLength", bass_module)
)
BASS_ChannelGetPosition = WINFUNCTYPE(QWORD, DWORD, DWORD)(
    ("BASS_ChannelGetPosition", bass_module)
)
BASS_ChannelPlay = WINFUNCTYPE(BOOL, DWORD, BOOL)(("BASS_ChannelPlay", bass_module))
BASS_StreamFree = WINFUNCTYPE(BOOL, HSTREAM)(("BASS_StreamFree", bass_module))
BASS_Init = WINFUNCTYPE(BOOL, c_int, DWORD, DWORD, HWND, c_void_p)(
    ("BASS_Init", bass_module)
)
BASS_StreamCreateFile = WINFUNCTYPE(HSTREAM, BOOL, c_void_p, QWORD, QWORD, DWORD)(
    ("BASS_StreamCreateFile", bass_module)
)
BASS_Free = WINFUNCTYPE(BOOL)(("BASS_Free", bass_module))
BASS_PluginLoad = WINFUNCTYPE(c_ulong, c_char_p, c_ulong)(
    ("BASS_PluginLoad", bass_module)
)


class WAVEFORMATEX(Structure):
    _fields_ = [
        ("wFormatTag", WORD),
        ("nChannels", WORD),
        ("nSamplesPerSec", DWORD),
        ("nAvgBytesPerSec", DWORD),
        ("nBlockAlign", WORD),
        ("wBitsPerSample", WORD),
        ("cbSize", WORD),
    ]


class BASS_CHANNELINFO(Structure):
    _fields_ = [
        ("freq", DWORD),
        ("chans", DWORD),
        ("flags", DWORD),
        ("ctype", DWORD),
        ("origres", DWORD),
        ("plugin", HPLUGIN),
        ("sample", HSAMPLE),
        ("filename", c_char_p),
    ]


BASS_ChannelGetInfo = WINFUNCTYPE(BOOL, DWORD, POINTER(BASS_CHANNELINFO))(
    ("BASS_ChannelGetInfo", bass_module)
)
BASS_ChannelIsActive = WINFUNCTYPE(DWORD, DWORD)(("BASS_ChannelIsActive", bass_module))
BASS_ChannelGetData = WINFUNCTYPE(DWORD, DWORD, c_void_p, DWORD)(
    ("BASS_ChannelGetData", bass_module)
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
plugins = {".spx": "bass_spx.dll", ".aac": "bass_aac.dll"}

pluginshandle = {}


def load_ext(ext=None):
    if ext and plugins.get(ext) and not pluginshandle.get(ext):
        pluginshandle[ext] = BASS_PluginLoad(
            gobject.GetDllpath(plugins.get(ext)).encode("utf8"), 0
        )


def bass_decode(bs, ext=None):
    load_ext(ext)
    stream = BASS_StreamCreateFile(True, bs, 0, len(bs), BASS_STREAM_DECODE)
    if not stream:
        return
    info = BASS_CHANNELINFO()
    if not BASS_ChannelGetInfo(stream, pointer(info)):
        return
    wf = WAVEFORMATEX()
    wf.wFormatTag = 1
    wf.nChannels = info.chans
    wf.wBitsPerSample = 8 if info.flags & BASS_SAMPLE_8BITS else 16
    wf.nBlockAlign = wf.nChannels * wf.wBitsPerSample // 8
    wf.nSamplesPerSec = info.freq
    wf.nAvgBytesPerSec = wf.nSamplesPerSec * wf.nBlockAlign
    res = []
    size = 0
    buff = create_string_buffer(0x10000)
    while BASS_ChannelIsActive(stream):
        get = BASS_ChannelGetData(stream, buff, 0x10000)
        res.append(buff[:get])
        size += get
    header = []
    header.append(b"RIFF")
    header.append(bytes(c_int(size + 44)))
    header.append(b"WAVE")
    header.append(b"fmt ")
    header.append(bytes(c_int(sizeof(WAVEFORMATEX))))
    header.append(bytes(wf))
    header.append(b"data")
    header.append(bytes(c_int(size)))
    header.extend(res)
    data = b"".join(header)
    return winsharedutils.encodemp3(data, 64)


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
        threading.Thread(target=self.__dotasks).start()

    def stop(self):
        self.timestamp = None
        try:
            self.tasks = (None, 0, True)
            self.lock.release()
        except:
            pass

    def play(self, binary, volume=100, force=False, timestamp=None, ext=None):
        if timestamp and (timestamp != self.timestamp):
            return
        self.timestamp = timestamp
        load_ext(ext)
        try:
            self.tasks = (binary, volume, force)
            self.lock.release()
        except:
            pass

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
