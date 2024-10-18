from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://www.bing.com/translator/"

    def check_url_is_translator_url(self, url):
        return ".bing.com/translator/" in url

    def translate(self, content):
        self.Runtime_evaluate('document.getElementById("tta_clear").click();')
        self.Runtime_evaluate('document.querySelector("#tta_input_ta").click();')
        self.send_keys(content)
        return self.wait_for_result(
            "document.getElementById('tta_output_ta').value", " ..."
        )
