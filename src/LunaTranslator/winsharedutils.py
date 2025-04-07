from ctypes import (
    c_uint,
    c_bool,
    POINTER,
    c_char_p,
    c_wchar_p,
    pointer,
    CDLL,
    c_int,
    c_void_p,
    cast,
    create_unicode_buffer,
    create_string_buffer,
    c_size_t,
    c_double,
    c_char,
    CFUNCTYPE,
)
from ctypes.wintypes import (
    WORD,
    HWND,
    DWORD,
    RECT,
    HANDLE,
    UINT,
    BOOL,
    LONG,
    LPCWSTR,
    MAX_PATH,
)
import platform, windows, functools, os, re

isbit64 = platform.architecture()[0] == "64bit"
utilsdll = CDLL(
    os.path.join(
        os.path.abspath("files/plugins/DLL" + ("32", "64")[isbit64]),
        "winsharedutils.dll",
    )
)

OpenFileEx = utilsdll.OpenFileEx
OpenFileEx.argtypes = (LPCWSTR,)
SetCurrProcessMute = utilsdll.SetCurrProcessMute
SetCurrProcessMute.argtypes = (c_bool,)
MonitorPidVolume = utilsdll.MonitorPidVolume
MonitorPidVolume.argtypes = (DWORD,)
MonitorPidVolume_callback_t = CFUNCTYPE(None, BOOL)
StartMonitorVolume = utilsdll.StartMonitorVolume
StartMonitorVolume.argtypes = (MonitorPidVolume_callback_t,)
_SAPI_List = utilsdll.SAPI_List
_SAPI_List.argtypes = (c_uint, c_void_p)

_SAPI_Speak = utilsdll.SAPI_Speak
_SAPI_Speak.argtypes = (c_wchar_p, c_uint, c_uint, c_uint, c_uint, c_void_p)
_SAPI_Speak.restype = c_bool


levenshtein_distance = utilsdll.levenshtein_distance
levenshtein_distance.argtypes = c_size_t, c_wchar_p, c_size_t, c_wchar_p
levenshtein_distance.restype = c_size_t
levenshtein_normalized_similarity = utilsdll.levenshtein_normalized_similarity
levenshtein_normalized_similarity.argtypes = c_size_t, c_wchar_p, c_size_t, c_wchar_p
levenshtein_normalized_similarity.restype = c_double

mecab_init = utilsdll.mecab_init
mecab_init.argtypes = (c_char_p,)
mecab_init.restype = c_void_p
mecab_parse_cb_a = CFUNCTYPE(None, c_char_p, c_char_p)
mecab_parse_cb_w = CFUNCTYPE(None, c_wchar_p, c_wchar_p)
mecab_parse = utilsdll.mecab_parse
mecab_parse.argtypes = (c_void_p, c_char_p, c_void_p)
mecab_parse.restype = c_bool
mecab_dictionary_codec = utilsdll.mecab_dictionary_codec
mecab_dictionary_codec.argtypes = (c_void_p,)
mecab_dictionary_codec.restype = c_char_p
mecab_end = utilsdll.mecab_end
mecab_end.argtypes = (c_void_p,)

_clipboard_get = utilsdll.clipboard_get
_clipboard_get.argtypes = (c_void_p,)
_clipboard_get.restype = c_bool
clipboard_set = utilsdll.clipboard_set
clipboard_set.argtypes = (c_wchar_p,)
_clipboard_set_image = utilsdll.clipboard_set_image
_clipboard_set_image.argtypes = (c_void_p, c_size_t)
_clipboard_set_image.restype = c_bool


def SAPI_List(v):
    ret = []
    _SAPI_List(v, CFUNCTYPE(None, c_wchar_p)(ret.append))
    return ret


def SAPI_Speak(content, v, voiceid, rate, volume):
    ret = []

    def _cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    fp = CFUNCTYPE(None, c_void_p, c_size_t)(_cb)
    succ = _SAPI_Speak(content, v, voiceid, int(rate), int(volume), fp)
    if not succ:
        return None
    return ret[0]


def distance(s1, s2):
    # 词典更适合用编辑距离，因为就一两个字符，相似度会很小，预翻译适合用相似度
    return levenshtein_distance(len(s1), s1, len(s2), s2)


def similarity(s1, s2):
    return levenshtein_normalized_similarity(len(s1), s1, len(s2), s2)


def clipboard_set_image(bytes_):
    return _clipboard_set_image(bytes_, len(bytes_))


def clipboard_get():
    ret = []
    if not _clipboard_get(CFUNCTYPE(None, c_wchar_p)(ret.append)):
        return ""
    return ret[0]


