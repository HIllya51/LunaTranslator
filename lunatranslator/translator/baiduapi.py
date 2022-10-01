
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
    def inittranslator(self):
        self.session=requests.session()
    def translate(self,query): 
                
        if os.path.exists(globalconfig['fanyi'][self.typename]['otherpath']) and globalconfig['fanyi'][self.typename]['args']['APP ID']=="":
            with open(globalconfig['fanyi'][self.typename]['otherpath'],'r',encoding='utf8') as ff:
                js=json.load(ff)
            appid=js['APP ID']
            secretKey=js['密钥']
        else:
            appid = globalconfig['fanyi'][self.typename]['args']['APP ID']
            secretKey = globalconfig['fanyi'][self.typename]['args']['密钥']
  
        myurl = '/api/trans/vip/translate'

        fromLang = 'auto'   #原文语种
        toLang = 'zh'   #译文语种
        salt = random.randint(32768, 65536)
        q= query
        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
        try:
            res=self.session.get('https://api.fanyi.baidu.com'+myurl,timeout=5, proxies=  {'http': None,'https': None}).json()  
            globalconfig['fanyi'][self.typename]['args']['字数统计']=str(int(globalconfig['fanyi'][self.typename]['args']['字数统计'])+len(query))
            globalconfig['fanyi'][self.typename]['args']['次数统计']=str(int(globalconfig['fanyi'][self.typename]['args']['次数统计'])+1)
            with open('./files/config.json','w',encoding='utf-8') as ff:
                ff.write(json.dumps(globalconfig,ensure_ascii=False,sort_keys=False, indent=4))
            #print(res['trans_result'][0]['dst'])
            return res['trans_result'][0]['dst']
        except:
            print_exc()
            return '出错了'
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))