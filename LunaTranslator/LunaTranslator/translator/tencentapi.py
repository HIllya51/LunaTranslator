 
from traceback import print_exc 
import requests  
from utils.config import globalconfig  
from translator.basetranslator import basetrans  
import time
import base64
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
import os
def get_string_to_sign(method, endpoint, params):
    s = method + endpoint + "/?"
    query_str = "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    return s + query_str


def sign_str(key, s, method):
    hmac_str = hmac.new(key.encode("utf8"), s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)


def trans_tencent(q ,secret_id,secret_key,proxy, fromLang='auto', toLang='en'):
    
    endpoint = "tmt.tencentcloudapi.com"
    data = {
        'SourceText': q,
        'Source': fromLang,
        'Target': toLang,
        'Action': "TextTranslate",
        'Nonce': random.randint(32768, 65536),
        'ProjectId': 0,
        'Region': 'ap-hongkong',
        'SecretId': secret_id,
        'SignatureMethod': 'HmacSHA1',
        'Timestamp': int(time.time()),
        'Version': '2018-03-21',
    }
    s = get_string_to_sign("GET", endpoint, data)
    data["Signature"] = sign_str(secret_key, s, hashlib.sha1)

    # 此处会实际调用，成功后可能产生计费
    r = requests.get("https://" + endpoint, params=data, timeout=3,proxies=proxy)
    # print(r.json())
    return r.json()['Response']['TargetText']
class TS(basetrans): 
    def langmap(self):
        return {'cht':'zh-TW'}
    def translate(self,query):  
        self.checkempty(['SecretId','SecretKey'])
        
        appid = self.config['SecretId']
        secretKey = self.config['SecretKey']
        if '|' in appid:
            SecretIds = self.config['SecretId'].split('|')
            SecretKeys = self.config['SecretKey'].split('|')
            id_length = len(SecretIds)
            if id_length != len(SecretKeys):
                appid = SecretIds[0]
                secretKey = SecretKeys[0]
            else:
                self.multiapikeycurrentidx = self.multiapikeycurrentidx % id_length
                appid = SecretIds[self.multiapikeycurrentidx]
                secretKey = SecretKeys[self.multiapikeycurrentidx]
                self.multiapikeycurrentidx += 1
                
        try:
            ret=trans_tencent(query,appid,secretKey,self.proxy,self.srclang,self.tgtlang) 
            self.countnum(query)
            return ret  
        except:
            raise Exception(ret)