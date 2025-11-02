import NativeUtils
import os
from myutils.config import globalconfig
from traceback import print_exc
from qtsymbols import *
from sometypes import WordSegResult

# fmt: off
allkata="ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ"
allhira="ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"    
hira_s=["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん","が","ぎ","ぐ","げ","ご","ざ","じ","ず","ぜ","ぞ","だ","ぢ","づ","で","ど","ば","び","ぶ","べ","ぼ","ぱ","ぴ","ぷ","ぺ","ぽ","きゃ","きぃ","きゅ","きぇ","きょ","しゃ","しぃ","しゅ","しぇ","しょ","ちゃ","ちぃ","ちゅ","ちぇ","ちょ","にゃ","にぃ","にゅ","にぇ","にょ","ひゃ","ひぃ","ひゅ","ひぇ","ひょ","みゃ","みぃ","みゅ","みぇ","みょ","りゃ","りぃ","りゅ","りぇ","りょ","ぎゃ","ぎぃ","ぎゅ","ぎぇ","ぎょ","じゃ","じぃ","じゅ","じぇ","じょ","ぢゃ","ぢぃ","ぢゅ","ぢぇ","ぢょ","びゃ","びぃ","びゅ","びぇ","びょ","ぴゃ","ぴぃ","ぴゅ","ぴぇ","ぴょ","ぐぁ","ぐぃ","ぐぅ","ぐぇ","ぐぉ","つぁ","つぃ","つぇ","つぉ","ふぁ","ふぃ","ふぇ","ふぉ","うぁ","うぃ","うぅ","うぇ","うぉ","ヴぁ","ヴぃ","ヴ","ヴぇ","ヴぉ","でゃ","でぃ","でゅ","でぇ","でょ","てゃ","てぃ","てゅ","てぇ","てょ","っ"]
kata_s=["ア","イ","ウ","エ","オ","カ","キ","ク","ケ","コ","サ","シ","ス","セ","ソ","タ","チ","ツ","テ","ト","ナ","ニ","ヌ","ネ","ノ","ハ","ヒ","フ","ヘ","ホ","マ","ミ","ム","メ","モ","ヤ","ユ","ヨ","ラ","リ","ル","レ","ロ","ワ","ヲ","ン","ガ","ギ","グ","ゲ","ゴ","ザ","ジ","ズ","ゼ","ゾ","ダ","ヂ","ヅ","デ","ド","バ","ビ","ブ","ベ","ボ","パ","ピ","プ","ペ","ポ","キャ","キィ","キュ","キェ","キョ","シャ","シィ","シュ","シェ","ショ","チャ","チィ","チュ","チェ","チョ","ニャ","ニィ","ニュ","ニェ","ニョ","ヒャ","ヒィ","ヒュ","ヒェ","ヒョ","ミャ","ミィ","ミュ","ミェ","ミョ","リャ","リィ","リュ","リェ","リョ","ギャ","ギィ","ギュ","ギェ","ギョ","ジャ","ジィ","ジュ","ジェ","ジョ","ヂャ","ヂィ","ヂュ","ヂェ","ヂョ","ビャ","ビィ","ビュ","ビェ","ビョ","ピャ","ピィ","ピュ","ピェ","ピョ","グァ","グィ","グゥ","グェ","グォ","ツァ","ツィ","ツェ","ツォ","ファ","フィ","フェ","フォ","ウァ","ウィ","ウゥ","ウェ","ウォ","ヴァ","ヴィ","ヴ","ヴェ","ヴォ","デャ","ディ","デュ","デェ","デョ","テャ","ティ","テュ","テェ","テョ","ッ"]
roma_s=["a","i","u","e","o","ka","ki","ku","ke","ko","sa","shi","su","se","so","ta","chi","tsu","te","to","na","ni","nu","ne","no","ha","hi","hu","he","ho","ma","mi","mu","me","mo","ya","yu","yo","ra","ri","ru","re","ro","wa","wo","n","ga","gi","gu","ge","go","za","ji","zu","ze","zo","da","ji","du","de","do","ba","bi","bu","be","bo","pa","pi","pu","pe","po","kya","kyi","kyu","kye","kyo","sha","syi","shu","she","sho","cha","cyi","chu","che","cho","nya","nyi","nyu","nye","nyo","hya","hyi","hyu","hye","hyo","mya","myi","myu","mye","myo","rya","ryi","ryu","rye","ryo","gya","gyi","gyu","gye","gyo","ja","ji","ju","je","jo","dya","dyi","dyu","dye","dyo","bya","byi","byu","bye","byo","pya","pyi","pyu","pye","pyo","gwa","gwi","gwu","gwe","gwo","tsa","tsi","tse","tso","fa","fi","fe","fo","wha","whi","whu","whe","who","va","vi","vu","ve","vo","dha","dhi","dhu","dhe","dho","tha","thi","thu","the","tho","-"]
# fmt: on

# fmt: off
punctuations = [
    "【","】","。","，","！","？","　","‘","’","“","”","、","《","》","；","：","…","（","）","」","「",
    " ",",","·",".","'","\"","?","/",";",":","|","[","]","{","}","-","_","=","+","`","~","!","#","$","%","^","&","*","(",")","\\"
]
# fmt: on

castkata2hira = str.maketrans(allkata, allhira)
casthira2kata = str.maketrans(allhira, allkata)


