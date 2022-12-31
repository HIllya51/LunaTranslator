
from traceback import print_exc 
 
import requests 
import os

from utils.config import globalconfig ,translatorsetting
from translator.basetranslator import basetrans  
import json
class TS(basetrans):  
    
    def translate(self,query): 
        js=translatorsetting[self.typename]
        if js['args']['app_id']=="":
            return 
        else:
            app_id = js['args']['app_id']  
            app_secret = js['args']['app_secret']  
        
                
        res=requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',headers={'Content-Type':"application/json; charset=utf-8"}, proxies=  {'http': None,'https': None},json={
            "app_id": app_id,
            "app_secret": app_secret
        })
        token=res.json()['tenant_access_token']
        res=requests.post('https://open.feishu.cn/open-apis/translation/v1/text/translate', proxies=  {'http': None,'https': None},headers={'Content-Type':"application/json; charset=utf-8",'Authorization':'Bearer '+token},json={
            "source_language": self.srclang,
            "text": query,
            "target_language": self.tgtlang,
            "glossary": [  ]
            })
        return res.json()['data']['text']
        
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))