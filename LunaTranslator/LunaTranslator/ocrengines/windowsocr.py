import os
import winrtutils
from myutils.config import _TR, static_data
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    def initocr(self):
        _allsupport = winrtutils.getlanguagelist()
        self.supportmap = {}
        for lang in static_data["language_list_translator_inner"] + [
            "zh-Hans",
            "zh-Hant",
        ]:
            if lang == "zh" or lang == "cht":
                continue
            for s in _allsupport:
                if s.startswith(lang) or lang.startswith(s):
                    self.supportmap[lang] = s
                    break
        if "zh-Hans" in self.supportmap:
            v = self.supportmap.pop("zh-Hans")
            self.supportmap["zh"] = v
        if "zh-Hant" in self.supportmap:
            v = self.supportmap.pop("zh-Hant")
            self.supportmap["cht"] = v

    def ocr(self, imagebinary):
        if self.srclang not in self.supportmap:
            idx = static_data["language_list_translator_inner"].index(self.srclang)
            raise Exception(
                _TR("系统未安装")
                + _TR(static_data["language_list_translator"][idx])
                + _TR("的OCR模型")
            )

        if self.srclang in ["zh", "ja", "cht"]:
            space = ""
        else:
            space = " "

        ret = winrtutils.OCR_f(imagebinary, self.supportmap[self.srclang], space)
        boxs = [_[1:] for _ in ret]
        texts = [_[0] for _ in ret]

        return self.common_solve_text_orientation(boxs, texts)
