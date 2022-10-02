
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
                "注册网址": "https://fanyi-api.baidu.com/api/trans/product/desktop",
                "APP ID": "",
                "密钥": "",
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
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        if js['args']['APP ID']=="":
            return 
        else:
            appid = js['args']['APP ID']
            secretKey = js['args']['密钥']
  
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
            js['args']['字数统计']=str(int(js['args']['字数统计'])+len(query))
            js['args']['次数统计']=str(int(js['args']['次数统计'])+1)
            with open(configfile,'w',encoding='utf-8') as ff:
                ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
            #print(res['trans_result'][0]['dst'])
            return res['trans_result'][0]['dst']
        except:
            print_exc()
            return '出错了'
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))