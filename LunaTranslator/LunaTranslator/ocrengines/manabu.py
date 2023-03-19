
import requests
import base64  
from ocrengines.baseocrclass import baseocr 
class OCR(baseocr): 
    def ocr(self,imgfile):  
                
        headers = {
            'authority': 'www.manabu.sg',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryhC6izq7fp7UsK1uY', 
            'origin': 'https://www.manabu.sg',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44',
            'x-requested-with': 'XMLHttpRequest',
        }

        with open(imgfile,'rb') as ff:
            b=ff.read()

        data = '------WebKitFormBoundaryhC6izq7fp7UsK1uY\r\nContent-Disposition: form-data; name="uploadedImages"; filename="1.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'+b.decode('latin-1')+'\r\n------WebKitFormBoundaryhC6izq7fp7UsK1uY--\r\n'

        response = requests.post('https://www.manabu.sg/api/v1/contents/ocr',    headers=headers, data=data) 
        return self.space.join((response.json()['ocrContents'][0][0][0]['description']).split('\n'))
