import requests
from urllib.parse import quote,unquote
from translator.basetranslator import basetrans
class TS(basetrans):
    def langmap(self):
        return {'zh':'zh-Hans','cht':'zh-Hant'}
    def translate(self,content): 
                        
                        
                
                
        headers = {
            'authority': 'api.microsofttranslator.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'origin': 'https://nicetranslator.com',
            'pragma': 'no-cache',
            'referer': 'https://nicetranslator.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69',
        } 
         
        response = requests.get(
            f'https://api.microsofttranslator.com/V2/Ajax.svc/Translate?appId=DB50E2E9FBE2E92B103E696DCF4E3E512A8826FB&oncomplete=?&from={self.srclang}&to={self.tgtlang}',params={
            'text':content
            },
            headers=headers,proxies=self.proxy
        )

        return response.content.decode('utf_8_sig')