class _base:
    def init(self):
        pass

    def parse(self, text) -> "list[WordSegResult]": ...

    def __init__(self, *_) -> None:
        self.needinit = True
        self.init()
        self.needinit = False

    def splitspace(self, word: str):
        start = ""
        end = ""
        while word.startswith(" "):
            start += " "
            word = word[1:]
        while word.endswith(" "):
            end += " "
            word = word[:-1]
        return start, word, end

    def safeparse(self, text):
        try:
            if self.needinit:
                self.init()
                self.needinit = False
            return self.parse_multilines(text)
        except:
            print_exc()
            self.needinit = True
            return []

    def parse_multilines(self, text: str):

        hira: "list[WordSegResult]" = []
        for i, _ in enumerate(text.split("\n")):
            h = self.parse_singleline(_)
            if "".join(__.word for __ in h) != _:
                raise Exception("not match")
            if i:
                hira += [WordSegResult("\n")]
            hira += h
        return hira

    def parse_singleline(self, text):
        hira = self.parse(text)

        __parsekonge: "list[WordSegResult]" = []
        for word in hira:
            if word.word in punctuations:
                __parsekonge.append(WordSegResult(word.word, isdeli=True))
                continue
            start, w, end = self.splitspace(word.word)
            if len(start) == 0 and len(end) == 0:
                __parsekonge.append(word)
                continue
            word.word = w
            if word.kana:
                word.kana = self.splitspace(word.kana)[1]

            if start:
                __parsekonge.append(WordSegResult(start, isdeli=True))
            if word.word:
                __parsekonge.append(word)
            if end:
                __parsekonge.append(WordSegResult(end, isdeli=True))
        for _ in __parsekonge:
            if _.word.isascii():
                _.kana = None
        return __parsekonge

    @staticmethod
    def parseastarget(hira: "list[WordSegResult]"):
        for _1 in range(len(hira)):
            _ = len(hira) - 1 - _1
            if not hira[_].kana:
                continue
            hira_vis_type = globalconfig["hira_vis_type"]
            if hira_vis_type in (0, 1):
                if len(set(hira[_].word) - set(allkata + allhira)) == 0:
                    hira[_].hidekana = True
            if hira_vis_type == 0:
                hira[_].kana = hira[_].kana.translate(castkata2hira)
            elif hira_vis_type == 1:
                hira[_].kana = hira[_].kana.translate(casthira2kata)
            elif hira_vis_type == 2:
                __kanas = [hira_s, kata_s]
                target = roma_s
                for _ka in __kanas:
                    for __idx in range(len(_ka)):
                        _reverse_idx = len(_ka) - 1 - __idx
                        hira[_].kana = hira[_].kana.replace(
                            _ka[_reverse_idx], target[_reverse_idx]
                        )
        return hira

    @staticmethod
    def makerubyhtml(hira):
        ruby = _base.parseastarget(hira)
        if not ruby:
            return ""
        html = ""
        allsame = True
        for i in range(len(ruby)):
            html += ruby[i].word
            if ruby[i].kana and (ruby[i].word != ruby[i].kana):
                allsame = False
                html += "<rt>" + ruby[i].kana + "</rt>"
            else:
                html += "<rt></rt>"
        if allsame:
            return ""
        html = "<ruby>" + html + "</ruby>"
        return html


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


class mecab(_base):
    @property
    def config(self):
        return globalconfig["hirasetting"]["mecab"]["args"]

    def init(self) -> None:
        for ___ in (
            self.config["path"],
            ".",
            r"C:\Program Files\MeCab\dic",
            r"C:\Program Files (x86)\MeCab\dic",
        ):
            if not os.path.isdir(___):
                continue
            for _dir, _, __ in os.walk(___):
                self.kks = NativeUtils.mecab.create(os.path.abspath(_dir))
                if self.kks:
                    return
        raise Exception("not find")

    def maybeenglish(self, field: str):
        _ = field.split("-")
        if len(_) == 2:
            if _[1].isascii():
                return _[1]

    def parse(self, text):
        start = 0
        result: "list[WordSegResult]" = []
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
            fields = list(dict.fromkeys(fields))
            if "*" in fields:
                fields.remove("*")
            result.append(
                WordSegResult(
                    orig, kana=kana, prototype=origorig, wordclass=pos1, info=fields
                )
            )
        extras = text[start:]
        if len(extras):
            result.append(WordSegResult(extras, kana=extras, prototype=extras))
        return result


def splitstr(input_str: str, delimiters: "list[str]") -> "list[str]":
    lst = []
    cl = ""
    while len(input_str):
        su = False
        for deli in delimiters:
            if input_str.startswith(deli):
                if len(cl):
                    lst.append(cl)
                    cl = ""
                lst.append(deli)
                input_str = input_str[len(deli) :]
                su = True
                break
        if su:
            continue
        else:
            cl += input_str[0]
            input_str = input_str[1:]
    if len(cl):
        lst.append(cl)
    return lst


class latin(_base):

    def parse(self, text: str):
        return (
            WordSegResult(_, donthighlight=True, isshit=not _.isascii())
            for _ in splitstr(text, punctuations)
        )


class jiebapinyin(_base):

    def parse(self, text: str):
        import jieba
        import pypinyin

        py = pypinyin.pinyin(text)
        py = [_[0] for _ in py]
        jb = list(jieba.cut(text))

        jbidx = 0
        pyidx = 0
        result: "list[tuple[str, str]]" = []

        while pyidx < len(py) and jbidx < len(jb):
            if py[pyidx].startswith(jb[jbidx]):
                cnt = len(py[pyidx])
                while cnt:
                    cnt -= len(jb[jbidx])
                    jbidx += 1
                result.append((py[pyidx], ""))
                pyidx += 1
            else:
                cnt = len(jb[jbidx])
                pys = ""
                while cnt:
                    pys += py[pyidx]
                    pyidx += 1
                    cnt -= 1
                result.append((jb[jbidx], pys))
                jbidx += 1
        return (WordSegResult(t, kana=py, isshit=not py) for t, py in result)
