   
import os
import re
import base64
import requests 
from traceback import print_exc
from utils.config import globalconfig 
import time 
class tts():
    
    def __init__(self,showlist): 
        self.voicelist=['jp_male_satoshi','jp_female_mai']
        showlist.emit(self.voicelist)
        self.speaking=None
    def read(self,content,usevoice):
        print('reading',content)
        i=self.voicelist.index(globalconfig['huoshantts']['voice'])
        try: 
            headers = {
                'authority': 'translate.volcengine.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'chrome-extension://klgfhbdadaspgppeadghjjemk',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'none',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            }

            json_data = {
                'text': 'おはよう',
                'speaker': 'jp_male_satoshi',
            }#
            response = requests.post('https://translate.volcengine.com/crx/tts/v1/',  headers=headers, json=json_data)
            fname=str(time.time())
            b64=base64.b64decode(response.json()['audio']['data'])
            with open('./files/ttscache/'+fname+'.mp3','wb') as ff:
                ff.write(b64)
                        
            self.signal.emit('./files/ttscache/'+fname+'.mp3')
            
        except:
            print_exc()
            pass
     
if __name__=='__main__':
    js=edgetts()   
    js.read('アマツツミ + 予約特典 +同梱特典',0)
     