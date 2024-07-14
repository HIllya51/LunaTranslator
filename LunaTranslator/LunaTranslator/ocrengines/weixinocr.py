import gobject, os, uuid
from ocrengines.baseocrclass import baseocr
from ctypes import CDLL, c_void_p, c_wchar_p, c_char_p, CFUNCTYPE, c_bool, c_int


class OCR(baseocr):
    def initocr(self):
        self.wcocr = CDLL(gobject.GetDllpath(("wcocr.dll")))
        wcocr_init = self.wcocr.wcocr_init
        wcocr_init.argtypes = (
            c_wchar_p,
            c_wchar_p,
        )
        wcocr_init.restype = c_void_p

        base = r"C:\Program Files\Tencent\WeChat"
        for _ in os.listdir(base):
            if _.startswith("["):
                wechat_path = os.path.join(
                    base,
                    _,
                )
                break
        wechatocr_path = (
            os.getenv("APPDATA")
            + r"\Tencent\WeChat\XPlugin\Plugins\WeChatOCR\7079\extracted\WeChatOCR.exe"
        )
        self.pobj = wcocr_init(wechatocr_path, wechat_path)

    def end(self):

        wcocr_destroy = self.wcocr.wcocr_destroy
        wcocr_destroy.argtypes = c_void_p
        wcocr_destroy(self.pobj)

    def ocr(self, imagebinary):
        if not self.pobj:
            raise Exception("找不到微信&微信OCR路径")
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
