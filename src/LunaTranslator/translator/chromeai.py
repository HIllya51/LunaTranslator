import windows
from translator.basetranslator import basetrans
from myutils.wrapper import threader
import NativeUtils, uuid, threading, functools, os
from ctypes import cast, c_wchar_p
from translator.cdp_helper import cdp_helper
from language import Languages

# https://developer.chrome.com/docs/ai/translator-api?hl=zh-cn


# webview2暂时不支持这个API，先放在这里。
class _simplewindow:
    WM_EVAL_JS = windows.WM_APP + 10

    def eval(self, js):
        sema = threading.Event()
        uid = str(uuid.uuid4())
        self.events[uid] = (sema, [])
        windows.SendMessage(self.devtool, self.WM_EVAL_JS, js, uid)
        sema.wait()
        _ = self.events.pop(uid)[1]
        if _:
            return _[0]

    def __jscb(self, uid, _):
        self.events[uid][1].append(_)
        self.events[uid][0].set()

    def WndProc(self, msg, wParam, lParam):
        # 其实所有webview2 eval都应该这样来实现的。不过目前没出问题，就先不改了。
        if msg == self.WM_EVAL_JS:
            self.webview.eval(
                cast(wParam, c_wchar_p).value,
                functools.partial(self.__jscb, cast(lParam, c_wchar_p).value),
            )

    def __init__(self, sema, error):
        self.events: "dict[str, tuple[threading.Event, list]]" = {}
        self.init(sema, error)

    @threader
    def init(self, sema: threading.Event, error: list):
        self._fp = NativeUtils.WindowMessageCallback_t(self.WndProc)
        self.devtool = NativeUtils.CreateMessageWindow(self._fp)
        try:
            windows.ShowWindow(self.devtool, windows.SW_SHOW)
            windows.MoveWindow(self.devtool, 0, 0, 300, 300, False)
            self.webview = NativeUtils.WebView2(self.devtool)
            self.webview.resize(300, 300)
        except Exception as e:
            error.append(e)
        sema.set()

        NativeUtils.RunMessageLoop()

    def __del__(self):
        windows.DestroyWindow(self.devtool)


class cdp_chromeai(cdp_helper):
    target_url = ""


class TS(basetrans):
    needzhconv = True

    def init1(self):
        sema = threading.Event()
        error = []
        self.devtool = _simplewindow(sema, error)
        sema.wait()
        if error:
            raise error[0]

    @property
    def srclang(self):
        if self.srclang_1 == Languages.TradChinese:
            return "zh"
        return self.srclang_1

    @property
    def tgtlang(self):
        if self.tgtlang_1 == Languages.TradChinese:
            return "zh"
        return self.tgtlang_1

    def init(self):
        self.devtool = cdp_chromeai(self)

    def translate(self, query: str):
        with open(
            os.path.join(os.path.dirname(__file__), "chromeai.js"),
            "r",
            encoding="utf8",
        ) as ff:
            f = ff.read()
        f = (
            f.replace("{srclang}", str(self.srclang))
            .replace("{tgtlang}", str(self.tgtlang))
            .replace("{query}", query)
        )
        return self.devtool.wait_for_result(f, awaitPromise=True, ignoreException=False)
