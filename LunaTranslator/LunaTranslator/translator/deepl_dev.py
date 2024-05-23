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
            r"""document.querySelector("#textareasContainer > div.rounded-ee-inherit.relative.min-h-\\[240px\\].min-w-0.md\\:min-h-\\[clamp\\(250px\\,50vh\\,557px\\)\\].mobile\\:min-h-0.mobile\\:flex-1.max-\\[768px\\]\\:min-h-\\[375px\\] > section > div.rounded-inherit.mobile\\:min-h-0.relative.flex.flex-1.flex-col > d-textarea").textContent"""
        )
