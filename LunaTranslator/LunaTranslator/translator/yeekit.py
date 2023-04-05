 
from traceback import print_exc
import requests
from urllib.parse import quote
import re

from utils.config import globalconfig
import json  
from translator.basetranslator import basetrans
import time
class TS(basetrans): 
    def langmap(self):
        return {"zh":"nzh","ja":"nja","en":"nen"} 
    def translate(self,content): 
                
                
                
        headers = {
            'authority': 'www.yeekit.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.yeekit.com',
            'referer': 'https://www.yeekit.com/site/translate',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
             'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'content[]': content,
            'sourceLang':self.srclang  ,
            'targetLang':self.tgtlang ,
        }

        response = requests.post('https://www.yeekit.com/site/dotranslate',   headers=headers, data=data,  proxies= self.proxy)
        res=''
        #print(response.json())
        for _ in response.json():
                
            _=json.loads(_)
            #print(_)
            res+=_['translation'][0]['translated'][0]['text']
        #print(res)
        return res 
if __name__=='__main__':
    g=GOO()
    print(g.gettask('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))