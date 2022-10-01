 
from traceback import print_exc
import requests
from urllib.parse import quote
import re
import json  
from translator.basetranslator import basetrans
import time
class TS(basetrans):
    
    def inittranslator(self)  : 
        self.typename='byte'
          
    def realfy(self,content): 
                
                
        headers = {
            'authority': 'translate-crx.bytedance.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'auth': 'auth-v1/mt.content.ext/1664604057493/300/a15ee3975145d64ee59308207a8ca0192114b25fc52f10531a8f43e2488a77b',
            'cache-control': 'no-cache',
            'origin': 'chrome-extension://klgfhbiooeogdfodpopgppeadghjjemk',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'none',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
        }

        json_data = {
            'src_lang': None,
            'tgt_lang': 'zh',
            'mode': 0,
            'from': 'https://tieba.baidu.com/',
            'text': content,
            'browser': 0,
        }
        try:
                        
            response = requests.post('https://translate-crx.bytedance.com/e1/flask/translation',   headers=headers, json=json_data,timeout=5, proxies=  {'http': None,'https': None})

            return(response.json()['results'][0]['translate'][0])
        except:
            print_exc()
            return '出错了'
         
        return res[0]
   
if __name__=='__main__':
    g=GOO()
    print(g.gettask('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))