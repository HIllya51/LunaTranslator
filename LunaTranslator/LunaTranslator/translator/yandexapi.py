
import requests
from translator.basetranslator import basetrans   
class TS(basetrans): 
     
    def translate(self, content): 
        self.checkempty(['key'])
        
        key = self.config['key']
        
        
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'    
    
        params = {
            'key': key,
            'lang': f'{self.srclang}-{self.tgtlang}' ,
            'text': content,
        }

        response = requests.get(url, params=params,proxies=self.proxy)
        
        try:
            return response.json() ['text'][0]
        except:
            raise Exception( response.text)
    