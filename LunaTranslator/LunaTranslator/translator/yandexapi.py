import requests
from translator.basetranslator import basetrans   
class TS(basetrans): 
     
    def translate(self, content): 
        if self.config['key'].strip()=="":
            return 
        else:
            key = self.config['key'].strip() 
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'    
    
        params = {
            'key': key,
            'lang': f'{self.srclang}-{self.tgtlang}' ,
            'text': content,
        }
        response = requests.get(url, params=params).json() 
        print(response)
        return response['text'][0]
    