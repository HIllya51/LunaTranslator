from translator.basetranslator_dev import basetransdev
import time

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
        return self.wait_for_result(
            r"""childs=document.querySelector("#texttarget > div").children;
t=""
for(i=0;i<childs.length;i++){
	x="#texttarget > div > div:nth-child("+(i+1)+") > span"
	if(document.querySelector(x)){
	if(t.length)t+="\n"
	t+=document.querySelector(x).innerText
}
}
t
"""
        )
