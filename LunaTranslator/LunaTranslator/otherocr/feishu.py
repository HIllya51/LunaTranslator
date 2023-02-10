import requests
import base64
import os
import json
import time
from utils.config import globalconfig,ocrsetting
 
cacheapikey=("","")
cacheaccstoken=""
def ocr(imgfile,lang,space):
    global cacheapikey,cacheaccstoken
    js=ocrsetting['feishu']

    app_id = js['args']['app_id']  
    app_secret = js['args']['app_secret']  
    
            
    res=requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',headers={'Content-Type':"application/json; charset=utf-8"}, proxies=  {'http': None,'https': None},json={
        "app_id": app_id,
        "app_secret": app_secret
    })
    token=res.json()['tenant_access_token']
    with open(imgfile,'rb') as ff:
        f=ff.read()
    b64=base64.b64encode(f)
    res=requests.post('https://open.feishu.cn/open-apis/optical_char_recognition/v1/image/basic_recognize', proxies=  {'http': None,'https': None},headers={'Content-Type':"application/json; charset=utf-8",'Authorization':'Bearer '+token},json={
    "image": str(b64,encoding='utf8'),
    })
    return space.join(res.json()['data']['text_list'])
if __name__=="__main__":
    baiduocr('1.jpg')