from translator.basetranslator import basetrans
from zhconv import convert
import NativeUtils
from language import Languages


class TS(basetrans):
    def translate(self, content):
        tp = (self.srclang, self.tgtlang)
        if Languages.Chinese in tp:
            ret = convert(content, "zh-cn")
        elif Languages.TradChinese in tp:
            ret = convert(content, "zh-tw")
        else:
            chs = convert(content, "zh-cn")
            cht = convert(content, "zh-tw")
            ret = (chs, cht)[
                NativeUtils.distance(content, chs) < NativeUtils.distance(content, cht)
            ]

        return ret
