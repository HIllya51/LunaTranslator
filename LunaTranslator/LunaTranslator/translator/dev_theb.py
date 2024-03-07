 
 
import json
from translator.basetranslator_dev import basetransdev
import time
 
class TS(basetransdev): 
    target_url='https://beta.theb.ai/'
    def langmap(self):
        return {'zh': 'Simplified Chinese', 'ja': 'Japanese', 'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'ko': 'Korean', 'fr': 'French', 'cht': 'Traditional Chinese', 'vi': 'Vietnamese', 'tr': 'Turkish', 'pl': 'Polish', 'uk': 'Ukrainian', 'it': 'Italian', 'ar': 'Arabic', 'th': 'Thai'}
    def translate(self,content):
        try:
            self.num=self.Runtime_evaluate('''document.querySelector("#html2canvas").children.length''')['result']['value']
            if self.num==1:
                self.num=0
        except:
            self.num=2
        print(self.num)
        self.Runtime_evaluate('''document.querySelector("#textareaAutosize").click()''')
        content='Please help me translate the following {} text into {}, and you should only tell me the translation.'.format(self.srclang,self.tgtlang)+'\n'+content
        self.send_keys(content)
        self.Runtime_evaluate(r'''document.querySelector("#INPUT > div.md\\:bg-white.md\\:dark\\:bg-n-6 > div.max-w-\\[66rem\\].m-auto.relative.z-2.border-2.border-n-3.rounded-xl.overflow-hidden.dark\\:border-n-5.bg-white.dark\\:bg-n-6 > div > button.group.absolute.right-3.bottom-2.rounded-xl.transition-colors.disabled\\:bg-slate-400.disabled\\:hover\\:bg-slate-400.disabled\\:cursor-no-drop.w-10.h-10.bg-primary-1.hover\\:bg-primary-1\\/90").click()''')
        if self.config['流式输出']==False:
            while 1:
                time.sleep(0.1)
                if 'stop' not in self.wait_for_result(r'''document.querySelector("#INPUT > div.md\\:bg-white.md\\:dark\\:bg-n-6 > div.flex.justify-center.relative > button").innerText''').lower():
                    break
            yield self.wait_for_result('''document.querySelector("#html2canvas > div:nth-child({}) > div.markdown.overflow-x-auto.prose").textContent'''.format(self.num+2))
        else:
            currtext=''
            while True:
                time.sleep(0.1)
                newcurr=self.wait_for_result('''document.querySelector("#html2canvas > div:nth-child({}) > div.markdown.overflow-x-auto.prose").textContent'''.format(self.num+2))
                if newcurr=='...':continue
                yield newcurr[len(currtext):]
                currtext=newcurr
                if 'stop' not in self.wait_for_result(r'''document.querySelector("#INPUT > div.md\\:bg-white.md\\:dark\\:bg-n-6 > div.flex.justify-center.relative > button").innerText''').lower():
                    newcurr=self.wait_for_result('''document.querySelector("#html2canvas > div:nth-child({}) > div.markdown.overflow-x-auto.prose").textContent'''.format(self.num+2))
                    yield newcurr[len(currtext):]
                    break