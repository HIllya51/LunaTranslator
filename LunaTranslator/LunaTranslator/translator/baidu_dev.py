from translator.basetranslator_dev import basetransdev
from urllib.parse import quote


class TS(basetransdev):
    target_url = "https://fanyi.baidu.com/#"

    def langmap(self):
        return {
            "es": "spa",
            "ko": "kor",
            "fr": "fra",
            "ja": "jp",
            "cht": "cht",
            "vi": "vie",
            "uk": "ukr",
        }

    def translate(self, content):
        self.Runtime_evaluate(
            "document.getElementsByClassName('textarea-clear-btn')[0].click()"
        )

        self.Page_navigate(
            "https://fanyi.baidu.com/#{}/{}/{}".format(
                self.srclang, self.tgtlang, quote(content)
            )
        )
        res = self.wait_for_result(
            "document.querySelector('div.output-bd')===null?'':document.querySelector('div.output-bd').innerText"
        ).replace("\n\n", "\n")
        return res
