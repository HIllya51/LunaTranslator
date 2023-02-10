 
from traceback import print_exc
import requests
from urllib.parse import quote
import re 
from utils.config import globalconfig
import json  
from translator.basetranslator import basetrans
import time
class TS(basetrans): 
    def translate(self,content):  

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42',
            'sec-ch-ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'lang': self.srclang+"_"+self.tgtlang,
            'src': content,
        }

        response = requests.get('https://sz-nmt-1.cloudtranslation.com/nmt', params=params, headers=headers,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None}).content.decode('utf8' )

        return response 
if __name__=='__main__':
    g=TS()
    print(g.translate("おはよう\nおはよう"))