from translator.basetranslator_dev import basetransdev


class TS(basetransdev):
    target_url = "https://fanyi.caiyunapp.com/#/"

    def translate(self, content):
        self.Runtime_evaluate(
            'document.querySelector("#app > div > div.fanyi-containers.router > div.scrollable-content > div:nth-child(1) > div.lang-middle > div.choose-box > div.two-column-layout > div:nth-child(1) > div > div.column-choose-langBox > img.closeImg").click()'
        )
        self.Runtime_evaluate(
            'i=document.querySelector("#textarea");i.value=``;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);i.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'.format(
                content
            )
        )
        _ = self.wait_for_result(
            'document.querySelector("#target-textblock").innerText'
        )
        if _ == "通用模型翻译中":
            _ = self.wait_for_result(
                'document.querySelector("#target-textblock").innerText',
                "通用模型翻译中",
            )
        return _
