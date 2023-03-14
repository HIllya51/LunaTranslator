 
import requests

import base64  
from ocrengines.baseocrclass import baseocr 
class OCR(baseocr):
    def langmap(self):
        return {"ja":"jpn","zh":"chs","en":"eng","ko":"kor","es":"spa","fr":"fre","ru":"rus","cht":"cht"}
    def ocr(self,imgfile):  
        self.checkempty(['apikey'])
        apikey=self.config['apikey']
        headers = {
            'authority': 'apipro3.ocr.space',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            
            'origin': 'https://identity.getpostman.com',
            'pragma': 'no-cache',
            'referer': 'https://identity.getpostman.com/',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
        }

        with open(imgfile,'rb') as ff:
            f=ff.read()
        b64=base64.b64encode(f)
        data={'language':self.srclang,'base64Image':'data:image/jpeg;base64,'+str(b64,encoding='utf8'),'isOverlayRequired':'true','OCREngine':1,'apikey':apikey}
        
        response = requests.post('https://apipro3.ocr.space/parse/image', headers=headers, data=data, proxies=  {'http': None,'https': None})
        #print(response.text)
        try:
            
            _= response.json()['ParsedResults'][0]['ParsedText']
            self.countnum()
            return _
        except:
            raise Exception(response.text)