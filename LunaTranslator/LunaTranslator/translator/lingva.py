import requests
import re
import urllib 
 
from translator.basetranslator import basetrans
class TS(basetrans):
    def langmap(self):
        return { "cht":"zh_HANT"}
    def inittranslator(self):  
        res=requests.get('https://lingva.ml/',headers=
            {
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
            'Referer': 'https://lingva.ml/',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
            'sec-ch-ua-platform': '"Windows"',
        },proxies=self.proxy).text
        _id=re.findall('buildId":"(.*?)"',res)[0]
        self.url=f'https://lingva.ml/_next/data/{_id}/%s/%s/%s.json'
    def translate(self,content):  
        print(self.url%(self.srclang,self.tgtlang,urllib.parse.quote(content)))
        x=requests.get(self.url%(self.srclang,self.tgtlang,urllib.parse.quote(content)),headers = {
            'authority': 'lingva.ml',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://lingva.ml/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
        },proxies=self.proxy).json() 
        return x['pageProps']['translation']