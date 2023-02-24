
from traceback import print_exc 
 
import requests  
  
from translator.basetranslator import basetrans   
from urllib.parse import quote
class TS(basetrans):   
    def langmap(self):
        return  { "zh":"zh-CN","cht":"zh-TW"} 
    def translate(self,query):  
        if self.config['args']['key']=="":
            return 
        else:
            key = self.config['args']['key'].strip() 
   
        params={'key': key,'source':self.srclang, 'target':self.tgtlang, 'q':  (query)}
        response = requests.get("https://translation.googleapis.com/language/translate/v2/",params=params )
         
        return response.json()['data']['translations'][0]['translatedText']
     