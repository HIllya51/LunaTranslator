 
 
import json
from translator.basetranslator_dev import basetransdev
import time
 
class TS(basetransdev): 
    target_url='https://www.phind.com/agent'
    def langmap(self):
        return {'zh': 'Simplified Chinese', 'ja': 'Japanese', 'en': 'English', 'ru': 'Russian', 'es': 'Spanish', 'ko': 'Korean', 'fr': 'French', 'cht': 'Traditional Chinese', 'vi': 'Vietnamese', 'tr': 'Turkish', 'pl': 'Polish', 'uk': 'Ukrainian', 'it': 'Italian', 'ar': 'Arabic', 'th': 'Thai'}
    def translate(self,content):
        content='Please help me translate the following {} text into {}, and you should only tell me the translation.\n'.format(self.srclang,self.tgtlang)+content

        num=self.wait_for_result('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.mt-8").children.length''')
        if num==1:
            num=0
        self.Runtime_evaluate('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.fixed-bottom.bg-gradient-light > div > div > div.col-12 > div > form > div > textarea").click()''')
        self.send_keys(content)
        self.Runtime_evaluate('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.fixed-bottom.bg-gradient-light > div > div > div.col-12 > div > form > div > div > button").click()''')
        if self.config['流式输出']==False:
            self.wait_for_result('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.fixed-bottom.bg-gradient-light > div > div > div.col-12 > div > button")''')   #不为null时会exception continue
            yield self.wait_for_result('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.mt-8 > div:nth-child({}) > div > div > div > div:nth-child(1) > div:nth-child(3)").textContent'''.format(num+2))
        else:
            currtext=''
            while True:
                time.sleep(0.1)
                newcurr=self.wait_for_result('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.mt-8 > div:nth-child({}) > div > div > div > div:nth-child(1) > div:nth-child(3)").textContent'''.format(num+2))
                if newcurr=='...':continue
                yield newcurr[len(currtext):]
                currtext=newcurr
                if 'className' not in (self.Runtime_evaluate('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.fixed-bottom.bg-gradient-light > div > div > div.col-12 > div > button")'''))['result']:
                    newcurr=self.wait_for_result('''document.querySelector("#__next > div > div > div.col-lg-12.sidebar > main > div > div > div > div > div.mt-8 > div:nth-child({}) > div > div > div > div:nth-child(1) > div:nth-child(3)").textContent'''.format(num+2))
                    yield newcurr[len(currtext):]
                    break

                