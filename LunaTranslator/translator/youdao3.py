import time
import hashlib
from traceback import print_exc 
from urllib.parse import quote
from translator.basetranslator import basetrans  
import random 
import json

from utils.config import globalconfig
import requests
import re
class TS(basetrans):
     
    def inittranslator(self): 
        self.ss=requests.session()
        self.ss.get('https://m.youdao.com/translate',headers =  {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
             'Pragma': 'no-cache',
            'Referer': 'https://www.youdao.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }, proxies=  {'http': None,'https': None},timeout = globalconfig['translatortimeout']).text
    def translate(self, content):
        data = {
            'inputtext': content,
            'type': 'JA2ZH_CN',
        }
                
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
             'Origin': 'https://m.youdao.com',
            'Pragma': 'no-cache',
            'Referer': 'https://m.youdao.com/translate',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.ss.cookies.update({ '_yd_btn_fanyi_29': 'true',
    '_yd_newbanner_day': '29',})
        try:
            response = self.ss.post('https://m.youdao.com/translate',   data=data,headers=headers,timeout = globalconfig['translatortimeout'], proxies=  {'http': None,'https': None}).text
         
            return re.search('<ul id="translateResult">([\\s\\S]*?)<li>([\\s\\S]*?)</li>([\\s\\S]*?)<\/ul>',response).groups()[1] 
        except:
            print(response)
            self.inittranslator()
            print_exc()
            return '出错了'