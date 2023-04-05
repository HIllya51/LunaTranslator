
from traceback import print_exc 
 
import requests  
from translator.basetranslator import basetrans  
import json
class TS(basetrans):  
    def langmap(self):
        return {"cht":"zh-Hant"}
    def translate(self,query):  
        self.checkempty(['app_id','app_secret'])
         
        app_id = self.config['app_id']
        app_secret = self.config['app_secret']
        
                
        res=requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',headers={'Content-Type':"application/json; charset=utf-8"}, proxies= self.proxy,json={
            "app_id": app_id,
            "app_secret": app_secret
        })
        token=res.json()['tenant_access_token']
        res=requests.post('https://open.feishu.cn/open-apis/translation/v1/text/translate', proxies=  self.proxy,headers={'Content-Type':"application/json; charset=utf-8",'Authorization':'Bearer '+token},json={
            "source_language": self.srclang,
            "text": query,
            "target_language": self.tgtlang,
            "glossary": [  ]
            })
        try:
            return res.json()['data']['text']
        except:
            raise Exception(res.text)
         