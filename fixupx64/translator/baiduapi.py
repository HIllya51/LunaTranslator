 
 
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
    
    def inittranslator(self)  : 
        self.typename='baiduapi'
         
    def realfy(self,query): 
                
        if os.path.exists(globalconfig['fanyi'][self.typename]['otherpath']) and globalconfig['fanyi'][self.typename]['args']['APP ID']=="":
            with open(globalconfig['fanyi'][self.typename]['otherpath'],'r',encoding='utf8') as ff:
                js=json.load(ff)
            appid=js['APP ID']
            secretKey=js['密钥']
        else:
            appid = globalconfig['fanyi'][self.typename]['args']['APP ID']
            secretKey = globalconfig['fanyi'][self.typename]['args']['密钥']

        httpClient = None
        myurl = '/api/trans/vip/translate'

        fromLang = 'auto'   #原文语种
        toLang = 'zh'   #译文语种
        salt = random.randint(32768, 65536)
        q= query
        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
        res=requests.get('https://api.fanyi.baidu.com'+myurl,proxies=  {'http': None,'https': None}).json()  
        return res['trans_result'][0]['dst']
        
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))