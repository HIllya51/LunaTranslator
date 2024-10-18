from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://fanyi.youdao.com/"

    def translate(self, content):
        self.Runtime_evaluate(
            'document.querySelector("#TextTranslate > div.source > div.text-translate-top-right > a").click()'
        )
        self.Runtime_evaluate(
            'i=document.querySelector("#js_fanyi_input");i.innerText=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'.format(
                content
            )
        )
        return self.wait_for_result(
            '(o=document.querySelector("#js_fanyi_output_resultOutput"))?o.textContent:""'
        )
