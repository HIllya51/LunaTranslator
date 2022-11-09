
from traceback import print_exc 
 
import requests
from urllib import parse 
import os

from utils.config import globalconfig,translatorsetting
import re 
from translator.basetranslator import basetrans  
import json
class TS(basetrans):  
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query): 
        js=translatorsetting[self.typename]
        if js['args']['DeepL-Auth-Key']=="":
            return 
        else:
            appid = js['args']['DeepL-Auth-Key'] 
  
        headers = {
        'Authorization': 'DeepL-Auth-Key '+appid,
        'Content-Type': 'application/x-www-form-urlencoded',
                }

        data = 'text='+parse.quote(query)+'&target_lang='+self.tgtlang+'&source_lang='+self.srclang
        if globalconfig['useproxy']:
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data ).json()  
        else:
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data ,proxies={"https":None,"http":None}).json()  
        js['args']['字数统计']=str(int(js['args']['字数统计'])+len(query))
        js['args']['次数统计']=str(int(js['args']['次数统计'])+1) 
        #print(res['trans_result'][0]['dst'])
        return response['translations'][0]['text']
    
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))