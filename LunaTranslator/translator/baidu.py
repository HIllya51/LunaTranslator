 
 
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
    def srclang(self):
        return ['jp','en'][globalconfig['srclang']]
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
        try:
            self.session.get(url=index_url, headers=self.headers, proxies=  {'http': None,'https': None},timeout = globalconfig['translatortimeout'] )  #session自动生成cookie
            response_index = self.session.get(url=index_url ,headers=self.headers, proxies=  {'http': None,'https': None}  )
            
            self.token = re.findall(r"token: '([0-9a-z]+)'", response_index.text)[0]
            self.gtk = re.findall(r'gtk = "(.*?)"', response_index.text)[0]
            dirname, filename = os.path.split(os.path.abspath(__file__))
            #print(self.gtk)
            with open(os.path.join('./files/scripts/baidufanyi_encrypt.js'), 'r', encoding='utf-8') as f:
                baidu_js = f.read()
            #self.jsrun=execjs.get('local_node').compile(baidu_js)
            self.ctx=  EvalJs()
            self.ctx.execute(baidu_js)
        except:
            print_exc()
    
    
    # 获取今天任意时刻的时间戳
    def today_anytime_tsp(self,hour, minute, second=0):
        from datetime import datetime, timedelta
        now = datetime.now()
        today_0 = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        today_anytime = today_0 + timedelta(hours=hour, minutes=minute, seconds=second)
        tsp = today_anytime.timestamp()
         
        return str(int(tsp*1000))
 
    def translate(self,query): 
        try:
        #sign =self.jsrun.call('e', query, self.gtk)
            sign=self.ctx.e(query,self.gtk)
            translate_url = 'https://fanyi.baidu.com/#'+self.srclang()+'/zh/%s' % ( parse.quote(query))
            #acs_token = self.jsrun.call('ascToken', translate_url)

            acs_token=self.today_anytime_tsp(15,0,9)+ self.ctx.ascToken(translate_url)
            data = {
                'from': self.srclang(),
                'to': 'zh',
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
            print(response.json())
            result ='\n'.join([_['dst'] for _ in response.json()['trans_result']['data']])  
            params = {
                'req': 'check',
                'fanyi_src': query,
                'direction': self.srclang()+'2zh',
                '_': int(time.time()*1000),
            }

            #response = self.session.get('https://fanyi.baidu.com/pcnewcollection', params=params,timeout = globalconfig['translatortimeout'],proxies=  {'http': None,'https': None} )
            return result
        except:
            self.inittranslator()
            print_exc()
            try :
                print(response.json())
            except:
                pass
            result='出错了'
            return result
        
        
    def show(self,res):
        print('百度','\033[0;32;47m',res,'\033[0m',flush=True)
     
if __name__=='__main__':
    g=BD()
    print(g.realfy('あずきさんからアサリのスパゲティの作り方を学んだりもした。'))