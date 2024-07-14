import gobject, os, uuid, windows
from ocrengines.baseocrclass import baseocr
from ctypes import CDLL, c_void_p, c_wchar_p, c_char_p, CFUNCTYPE, c_bool, c_int
import winsharedutils


class OCR(baseocr):
    def initocr(self):
        self.wcocr = CDLL(gobject.GetDllpath(("wcocr.dll")))
        wcocr_init = self.wcocr.wcocr_init
        wcocr_init.argtypes = (
            c_wchar_p,
            c_wchar_p,
        )
        wcocr_init.restype = c_void_p
        try:
            key = windows.RegOpenKeyEx(
                windows.HKEY_CURRENT_USER,
                "SOFTWARE\Tencent\WeChat",
                0,
                windows.KEY_QUERY_VALUE,
            )
            base = windows.RegQueryValueEx(key, "InstallPath")
            windows.RegCloseKey(key)
            WeChatexe = os.path.join(base, "WeChat.exe")
            version = winsharedutils.queryversion(WeChatexe)
            if not version:
                raise Exception

        except:
            from traceback import print_exc

            print_exc()
            raise Exception("未找到WeChat")

        versionf = ".".join((str(_) for _ in version))
        wechat_path = os.path.join(base, "[" + versionf + "]")
        wechatocr_path = (
            os.getenv("APPDATA") + r"\Tencent\WeChat\XPlugin\Plugins\WeChatOCR"
        )
        try:
            wechatocr_path = os.path.join(
                wechatocr_path,
                os.listdir(wechatocr_path)[0],
                r"extracted\WeChatOCR.exe",
            )
        except:
            raise Exception("未找到WeChatOCR")
        self.pobj = wcocr_init(wechatocr_path, wechat_path)
        if not self.pobj:
            raise Exception("加载失败")

    def end(self):

        wcocr_destroy = self.wcocr.wcocr_destroy
        wcocr_destroy.argtypes = c_void_p
        wcocr_destroy(self.pobj)

    def ocr(self, imagebinary):
        fname = gobject.gettempdir(str(uuid.uuid4()) + ".png")
        with open(fname, "wb") as ff:
            ff.write(imagebinary)
        imgfile = os.path.abspath(fname)
        wcocr_ocr = self.wcocr.wcocr_ocr
        wcocr_ocr.argtypes = c_void_p, c_char_p, c_void_p
        wcocr_ocr.restype = c_bool
        ret = []

        def cb(x1, y1, x2, y2, text: bytes):
            ret.append((x1, y1, x2, y2, text.decode("utf8")))

        succ = wcocr_ocr(
            self.pobj,
            imgfile.encode("utf8"),
            CFUNCTYPE(None, c_int, c_int, c_int, c_int, c_char_p)(cb),
        )
        if not succ:
            return
        os.remove(imgfile)
        boxs = []
        texts = []
        for line in ret:
            x1, y1, x2, y2, text = line
            boxs.append((x1, y1, x2, y2))
            texts.append(text)
        return self.common_solve_text_orientation(boxs, texts)
