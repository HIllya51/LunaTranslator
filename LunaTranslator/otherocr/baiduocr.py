import requests
import base64
import os
import json
import time
from utils.config import globalconfig
def default():
    return {
            "args": {
                "注册网址": "https://cloud.baidu.com/product/ocr",
                "API Key": "",
                "Secret Key": "",
                "access_token": "",
                "备注":"可以只填写API Key和Secret Key;也可以只填写access_token;优先使用API Key和Secret Key", 
                "次数统计": "0"
            },
            "notwriteable": [ 
                "备注",
                "注册网址", 
                "次数统计"
            ]
        }
cacheapikey=("","")
cacheaccstoken=""
def ocr(imgfile):
    global cacheapikey,cacheaccstoken
    configfile=globalconfig['ocr']['baiduocr']['argsfile']
    if os.path.exists(configfile) ==False:
            return ''
    with open(configfile,'r',encoding='utf8') as ff:
        js=json.load(ff)

    appid = js['args']['API Key']
    secretKey = js['args']['Secret Key']
    cacheaccstoken=js['args']['access_token']
    if (appid,secretKey)!=cacheapikey:
        try:
            cacheaccstoken=requests.get('https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+appid+'&client_secret='+secretKey, proxies=  {'http': None,'https': None}).json()['access_token']
            cacheapikey=(appid,secretKey)
            
        except:
            #appid无效，则使用输入的accstoken，并清空
            pass

    if cacheaccstoken=="":
        
        return ''
     
        
    #print(cacheaccstoken)
    headers = {
        'authority': 'aip.baidubce.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'chrome-extension://hmpjibmn1ncjokocepchnea',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'none',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
    }

    params = {
        'access_token':cacheaccstoken# '',
    }
    with open(imgfile,'rb') as ff:
        f=ff.read()
    b64=base64.b64encode(f)
    data = {
        'image': b64 ,
        'detect_language': 'true',
    # 'language_type': 'CHN_ENG',
        }
    js['args']['次数统计']=str(int(js['args']['次数统计'])+1)
    with open(configfile,'w',encoding='utf-8') as ff:
        ff.write(json.dumps(js,ensure_ascii=False,sort_keys=False, indent=4))
    response = requests.post('https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic', params=params, headers=headers, data=data, proxies=  {'http': None,'https': None})
    try:
        return ''.join([x['words']  for x in response.json()['words_result']])
    except:
        print(response.text)
        if 'error_msg' in response.json():
            return response.json()['error_msg']
        
        return ''
if __name__=="__main__":
    baiduocr('1.jpg')