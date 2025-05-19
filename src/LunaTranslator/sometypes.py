class TranslateResult:
    def __init__(self, id=None, result=None):
        self.id = id
        self.result = result

    def __bool__(self):
        return bool(self.result)


class TranslateError:

    def __init__(self, id=None, message=None):
        self.id = id
        self.message = message

    def __bool__(self):
        return bool(self.message)


class WordSegResult:
    def __init__(
        self,
        word,
        kana: str = None,
        isdeli=False,
        wordclass: str = None,
        prototype: str = None,
        donthighlight=False,
        hidekana=False,
        info=None,
        isshit=False,
        **_
    ):
        self.donthighlight = donthighlight
        self.word = word
        self.kana = kana
        self.isdeli = isdeli
        self.wordclass = wordclass
        self._prototype = prototype
        self.hidekana = hidekana
        self.info = info
        self.isshit = isshit

    @property
    def prototype(self):
        if self._prototype:
            return self._prototype
        return self.word

    def as_dict(self):
        return dict(
            word=self.word,
            kana=self.kana,
            isdeli=self.isdeli,
            wordclass=self.wordclass,
            prototype=self._prototype,
            hidekana=self.hidekana,
            info=self.info,
            isshit=self.isshit,
        )

    def __str__(self):
        return str(self.as_dict())

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_dict(d: dict):
        return WordSegResult(
            d["word"],
            d.get("kana"),
            d.get("isdeli", False),
            d.get("wordclass"),
            d.get("prototype"),
            info=d.get("info"),
            isshit=d.get("isshit", False),
        )
