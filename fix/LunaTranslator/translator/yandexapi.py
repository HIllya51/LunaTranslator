import time
import hashlib
from traceback import print_exc 
import requests
from translator.basetranslator import basetrans  
import uuid 

from utils.config import translatorsetting
import json
class TS(basetrans): 
     
    def translate(self, content):
        js=translatorsetting[self.typename]
        if js['args']['key']=="":
            return 
        else:
            key = js['args']['key'] 
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'    
    
        params = {
            'key': key,
            'lang': f'{self.srclang}-{self.tgtlang}' ,
            'text': content,
        }
        response = requests.get(url, params=params).json() 
        print(response)
        return response['text'][0]
    