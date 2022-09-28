 
from traceback import print_exc
import requests
from urllib.parse import quote
import re
import json  
from translator.basetranslator import basetrans
import time
class TS(basetrans):
    
    def inittranslator(self)  : 
        self.typename='xiuniu'
        
    def realfy(self,content): 
        with requests.session() as sess:
            sess.get('https://niutrans.com/trans?type=text', proxies=  {'http': None,'https': None})
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Origin': 'https://niutrans.com',
                'Pragma': 'no-cache',
                'Referer': 'https://niutrans.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
                'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params = {
                'from': 'ja',
                'to': 'zh',
                'src_text': content,
                'source': 'text',
                'dictNo': '',
                'memoryNo': '',
                'isUseDict': '0',
                'isUseMemory': '0',
                'time': str(int(time.time()*1000)),
            }
            try:
                response = sess.get('https://test.niutrans.com/NiuTransServer/testaligntrans', params=params , headers=headers, proxies=  {'http': None,'https': None})
             
                res=response.json()['tgt_text']
            except:
                print_exc()
                return '出错了'
         
        return res 
   
if __name__=='__main__':
    g=GOO()
    print(g.gettask('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))