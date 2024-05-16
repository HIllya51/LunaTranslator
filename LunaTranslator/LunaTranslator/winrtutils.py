from ctypes import (
    c_uint,
    c_bool,
    POINTER,
    c_wchar_p,
    pointer,
    CDLL,
    c_size_t,
    Structure,
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

    class ocrres(Structure):
        _fields_ = [
            ("lines", POINTER(c_wchar_p)),
            ("xs", POINTER(c_uint)),
            ("ys", POINTER(c_uint)),
            ("xs2", POINTER(c_uint)),
            ("ys2", POINTER(c_uint)),
        ]

    _OCR_f = winrtutilsdll.OCR
    _OCR_f.argtypes = c_void_p, c_size_t, c_wchar_p, c_wchar_p, POINTER(c_uint)
    _OCR_f.restype = ocrres
    _freeocrres = winrtutilsdll.freeocrres
    _freeocrres.argtypes = ocrres, c_uint

    _freewstringlist = winrtutilsdll.freewstringlist
    _freewstringlist.argtypes = POINTER(c_wchar_p), c_uint
    _check_language_valid = winrtutilsdll.check_language_valid
    _check_language_valid.argtypes = (c_wchar_p,)
    _check_language_valid.restype = c_bool

    _getlanguagelist = winrtutilsdll.getlanguagelist
    _getlanguagelist.argtypes = (POINTER(c_uint),)
    _getlanguagelist.restype = POINTER(c_wchar_p)

    def getlanguagelist():
        num = c_uint()
        ret = _getlanguagelist(pointer(num))
        _allsupport = []
        for i in range(num.value):
            _allsupport.append(ret[i])
        _freewstringlist(ret, num.value)
        return _allsupport

    def OCR_f(data, lang, space):
        num = c_uint()
        ret = _OCR_f(data, len(data), lang, space, pointer(num))
        res = []
        for i in range(num.value):
            res.append((ret.lines[i], ret.xs[i], ret.ys[i], ret.xs2[i], ret.ys2[i]))

        _freeocrres(ret, num.value)
        return res

    _winrt_capture_window = winrtutilsdll.winrt_capture_window
    _winrt_capture_window.argtypes = c_wchar_p, c_void_p
