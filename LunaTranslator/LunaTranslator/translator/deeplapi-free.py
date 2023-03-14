 
import requests
from urllib import parse  
from utils.exceptions import ApiExc
from utils.config import globalconfig  
from translator.basetranslator import basetrans   
class TS(basetrans):  
    def langmap(self):
        return  {"zh":"ZH","ja":"JA","en":"EN","es":"ES","fr":"FR","ru":"RU"}
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query):  
        self.checkempty(['DeepL-Auth-Key'])

        appid = self.config['DeepL-Auth-Key']
  
        headers = {
        'Authorization': 'DeepL-Auth-Key '+appid,
        'Content-Type': 'application/x-www-form-urlencoded',
                }

        data = 'text='+parse.quote(query)+'&target_lang='+self.tgtlang+'&source_lang='+self.srclang
        if globalconfig['useproxy']:
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data )
        else:
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data ,proxies={"https":None,"http":None}) 
        
        try:
            #print(res['trans_result'][0]['dst'])
            _= response.json()  ['translations'][0]['text']
        
            self.countnum(query)
            return _
        except:
            raise ApiExc(response.text)
     