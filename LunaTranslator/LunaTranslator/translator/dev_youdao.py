from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://fanyi.youdao.com/"

    def translate(self, content):

        self.Runtime_evaluate(
            '(a=document.querySelector("#TextTranslate > div.source > a"))?a.click():"";i=document.querySelector("#js_fanyi_input");i.innerText=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'.format(
                content
            )
        )
        return self.wait_for_result(
            '(o=document.querySelector("#js_fanyi_output_resultOutput"))?o.textContent:""'
        )
