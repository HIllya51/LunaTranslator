from myutils.config import globalconfig
import winsharedutils
import os


class hira:
    def __init__(self) -> None:
        hirasettingbase = globalconfig["hirasetting"]

        mecabpath = hirasettingbase["mecab"]["path"]
        if os.path.exists(mecabpath):
            self.kks = winsharedutils.mecabwrap(
                mecabpath
            )  #  fugashi.Tagger('-r nul -d "{}" -Owakati'.format(mecabpath))

    def fy(self, text):
        start = 0
        result = []
        codec = ["utf8", "shiftjis"][globalconfig["hirasetting"]["mecab"]["codec"]]
        for node, fields in self.kks.parse(
            text, codec
        ):  # self.kks.parseToNodeList(text):
            if len(fields):
                pos1 = fields[0]
                if len(fields) > 29:
                    kana = fields[22]
                elif len(fields) == 29:
                    kana = fields[20]
                elif 29 > len(fields) >= 26:
                    kana = fields[17]
                elif len(fields) > 9:
                    kana = fields[9]  # 无kana，用lform代替
                elif len(fields) == 9:
                    kana = fields[8]  # 7/8均可，issues/514
                else:
                    kana = ""
            else:
                kana = ""
                pos1 = ""
            l = 0
            if text[start] == "\n":
                start += 1
            while str(node) not in text[start : start + l]:
                l += 1
            orig = text[start : start + l]
            start += l
            hira = kana  # .translate(self.h2k)

            if hira == "*":
                hira = ""
            # print(node.feature)
            result.append({"orig": orig, "hira": hira, "cixing": pos1})
        return result
