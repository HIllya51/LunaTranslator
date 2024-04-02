import platform, os
from ctypes import (
    CDLL,
    c_int,
    c_void_p,
    c_char_p,
    Structure,
    c_uint,
    c_char,
    POINTER,
    CFUNCTYPE,
    cast,
    pointer,
)
from typing import Callable, Union, Tuple

HWND = c_void_p
webview_t = c_void_p
isbit64 = platform.architecture()[0] == "64bit"
DLL3264path = os.path.abspath(
    os.path.join("files/plugins/", ("DLL32", "DLL64")[isbit64])
)

try:
    _webview = CDLL(os.path.join(DLL3264path, "webview"))
except:
    raise Exception(
        'load module "{}" failed'.format(os.path.join(DLL3264path, "webview"))
    )


class webview_version_t(Structure):
    _fields_ = [("major", c_uint), ("minor", c_uint), ("patch", c_uint)]


class webview_version_info_t(Structure):
    _fields_ = [
        ("version", webview_version_t),
        ("version_number", c_char * 32),
        ("pre_release", c_char * 48),
        ("build_metadata", c_char * 48),
    ]


class SizeHints(c_int):
    WEBVIEW_HINT_NONE = 0
    WEBVIEW_HINT_MIN = 1
    WEBVIEW_HINT_MAX = 2
    WEBVIEW_HINT_FIXED = 3


_webview_create = _webview.webview_create
_webview_create.argtypes = c_int, c_void_p
_webview_create.restype = webview_t
_webview_destroy = _webview.webview_destroy
_webview_destroy.argtypes = (webview_t,)
_webview_set_title = _webview.webview_set_title
_webview_set_title.argtypes = webview_t, c_char_p
_webview_set_size = _webview.webview_set_size
_webview_set_geo = _webview.webview_set_geo
_webview_set_size.argtypes = webview_t, c_int, c_int, c_int
_webview_set_geo.argtypes = webview_t, c_int, c_int, c_int, c_int
_webview_set_html = _webview.webview_set_html
_webview_set_html.argtypes = webview_t, c_char_p
_webview_run = _webview.webview_run
_webview_run.argtypes = (webview_t,)
_webview_destroy = _webview.webview_destroy
_webview_destroy.argtypes = (webview_t,)
_webview_navigate = _webview.webview_navigate
_webview_navigate.argtypes = webview_t, c_char_p
_webview_eval = _webview.webview_eval
_webview_eval.argtypes = webview_t, c_char_p
_webview_get_window = _webview.webview_get_window
_webview_get_window.argtypes = (webview_t,)
_webview_get_window.restype = HWND
_webview_init = _webview.webview_init
_webview_init.argtypes = webview_t, c_char_p
_webview_version = _webview.webview_version
_webview_version.restype = POINTER(webview_version_info_t)
_webview_terminate = _webview.webview_terminate
_webview_terminate.argtypes = (webview_t,)
_webview_unbind = _webview.webview_unbind
_webview_unbind.argtypes = webview_t, c_char_p
_webview_return = _webview.webview_return
_webview_return.argtypes = webview_t, c_char_p, c_uint, c_char_p
_webview_dispatch = _webview.webview_dispatch
_webview_dispatch.argtypes = webview_t, c_void_p, c_void_p

_webview_bind = _webview.webview_bind
_webview_bind.argtypes = webview_t, c_char_p, c_void_p, c_void_p


class _Webview_Version:
    def __init__(self, v: webview_version_t) -> None:
        self.major = v.major
        self.minor = v.minor
        self.patch = v.patch

    def __repr__(self) -> str:
        return "{}.{}.{}".format(self.major, self.minor, self.patch)


class Webview_Version:
    def __repr__(self) -> str:
        return self.version_number

    def __init__(self, lpwv: POINTER(webview_version_info_t)) -> None:
        self.version = _Webview_Version(lpwv.contents.version)
        self.version_number = lpwv.contents.version_number.decode("utf8")
        self.pre_release = lpwv.contents.pre_release.decode("utf8")
        self.build_metadata = lpwv.contents.build_metadata.decode("utf8")


class Webview:
    def __init__(
        self, debug: bool = False, wnd: HWND = None, init_js: str = None
    ) -> None:
        self.pwebview = 0
        if wnd:  # 很坑，这个wnd并不是HWND，而是指向HWND的一个指针
            _HWND = HWND(wnd)
            wnd = pointer(_HWND)
        _w = _webview_create(debug, wnd)
        if _w == 0:
            raise Exception()
        self.pwebview = _w
        if init_js:
            self.init(init_js)

    def resolve(self, seq: str, status: int, result: str):
        _webview_return(
            self.pwebview, seq.encode("utf8"), status, result.encode("utf8")
        )

    def bind(
        self, name: str, fn: Callable[[str, str], Union[None, str, Tuple[str, int]]]
    ) -> None:

        def wrapped_fn(seq: c_char_p, req: c_char_p, args: c_void_p):
            _result = fn(seq.decode("utf8"), req.decode("utf8"))

            if _result is None:
                return
            if isinstance(_result, str):
                result, status = _result, 0
            elif isinstance(_result, Tuple[str, int]):
                result, status = _result

            _webview_return(self.pwebview, seq, status, result.encode("utf8"))

        webview_bind_fn_t = CFUNCTYPE(None, c_char_p, c_char_p, c_void_p)

        _webview_bind(
            self.pwebview,
            name.encode("utf8"),
            cast(webview_bind_fn_t(wrapped_fn), c_void_p).value,
            None,
        )

    def dispatch(self, fn: Callable[[], None]) -> None:
        def wrapped_fn(_w: webview_t, _arg: c_void_p):
            fn()

        webview_dispatch_fn_t = CFUNCTYPE(None, webview_t, c_void_p)
        _webview_dispatch(
            self.pwebview, cast(webview_dispatch_fn_t(wrapped_fn), c_void_p).value, None
        )

    def unbind(self, name: str) -> None:
        _webview_unbind(self.pwebview, name.encode("utf8"))

    def get_window(self) -> HWND:
        return _webview_get_window(self.pwebview)

    def eval(self, js: str) -> None:
        _webview_eval(self.pwebview, js.encode("utf8"))

    def navigate(self, url: str) -> None:
        _webview_navigate(self.pwebview, url.encode("utf8"))

    def init(self, js: str):
        _webview_init(self.pwebview, js.encode("utf8"))

    def __del__(self) -> None:
        if self.pwebview:
            _webview_destroy(self.pwebview)

    def run(self) -> None:
        _webview_run(self.pwebview)

    def set_html(self, html: str) -> None:
        _webview_set_html(self.pwebview, html.encode("utf8"))

    def set_size(
        self, width: int, height: int, hints: SizeHints = SizeHints.WEBVIEW_HINT_NONE
    ) -> None:
        _webview_set_size(self.pwebview, width, height, hints)

    def set_geo(self, X: int, Y: int, width: int, height: int) -> None:
        _webview_set_geo(self.pwebview, X, Y, width, height)

    def set_title(self, title: str) -> None:
        _webview_set_title(self.pwebview, title.encode("utf8"))

    def terminate(self):
        _webview_terminate(self.pwebview)

    @staticmethod
    def version() -> Webview_Version:
        return Webview_Version(_webview_version())
