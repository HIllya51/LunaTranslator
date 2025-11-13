import random
import requests
import NativeUtils
from qtsymbols import *
from ocrengines.baseocrclass import baseocr, OCRResult
from myutils.utils import qimage2binary


class GoogleLens:
    LENS_ENDPOINT: str = "https://lensfrontend-pa.googleapis.com/v1/crupload"

    HEADERS: "dict[str, str]" = {
        "Host": "lensfrontend-pa.googleapis.com",
        "Connection": "keep-alive",
        "Content-Type": "application/x-protobuf",
        "X-Goog-Api-Key": "AIzaSyDr2UxVnv_U85AbhhY8XSHSIavUW0DC-sY",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "empty",
    }

    def __init__(self, session: requests.Session):
        self.client = session

    def __call__(self, raw_bytes: str, width: int, height: int):

        rint = random.randint(0, 2**64 - 1)
        rbyte = random.getrandbits(16 * 8).to_bytes(16, "little")
        ret = []

        def __(ptr, size):
            ret.append(ptr[:size])

        NativeUtils.glens_create_request(
            rint,
            rbyte,
            len(rbyte),
            raw_bytes,
            len(raw_bytes),
            width,
            height,
            NativeUtils.glens_create_request_CB(__),
        )
        res = self.client.post(
            self.LENS_ENDPOINT, data=ret[0], headers=self.HEADERS, timeout=40
        )
        result = []
        boxs = []

        def __2(string: bytes, x, y, w, h):
            result.append(string.decode())

            centerX = x * width
            centerY = y * height
            _width = w * width / 2
            _height = h * height / 2
            boxs.append(
                [
                    centerX - _width,
                    centerY - _height,
                    centerX + _width,
                    centerY + _height,
                ]
            )

        NativeUtils.glens_parse_response(
            res.content, len(res.content), NativeUtils.glens_parse_response_CB(__2)
        )
        return OCRResult(boxs=boxs, texts=result)


class OCR(baseocr):

    required_image_format = QImage

    def ocr(self, data: QImage):
        return GoogleLens(self.proxysession)(
            qimage2binary(data, "PNG"), data.width(), data.height()
        )
