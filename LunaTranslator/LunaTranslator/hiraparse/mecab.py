import winsharedutils
import os

from hiraparse.basehira import basehira


class mecab(basehira):
    def init(self) -> None:
        mecabpath = self.config["path"]
        if os.path.exists(mecabpath):
            self.kks = winsharedutils.mecabwrap(
                mecabpath
            )  #  fugashi.Tagger('-r nul -d "{}" -Owakati'.format(mecabpath))

    def parse(self, text):
        start = 0
        result = []
        codec = ["utf8", "shiftjis"][self.config["codec"]]
        for node, fields in self.kks.parse(
            text, codec
        ):  # self.kks.parseToNodeList(text):
            kana = ""
            pos1 = ""
            origorig = None
            if len(fields):
                pos1 = fields[0]
                if len(fields) > 29:
                    kana = fields[22]
                elif len(fields) == 29:
                    kana = fields[20]
                elif 29 > len(fields) >= 26:
                    kana = fields[17]
                    origorig = fields[7]
                elif len(fields) > 9:
                    kana = fields[9]  # 无kana，用lform代替
                elif len(fields) == 9:
                    kana = fields[8]  # 7/8均可，issues/514
                else:
                    kana = ""
                if len(fields) >= 8:
                    origorig = fields[7]  # unsafe
            l = 0
            if text[start] == "\n":
                start += 1
            while str(node) not in text[start : start + l]:
                l += 1
            orig = text[start : start + l]
            if origorig is None:
                origorig = orig

            start += l
            hira = kana  # .translate(self.h2k)

            if hira == "*":
                hira = ""
            # print(node.feature)
            if "-" in origorig:
                try:
                    hira_ = origorig.split("-")[1]
                    if hira_.isascii():  # 腰を引いて-->引く-他動詞
                        hira = hira_
                    origorig = origorig.split("-")[0]
                except:
                    pass

            result.append(
                {"orig": orig, "hira": hira, "cixing": pos1, "origorig": origorig}
            )
        return result
