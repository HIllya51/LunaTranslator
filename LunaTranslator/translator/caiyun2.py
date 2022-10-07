  
from translator.basetranslator import basetrans 
import requests
from traceback import print_exc

from utils.config import globalconfig
class TS(basetrans): 
    def srclang(self):
        return ['ja','en'][globalconfig['srclang']]
    def translate(self,content): 
        try:
            
            headers = {
                'authority': 'api.interpreter.caiyunai.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'zh-CN,zh;q=0.9',
                # Already added when you pass json=
                # 'content-type': 'application/json',
                'origin': 'chrome-extension://cdonnmffkdaoajfknoeeecmchibpmkmg',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'none',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                'x-authorization': 'token ukiw3nrioeilf0mlpam7',
            }

            json_data = {
                'source': [
                    content,
                ],
                'trans_type': self.srclang()+'2zh',
                'detect': False,
            }

            response = requests.post('https://api.interpreter.caiyunai.com/v1/translator', headers=headers, json=json_data,timeout=globalconfig['translatortimeout'], proxies=  {'http': None,'https': None})
            return response.json()['target'][0]
        except:
            print_exc()
             
            return '出错了'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')