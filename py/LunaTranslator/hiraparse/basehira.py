from myutils.config import globalconfig, static_data
from traceback import print_exc
from myutils.proxy import getproxy

# fmt: off
allkata="ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヽヾ",
allhira="ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ"    
hira_s=["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん","が","ぎ","ぐ","げ","ご","ざ","じ","ず","ぜ","ぞ","だ","ぢ","づ","で","ど","ば","び","ぶ","べ","ぼ","ぱ","ぴ","ぷ","ぺ","ぽ","きゃ","きぃ","きゅ","きぇ","きょ","しゃ","しぃ","しゅ","しぇ","しょ","ちゃ","ちぃ","ちゅ","ちぇ","ちょ","にゃ","にぃ","にゅ","にぇ","にょ","ひゃ","ひぃ","ひゅ","ひぇ","ひょ","みゃ","みぃ","みゅ","みぇ","みょ","りゃ","りぃ","りゅ","りぇ","りょ","ぎゃ","ぎぃ","ぎゅ","ぎぇ","ぎょ","じゃ","じぃ","じゅ","じぇ","じょ","ぢゃ","ぢぃ","ぢゅ","ぢぇ","ぢょ","びゃ","びぃ","びゅ","びぇ","びょ","ぴゃ","ぴぃ","ぴゅ","ぴぇ","ぴょ","ぐぁ","ぐぃ","ぐぅ","ぐぇ","ぐぉ","つぁ","つぃ","つぇ","つぉ","ふぁ","ふぃ","ふぇ","ふぉ","うぁ","うぃ","うぅ","うぇ","うぉ","ヴぁ","ヴぃ","ヴ","ヴぇ","ヴぉ","でゃ","でぃ","でゅ","でぇ","でょ","てゃ","てぃ","てゅ","てぇ","てょ","っ"]
kata_s=["ア","イ","ウ","エ","オ","カ","キ","ク","ケ","コ","サ","シ","ス","セ","ソ","タ","チ","ツ","テ","ト","ナ","ニ","ヌ","ネ","ノ","ハ","ヒ","フ","ヘ","ホ","マ","ミ","ム","メ","モ","ヤ","ユ","ヨ","ラ","リ","ル","レ","ロ","ワ","ヲ","ン","ガ","ギ","グ","ゲ","ゴ","ザ","ジ","ズ","ゼ","ゾ","ダ","ヂ","ヅ","デ","ド","バ","ビ","ブ","ベ","ボ","パ","ピ","プ","ペ","ポ","キャ","キィ","キュ","キェ","キョ","シャ","シィ","シュ","シェ","ショ","チャ","チィ","チュ","チェ","チョ","ニャ","ニィ","ニュ","ニェ","ニョ","ヒャ","ヒィ","ヒュ","ヒェ","ヒョ","ミャ","ミィ","ミュ","ミェ","ミョ","リャ","リィ","リュ","リェ","リョ","ギャ","ギィ","ギュ","ギェ","ギョ","ジャ","ジィ","ジュ","ジェ","ジョ","ヂャ","ヂィ","ヂュ","ヂェ","ヂョ","ビャ","ビィ","ビュ","ビェ","ビョ","ピャ","ピィ","ピュ","ピェ","ピョ","グァ","グィ","グゥ","グェ","グォ","ツァ","ツィ","ツェ","ツォ","ファ","フィ","フェ","フォ","ウァ","ウィ","ウゥ","ウェ","ウォ","ヴァ","ヴィ","ヴ","ヴェ","ヴォ","デャ","ディ","デュ","デェ","デョ","テャ","ティ","テュ","テェ","テョ","ッ"]
roma_s=["a","i","u","e","o","ka","ki","ku","ke","ko","sa","shi","su","se","so","ta","chi","tsu","te","to","na","ni","nu","ne","no","ha","hi","hu","he","ho","ma","mi","mu","me","mo","ya","yu","yo","ra","ri","ru","re","ro","wa","wo","n","ga","gi","gu","ge","go","za","ji","zu","ze","zo","da","ji","du","de","do","ba","bi","bu","be","bo","pa","pi","pu","pe","po","kya","kyi","kyu","kye","kyo","sha","syi","shu","she","sho","cha","cyi","chu","che","cho","nya","nyi","nyu","nye","nyo","hya","hyi","hyu","hye","hyo","mya","myi","myu","mye","myo","rya","ryi","ryu","rye","ryo","gya","gyi","gyu","gye","gyo","ja","ji","ju","je","jo","dya","dyi","dyu","dye","dyo","bya","byi","byu","bye","byo","pya","pyi","pyu","pye","pyo","gwa","gwi","gwu","gwe","gwo","tsa","tsi","tse","tso","fa","fi","fe","fo","wha","whi","whu","whe","who","va","vi","vu","ve","vo","dha","dhi","dhu","dhe","dho","tha","thi","thu","the","tho","-"]
# fmt: on


class basehira:
    def init(self):
        pass

    def parse(self, text):
        return []

    def __init__(self, typename) -> None:
        self.typename = typename
        self.castkata2hira = str.maketrans(allkata, allhira)
        self.casthira2kata = str.maketrans(allhira, allkata)
        self.needinit = True
        self.init()
        self.needinit = False

    @property
    def config(self):
        return globalconfig["hirasetting"][self.typename]["args"]

    @property
    def proxy(self):
        return getproxy(("hirasetting", self.typename))

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

    def parse_multilines(self, text):

        hira = []
        for i, _ in enumerate(text.split("\n")):
            h = self.parse_singleline(_)
            if "".join(__["orig"] for __ in h) != _:
                raise Exception("not match")
            if i:
                hira += [{"orig": "\n", "hira": "\n"}]
            hira += h
        return hira

    def parse_singleline(self, text):
        hira = self.parse(text)

        __parsekonge = []
        for word in hira:
            ori = word["orig"]
            start, w, end = self.splitspace(ori)
            if len(start) == 0 and len(end) == 0:
                __parsekonge.append(word)
                continue
            word["orig"] = w
            word["hira"] = self.splitspace(word["hira"])[1]

            if len(start):
                __parsekonge.append({"orig": start, "hira": start})
            __parsekonge.append(word)
            if len(end):
                __parsekonge.append({"orig": end, "hira": end})
        hira = __parsekonge
        for _1 in range(len(hira)):
            _ = len(hira) - 1 - _1
            if globalconfig["hira_vis_type"] == 0:
                hira[_]["hira"] = hira[_]["hira"].translate(self.castkata2hira)
            elif globalconfig["hira_vis_type"] == 1:
                hira[_]["hira"] = hira[_]["hira"].translate(self.casthira2kata)
            elif globalconfig["hira_vis_type"] == 2:
                __kanas = [hira_s, kata_s]
                target = roma_s
                for _ka in __kanas:
                    for __idx in range(len(_ka)):
                        _reverse_idx = len(_ka) - 1 - __idx
                        hira[_]["hira"] = hira[_]["hira"].replace(
                            _ka[_reverse_idx], target[_reverse_idx]
                        )

        return hira
