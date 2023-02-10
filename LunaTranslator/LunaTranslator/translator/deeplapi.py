 
import requests
from urllib import parse  

from utils.config import globalconfig  
from translator.basetranslator import basetrans   
class TS(basetrans):  
     
    def translate(self,query):  
        if self.config['args']['DeepL-Auth-Key']=="":
            return 
        else:
            appid = self.config['args']['DeepL-Auth-Key'] 
  
        headers = {
        'Authorization': 'DeepL-Auth-Key '+appid,
        'Content-Type': 'application/x-www-form-urlencoded',
                }

        data = 'text='+parse.quote(query)+'&target_lang='+self.tgtlang+'&source_lang='+self.srclang
        if globalconfig['useproxy']:
            response = requests.post('https://api.deepl.com/v2/translate', headers=headers, verify=False, data=data ).json()  
        else:
            response = requests.post('https://api.deepl.com/v2/translate', headers=headers, verify=False, data=data ,proxies={"https":None,"http":None}).json()   
        self.config['args']['字数统计']=str(int(self.config['args']['字数统计'])+len(query))
        self.config['args']['次数统计']=str(int(self.config['args']['次数统计'])+1) 
        #print(res['trans_result'][0]['dst'])
        return response['translations'][0]['text']
     