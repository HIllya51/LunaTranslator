
from traceback import print_exc 
 
import requests  
 
from translator.basetranslator import basetrans  
import json
class TS(basetrans):  
    def langmap(self):
        return {"cht":"zh-Hant"}
    def translate(self,query):  
        if self.config['app_id'].strip()=="" or self.config['app_secret'].strip()=="":
            return 
        else:
            app_id = self.config['app_id'].strip()  
            app_secret = self.config['app_secret'].strip()  
        
                
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
         