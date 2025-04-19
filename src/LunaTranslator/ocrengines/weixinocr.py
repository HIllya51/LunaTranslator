import gobject, os, uuid
from ocrengines.baseocrclass import baseocr, OCRResult
from ctypes import CDLL, c_void_p, c_wchar_p, c_char_p, CFUNCTYPE, c_bool, c_float
import NativeUtils, threading
import winreg
from traceback import print_exc


class wcocr:
    def __init__(self):
        self.wcocr = CDLL(gobject.GetDllpath("wcocr.dll"))
        wcocr_init = self.wcocr.wcocr_init
        wcocr_init.argtypes = (
            c_wchar_p,
            c_wchar_p,
        )
        wcocr_init.restype = c_void_p
        self.pobj = None
        for function in [self.findwechat, self.findqqnt]:
            try:
                _ = function()
                if not _:
                    continue
                wechatocr_path, wechat_path = _
                if any([not os.path.exists(_) for _ in (wechatocr_path, wechat_path)]):
                    continue
                self.pobj = wcocr_init(wechatocr_path, wechat_path)
                if self.pobj:
                    break
            except:
                print_exc()
        if not self.pobj:
            raise Exception("找不到(微信和WeChatOCR)或(QQNT和TencentOCR)")

    def findqqnt(self):
        default = r"C:\Program Files\Tencent\QQNT"
        version = NativeUtils.QueryVersion(os.path.join(default, "QQ.exe"))
        if not version:
            return
        mojo = os.path.join(
            default,
            r"resources\app\versions",
            "{}.{}.{}-{}".format(version[0], version[1], version[2], version[3]),
        )
        ocr = os.path.join(mojo, r"QQScreenShot\Bin\TencentOCR.exe")
        return ocr, mojo

    def findwechat(self):
        k = winreg.OpenKeyEx(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Tencent\WeChat",
            0,
            winreg.KEY_QUERY_VALUE,
        )
        base = winreg.QueryValueEx(k, "InstallPath")[0]
        winreg.CloseKey(k)
        WeChatexe = os.path.join(base, "WeChat.exe")
        if not os.path.exists(WeChatexe):
            # 4.x
            WeChatexe = os.path.join(base, "Weixin.exe")
        version = NativeUtils.QueryVersion(WeChatexe)
        if not version:
            return
        versionf = ".".join((str(_) for _ in version))
        APPDATA = os.getenv("APPDATA")
        if version[0] == 4:
            wechat_path = os.path.join(base, versionf)
            wechatocr_path = os.path.join(
                APPDATA, r"Tencent\xwechat\XPlugin\plugins\WeChatOcr"
            )
            wechatocr_path = os.path.join(
                wechatocr_path,
                os.listdir(wechatocr_path)[0],
                r"extracted\wxocr.dll",
            )
        elif version[0] == 3:
            wechat_path = os.path.join(base, "[" + versionf + "]")
            wechatocr_path = os.path.join(
                APPDATA, r"Tencent\WeChat\XPlugin\Plugins\WeChatOCR"
            )
            wechatocr_path = os.path.join(
                wechatocr_path,
                os.listdir(wechatocr_path)[0],
                r"extracted\WeChatOCR.exe",
            )
        return wechatocr_path, wechat_path

    def __del__(self):

        wcocr_destroy = self.wcocr.wcocr_destroy
        wcocr_destroy.argtypes = (c_void_p,)
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

        fp = CFUNCTYPE(None, c_float, c_float, c_float, c_float, c_char_p)(cb)
        succ = wcocr_ocr(self.pobj, imgfile.encode("utf8"), fp)
        os.remove(imgfile)
        if not succ:
            return
        boxs = []
        texts = []
        for line in ret:
            x1, y1, x2, y2, text = line
            boxs.append((x1, y1, x2, y2))
            texts.append(text)
        return boxs, texts


globaloncelock = threading.Lock()
globalonce = None
# 这个wcocr，析构有问题。既然内存占用也不高，干脆不要释放了。


class OCR(baseocr):
    def init(self):
        global globalonce, globaloncelock
        if globalonce is None:
            with globaloncelock:
                globalonce = wcocr()

    def ocr(self, imagebinary):
        global globalonce
        boxs, texts = globalonce.ocr(imagebinary)
        return OCRResult(boxs=boxs, texts=texts)
