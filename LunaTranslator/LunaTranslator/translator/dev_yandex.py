from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://translate.yandex.com/"

    def inittranslator(self):
        self.last = ""

    def translate(self, content):
        self.Runtime_evaluate('document.querySelector("#fakeArea").innerText=""')
        self.Runtime_evaluate('document.querySelector("#fakeArea").click()')
        self.send_keys(content)
        last = self.wait_for_result(
            'document.querySelector("#translation > span").innerText', self.last
        )
        self.last = last
        return self.last
