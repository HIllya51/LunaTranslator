from ctypes import (
    c_uint,
    c_bool,
    POINTER,
    c_char_p,
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
    c_long,
)
from ctypes.wintypes import WORD, HANDLE, HWND, LONG, DWORD, RECT
from windows import WINDOWPLACEMENT
import gobject

utilsdll = CDLL(gobject.GetDllpath(("winsharedutils32.dll", "winsharedutils64.dll")))


_SetProcessMute = utilsdll.SetProcessMute
_SetProcessMute.argtypes = c_uint, c_bool

_GetProcessMute = utilsdll.GetProcessMute
_GetProcessMute.restype = c_bool

_SAPI_List = utilsdll.SAPI_List
_SAPI_List.argtypes = (c_uint, c_void_p)

_SAPI_Speak = utilsdll.SAPI_Speak
_SAPI_Speak.argtypes = (c_wchar_p, c_uint, c_uint, c_uint, c_uint, c_void_p)
_SAPI_Speak.restype = c_bool


_levenshtein_distance = utilsdll.levenshtein_distance
_levenshtein_distance.argtypes = c_uint, c_wchar_p, c_uint, c_wchar_p
_levenshtein_distance.restype = c_uint  # 实际上应该都是size_t，但size_t 32位64位宽度不同，都用32位就行了，用int64会内存越界
levenshtein_ratio = utilsdll.levenshtein_ratio
levenshtein_ratio.argtypes = c_uint, c_wchar_p, c_uint, c_wchar_p
levenshtein_ratio.restype = c_double

mecab_init = utilsdll.mecab_init
mecab_init.argtypes = c_char_p, c_wchar_p
mecab_init.restype = c_void_p

mecab_parse = utilsdll.mecab_parse
mecab_parse.argtypes = (c_void_p, c_char_p, c_void_p)
mecab_parse.restype = c_bool

mecab_end = utilsdll.mecab_end
mecab_end.argtypes = (c_void_p,)

_clipboard_get = utilsdll.clipboard_get
_clipboard_get.argtypes = (c_void_p,)
_clipboard_get.restype = c_bool
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
    ret = []
    _SAPI_List(v, CFUNCTYPE(None, c_wchar_p)(ret.append))
    return ret


def SAPI_Speak(content, v, voiceid, rate, volume):
    ret = []

    def _cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    succ = _SAPI_Speak(
        content,
        v,
        voiceid,
        int(rate),
        int(volume),
        CFUNCTYPE(None, c_void_p, c_size_t)(_cb),
    )
    if not succ:
        return None
    return ret[0]


def distance(
    s1, s2
):  # 词典更适合用编辑距离，因为就一两个字符，相似度会很小，预翻译适合用相似度
    return _levenshtein_distance(len(s1), s1, len(s2), s2)


def distance_ratio(s1, s2):
    return levenshtein_ratio(len(s1), s1, len(s2), s2)


clphwnd = windll.user32.CreateWindowExW(0, "STATIC", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def clipboard_set(text):
    global clphwnd
    # _set_clip_board_queue.put(text)
    return _clipboard_set(clphwnd, text)


def clipboard_get():
    ret = []
    if not _clipboard_get(CFUNCTYPE(None, c_wchar_p)(ret.append)):
        return ""
    return ret[0]


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
_extracticon2data.argtypes = c_wchar_p, c_void_p
_extracticon2data.restype = c_bool


def extracticon2data(fname):
    ret = []

    def cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    succ = _extracticon2data(fname, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
    if not succ:
        return None
    return ret[0]


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


def collect_running_pids(pids):
    _ = []
    for __ in pids:
        if not pid_running(__):
            continue
        _.append(__)
    return _


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
_gdi_screenshot.argtypes = HWND, RECT, c_void_p
_gdi_screenshot.restype = c_bool


def gdi_screenshot(x1, y1, x2, y2, hwnd=None):
    rect = RECT()
    rect.left = x1
    rect.top = y1
    rect.right = x2
    rect.bottom = y2
    ret = []

    def cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    bf = _gdi_screenshot(hwnd, rect, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
    if not bf:
        return None
    return ret[0]


maximum_window = utilsdll.maximum_window
maximum_window.argtypes = (HWND,)

setAeroEffect = utilsdll.setAeroEffect
setAeroEffect.argtypes = (HWND, c_bool)
setAcrylicEffect = utilsdll.setAcrylicEffect
setAcrylicEffect.argtypes = (HWND, c_bool)
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
put_PreferredColorScheme = utilsdll.put_PreferredColorScheme
put_PreferredColorScheme.argtypes = c_void_p, c_int
put_PreferredColorScheme.restype = c_long
set_transparent_background = utilsdll.set_transparent_background
set_transparent_background.argtypes = (c_void_p,)


clipboard_callback = utilsdll.clipboard_callback
clipboard_callback.argtypes = (c_void_p,)
clipboard_callback.restype = HWND
clipboard_callback_stop = utilsdll.clipboard_callback_stop
clipboard_callback_stop.argtypes = (HWND,)
clipboard_callback_type = CFUNCTYPE(None, c_wchar_p, c_bool)
