 
import requests
from urllib.parse import quote
import re
import json  
from translator.basetranslator import basetrans
import time
class TS(basetrans):
    
    def inittranslator(self)  : 
        self.typename='google2'
        self.updateheader('https://translate.google.cn') 
     
    def realfy1(self,content): 
        t1=time.time()
        params = {
            'rpcids': 'MkEWBc',
            'source-path': '/',
            'f.sid': '2488443761035659778',
            'bl': 'boq_translate-webserver_20220907.09_p0',
            'hl': 'zh-CN',
            'soc-app': '1',
            'soc-platform': '1',
            'soc-device': '1',
            '_reqid': '86225',
            'rt': 'c',
        }
        
        data = 'f.req=%5B%5B%5B%22MkEWBc%22%2C%22%5B%5B%5C%22'+quote(content)+'%5C%22%2C%5C%22ja%5C%22%2C%5C%22zh-CN%5C%22%2Ctrue%5D%2C%5Bnull%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&'
         
        response = self.session.post('https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute', params=params , data=data, proxies=  {'http': None,'https': None})
        good=response.text.split('\n')[3]
         
        good=json.loads(good) 
        res=good[0][2] 
        res=json.loads(res)
        #print(json.dumps(res,ensure_ascii=False))
        #print(time.time()-t1)
        res=res[1][0][0][-1][0][0]
        return res
   
    def realfy(self,content): 
        s=self.realfy1(content)
        #print(s,time.time()-t1)
        return s  