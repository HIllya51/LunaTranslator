
from traceback import print_exc 
import re 
import requests 
from urllib.parse import quote 
from translator.basetranslator import basetrans
 
class TS(basetrans):
    def langmap(self):
         return  {"zh":"zh-Hans","cht":"zh-Hant"} 
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
         
        response = self.ss.get('https://cn.bing.com/translator/' ,headers=headers)
        text=response.text
        
        res=re.compile('var params_AbusePreventionHelper = (.*?);').findall(text)[0]
         
        self.key=str(eval(res)[0])
        self.token=str(eval(res)[1])

        iid = 'translator.5028'
        ig = re.compile('IG:"(.*?)"').findall(text)[0]
          
        self.IG=ig
 

        self.iid=iid 
   
    def translate(self,content): 
            print(content) 
                    
            headers = { 
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
        
            response = self.ss.post('https://cn.bing.com/ttranslatev3?isVertical=1&&IG='+self.IG+'&IID='+self.iid,headers=headers, data={
                 'fromLang':self.srclang,'text':content,'to':self.tgtlang,'token':self.token,'key':self.key
            })#data=data )
            js=response.json() 
            ch=js[0]['translations'][0]['text']
            
            return ch
         