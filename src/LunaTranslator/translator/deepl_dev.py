from urllib.parse import quote
from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://www.deepl.com/en/translator"

    @property
    def srclang(self):
        if self.srclang_1 == "cht":
            return "zh"
        return self.srclang_1

    @property
    def tgtlang(self):
        if self.tgtlang_1 == "cht":
            return "zh-hant"
        return self.tgtlang_1

    def translate(self, content):
        self.Page_navigate(
            "https://www.deepl.com/en/translator#{}/{}/{}".format(
                self.parse_maybe_autolang(content), self.tgtlang, quote(content)
            )
        )
        return self.wait_for_result(
            'document.getElementsByTagName("d-textarea")[1].textContent',
            ("complete", ""),
            multi=True,
        )
