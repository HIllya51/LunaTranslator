from qtsymbols import *
from ocrengines.baseocrclass import baseocr
from requests import Requesters
from myutils.commonbase import proxysession
from myutils.utils import qimage2binary
from .OCR.gglens import GoogleLens


class OCR(baseocr):

    required_image_format = QImage

    def renewsesion(self):
        self.proxysession = proxysession(
            self._globalconfig_key, self.typename, Requesters.winhttp
        )

    def ocr(self, data: QImage):
        return GoogleLens(self.proxysession)(
            qimage2binary(data, "PNG"), data.width(), data.height()
        )
