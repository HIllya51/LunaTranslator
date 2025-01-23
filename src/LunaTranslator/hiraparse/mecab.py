import winsharedutils
import os, csv, gobject
from hiraparse.basehira import basehira
from myutils.config import isascii

# # 2.1.2 src schema
# UnidicFeatures17 = namedtuple('UnidicFeatures17',
#         ('pos1 pos2 pos3 pos4 cType cForm lForm lemma orth pron '
#         'orthBase pronBase goshu iType iForm fType fForm').split(' '))

# # 2.1.2 bin schema
# # The unidic-mecab-2.1.2_bin distribution adds kana accent fields.
# UnidicFeatures26 = namedtuple('UnidicFeatures26',
#         ('pos1 pos2 pos3 pos4 cType cForm lForm lemma orth pron '
#         'orthBase pronBase goshu iType iForm fType fForm '
#         'kana kanaBase form formBase iConType fConType aType '
#         'aConType aModeType').split(' '))

# # schema used in 2.2.0, 2.3.0
# UnidicFeatures29 = namedtuple('UnidicFeatures29', 'pos1 pos2 pos3 pos4 cType '
#         'cForm lForm lemma orth pron orthBase pronBase goshu iType iForm fType '
#         'fForm iConType fConType type kana kanaBase form formBase aType aConType '
#         'aModType lid lemma_id'.split(' '))


class mecabwrap:

    def __init__(self, mecabpath) -> None:

        maybepaths = (
            [mecabpath]
            + os.listdir(".")
            + [".", r"C:\Program Files (x86)\MeCab\dic\ipadic"]
        )
        for _ in maybepaths:
            self.kks = winsharedutils.mecab_init(
                os.path.abspath(_).encode("utf8"), gobject.GetDllpath("libmecab.dll")
            )
            if self.kks:
                self.codec = winsharedutils.mecab_dictionary_codec(self.kks).decode()
                return

        raise Exception("not find")

    def __del__(self):
        winsharedutils.mecab_end(self.kks)

    def parse(self, text: str):
        res = []
        codec = self.codec

        def cb(surface: bytes, feature: bytes):
            fields = list(csv.reader([feature.decode(codec)]))[0]
            res.append((surface.decode(codec), fields))

        fp = winsharedutils.mecab_parse_cb(cb)
        succ = winsharedutils.mecab_parse(self.kks, text.encode(codec), fp)
        if not succ:
            raise Exception("mecab parse failed")

        return res


class mecab(basehira):
    def init(self) -> None:
        mecabpath = self.config["path"]
        self.kks = mecabwrap(mecabpath)

    def parse(self, text):
        start = 0
        result = []
        for node, fields in self.kks.parse(text):
            kana = ""
            origorig = ""
            pos1 = fields[0]
            if len(fields) == 26:
                kana = fields[17]
                origorig = fields[7]
            elif len(fields) == 29:
                kana = fields[20]
                origorig = fields[7]
            elif len(fields) == 17:
                kana = fields[9]
                origorig = fields[7]
            elif len(fields) == 9:
                kana = fields[8]
                origorig = fields[7]
            elif len(fields) == 6:  # 英文
                kana = origorig = node
            l = 0

            while str(node) not in text[start : start + l]:
                l += 1
            orig = text[start : start + l]
            start += l
            hira = kana  # .translate(self.h2k)

            if hira == "*":
                hira = ""
            # print(node.feature)
            if "-" in origorig:
                try:
                    maybe_english = origorig.split("-")[1]
                    if isascii(maybe_english):
                        # コンビニを --> コンビニ-convenience
                        hira = origorig = maybe_english
                    else:
                        # 腰を引いて --> 引く-他動詞
                        origorig = origorig.split("-")[0]
                except:
                    pass

            result.append(
                {"orig": orig, "hira": hira, "cixing": pos1, "origorig": origorig}
            )
        extras = text[start:]
        if len(extras):
            result.append(
                {"orig": extras, "hira": extras, "cixing": "", "origorig": extras}
            )
        return result
