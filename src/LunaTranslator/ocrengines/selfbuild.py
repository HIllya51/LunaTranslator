from ocrengines.baseocrclass import baseocr
from myutils.utils import checkmd5reloadmodule
import gobject


class OCR(baseocr):
    def mayreinit(self):
        module = checkmd5reloadmodule(
            gobject.getconfig("selfbuild_ocr.py"), "selfbuild_ocr"
        )
        if module and (module.OCR != self.__lastm):
            self.__lastm = module.OCR
            self.internal: baseocr = module.OCR("selfbuild")
            self.internal.init()

    def init(self):
        self.internal = None
        self.__lastm = None
        self.mayreinit()

    def langmap(self):
        self.mayreinit()
        if not self.internal:
            return {}
        return self.internal.langmap()

    def ocr(self, content):
        self.mayreinit()
        if not self.internal:
            return ""
        return self.internal.ocr(content)
