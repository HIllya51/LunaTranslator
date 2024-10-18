from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://niutrans.com/trans?type=text"

    def translate(self, content):
        self.Runtime_evaluate(
            '(a=document.querySelector("#textTrans > div.translation-box > div > div:nth-child(1) > div > i"))?a.click():"";i=document.querySelector("#textarea");i.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'.format(
                content
            )
        )
        return self.wait_for_result(
            "document.getElementsByClassName('results-container')[0].innerText"
        )
