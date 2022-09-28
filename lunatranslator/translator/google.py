 
import requests
from urllib.parse import quote
import re
import json  
from translator.basetranslator import basetrans
import time
class TS(basetrans):
    
    def inittranslator(self)  : 
        self.typename='google'
        self.updateheader('https://translate.google.cn')
        #self.session1= httpx.Client(headers=self.headers)
    def show(self,res):
        print('谷歌','\033[0;32;47m',res,'\033[0m',flush=True)
    def realfy2(self,content): 
        
        params = {
            'sl': 'ja',
            'tl': 'zh-CN',
            'hl': 'zh-CN',
            'q': content,
        }
        try:
            response = self.session.get('https://translate.google.cn/m', params=params,  timeout=5, proxies=  {'http': None,'https': None})
        except requests.exceptions.ConnectTimeout:
            return ''
        except requests.exceptions.ReadTimeout:
            return ''
        try:
            res=re.search('<div class="result-container">(.*?)</div>',response.text).groups()
        except:
            return ''
         
        return res[0]
   
    def realfy(self,content):
        s=self.realfy2(content)
        #print(s,time.time()-t1)
        return s
if __name__=='__main__':
    g=GOO()
    print(g.gettask('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))