import time
import hashlib 
 
from translator.basetranslator import basetrans  
import random 
import json
class TS(basetrans):
    def youdaoSIGN(self,useragent,e):
        t=hashlib.md5(bytes(useragent,encoding='utf-8')).hexdigest()
        
        r=int(1000*time.time())
        i=r+int(10*random.random())
        return {'ts':r,'bv':t,'salt':i,'sign':hashlib.md5(bytes("fanyideskweb" + str(e) + str(i) + "Ygy_4c=r#e#4EX^NUGUc5",encoding='utf-8')).hexdigest()}
        
    def inittranslator(self):
        self.typename='youdao'
        self.updateheader('https://fanyi.youdao.com/')
        self.session.get('https://fanyi.youdao.com')
    def realfy(self, content):
         
        params = {
            'smartresult': [
                'dict',
                'rule',
            ],
        }
        sign=self.youdaoSIGN(self.headers['User-Agent'],content)
        data = {
            'i': content,
            'from': 'ja',
            'to': 'zh-CHS',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': sign['salt'],
            'sign': sign['sign'],
            'lts': sign['ts'],
            'bv': sign['bv'],
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CLICKBUTTION',
        }

        response =self.session.post('https://fanyi.youdao.com/translate_o', params=params , data=data, proxies=  {'http': None,'https': None})
        try:
            js=response.json()
        except json.decoder.JSONDecodeError:
              
            time.sleep(30)
            return None
        return js['translateResult'][0][0]['tgt']
    def show(self,res):
        print('有道','\033[0;33;47m',res,'\033[0m',flush=True)
if __name__=="__main__":
    #youdaoSIGN("5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33",'')
    a=youdaots()
    a.gettask('はーい、おやすみなさい')