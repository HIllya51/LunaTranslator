from translator.basetranslator import basetrans
from zhconv import convert


class TS(basetrans):
    def translate(self, content):

        if self.tgtlang == "zh":
            ret = convert(content, "zh-cn")
        elif self.tgtlang == "cht":
            ret = convert(content, "zh-tw")
        return ret
