class _LanguageInfo:
    def __init__(
        self,
        code: str,
        zhsname: str,
        engname: str,
        nativename: str,
        isoLANGNAME=None,
        isoCTRYNAME=None,
    ):
        self.code = code
        self.zhsname = zhsname
        self.engname = engname
        self.nativename = nativename
        self.isoLANGNAME = isoLANGNAME if isoLANGNAME else code
        self.isoCTRYNAME = isoCTRYNAME
        self.space = "" if (code in ("zh", "ja", "cht")) else " "

    def __eq__(self, value):
        if isinstance(value, _LanguageInfo):
            value = value.code
        return value == self.code

    def __str__(self):
        return self.code

    def __hash__(self):
        return self.code.__hash__()

    def upper(self):
        return self.code.upper()

    def lower(self):
        return self.code.lower()

    def encode(self, *argc, **kwargv):
        return self.code.encode(*argc, **kwargv)


class Languages(_LanguageInfo):
    Auto = _LanguageInfo("auto", "", "", "")
    Chinese = _LanguageInfo("zh", "简体中文", "Simplified Chinese", "简体中文")
    Japanese = _LanguageInfo("ja", "日语", "Japanese", "日本語")
    TradChinese = _LanguageInfo(
        "cht",
        "繁体中文",
        "Traditional Chinese",
        "繁體中文",
        isoLANGNAME="zh",
        isoCTRYNAME=["HK", "TW"],
    )
    English = _LanguageInfo("en", "英语", "English", "English")
    Russian = _LanguageInfo("ru", "俄语", "Russian", "Русский язык")
    Spanish = _LanguageInfo("es", "西班牙语", "Spanish", "Español")
    Korean = _LanguageInfo("ko", "韩语", "Korean", "한국어")
    French = _LanguageInfo("fr", "法语", "French", "Français")
    Vietnamese = _LanguageInfo("vi", "越南语", "Vietnamese", "Tiếng Việt")
    Turkish = _LanguageInfo("tr", "土耳其语", "Turkish", "Türkçe")
    Polish = _LanguageInfo("pl", "波兰语", "Polish", "Polski")
    Ukrainian = _LanguageInfo("uk", "乌克兰语", "Ukrainian", "Українська Мова")
    Italian = _LanguageInfo("it", "意大利语", "Italian", "Italiano")
    Arabic = _LanguageInfo("ar", "阿拉伯语", "Arabic", "اللغة العربية")
    Thai = _LanguageInfo("th", "泰语", "Thai", "ภาษาไทย")
    Tibetan = _LanguageInfo("bo", "藏语", "Tibetan", "བོད་པ་")
    German = _LanguageInfo("de", "德语", "German", "Deutsch")
    Swedish = _LanguageInfo("sv", "瑞典语", "Swedish", "Svenska")
    Dutch = _LanguageInfo("nl", "荷兰语", "Dutch", "Nederlands")
    Czech = _LanguageInfo("cs", "捷克语", "Czech", "Čeština")
    Portuguese = _LanguageInfo("pt", "葡萄牙语", "Portuguese", "Português")
    BrazilianPortuguese = _LanguageInfo("pt-br", "葡萄牙语_(巴西)", "Brazilian Portuguese", "Português Brasileiro")
    Hungarian = _LanguageInfo("hu", "匈牙利语", "Hungarian", "Magyar")
    Latin = _LanguageInfo("la", "拉丁语", "Latin language", "Lingua Latīna")

    @staticmethod
    def fromcode(code):
        for v in vars(Languages).values():
            if isinstance(v, _LanguageInfo):
                if v.code == code:
                    return v
        raise Exception("unknown code: " + code)

    @staticmethod
    def create_langmap(langmap=None):
        _ = dict(
            zip(
                TransLanguages,
                [_.code for _ in TransLanguages],
            )
        )
        if langmap:
            _.update(langmap)
        return _

    @staticmethod
    def createenglishlangmap():
        mp = dict(
            zip(
                TransLanguages,
                [_.engname for _ in TransLanguages],
            )
        )
        mp.update({Languages.Auto: ""})
        return mp


UILanguages = [
    Languages.Chinese,
    Languages.TradChinese,
    Languages.English,
    Languages.Russian,
    Languages.Japanese,
    Languages.Spanish,
    Languages.Korean,
    Languages.French,
    Languages.Vietnamese,
    Languages.Turkish,
    Languages.Polish,
    Languages.Ukrainian,
    Languages.Italian,
    Languages.Arabic,
    Languages.Thai,
    Languages.German,
    Languages.Swedish,
    Languages.Dutch,
    Languages.Czech,
    Languages.Portuguese,
    Languages.BrazilianPortuguese,
]

TransLanguages = [
    Languages.Chinese,
    Languages.Japanese,
    Languages.TradChinese,
    Languages.English,
    Languages.Russian,
    Languages.Spanish,
    Languages.Korean,
    Languages.French,
    Languages.Vietnamese,
    Languages.Turkish,
    Languages.Polish,
    Languages.Ukrainian,
    Languages.Italian,
    Languages.Arabic,
    Languages.Thai,
    Languages.Tibetan,
    Languages.German,
    Languages.Swedish,
    Languages.Dutch,
    Languages.Czech,
    Languages.Portuguese,
    Languages.BrazilianPortuguese,
    Languages.Hungarian,
    Languages.Latin,
]


def GetUILanguage(code: "tuple[str,str]"):
    lang, ctry = code
    matchs: "list[_LanguageInfo]" = []
    for v in UILanguages:
        if v.isoLANGNAME == lang:
            matchs.append(v)
    if not matchs:
        return Languages.English
    if len(matchs) == 1:
        return matchs[0]
    for _ in matchs:
        if _.isoCTRYNAME and ctry in _.isoCTRYNAME:
            return _
    for _ in matchs:
        if not _.isoCTRYNAME:
            return _
    return matchs[0]
