from translator.basetranslator import basetrans
from zhconv import convert
from language import Languages


class TS(basetrans):
    def translate(self, content):

        if self.tgtlang == Languages.Chinese:
            ret = convert(content, "zh-cn")
        elif self.tgtlang == Languages.TradChinese:
            ret = convert(content, "zh-tw")
        return ret
