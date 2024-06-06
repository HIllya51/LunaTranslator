from ctypes import (
    c_uint,
    c_bool,
    POINTER,
    c_char_p,
    c_uint64,
    c_wchar_p,
    pointer,
    CDLL,
    c_int,
    Structure,
    c_void_p,
    cast,
    memmove,
    create_unicode_buffer,
    create_string_buffer,
    c_size_t,
    windll,
    c_float,
    c_double,
    c_char,
    CFUNCTYPE,
)
from ctypes.wintypes import WORD, HANDLE, HWND, LONG, DWORD, RECT, BYTE
from windows import WINDOWPLACEMENT
import gobject, csv

utilsdll = CDLL(gobject.GetDllpath(("winsharedutils32.dll", "winsharedutils64.dll")))

_freewstringlist = utilsdll.freewstringlist
_freewstringlist.argtypes = POINTER(c_wchar_p), c_uint
_free_all = utilsdll.free_all
_free_all.argtypes = (c_void_p,)
_freestringlist = utilsdll.freestringlist
_freestringlist.argtypes = POINTER(c_char_p), c_uint

_SetProcessMute = utilsdll.SetProcessMute
_SetProcessMute.argtypes = c_uint, c_bool

_GetProcessMute = utilsdll.GetProcessMute
_GetProcessMute.restype = c_bool

_SAPI_List = utilsdll.SAPI_List
_SAPI_List.argtypes = (
    c_uint,
    POINTER(c_uint64),
)
_SAPI_List.restype = POINTER(c_wchar_p)


_SAPI_Speak = utilsdll.SAPI_Speak
_SAPI_Speak.argtypes = (
    c_wchar_p,
    c_uint,
    c_uint,
    c_uint,
    c_uint,
    POINTER(c_int),
    POINTER(c_void_p),
)
_SAPI_Speak.restype = c_bool


_levenshtein_distance = utilsdll.levenshtein_distance
_levenshtein_distance.argtypes = c_uint, c_wchar_p, c_uint, c_wchar_p
_levenshtein_distance.restype = c_uint  # 实际上应该都是size_t，但size_t 32位64位宽度不同，都用32位就行了，用int64会内存越界
levenshtein_ratio = utilsdll.levenshtein_ratio
levenshtein_ratio.argtypes = c_uint, c_wchar_p, c_uint, c_wchar_p
levenshtein_ratio.restype = c_double

_mecab_init = utilsdll.mecab_init
_mecab_init.argtypes = c_char_p, c_wchar_p
_mecab_init.restype = c_void_p

_mecab_parse = utilsdll.mecab_parse
_mecab_parse.argtypes = (
    c_void_p,
    c_char_p,
    POINTER(POINTER(c_char_p)),
    POINTER(POINTER(c_char_p)),
    POINTER(c_uint),
)
_mecab_parse.restype = c_bool

_mecab_end = utilsdll.mecab_end
_mecab_end.argtypes = (c_void_p,)

_clipboard_get = utilsdll.clipboard_get
_clipboard_get.restype = (
    c_void_p  # 实际上是c_wchar_p，但是写c_wchar_p 傻逼python自动转成str，没法拿到指针
)
_clipboard_set = utilsdll.clipboard_set
_clipboard_set.argtypes = (
    c_void_p,
    c_wchar_p,
)


def SetProcessMute(pid, mute):
    _SetProcessMute(pid, mute)


def GetProcessMute(pid):
    return _GetProcessMute(pid)


def SAPI_List(v):
    num = c_uint64()
    _list = _SAPI_List(v, pointer(num))
    ret = []
    for i in range(num.value):
        ret.append(_list[i])
    _freewstringlist(_list, num.value)
    return ret


def SAPI_Speak(content, v, voiceid, rate, volume):
    length = c_int()
    buff = c_void_p()
    succ = _SAPI_Speak(
        content, v, voiceid, int(rate), int(volume), pointer(length), pointer(buff)
    )
    if not succ:
        return None
    data = cast(buff, POINTER(c_char))[: length.value]
    c_free(buff)
    return data


def distance(
    s1, s2
):  # 词典更适合用编辑距离，因为就一两个字符，相似度会很小，预翻译适合用相似度
    return _levenshtein_distance(len(s1), s1, len(s2), s2)


def distance_ratio(s1, s2):
    return levenshtein_ratio(len(s1), s1, len(s2), s2)


