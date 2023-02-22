 
 
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
    def langmap(self):
        return {"es":"spa","ko":"kor","fr":"fra","ja":"jp","cht":"cht"}
    def inittranslator(self)  :  
        self.headers = {
            'Accept': '*/*',
            'Host': 'fanyi.baidu.com',
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
        self.starttime=int(time.time()*1000)
        self.token =   re.findall(r"token: '([0-9a-z]+)'", response_index.text)[0]
        self.gtk =   re.findall(r'gtk = "(.*?)"', response_index.text)[0]
        self.systime=int(re.findall(r"systime: '([0-9]+)'", response_index.text)[0])
        with open(os.path.join('./files/scripts/baidufanyi_encrypt.js'), 'r', encoding='utf-8') as f:
            baidu_js = f.read()
         
        self.ctx=  EvalJs()
        self.ctx.execute(baidu_js)
         
        url = 'https://dlswbr.baidu.com/heicha/mm/2060/acs-2060.js'
     
        res = self.session.get(url,headers= 
     {
    'authority': 'dlswbr.baidu.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
} ) 
        array='['+ re.findall('p.run\(\[(.*?)\]\)', res.text, re.DOTALL)[0]+']'
        array=eval(array) 
        print(array)
        self.timestamp =str(array[2][6][1])
        self.version=array[3][6]
        self.k1=array[3][7]
        self.step=20
        self.k2=array[3][8]
        print(self.timestamp,self.k1,self.k2,self.version)
        print(self.session.cookies)

        hm=re.findall(r'hm.src = "//(.*)"', response_index.text)[0]
                
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive', 
            'Pragma': 'no-cache',
            'Referer': 'https://fanyi.baidu.com/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        _ = self.session.get('https://'+hm, headers=headers)
        print(self.session.cookies)
        self.session.cookies.update({
            'APPGUIDE_10_0_2': '1',
    'REALTIME_TRANS_SWITCH': '1',
    'FANYI_WORD_SWITCH': '1',
    'HISTORY_SWITCH': '1',
    'SOUND_SPD_SWITCH': '1',
    'SOUND_PREFER_SWITCH': '1',
        })
    def translate(self,query):  
        
        #sign =self.jsrun.call('e', query, self.gtk)
            sign=self.ctx.e(query,self.gtk)
            translate_url = 'https://fanyi.baidu.com/#'+self.srclang +'/'+self.tgtlang +'/%s' %  ( parse.quote(query))
             
            acs_token=self.timestamp+ self.ctx.ascToken(translate_url, self.k1,self.k2,self.version,  str(int((time.time())*1000)-self.starttime+self.systime))
            #print(acs_token)
            params = {
                'from': self.srclang ,
                'to': self.tgtlang ,
            }
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
            print(data)
            
            headers = {
                'Accept': '*/*',
                'Host': 'fanyi.baidu.com',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://fanyi.baidu.com',
                'Referer': 'https://fanyi.baidu.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
             
            _ = self.session.post(url='https://fanyi.baidu.com/langdetect',headers=headers,   data={'query':query},timeout = globalconfig['translatortimeout'],proxies=  {'http': None,'https': None})


            headers["Acs-Token"]=acs_token
            response = self.session.post(url='https://fanyi.baidu.com/v2transapi',headers=headers,params=params,   data=data,timeout = globalconfig['translatortimeout'],proxies=  {'http': None,'https': None})
                        
            headers.pop('Acs-Token')
            params = {
                'req': 'check',
                'fanyi_src':query,
                'direction': self.srclang+'2'+ self.tgtlang,
                '_': self.systime+self.step,
            }
            self.step+=1
            _ = self.session.get('https://fanyi.baidu.com/pcnewcollection', params=params,  headers=headers)
            print(response.json())
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
     