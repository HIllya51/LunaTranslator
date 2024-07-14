from ctypes import (
    c_uint,
    c_bool,
    c_wchar_p,
    CDLL,
    c_size_t,
    CFUNCTYPE,
    c_void_p,
)
import platform, gobject

try:
    if platform.system() != "Windows" or int(platform.version().split(".")[0]) < 6:
        raise Exception()

    winrtutilsdll = CDLL(gobject.GetDllpath(("winrtutils32.dll", "winrtutils64.dll")))
except:
    winrtutilsdll = 0

if winrtutilsdll:

    _OCR_f = winrtutilsdll.OCR
    _OCR_f.argtypes = c_void_p, c_size_t, c_wchar_p, c_wchar_p, c_void_p

    _check_language_valid = winrtutilsdll.check_language_valid
    _check_language_valid.argtypes = (c_wchar_p,)
    _check_language_valid.restype = c_bool

    _getlanguagelist = winrtutilsdll.getlanguagelist
    _getlanguagelist.argtypes = (c_void_p,)

    def getlanguagelist():
        ret = []
        _getlanguagelist(CFUNCTYPE(None, c_wchar_p)(ret.append))
        return ret

    def OCR_f(data, lang, space):
        ret = []

        def cb(x1, y1, x2, y2, text):
            ret.append((text, x1, y1, x2, y2))

        _OCR_f(
            data,
            len(data),
            lang,
            space,
            CFUNCTYPE(None, c_uint, c_uint, c_uint, c_uint, c_wchar_p)(cb),
        )
        return ret

    _winrt_capture_window = winrtutilsdll.winrt_capture_window
    _winrt_capture_window.argtypes = c_wchar_p, c_void_p
