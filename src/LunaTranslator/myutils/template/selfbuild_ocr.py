import requests
from ocrengines.baseocrclass import baseocr, OCRResult


class OCR(baseocr):
    def ocr(self, imagebinary) -> "str | list[str] | OCRResult":
        raise Exception()

    def init(self):
        pass

    def langmap(self):
        # The mapping between standard language code and API language code, if not declared, defaults to using standard language code.
        # But the exception is cht. If api support cht, if must be explicitly declared the support of cht, otherwise it will translate to chs and then convert to cht.
        return {}
