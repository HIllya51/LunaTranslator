import NativeUtils
from myutils.config import _TR
from ocrengines.baseocrclass import baseocr, OCRResult
from language import Languages


class OCR(baseocr):
    required_mini_height = 40

    def langmap(self):
        return {Languages.Chinese: "zh-Hans", Languages.TradChinese: "zh-Hant"}

    def ocr(self, imagebinary):
        supports = [
            _[0] for _ in NativeUtils.WinRT.OCR_get_AvailableRecognizerLanguages()
        ]
        if len(supports) == 0:

            raise Exception(_TR("无可用语言"))
        if self.is_src_auto:
            if len(supports) == 1:
                uselang = supports[0]
            else:
                self.raise_cant_be_auto_lang()
        else:
            if not NativeUtils.WinRT.OCR_check_language_valid(self.srclang):
                raise Exception(
                    _TR(
                        "系统未安装“{currlang}”的OCR模型\n当前支持的语言：{langs}"
                    ).format(
                        currlang=_TR(self.srclang_1.zhsname),
                        langs=", ".join(
                            [
                                _[1]
                                for _ in NativeUtils.WinRT.OCR_get_AvailableRecognizerLanguages()
                            ]
                        ),
                    )
                )
            uselang = self.srclang
        ret = NativeUtils.WinRT.OCR(imagebinary, uselang)
        boxs = [_[1:] for _ in ret]
        texts = [_[0] for _ in ret]
        return OCRResult(boxs=boxs, texts=texts)
