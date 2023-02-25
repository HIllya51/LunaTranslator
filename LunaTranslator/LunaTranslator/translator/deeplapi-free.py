 
import requests
from urllib import parse  

from utils.config import globalconfig  
from translator.basetranslator import basetrans   
class TS(basetrans):  
    def langmap(self):
        return  {"zh":"ZH","ja":"JA","en":"EN","es":"ES","fr":"FR","ru":"RU"}
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query):  
        if self.config['DeepL-Auth-Key']=="":
            return 
        else:
            appid = self.config['DeepL-Auth-Key'].strip() 
  
        headers = {
        'Authorization': 'DeepL-Auth-Key '+appid,
        'Content-Type': 'application/x-www-form-urlencoded',
                }

        data = 'text='+parse.quote(query)+'&target_lang='+self.tgtlang+'&source_lang='+self.srclang
        if globalconfig['useproxy']:
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data ).json()  
        else:
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data ,proxies={"https":None,"http":None}).json()  
        self.countnum(query)
        #print(res['trans_result'][0]['dst'])
        return response['translations'][0]['text']
     