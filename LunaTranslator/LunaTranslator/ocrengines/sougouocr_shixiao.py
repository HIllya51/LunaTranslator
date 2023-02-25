 
import requests 
from ocrengines.baseocrclass import baseocr 
class OCR(baseocr):
     
    def ocr(self,imgfile):  
        headers = { 
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        
        file = open(imgfile,'rb')
        files = {'pic': ('pic.jpg', file) }
        r = requests.post(url='http://ocr.shouji.sogou.com/v2/ocr/json', files=files, headers=headers)  
        print(r.json())
        return self.space.join([_['content'] for _ in r.json()['result']])