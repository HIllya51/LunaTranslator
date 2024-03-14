import requests
from ocrengines.baseocrclass import baseocr
import os

class OCR(baseocr):
    
    def ocr(self, img_path):
        
        self.checkempty(['api_url'])
        api_url=self.config['api_url']
        
        response = requests.get(api_url, json={'image_path': os.path.abspath(img_path)})

        try:
            return response.json()['text']
        except:
            raise Exception(response.text)
