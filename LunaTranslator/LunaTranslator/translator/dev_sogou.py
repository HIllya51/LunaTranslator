from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://fanyi.sogou.com/"

    def translate(self, content):
        if "lastlang" not in dir(self) or self.lastlang != (self.srclang, self.tgtlang):
            self.Page_navigate(
                "https://fanyi.sogou.com/text?keyword=&transfrom={}&transto={}&model=general".format(
                    self.srclang, self.tgtlang
                )
            )
            self.lastlang = (self.srclang, self.tgtlang)
        self.Runtime_evaluate(
            r"""
document.querySelector("#J-container > div.translate-pc-main.text-translate > div.content-wrap > div > div.trans-box > div.trans-from > div > span").click()
textarea=document.querySelector("#trans-input");
event = new Event("input", {{bubbles: true, cancelable: true }});
textarea.dispatchEvent(event);
textarea=document.querySelector("textarea");
textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});
textarea.dispatchEvent(event);
                              """.format(
                content
            )
        )
        return self.wait_for_result('document.querySelector("#trans-result").innerText')
