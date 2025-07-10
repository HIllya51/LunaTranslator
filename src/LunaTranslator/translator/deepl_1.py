from translator.basetranslator import basetrans
from translator.cdp_helper import cdp_helper
from language import Languages


class cdp_deepl(cdp_helper):
    target_url = "https://www.deepl.com/en/translator"

    @property
    def using(self):
        return self.ref.using and self.config["usewhich"] == 1

    @property
    def srclang(self):
        if self.ref.srclang_1 == Languages.TradChinese:
            return "zh"
        return self.ref.srclang_1

    @property
    def tgtlang(self):
        if self.ref.tgtlang_1 == Languages.TradChinese:
            return "zh-hant"
        if self.ref.tgtlang_1 == Languages.Chinese:
            return "zh-hans"
        return self.ref.tgtlang_1

    def __init__(self, ref):
        super().__init__(ref)
        self.langs = None

    def checklang(self):
        if (self.srclang, self.tgtlang) == self.langs:
            return
        self.langs = (self.srclang, self.tgtlang)
        self.Page_navigate(
            "https://www.deepl.com/en/translator#{}/{}".format(
                self.srclang, self.tgtlang
            )
        )

    def translate(self, content):
        self.checklang()

        self.Runtime_evaluate(
            """document.querySelector("#translator-source-clear-button").click()"""
        )
        self.Runtime_evaluate(
            """document.getElementsByTagName("d-textarea")[1].querySelectorAll('span').forEach(e=>{e.innerText=''})"""
        )
        self.Runtime_evaluate("document.getElementsByTagName('d-textarea')[0].focus()")
        self.send_keys(content)
        return self.wait_for_result(
            'document.getElementsByTagName("d-textarea")[1].textContent'
        )


class TS(basetrans):
    def init(self):
        self.devtool = None
        if self.config["usewhich"] == 1:
            self.devtool = cdp_deepl(self)

    @property
    def srclang(self):
        if self.srclang_1 == Languages.TradChinese:
            return "ZH"
        return self.srclang_1.upper()

    @property
    def tgtlang(self):
        if self.tgtlang_1 == Languages.TradChinese:
            return "ZH-HANT"
        return self.tgtlang_1.upper()

    def translate(self, translateText):
        if self.config["usewhich"] == 0:

            return self.translate_via_deeplx(translateText)
        elif self.config["usewhich"] == 1:
            if not self.devtool:
                self.devtool = cdp_deepl(self)
            return self.devtool.translate(translateText)

    def translate_via_deeplx(self, query):
        self.checkempty(["api"])
        payload = {
            "text": query,
            "source_lang": self.srclang,
            "target_lang": self.tgtlang,
        }

        response = self.proxysession.post(self.multiapikeycurrent["api"], json=payload)

        try:
            return response.json()["data"]
        except:
            raise Exception(response)
