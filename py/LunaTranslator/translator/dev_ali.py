from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://translate.alibaba.com/"

    def translate(self, content):
        self.Runtime_evaluate('document.querySelector("#pre").innerText=""')
        self.Runtime_evaluate(
            'i=document.querySelector("#source");i.value=``;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);i.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'.format(
                content
            )
        )
        return self.wait_for_result('document.querySelector("#pre").innerText')
