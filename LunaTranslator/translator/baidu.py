 
 
from traceback import print_exc
import requests
from urllib import parse 
import os
import re 
from translator.basetranslator import basetrans 
from js2py import EvalJs

from utils.config import globalconfig
import time
class TS(basetrans):
     
    def inittranslator(self)  :  
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             'Origin': 'https://fanyi.baidu.com',
            'Referer': 'https://fanyi.baidu.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.session = requests.Session()
        #self.session1= httpx.Client(headers=self.headers)
        index_url = 'https://fanyi.baidu.com/'
        
        self.session.get(url=index_url, headers=self.headers, proxies=  {'http': None,'https': None},timeout = globalconfig['translatortimeout'] )  #session自动生成cookie
        response_index = self.session.get(url=index_url ,headers=self.headers, proxies=  {'http': None,'https': None}  )
        
        self.token = re.findall(r"token: '([0-9a-z]+)'", response_index.text)[0]
        self.gtk = re.findall(r'gtk = "(.*?)"', response_index.text)[0]
         
        with open(os.path.join('./files/scripts/baidufanyi_encrypt.js'), 'r', encoding='utf-8') as f:
            baidu_js = f.read()
        #self.jsrun=execjs.get('local_node').compile(baidu_js)
        self.ctx=  EvalJs()
        self.ctx.execute(baidu_js)
        
        url = 'https://dlswbr.baidu.com/heicha/mm/2060/acs-2060.js'
     
        res = self.session.get(url,headers= self.headers )
        encrypt = re.findall("\w{10,16}", re.findall('p.run\(\[(.*?)\]\)', res.text, re.DOTALL)[0])
        self.timestamp = encrypt[0]
        self.timestamp=str(int(self.timestamp *1000))
  
    def translate(self,query):  
        
        #sign =self.jsrun.call('e', query, self.gtk)
            sign=self.ctx.e(query,self.gtk)
            translate_url = 'https://fanyi.baidu.com/#'+self.srclang +'/'+self.tgtlang +'/%s' % ''#( parse.quote(query))
            #acs_token = self.jsrun.call('ascToken', translate_url) 
            acs_token=self.timestamp+ self.ctx.ascToken(translate_url,self.timestamp )
            data = {
                'from': self.srclang ,
                'to': self.tgtlang ,
                'query': query,
                'transtype': 'realtime',
                'simple_means_flag': '3',
                'sign': sign,
                'token': self.token,
                'domain': 'common'
            }
            
            
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://fanyi.baidu.com',
                'Referer': 'https://fanyi.baidu.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
            headers["Acs-Token"]=acs_token
            translate_api = 'https://fanyi.baidu.com/v2transapi'
                    
        
            response = self.session.post(url=translate_api,headers=headers,   data=data,timeout = globalconfig['translatortimeout'],proxies=  {'http': None,'https': None})
            
            result ='\n'.join([_['dst'] for _ in response.json()['trans_result']['data']])  
            # params = {
            #     'req': 'check',
            #     'fanyi_src': query,
            #     'direction': self.srclang +'2'+self.tgtlang ,
            #     '_': int(time.time()*1000),
            # }
             
            #response = self.session.get('https://fanyi.baidu.com/pcnewcollection', params=params,timeout = globalconfig['translatortimeout'],proxies=  {'http': None,'https': None} )
            return result
         
        
    def show(self,res):
        print('百度','\033[0;32;47m',res,'\033[0m',flush=True)
     