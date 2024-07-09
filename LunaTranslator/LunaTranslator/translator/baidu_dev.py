from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://fanyi.baidu.com/mtpe-individual/multimodal"

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
            """document.querySelector("#editor-text > div.AZLVLJHb > div.Ssl84aLh > span").click()"""
        )
        self.Runtime_evaluate(
            """document.querySelector("#editor-text > div.AZLVLJHb > div.Ssl84aLh > div.NNh5PamB.GEptIbSX > div > div").click()"""
        )
        self.send_keys(content)
        return self.wait_for_result(
            """document.querySelector("#trans-selection").innerText"""
        )
