
from traceback import print_exc 
 
import requests  

from utils.config import globalconfig,translatorsetting
import re 
from translator.basetranslator import basetrans  
import json
from urllib.parse import quote
class TS(basetrans):   
    def translate(self,query): 
        js=translatorsetting[self.typename]
        if js['args']['key']=="":
            return 
        else:
            key = js['args']['key'] 
   
        params={'key': key,'source':self.srclang, 'target':self.tgtlang, 'q':  (query)}
        response = requests.get("https://translation.googleapis.com/language/translate/v2/",params=params )
         
        return response.json()['data']['translations'][0]['translatedText']
     