class mecabwrap:
    def __init__(self, mecabpath) -> None:
        self.kks = _mecab_init(
            mecabpath.encode("utf8"), gobject.GetDllpath("libmecab.dll")
        )

    def __del__(self):
        _mecab_end(self.kks)

    def parse(self, text, codec):
        surface = POINTER(c_char_p)()
        feature = POINTER(c_char_p)()
        num = c_uint()
        succ = _mecab_parse(
            self.kks,
            text.encode(codec),
            pointer(surface),
            pointer(feature),
            pointer(num),
        )
        if not succ:
            raise Exception  # failed
        res = []
        for i in range(num.value):
            f = feature[i]
            fields = list(csv.reader([f.decode(codec)]))[0]
            res.append((surface[i].decode(codec), fields))
        _freestringlist(feature, num.value)
        _freestringlist(surface, num.value)
        return res


clphwnd = windll.user32.CreateWindowExW(0, "STATIC", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def clipboard_set(text):
    global clphwnd
    # _set_clip_board_queue.put(text)
    return _clipboard_set(clphwnd, text)


def clipboard_get():
    p = _clipboard_get()
    if p:
        v = cast(p, c_wchar_p).value
        _free_all(p)
        return v
    else:
        return ""


html_version = utilsdll.html_version
html_version.restype = DWORD
html_new = utilsdll.html_new
html_new.argtypes = (c_void_p,)
html_new.restype = c_void_p
html_navigate = utilsdll.html_navigate
html_navigate.argtypes = c_void_p, c_wchar_p
html_resize = utilsdll.html_resize
html_resize.argtypes = c_void_p, c_uint, c_uint, c_uint, c_uint
html_release = utilsdll.html_release
html_release.argtypes = (c_void_p,)
html_get_current_url = utilsdll.html_get_current_url
html_get_current_url.argtypes = c_void_p, c_wchar_p
html_set_html = utilsdll.html_set_html
html_set_html.argtypes = (
    c_void_p,
    c_wchar_p,
)


class HTMLBrowser:
    @staticmethod
    def version():
        return html_version()

    def __init__(self, parent) -> None:
        self.html = html_new(parent)

    def set_html(self, html):
        html_set_html(self.html, html)

    def resize(
        self,
        x,
        y,
        w,
        h,
    ):
        html_resize(self.html, x, y, w, h)

    def navigate(self, url):
        html_navigate(self.html, url)

    def get_current_url(self):
        w = create_unicode_buffer(65536)
        html_get_current_url(self.html, w)
        return w.value

    def __del__(self):
        html_release(self.html)


_GetLnkTargetPath = utilsdll.GetLnkTargetPath
_GetLnkTargetPath.argtypes = c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p


def GetLnkTargetPath(lnk):
    MAX_PATH = 260
    exe = create_unicode_buffer(MAX_PATH)
    arg = create_unicode_buffer(MAX_PATH)
    icon = create_unicode_buffer(MAX_PATH)
    dirp = create_unicode_buffer(MAX_PATH)
    _GetLnkTargetPath(lnk, exe, arg, icon, dirp)
    return exe.value, arg.value, icon.value, dirp.value


_otsu_binary = utilsdll.otsu_binary
_otsu_binary.argtypes = c_void_p, c_int


def otsu_binary(image, thresh):
    buf = create_string_buffer(len(image))
    memmove(buf, image, len(image))
    _otsu_binary(buf, thresh)
    return buf


_extracticon2data = utilsdll.extracticon2data
_extracticon2data.argtypes = c_wchar_p, POINTER(c_size_t)
_extracticon2data.restype = c_void_p


def extracticon2data(fname):
    length = c_size_t()
    datap = _extracticon2data(fname, pointer(length))
    if datap:
        save = create_string_buffer(length.value)
        memmove(save, datap, length.value)
        _free_all(datap)
        return save
    else:
        return None


c_free = utilsdll.c_free
c_free.argtypes = (c_void_p,)


_queryversion = utilsdll.queryversion
_queryversion.restype = c_bool
_queryversion.argtypes = (
    c_wchar_p,
    POINTER(WORD),
    POINTER(WORD),
    POINTER(WORD),
    POINTER(WORD),
)


def queryversion(exe):
    _1 = WORD()
    _2 = WORD()
    _3 = WORD()
    _4 = WORD()
    succ = _queryversion(exe, pointer(_1), pointer(_2), pointer(_3), pointer(_4))
    if succ:
        return _1.value, _2.value, _3.value, _4.value
    return None


startdarklistener = utilsdll.startdarklistener
startdarklistener.restype = HANDLE

_SetTheme = utilsdll._SetTheme
_SetTheme.argtypes = HWND, c_bool, c_int


def SetTheme(hwnd, dark, backdrop):
    _SetTheme(hwnd, dark, backdrop)


showintab = utilsdll.showintab
showintab.argtypes = HWND, c_bool


class windowstatus(Structure):
    _fields_ = [("wpc", WINDOWPLACEMENT), ("HWNDStyle", LONG), ("HWNDStyleEx", LONG)]


letfullscreen = utilsdll.letfullscreen
letfullscreen.argtypes = (HWND,)
letfullscreen.restype = windowstatus

recoverwindow = utilsdll.recoverwindow
recoverwindow.argtypes = HWND, windowstatus

pid_running = utilsdll.pid_running
pid_running.argtypes = (DWORD,)
pid_running.restype = c_bool

getpidhwndfirst = utilsdll.getpidhwndfirst
getpidhwndfirst.argtypes = (DWORD,)
getpidhwndfirst.restype = HWND

Is64bit = utilsdll.Is64bit
Is64bit.argtypes = (DWORD,)
Is64bit.restype = c_bool

isDark = utilsdll.isDark
isDark.restype = c_bool

startmaglistener = utilsdll.startmaglistener
startmaglistener.restype = HANDLE
endmaglistener = utilsdll.endmaglistener
endmaglistener.argtypes = (HANDLE,)

PlayAudioInMem = utilsdll.PlayAudioInMem
PlayAudioInMem.argtypes = (
    c_void_p,
    c_size_t,
    c_float,
    c_void_p,
    c_void_p,
    POINTER(c_float),
)
PlayAudioInMem.restype = c_int

PlayAudioInMem_Stop = utilsdll.PlayAudioInMem_Stop
PlayAudioInMem_Stop.argtypes = c_void_p, c_void_p

_gdi_screenshot = utilsdll.gdi_screenshot
_gdi_screenshot.argtypes = HWND, RECT, POINTER(c_size_t)
_gdi_screenshot.restype = POINTER(BYTE)


def gdi_screenshot(x1, y1, x2, y2, hwnd=None):
    sz = c_size_t()
    rect = RECT()
    rect.left = x1
    rect.top = y1
    rect.right = x2
    rect.bottom = y2
    bf = _gdi_screenshot(hwnd, rect, pointer(sz))
    if not (sz.value and bf):
        return None
    data = cast(bf, POINTER(c_char))[: sz.value]
    c_free(bf)
    return data


maximum_window = utilsdll.maximum_window
maximum_window.argtypes = (HWND,)

setAeroEffect = utilsdll.setAeroEffect
setAeroEffect.argtypes = (HWND,)
setAcrylicEffect = utilsdll.setAcrylicEffect
setAcrylicEffect.argtypes = (HWND,)
clearEffect = utilsdll.clearEffect
clearEffect.argtypes = (HWND,)

add_ZoomFactorChanged_CALLBACK = CFUNCTYPE(None, c_double)
add_ZoomFactorChanged = utilsdll.add_ZoomFactorChanged
add_ZoomFactorChanged.argtypes = (c_void_p, c_void_p)
add_ZoomFactorChanged.restype = c_void_p
remove_ZoomFactorChanged = utilsdll.remove_ZoomFactorChanged
remove_ZoomFactorChanged.argtypes = c_void_p, c_void_p
get_ZoomFactor = utilsdll.get_ZoomFactor
get_ZoomFactor.argtypes = (c_void_p,)
get_ZoomFactor.restype = c_double
put_ZoomFactor = utilsdll.put_ZoomFactor
put_ZoomFactor.argtypes = c_void_p, c_double

clipboard_callback = utilsdll.clipboard_callback
clipboard_callback.argtypes = (c_void_p,)
clipboard_callback.restype = HWND
clipboard_callback_stop = utilsdll.clipboard_callback_stop
clipboard_callback_stop.argtypes = (HWND,)
clipboard_callback_type = CFUNCTYPE(None, c_wchar_p, c_bool)
