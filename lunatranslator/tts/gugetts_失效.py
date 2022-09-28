   
import os
import re
import requests 
import datetime
import base64
from traceback import print_exc
from utils.config import globalconfig 
import time 
import re
class tts():
    
    def __init__(self,signal,signalshow): 
        self.signal=signal
        html=requests.get('https://translate.google.cn/',proxies={'http':None,'https':None}).text
        self.bl=re.search('"cfb2h":"(.*?)"',html).groups()[0]
        self.data=None
        signalshow.emit('语音朗读加载完毕','#0000ff')
    def read(self,content,usevoice):
         
        try: 
            headers = {
                    'authority': 'translate.google.cn',
                    'accept': '*/*',
                    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'cache-control': 'no-cache',
                    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'origin': 'https://translate.google.cn',
                    'pragma': 'no-cache',
                    'referer': 'https://translate.google.cn/',
                    'sec-ch-ua': '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
                    'sec-ch-ua-arch': '"x86"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-full-version': '"105.0.1343.53"',
                    'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", " Not;A Brand";v="99.0.0.0", "Chromium";v="105.0.5195.127"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-ch-ua-platform-version': '"10.0.0"',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
                    'x-same-domain': '1',
                }
            
            params = {
                'rpcids': 'jQ1olc',
                'source-path': '/',
                'f.sid': '-8046362090827789675',
                'bl': self.bl,
                'hl': 'zh-CN',
                'soc-app': '1',
                'soc-platform': '1',
                'soc-device': '1',
                '_reqid': '405556',
                'rt': 'c',
            } 
            from urllib.parse import quote 
            #data = 'f.req=%5B%5B%5B%22jQ1olc%22%2C%22%5B%5C%22%E4%BD%A0%E5%A5%BD1%5C%22%2C%5C%22ja%5C%22%2Cnull%2C%5C%22null%5C%22%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&'
            print(1,content,1)
            data = 'f.req=%5B%5B%5B%22jQ1olc%22%2C%22%5B%5C%22'+quote(content)+'%5C%22%2C%5C%22ja%5C%22%2Cnull%2C%5C%22null%5C%22%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&'
            print(data)
            import json
            try:
                response = requests.post('https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute', params=params,  headers=headers,  data=data,proxies={'http':None,'https':None})
                print(response.text)
                res=response.text.split('\n')[3]
                res=json.loads(res)
                b64=res[0][2]
                
                b64=json.loads(b64)[0]
    
                fname=str(time.time()) 
                with open('./files/ttscache/'+fname+'.mp3','wb') as ff:
                    ff.write(base64.b64decode(bytes(b64,encoding='utf-8')))
            except:
                print_exc()
                return 
            self.signal.emit('./files/ttscache/'+fname+'.mp3')
            
        except:
            print_exc()
            pass
     
if __name__=='__main__':
    js=edgetts()   
    js.read('アマツツミ + 予約特典 +同梱特典',0)
     