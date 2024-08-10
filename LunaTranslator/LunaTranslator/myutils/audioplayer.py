import time
from traceback import print_exc
from myutils.config import globalconfig
import threading
import gobject
from ctypes.wintypes import BOOL, DWORD, HWND
from ctypes import (
    WinDLL,
    WINFUNCTYPE,
    c_int,
    c_ulong,
    c_float,
    c_int64,
    c_void_p,
    c_double,
)


HMUSIC = c_ulong  # MOD music handle
HSAMPLE = c_ulong  # sample handle
HPLUGIN = c_ulong  # Plugin handle
QWORD = c_int64
HSTREAM = c_ulong  # sample stream handle

BASS_UNICODE = 0x80000000  # -2147483648
BASS_ATTRIB_VOL = 2
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
        channel_position = BASS_ChannelGetPosition(self.handle, BASS_POS_BYTE)
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


class series_audioplayer:
    def __init__(self):
        self.i = 0
        self.lastfile = None
        self.tasks = None
        self.lock = threading.Lock()
        self.lock.acquire()

        self.lastcontext = None
        threading.Thread(target=self.__dotasks).start()

    def play(self, binary, volume, force):
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
                _playonce = playonce(binary, volume)
                if globalconfig["ttsnointerrupt"]:
                    while _playonce.isplaying:
                        time.sleep(0.1)
                        if self.tasks and self.tasks[-1]:
                            break
        except:
            print_exc()
