
from distutils.command.config import config
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

import binascii
import hashlib
import hmac
import sys
import urllib.parse
import urllib.request
import time
import random
import requests
def sign(secretKey, signStr, signMethod): 
    if sys.version_info[0] > 2:
        signStr = signStr.encode("utf-8")
        secretKey = secretKey.encode("utf-8")
 
    if signMethod == 'HmacSHA256':
        digestmod = hashlib.sha256
    elif signMethod == 'HmacSHA1':
        digestmod = hashlib.sha1
 
    hashed = hmac.new(secretKey, signStr, digestmod)
    base64 = binascii.b2a_base64(hashed.digest())[:-1]

    if sys.version_info[0] > 2:
        base64 = base64.decode()

    return base64

def dictToStr(dictData): 
    tempList = []
    for eveKey, eveValue in dictData.items():
        tempList.append(str(eveKey) + "=" + str(eveValue))
    return "&".join(tempList)

 
def txfy(secretId,secretKey,content):
         
    
    timeData = str(int(time.time())) # 时间戳
    nonceData = int(random.random()*10000) # Nonce，官网给的信息：随机正整数，与 Timestamp 联合起来， 用于防止重放攻击
    actionData = "TextTranslate" # Action一般是操作名称
    uriData = "tmt.tencentcloudapi.com" # uri，请参考官网
    signMethod="HmacSHA256" # 加密方法
    requestMethod = "GET" # 请求方法，在签名时会遇到，如果签名时使用的是GET，那么在请求时也请使用GET
    regionData = "ap-hongkong" # 区域选择
    versionData = '2018-03-21' # 版本选择
    
    signDictData = {
        'Action' : actionData,
        'Nonce' : nonceData,
        'ProjectId':0,
        'Region' : regionData,
        'SecretId' : secretId,
        'SignatureMethod':signMethod,
        'Source': "ja",
        'SourceText':content,
        'Target': "zh",
        'Timestamp' : int(timeData),
        'Version':versionData ,
    }
    
    requestStr = "%s%s%s%s%s"%(requestMethod,uriData,"/","?",dictToStr(signDictData))
    
    signData = urllib.parse.quote(sign(secretKey,requestStr,signMethod))
    
    actionArgs = signDictData
    actionArgs["Signature"] = signData
    
    requestUrl = "https://%s/?"%(uriData) 
    requestUrlWithArgs = requestUrl + dictToStr(actionArgs)
    
    responseData = requests.get(requestUrlWithArgs,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None}).text

    #print(responseData)
     
    return (json.loads(responseData)["Response"]["TargetText"])
class TS(basetrans):
    @classmethod
    def defalutsetting(self):
        return {
            "args": {
                "注册网址": "https://console.cloud.tencent.com/cam/capi",
                "SecretId": "",
                "SecretKey": "",
                "字数统计": "0",
                "次数统计": "0"
            },
            "notwriteable": [
                "注册网址",
                "字数统计",
                "次数统计"
            ]
        }
    def translate(self,query): 
        configfile=globalconfig['fanyi'][self.typename]['argsfile']
        with open(configfile,'r',encoding='utf8') as ff:
            js=json.load(ff)
        if js['args']['SecretId']=="":
            return 
        else:
            appid = js['args']['SecretId']
            secretKey =js['args']['SecretKey']
   
        try:
            js['args']['字数统计']=str(int(js['args']['字数统计'])+len(query))
            js['args']['次数统计']=str(int(js['args']['次数统计'])+1)
            with open(configfile,'w',encoding='utf-8') as ff:
                ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
            ret=txfy(appid,secretKey,query)
            return ret
        except:

            print_exc()
            return '出错了'
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))