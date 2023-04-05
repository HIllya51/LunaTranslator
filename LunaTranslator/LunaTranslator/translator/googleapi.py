
from traceback import print_exc 
 
import requests  
from translator.basetranslator import basetrans   
from urllib.parse import quote
class TS(basetrans):   
    def langmap(self):
        return  { "zh":"zh-CN","cht":"zh-TW"} 
    def translate(self,query):  
        self.checkempty(['key'])

        key = self.config['key']
        
   
        params={'key': key,'source':self.srclang, 'target':self.tgtlang, 'q':  (query)}
        response = requests.get("https://translation.googleapis.com/language/translate/v2/",params=params ,proxies=self.proxy)
        
        try:
            return response.json()['data']['translations'][0]['translatedText']
        except:
            raise Exception(response.text)
     