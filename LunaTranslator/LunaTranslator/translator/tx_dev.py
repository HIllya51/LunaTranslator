from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://fanyi.qq.com/"

    def translate(self, content):
        tgtlist = [
            "zh",
            "en",
            "ja",
            "ko",
            "fr",
            "es",
            "it",
            "de",
            "tr",
            "ru",
            "pt",
            "vi",
            "id",
            "th",
            "ms",
            "ar",
            "hi",
        ]
        if self.tgtlang in tgtlist:
            tgtidx = tgtlist.index(self.srclang) + 1
        else:
            tgtidx = 1
        self.Runtime_evaluate(
            'document.querySelector("div.textpanel-tool.tool-close").click()'
        )
        self.Runtime_evaluate(
            """document.querySelector("#language-button-group-source > div.language-button-dropdown.language-source > ul > li:nth-child(1) > span").click();
            document.querySelector("#language-button-group-target > div.language-button-dropdown.language-target > ul > li:nth-child({}) > span");
            document.getElementsByClassName('textinput')[0].value=`{}`;
            document.getElementsByClassName('language-translate-button')[0].click();
            """.format(
                tgtidx, content
            )
        )
        return self.wait_for_result(
            "document.getElementsByClassName('textpanel-target-textblock')[0].innerText"
        )
