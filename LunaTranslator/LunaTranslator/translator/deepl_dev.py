from urllib.parse import quote
from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://www.deepl.com/en/translator"

    def translate(self, content):
        self.Page_navigate(
            "https://www.deepl.com/en/translator#{}/{}/{}".format(
                self.srclang, self.tgtlang, quote(content)
            )
        )
        return self.wait_for_result(
            r"""document.evaluate('//*[@id="headlessui-tabs-panel-7"]/div/div[1]/section/div/div[2]/div[3]/section/div[1]/d-textarea/div',document).iterateNext().textContent"""
        )
