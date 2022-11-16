
from traceback import print_exc 
 
import requests
from urllib import parse 
import os

from utils.config import globalconfig,translatorsetting
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
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query): 
        js=translatorsetting[self.typename]
        if js['args']['APP ID']=="":
            return 
        else:
            appid = js['args']['APP ID']
            secretKey = js['args']['密钥']
  
        myurl = '/api/trans/vip/translate'

        fromLang = self.srclang   #原文语种
        toLang = self.tgtlang   #译文语种
        salt = random.randint(32768, 65536)
        q= query
        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
        
        res=self.session.get('https://api.fanyi.baidu.com'+myurl,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None}).json()  
        js['args']['字数统计']=str(int(js['args']['字数统计'])+len(query))
        js['args']['次数统计']=str(int(js['args']['次数统计'])+1)
         
        return '\n'.join([_['dst'] for _ in res['trans_result']])  
         
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))