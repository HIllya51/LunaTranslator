 
 
from translator.basetranslator_dev import basetransdev 
 
class TS(basetransdev):  
    target_url='https://translate.yandex.com/'
     
    def translate(self,content):   
        self.Runtime_evaluate('document.querySelector("#translation > span").innerText=""') 
        self.Runtime_evaluate('i=document.querySelector("#fakeArea");i.innerText=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});i.dispatchEvent(event);'.format(content)) 
        return self.wait_for_result('document.querySelector("#translation > span").innerText') 
        