 
import requests
from urllib import parse  
from traceback import print_exc
from utils.config import globalconfig  
from translator.basetranslator import basetrans   
from utils import somedef

class TS(basetrans):
    def langmap(self):
        x={_:_.upper() for _ in somedef.language_list_translator_inner}
        x.pop('cht')
        return  x
    def translate(self,query):  
        self.checkempty(['DeepL-Auth-Key'])

        appid = self.config['DeepL-Auth-Key']
  
        headers = {
        'Authorization': 'DeepL-Auth-Key '+appid,
        'Content-Type': 'application/x-www-form-urlencoded',
                }

        data = 'text='+parse.quote(query)+'&target_lang='+self.tgtlang+'&source_lang='+self.srclang
        
        response = requests.post('https://api.deepl.com/v2/translate', headers=headers, verify=False, data=data )
        
        
        
        try:
            _= response.json()  ['translations'][0]['text']
        
            self.countnum(query)
            return _
        except:
            raise Exception(response.text)
     