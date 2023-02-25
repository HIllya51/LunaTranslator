 
import requests
import base64  
from ocrengines.baseocrclass import baseocr 
class OCR(baseocr):
      
    def ocr(self,imgfile):  
        app_id = self.config['app_id'].strip()  
        app_secret = self.config['app_secret'].strip()  
        
                
        res=requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',headers={'Content-Type':"application/json; charset=utf-8"}, proxies=  {'http': None,'https': None},json={
            "app_id": app_id,
            "app_secret": app_secret
        })
        token=res.json()['tenant_access_token']
        with open(imgfile,'rb') as ff:
            f=ff.read()
        b64=base64.b64encode(f)
        res=requests.post('https://open.feishu.cn/open-apis/optical_char_recognition/v1/image/basic_recognize', proxies=  {'http': None,'https': None},headers={'Content-Type':"application/json; charset=utf-8",'Authorization':'Bearer '+token},json={
        "image": str(b64,encoding='utf8'),
        })
        return self.space.join(res.json()['data']['text_list'])