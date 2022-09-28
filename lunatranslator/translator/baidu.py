 
 
import requests
from urllib import parse 
import os
import re 
from translator.basetranslator import basetrans 
from js2py import EvalJs
import time
class TS(basetrans):
    
    def inittranslator(self)  : 
        self.typename='baidu'
        self.headers= {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        #self.session1= httpx.Client(headers=self.headers)
        index_url = 'https://fanyi.baidu.com/'
        
        self.session.get(url=index_url, headers=self.headers, proxies=  {'http': None,'https': None} )  #session自动生成cookie
        response_index = self.session.get(url=index_url , proxies=  {'http': None,'https': None}  )
        
        self.token = re.findall(r"token: '([0-9a-z]+)'", response_index.text)[0]
        self.gtk = re.findall(r'gtk = "(.*?)"', response_index.text)[0]
        dirname, filename = os.path.split(os.path.abspath(__file__))
        #print(self.gtk)
        with open(os.path.join('./files/scripts/baidufanyi_encrypt.js'), 'r', encoding='utf-8') as f:
            baidu_js = f.read()
        #self.jsrun=execjs.get('local_node').compile(baidu_js)
        self.ctx=  EvalJs()
        self.ctx.execute(baidu_js)
        
    def realfy(self,query): 
        #sign =self.jsrun.call('e', query, self.gtk)
        sign=self.ctx.e(query,self.gtk)
        translate_url = 'https://fanyi.baidu.com/#jp/zh/%s' % ( parse.quote(query))
        #acs_token = self.jsrun.call('ascToken', translate_url)
        acs_token=self.ctx.ascToken(translate_url)
        data = {
            'from': 'jp',
            'to': 'zh',
            'query': query,
            'transtype': 'realtime',
            'simple_means_flag': '3',
            'sign': sign,
            'token': self.token,
        }
         
        self.session.headers["Acs-Token"]=acs_token
        translate_api = 'https://fanyi.baidu.com/v2transapi'
        response = self.session.post(url=translate_api,   data=data,timeout=5,proxies=  {'http': None,'https': None})
        try:
            result = response.json()['trans_result']['data'][0]['dst']
        except:
            print(response.text)
            self.__init__()
            result=''
        params = {
            'req': 'check',
            'fanyi_src': query,
            'direction': 'jp2zh',
            '_': int(time.time()*1000),
        }

        response = self.session.get('https://fanyi.baidu.com/pcnewcollection', params=params,timeout=5,proxies=  {'http': None,'https': None} )
        return result
    def show(self,res):
        print('百度','\033[0;32;47m',res,'\033[0m',flush=True)
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))