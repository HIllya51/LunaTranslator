 
import requests
import base64 
from utils.config import globalconfig 
from ocrengines.baseocrclass import baseocr 
class OCR(baseocr):
      
    def ocr(self,imgfile): 
        if self.config['token'].strip()=='':
            return ''
          
        headers = {
            'authority': 'ocrserver.docsumo.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
                'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryUjYOv45hug6CFh3t',

            'origin': 'https://www.zhihu.com',
            'pragma': 'no-cache',
            'referer': 'https://www.zhihu.com/',
            'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'token': self.config['token'].strip(),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }

        
        data = '------WebKitFormBoundaryUjYOv45hug6CFh3t\r\nContent-Disposition: form-data; name="file"; filename="screenshot.png"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode('latin-1')+open(imgfile, "rb").read()+'\r\n------WebKitFormBoundaryUjYOv45hug6CFh3t--\r\n'.encode('latin-1')

        response = requests.post('https://ocrserver.docsumo.com/api/v1/ocr/extract/',headers=headers,  data=data, proxies=  {'http': None,'https': None})
        #print(response.json())
        self.countnum()
        return response.json()['data']
         