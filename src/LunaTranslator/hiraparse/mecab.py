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
        for ___ in (
            mecabpath,
            ".",
            r"C:\Program Files\MeCab\dic",
            r"C:\Program Files (x86)\MeCab\dic",
        ):
            if not os.path.isdir(___):
                continue
            for _dir, _, __ in os.walk(___):
                self.kks = winsharedutils.mecab_init(
                    os.path.abspath(_dir).encode("utf8")
                )
                if self.kks:
                    self.codec: str = winsharedutils.mecab_dictionary_codec(
                        self.kks
                    ).decode()
                    self.isutf16 = (self.codec.lower().startswith("utf-16")) or (
                        self.codec.lower().startswith("utf16")
                    )
                    return
        raise Exception("not find")

    def __del__(self):
        winsharedutils.mecab_end(self.kks)

    def parse(self, text: str):
        res = []
        codec = self.codec
        if self.isutf16:

            def cb(surface: str, feature: str):
                fields = list(csv.reader([feature]))[0]
                res.append((surface, fields))

            fp = winsharedutils.mecab_parse_cb_w(cb)
        else:

            def cb(surface: bytes, feature: bytes):
                fields = list(csv.reader([feature.decode(codec)]))[0]
                res.append((surface.decode(codec), fields))

            fp = winsharedutils.mecab_parse_cb_a(cb)
        succ = winsharedutils.mecab_parse(
            self.kks,
            text.encode(codec),
            winsharedutils.cast(fp, winsharedutils.c_void_p).value,
        )
        if not succ:
            raise Exception("mecab parse failed")

        return res


class mecab(basehira):
    def init(self) -> None:
        mecabpath = self.config["path"]
        self.kks = mecabwrap(mecabpath)

    def maybeenglish(self, field: str):
        _ = field.split("-")
        if len(_) == 2:
            if isascii(_[1]):
                return _[1]

    def parse(self, text):
        start = 0
        result = []
        for node, fields in self.kks.parse(text):
            kana = ""
            origorig = ""
            pos1 = fields[0]
            if len(fields) == 26:
                kana = fields[17]
                origorig = fields[10]
                eng = self.maybeenglish(fields[7])
                if eng:
                    kana = eng
            elif len(fields) == 29:
                kana = fields[20]
                origorig = fields[10]
                eng = self.maybeenglish(fields[7])
                if eng:
                    kana = eng
            elif len(fields) == 17:
                kana = fields[9]
                origorig = fields[7]
                eng = self.maybeenglish(origorig)
                if eng:
                    kana = eng
            elif len(fields) == 9:
                kana = fields[8]
                origorig = fields[6]
                eng = self.maybeenglish(origorig)
                if eng:
                    kana = eng
            elif len(fields) == 7:  # Mecab/dic/ipadic utf-16 很垃圾，没啥卵用
                kana = origorig = node
            elif len(fields) == 6:  # 英文
                kana = origorig = node
            l = 0
            if node not in text:
                continue
            while str(node) not in text[start : start + l]:
                l += 1
            orig = text[start : start + l]
            start += l

            if kana == "*":
                kana = ""

            result.append(
                {"orig": orig, "hira": kana, "cixing": pos1, "origorig": origorig}
            )
        extras = text[start:]
        if len(extras):
            result.append(
                {"orig": extras, "hira": extras, "cixing": "", "origorig": extras}
            )
        return result