_GetLnkTargetPath = utilsdll.GetLnkTargetPath
_GetLnkTargetPath.argtypes = c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p


def GetLnkTargetPath(lnk):
    exe = create_unicode_buffer(MAX_PATH + 1)
    arg = create_unicode_buffer(MAX_PATH + 1)
    icon = create_unicode_buffer(MAX_PATH + 1)
    dirp = create_unicode_buffer(MAX_PATH + 1)
    _GetLnkTargetPath(lnk, exe, arg, icon, dirp)
    return exe.value, arg.value, icon.value, dirp.value


_extracticon2data = utilsdll.extracticon2data
_extracticon2data.argtypes = c_bool, c_wchar_p, c_void_p
_extracticon2data.restype = c_bool


def extracticon2data(file, large=False):

    file = windows.check_maybe_unc_file(file)
    if not file:
        return False
    ret = []

    def cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    succ = _extracticon2data(large, file, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
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


startclipboardlisten = utilsdll.startclipboardlisten
stopclipboardlisten = utilsdll.stopclipboardlisten
WindowMessageCallback_t = CFUNCTYPE(None, c_int, c_bool, c_wchar_p)
WinEventHookCALLBACK_t = CFUNCTYPE(None, DWORD, HWND, LONG)
globalmessagelistener = utilsdll.globalmessagelistener
globalmessagelistener.argtypes = (
    WinEventHookCALLBACK_t,
    WindowMessageCallback_t,
)
dispatchcloseevent = utilsdll.dispatchcloseevent

setdwmextendframe = utilsdll.setdwmextendframe
setdwmextendframe.argtypes = (HWND,)

SetTheme = utilsdll._SetTheme
SetTheme.argtypes = HWND, c_bool, c_int, c_bool


getprocesses = utilsdll.getprocesses
getprocesses.argtypes = (c_void_p,)


def Getprcesses():
    ret = []
    getprocesses(
        CFUNCTYPE(None, DWORD, c_wchar_p)(lambda pid, exe: ret.append((pid, exe)))
    )
    return ret


showintab = utilsdll.showintab
showintab.argtypes = HWND, c_bool, c_bool


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


_gdi_screenshot = utilsdll.gdi_screenshot
_gdi_screenshot.argtypes = HWND, c_void_p

_crop_image = utilsdll.crop_image
_crop_image.argtypes = HWND, RECT, c_void_p


def gdi_screenshot(hwnd):
    if windows.GetClassName(hwnd) == "UnityWndClass":
        return None
    ret = []

    def cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    _gdi_screenshot(hwnd, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
    if len(ret) == 0:
        return None
    return ret[0]


def crop_image(x1, y1, x2, y2, hwnd=None):
    rect = RECT()
    rect.left = x1
    rect.top = y1
    rect.right = x2
    rect.bottom = y2
    ret = []

    def cb(ptr, size):
        ret.append(cast(ptr, POINTER(c_char))[:size])

    if windows.GetClassName(hwnd) == "UnityWndClass":
        hwnd = None
    _crop_image(hwnd, rect, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
    if len(ret) == 0:
        return None
    return ret[0]


maximum_window = utilsdll.maximum_window
maximum_window.argtypes = (HWND,)
setbackdropX = utilsdll.setbackdropX
setbackdropX.argtypes = HWND, c_bool, c_bool
setAeroEffect = utilsdll.setAeroEffect
setAeroEffect.argtypes = (HWND, c_bool)
setAcrylicEffect = utilsdll.setAcrylicEffect
setAcrylicEffect.argtypes = (HWND, c_bool)
clearEffect = utilsdll.clearEffect
clearEffect.argtypes = (HWND,)


# MSHTML
MSHTMLptr = c_void_p
html_version = utilsdll.html_version
html_version.restype = DWORD
html_new = utilsdll.html_new
html_new.argtypes = (HWND,)
html_new.restype = MSHTMLptr
html_navigate = utilsdll.html_navigate
html_navigate.argtypes = MSHTMLptr, c_wchar_p
html_resize = utilsdll.html_resize
html_resize.argtypes = MSHTMLptr, c_uint, c_uint, c_uint, c_uint
html_release = utilsdll.html_release
html_release.argtypes = (MSHTMLptr,)
html_get_current_url = utilsdll.html_get_current_url
html_get_current_url.argtypes = (MSHTMLptr, c_void_p)
html_set_html = utilsdll.html_set_html
html_set_html.argtypes = (MSHTMLptr, c_wchar_p)
html_add_menu_gettext = CFUNCTYPE(c_wchar_p)
html_add_menu = utilsdll.html_add_menu
html_add_menu_cb = CFUNCTYPE(c_void_p, c_wchar_p)
html_add_menu.argtypes = (MSHTMLptr, c_int, c_void_p, c_void_p)
html_add_menu_noselect = utilsdll.html_add_menu_noselect
html_add_menu_cb2 = CFUNCTYPE(c_void_p)
html_add_menu_noselect.argtypes = (MSHTMLptr, c_int, c_void_p, c_void_p)
html_get_select_text = utilsdll.html_get_select_text
html_get_select_text_cb = CFUNCTYPE(None, c_wchar_p)
html_get_select_text.argtypes = (MSHTMLptr, c_void_p)
html_get_html = utilsdll.html_get_html
html_get_html.argtypes = (MSHTMLptr, c_void_p, c_wchar_p)
html_bind_function_FT = CFUNCTYPE(None, POINTER(c_wchar_p), c_int)
html_bind_function = utilsdll.html_bind_function
html_bind_function.argtypes = MSHTMLptr, c_wchar_p, html_bind_function_FT
html_check_ctrlc = utilsdll.html_check_ctrlc
html_check_ctrlc.argtypes = (MSHTMLptr,)
html_check_ctrlc.restype = c_bool
html_eval = utilsdll.html_eval
html_eval.argtypes = MSHTMLptr, c_wchar_p
# MSHTML

# WebView2
WebView2PTR = c_void_p
webview2_create = utilsdll.webview2_create
webview2_create.argtypes = (
    POINTER(WebView2PTR),
    HWND,
    c_bool,
    c_bool,
)
webview2_create.restype = LONG
webview2_destroy = utilsdll.webview2_destroy
webview2_destroy.argtypes = (WebView2PTR,)
webview2_resize = utilsdll.webview2_resize
webview2_resize.argtypes = WebView2PTR, c_int, c_int
webview2_add_menu_noselect = utilsdll.webview2_add_menu_noselect
webview2_add_menu_noselect_CALLBACK = CFUNCTYPE(None)
webview2_add_menu_noselect_getchecked = CFUNCTYPE(c_bool)
webview2_add_menu_noselect_getuse = CFUNCTYPE(c_bool)
webview2_contextmenu_gettext = CFUNCTYPE(c_wchar_p)
webview2_add_menu_noselect.argtypes = (
    WebView2PTR,
    c_int,
    c_void_p,
    c_void_p,
    c_bool,
    c_void_p,
    c_void_p,
)
webview2_add_menu = utilsdll.webview2_add_menu
webview2_add_menu_CALLBACK = CFUNCTYPE(None, c_wchar_p)
webview2_add_menu.argtypes = (
    WebView2PTR,
    c_int,
    c_void_p,
    c_void_p,
)
webview2_evaljs = utilsdll.webview2_evaljs
webview2_evaljs_CALLBACK = CFUNCTYPE(None, c_wchar_p)
webview2_evaljs.argtypes = WebView2PTR, c_wchar_p, c_void_p
webview2_set_observe_ptrs = utilsdll.webview2_set_observe_ptrs
webview2_zoomchange_callback_t = CFUNCTYPE(None, c_double)
webview2_navigating_callback_t = CFUNCTYPE(None, c_wchar_p, c_bool)
webview2_webmessage_callback_t = CFUNCTYPE(None, c_wchar_p)
webview2_FilesDropped_callback_t = CFUNCTYPE(None, c_wchar_p)
webview2_titlechange_callback_t = CFUNCTYPE(None, c_wchar_p)
webview2_IconChanged_callback_t = CFUNCTYPE(None, c_void_p, c_size_t)
webview2_set_observe_ptrs.argtypes = (
    WebView2PTR,
    webview2_zoomchange_callback_t,
    webview2_navigating_callback_t,
    webview2_webmessage_callback_t,
    webview2_FilesDropped_callback_t,
    webview2_titlechange_callback_t,
    webview2_IconChanged_callback_t,
)
webview2_bind = utilsdll.webview2_bind
webview2_bind.argtypes = WebView2PTR, c_wchar_p
webview2_navigate = utilsdll.webview2_navigate
webview2_navigate.argtypes = WebView2PTR, c_wchar_p
webview2_sethtml = utilsdll.webview2_sethtml
webview2_sethtml.argtypes = WebView2PTR, c_wchar_p
webview2_put_PreferredColorScheme = utilsdll.webview2_put_PreferredColorScheme
webview2_put_PreferredColorScheme.argtypes = WebView2PTR, c_int
webview2_put_ZoomFactor = utilsdll.webview2_put_ZoomFactor
webview2_put_ZoomFactor.argtypes = WebView2PTR, c_double
webview2_get_ZoomFactor = utilsdll.webview2_get_ZoomFactor
webview2_get_ZoomFactor.argtypes = (WebView2PTR,)
webview2_get_ZoomFactor.restype = c_double

_webview2_detect_version = utilsdll.webview2_detect_version
_webview2_detect_version.argtypes = c_wchar_p, c_void_p


def safe_int(s):
    match = re.search(r"\d+", s)
    if match:
        return int(match.group())
    else:
        return 0


def detect_webview2_version(directory=None):
    _ = []
    _f = CFUNCTYPE(c_void_p, c_wchar_p)(_.append)
    _webview2_detect_version(directory, _f)
    if _:
        # X.X.X.X beta
        return tuple(safe_int(_) for _ in _[0].split("."))


webview2_ext_add = utilsdll.webview2_ext_add
webview2_ext_add.argtypes = (c_wchar_p,)
webview2_ext_add.restype = LONG
webview2_list_ext_CALLBACK_T = CFUNCTYPE(None, c_wchar_p, c_wchar_p, BOOL)
webview2_ext_list = utilsdll.webview2_ext_list
webview2_ext_list.argtypes = (webview2_list_ext_CALLBACK_T,)
webview2_ext_list.restype = LONG
webview2_ext_enable = utilsdll.webview2_ext_enable
webview2_ext_enable.argtypes = (c_wchar_p, BOOL)
webview2_ext_enable.restype = LONG
webview2_ext_rm = utilsdll.webview2_ext_rm
webview2_ext_rm.argtypes = (c_wchar_p,)
webview2_ext_rm.restype = LONG
webview2_get_userdir = utilsdll.webview2_get_userdir
webview2_get_userdir_callback = CFUNCTYPE(None, c_wchar_p)
webview2_get_userdir.argtypes = (webview2_get_userdir_callback,)
# WebView2

# LoopBack
StartCaptureAsync_cb = CFUNCTYPE(None, c_void_p, c_size_t)
StartCaptureAsync = utilsdll.StartCaptureAsync
StartCaptureAsync.argtypes = (POINTER(c_void_p),)
StartCaptureAsync.restype = LONG
StopCaptureAsync = utilsdll.StopCaptureAsync
StopCaptureAsync.argtypes = (c_void_p, StartCaptureAsync_cb)


class loopbackrecorder:
    def __datacollect(self, ptr, size):
        self.data = cast(ptr, POINTER(c_char))[:size]

    def stop(self):
        __ = StartCaptureAsync_cb(self.__datacollect)
        StopCaptureAsync(self.ptr, __)
        self.ptr = None

    def __del__(self):
        self.stop()

    def __init__(self) -> None:
        self.data = None
        self.ptr = c_void_p()
        windows.CHECK_FAILURE(StartCaptureAsync(pointer(self.ptr)))


# LoopBack

check_window_viewable = utilsdll.check_window_viewable
check_window_viewable.argtypes = (HWND,)
check_window_viewable.restype = c_bool
_GetSelectedText = utilsdll.GetSelectedText
_GetSelectedText.argtypes = (c_void_p,)
_GetSelectedText.restype = c_bool


def GetSelectedText():
    ret = []
    support = _GetSelectedText(CFUNCTYPE(None, c_wchar_p)(ret.append))
    if not support:
        return None
    if len(ret):
        return ret[0]
    return ""


get_allAccess_ptr = utilsdll.get_allAccess_ptr
get_allAccess_ptr.restype = c_void_p
windows.CreateEvent = functools.partial(windows.CreateEvent, psecu=get_allAccess_ptr())
windows.CreateMutex = functools.partial(windows.CreateMutex, psecu=get_allAccess_ptr())

createprocess = utilsdll.createprocess
createprocess.argtypes = c_wchar_p, c_wchar_p, POINTER(DWORD)
createprocess.restype = HANDLE


class AutoKillProcess_:
    def __init__(self, handle, pid):
        self.handle = windows.AutoHandle(handle)
        self.pid = pid


def AutoKillProcess(command, path=None):
    pid = DWORD()
    return AutoKillProcess_(createprocess(command, path, pointer(pid)), pid.value)


_registhotkey = utilsdll.registhotkey
hotkeycallback_t = CFUNCTYPE(None)
_registhotkey.argtypes = UINT, UINT, hotkeycallback_t
_registhotkey.restype = c_int
_unregisthotkey = utilsdll.unregisthotkey
_unregisthotkey.argtypes = (c_int,)
__hotkeycallback_s = {}


def registhotkey(_, cb):
    mod, vk = _
    cb = hotkeycallback_t(cb)
    uid = _registhotkey(mod, vk, cb)
    if uid:
        __hotkeycallback_s[uid] = cb
    return uid


def unregisthotkey(uid):
    _unregisthotkey(uid)
    try:
        __hotkeycallback_s.pop(uid)
    except:
        pass


# winrt
winrt_OCR = utilsdll.winrt_OCR
winrt_OCR.argtypes = c_void_p, c_size_t, c_wchar_p, c_void_p

winrt_OCR_check_language_valid = utilsdll.winrt_OCR_check_language_valid
winrt_OCR_check_language_valid.argtypes = (c_wchar_p,)
winrt_OCR_check_language_valid.restype = c_bool

winrt_OCR_get_AvailableRecognizerLanguages = (
    utilsdll.winrt_OCR_get_AvailableRecognizerLanguages
)
winrt_OCR_get_AvailableRecognizerLanguages.argtypes = (c_void_p,)

winrt_capture_window = utilsdll.winrt_capture_window
winrt_capture_window.argtypes = c_void_p, c_void_p


class WinRT:
    @staticmethod
    def OCR_check_language_valid(lang: str) -> bool:
        return winrt_OCR_check_language_valid(lang)

    @staticmethod
    def OCR(data: bytes, lang: str):
        ret = []

        def cb(x1, y1, x2, y2, text):
            ret.append((text, x1, y1, x2, y2))

        winrt_OCR(
            data,
            len(data),
            lang,
            CFUNCTYPE(None, c_uint, c_uint, c_uint, c_uint, c_wchar_p)(cb),
        )
        return ret

    @staticmethod
    def OCR_get_AvailableRecognizerLanguages():
        ret = []
        winrt_OCR_get_AvailableRecognizerLanguages(
            CFUNCTYPE(None, c_wchar_p, c_wchar_p)(lambda t, d: ret.append((t, d)))
        )
        return ret

    @staticmethod
    def capture_window(hwnd):
        ret = []

        def cb(ptr, size):
            ret.append(cast(ptr, POINTER(c_char))[:size])

        winrt_capture_window(hwnd, CFUNCTYPE(None, c_void_p, c_size_t)(cb))
        if len(ret):
            return ret[0]
        return None


# winrt
_AES_decrypt = utilsdll.AES_decrypt
_AES_decrypt.argtypes = c_void_p, c_void_p, c_void_p, c_size_t


def AES_decrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    buff = create_string_buffer(data)
    _AES_decrypt(key, iv, buff, len(data))
    return bytes(buff)[:-1]


IsDLLBit64 = utilsdll.IsDLLBit64
IsDLLBit64.argtypes = (c_wchar_p,)
IsDLLBit64.restype = c_bool

CreateShortcut = utilsdll.CreateShortcut
CreateShortcut.argtypes = LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR

str_alloc = utilsdll.str_alloc
str_alloc.argtypes = (c_wchar_p,)
str_alloc.restype = c_void_p
GetParentProcessID = utilsdll.GetParentProcessID
GetParentProcessID.argtypes = (DWORD,)
GetParentProcessID.restype = DWORD
MouseMoveWindow = utilsdll.MouseMoveWindow
MouseMoveWindow.argtypes = (HWND,)
NeedUseSysMove = utilsdll.NeedUseSysMove
NeedUseSysMove.restype = c_bool

AdaptersServiceUninitialize = utilsdll.AdaptersServiceUninitialize
AdaptersServiceStartMonitor_Callback = CFUNCTYPE(None)
AdaptersServiceStartMonitor = utilsdll.AdaptersServiceStartMonitor
AdaptersServiceStartMonitor.argtypes = (AdaptersServiceStartMonitor_Callback,)
AdaptersServiceAdapterInfos_Callback = CFUNCTYPE(None, c_uint, c_uint, c_uint, LPCWSTR)
AdaptersServiceAdapterInfos = utilsdll.AdaptersServiceAdapterInfos
AdaptersServiceAdapterInfos.argtypes = (AdaptersServiceAdapterInfos_Callback,)


_GetPackagePathByPackageFamily = utilsdll.GetPackagePathByPackageFamily
GetPackagePathByPackageFamily_CALLBACK = CFUNCTYPE(None, LPCWSTR)
_GetPackagePathByPackageFamily.argtypes = (
    LPCWSTR,
    GetPackagePathByPackageFamily_CALLBACK,
)


def GetPackagePathByPackageFamily(packagename: str):
    ret: "list[str]" = []
    cb = GetPackagePathByPackageFamily_CALLBACK(ret.append)
    _GetPackagePathByPackageFamily(packagename, cb)
    if ret:
        return ret[0]
    return None
