  
import requests  

from utils.config import globalconfig 
from translator.basetranslator import basetrans 
class TS(basetrans):
    def langmap(self):
        return {"cht":"zh-Hant"}
    def translate(self,content): 
                
                
        headers = { 
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6', 
            'cache-control': 'no-cache', 
            'pragma': 'no-cache',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'none',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
        }

        json_data = {
                'text' : content,
                'source': self.srclang ,
                'target' : self.tgtlang
            } 
        
        response = requests.post('https://www.volcengine.com/api/exp/2/model-ii',   headers=headers, json=json_data,timeout=globalconfig['translatortimeout'], proxies= self.proxy)
            
        return '\n'.join([_['Translation'] for _ in response.json()['Result']['TranslationList'] ])
        
   
if __name__=='__main__':
    g=GOO()
    print(g.gettask('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))