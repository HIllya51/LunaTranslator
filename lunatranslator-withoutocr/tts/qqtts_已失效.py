   
import os
import re
import requests 
from traceback import print_exc
from utils.config import globalconfig 
import time 
class tts():
    
    def __init__(self,signal,signalshow): 
        self.signal=signal
        self.session=requests.session()
        self.session.headers.update({
                    
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'Origin': 'https://fanyi.qq.com',
            'Referer': 'https://fanyi.qq.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
         
        })
        self.session.get('https://fanyi.qq.com',proxies=  {'http': None,'https': None})
        self.data=None
        signalshow.emit('语音朗读加载完毕','#0000ff')
    def read(self,content,usevoice):
        print('reading',content)
        try: 
            if self.data is None:
                self.data = {
                    
                }

            response = self.session.post('https://fanyi.qq.com/api/reauth12f', data=self.data,proxies=  {'http': None,'https': None})

            self.data=response.json()
            self.session.cookies.update(self.data)
            print(self.data)
            import uuid
            params = {
                'platform': 'PC_Website',
                'lang': 'zh',
                'text': content,
                'guid': uuid.uuid1(),
            }
            fname=str(time.time())
            response = requests.get('https://fanyi.qq.com/api/tts',headers=self.session.headers, params=params ,proxies=  {'http': None,'https': None} ) 
            with open('./files/ttscache/'+fname+'.mp3','wb') as ff:
                ff.write(response.content)
                        
            self.signal.emit('./files/ttscache/'+fname+'.mp3')
            
        except:
            print_exc()
            pass
     
if __name__=='__main__':
    js=edgetts()   
    js.read('アマツツミ + 予約特典 +同梱特典',0)
     