
from traceback import print_exc 
import re
import time
import requests
from urllib.parse import quote 
from translator.basetranslator import basetrans

from utils.config import globalconfig
class TS(basetrans):
    def srclang(self):
        return ['ja','en'][globalconfig['srclang']]
    def inittranslator(self):  
        self.ss=requests.session()
        headers = { 
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-bitness': '"64"',
                'sec-ch-ua-full-version': '"105.0.1343.53"',
                'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"10.0.0"',
                'sec-ch-ua-wow64': '?0',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
            }
         
        response = self.ss.get('https://cn.bing.com/translator/' ,headers=headers, timeout = globalconfig['translatortimeout'], proxies=  {'http': None,'https': None})
        text=response.text
        
        res=re.search('var params_RichTranslateHelper = \[([0-9]+),"(([0-9a-zA-Z]|-|_)+)"',text).group()
         
        self.key=res.split(',')[0].split('[')[1]
        self.token=res.split(',')[1][1:-1] 

        res=re.search('IG:"(([0-9a-zA-Z]|-|_)+)"',text).group()
        self.IG=res[4:-1]
 

        self.iid=re.findall('<div id="rich_tta" data-iid="(.*)"\)">',text)[0] 
        #print( self.IG)
        self.iid_i=1
  
    def show(self,res):
        print('必应','\033[0;31;47m',res,'\033[0m',flush=True)
    def translate(self,content): 
        try:
            data = '&fromLang='+self.srclang()+'&text='+quote(content)+'&to=zh-Hans&token='+self.token+'&key='+self.key
            self.iid_i+=1
                    
            headers = {
                'path':'/ttranslatev3?isVertical=1&&IG='+self.IG+'&IID='+self.iid+'.'+str(self.iid_i),

                'authority': 'cn.bing.com',
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://cn.bing.com',
                'pragma': 'no-cache',
                'referer': 'https://cn.bing.com/translator/',
                'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-bitness': '"64"',
                'sec-ch-ua-full-version': '"105.0.1343.53"',
                'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"10.0.0"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
                'x-edge-shopping-flag': '1',
            }
        
            response = self.ss.post('https://cn.bing.com/ttranslatev3?isVertical=1&&IG='+self.IG+'&IID='+self.iid+'.'+str(self.iid_i) ,headers=headers, data=data, proxies=  {'http': None,'https': None},timeout = globalconfig['translatortimeout'])
            js=response.json() 
            ch=js[0]['translations'][0]['text']
            
            return ch
        except:
            
            self.inittranslator()
            try:
                print(response.json())
            except:
                pass
            print_exc()
            return '出错了'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')