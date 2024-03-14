import requests
from ocrengines.baseocrclass import baseocr
import os

class OCR(baseocr):
    
    def ocr(self, img_path):
        
        self.checkempty(['Port'])
        self.port = self.config['Port']

        absolute_img_path = os.path.abspath(img_path)
        params = {'image_path': absolute_img_path}
        
        response = requests.get(f'http://127.0.0.1:{self.port}/image', params=params)

        try:
            return response.json()['text']
        except Exception as e:
            raise Exception(response.text) from e
