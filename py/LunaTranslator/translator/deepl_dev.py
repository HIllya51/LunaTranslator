from urllib.parse import quote
import time
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
        if self.srclang == "auto":
            self.Runtime_evaluate(
                'document.querySelector("#translator-source-clear-button").click()'
            )
            self.Runtime_evaluate(
                "document.getElementsByTagName('d-textarea')[0].focus()"
            )
            self.send_keys(content)
            result = self.wait_for_result(
                'document.getElementsByTagName("d-textarea")[1].textContent',
                ("complete", ""),
                multi=True,
            )
            while True:
                href: str = self.wait_for_result("window.location.href")
                try:
                    src, tgt = href.split("#")[1].split("/")[:2]
                    break
                except:
                    time.sleep(0.1)
            if tgt != self.tgtlang:
                self.Page_navigate(
                    "https://www.deepl.com/en/translator#{}/{}/{}".format(
                        src, self.tgtlang, quote(content)
                    )
                )
                return self.wait_for_result(
                    'document.getElementsByTagName("d-textarea")[1].textContent',
                    ("complete", ""),
                    multi=True,
                )
            else:
                return result

        else:
            self.Page_navigate(
                "https://www.deepl.com/en/translator#{}/{}/{}".format(
                    self.srclang, self.tgtlang, quote(content)
                )
            )
            return self.wait_for_result(
                'document.getElementsByTagName("d-textarea")[1].textContent',
                ("complete", ""),
                multi=True,
            )
