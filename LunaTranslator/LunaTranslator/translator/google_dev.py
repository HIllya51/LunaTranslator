from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    target_url = "https://translate.google.com/"

    def translate(self, content):
        if "lastlang" not in dir(self) or self.lastlang != (self.srclang, self.tgtlang):
            self.Page_navigate(
                "https://translate.google.com/?sl={}&tl={}".format(
                    self.srclang, self.tgtlang
                )
            )
            self.lastlang = (self.srclang, self.tgtlang)
        self.Runtime_evaluate(
            'textarea=document.querySelector("textarea");textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea=document.querySelector("textarea");textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(
                content
            )
        )
        return self.wait_for_result(
            'document.querySelector("#yDmH0d > c-wiz > div > div.ToWKne > c-wiz > div.OlSOob > c-wiz > div.ccvoYb > div.AxqVh > div.OPPzxe > c-wiz.sciAJc > div > div.usGWQd > div > div.lRu31").innerText'
        )
