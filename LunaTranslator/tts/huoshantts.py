import threading
from traceback import print_exc
import requests
from utils.config import globalconfig    
import base64
import os
import time
class tts():
    
    def __init__(self,showlist,mp3playsignal): 
        self.voicelist=['jp_male_satoshi','jp_female_mai','zh_male_rap','zh_female_sichuan','zh_male_xiaoming','zh_male_zhubo','zh_female_zhubo','zh_female_qingxin','zh_female_story','en_male_adam','en_male_bob','en_female_sarah']
        showlist.emit(self.voicelist)
        
        if  len(self.voicelist)>0 and globalconfig['reader']['huoshantts']['voice'] not in self.voicelist: 
            globalconfig['reader']['huoshantts']['voice']=self.voicelist[0]
        self.speaking=None
        self.speaking=None
        self.mp3playsignal=mp3playsignal
    def read(self,content):
        threading.Thread(target=self.read_t,args=(content,)).start()
         
    def read_t(self,content):
        print('reading',content)
        if len(content)=='':
            return
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
                'text': content,
                'speaker': globalconfig['reader']['huoshantts']['voice'],
            }#
            response = requests.post('https://translate.volcengine.com/crx/tts/v1/',  headers=headers, json=json_data,proxies={'http':None,'https':None})
            fname=str(time.time())
            b64=base64.b64decode(response.json()['audio']['data'])
             
            with open('./ttscache/'+fname+'.mp3','wb') as ff:
                ff.write(b64)
                        
            self.mp3playsignal.emit('./ttscache/'+fname+'.mp3',globalconfig["ttscommon"]["volume"])
            
        except:
            print_exc()
            pass
     
if __name__=='__main__':
    js=edgetts()   
    js.read('アマツツミ + 予約特典 +同梱特典',0)
     