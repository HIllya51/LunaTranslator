
from traceback import print_exc 
 
import requests
from urllib import parse 
import os

from utils.config import globalconfig
import re 
from translator.basetranslator import basetrans 
from js2py import EvalJs
import time

import http.client
import hashlib
import urllib
import random
import json
class TS(basetrans): 
    @classmethod
    def defaultsetting(self):
        return {
            "args": {
                "注册网址": "https://www.deepl.com/translator",
                "DeepL-Auth-Key": "", 
                "字数统计": "0",
                "次数统计": "0"
            },
            "notwriteable": [
                "注册网址",
                "字数统计",
                "次数统计"
            ]
        }
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query): 
        configfile=globalconfig['fanyi'][self.typename]['argsfile']
        if os.path.exists(configfile) ==False:
            return 
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        if js['args']['DeepL-Auth-Key']=="":
            return 
        else:
            appid = js['args']['DeepL-Auth-Key'] 
  
        headers = {
        'Authorization': 'DeepL-Auth-Key '+appid,
        'Content-Type': 'application/x-www-form-urlencoded',
                }

        data = 'text='+parse.quote(query)+'&target_lang='+self.tgtlang+'&source_lang='+self.srclang

        response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, verify=False, data=data ).json()  
        js['args']['字数统计']=str(int(js['args']['字数统计'])+len(query))
        js['args']['次数统计']=str(int(js['args']['次数统计'])+1)
        with open(configfile,'w',encoding='utf-8') as ff:
            ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
        #print(res['trans_result'][0]['dst'])
        return response['translations'][0]['text']
    
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))