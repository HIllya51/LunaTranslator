import queue
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
    def srclang(self):
        return ['jap','eng'][globalconfig['srclang']]
     
    def translate(self, content):
            
        headers =  {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://www.youdao.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = requests.get('https://www.youdao.com/w/'+self.srclang()+'/'+quote(content)+'/',headers=headers,timeout = globalconfig['translatortimeout'], proxies=  {'http': None,'https': None}).text

             
         
            return re.search('<div class="trans-container">([\\s\\S]*?)<p>([\\s\\S]*?)</p>([\\s\\S]*?)<p>([\\s\\S]*?)</p>',response).groups()[3] 
        except:
            print(response)
            self.inittranslator()
            print_exc()
            return '出错了'