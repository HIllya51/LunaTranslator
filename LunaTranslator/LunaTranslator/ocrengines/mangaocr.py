import requests
from ocrengines.baseocrclass import baseocr
import os, uuid
from myutils.ocrutil import binary2qimage


class OCR(baseocr):

    def ocr(self, imagebinary):
        qimage = binary2qimage(imagebinary)
        os.makedirs("./cache/ocr", exist_ok=True)
        fname = "./cache/ocr/" + str(uuid.uuid4()) + ".png"
        qimage.save(fname)
        self.checkempty(["Port"])
        self.port = self.config["Port"]

        absolute_img_path = os.path.abspath(fname)
        params = {"image_path": absolute_img_path}

        response = requests.get(f"http://127.0.0.1:{self.port}/image", params=params)
        os.remove(absolute_img_path)
        try:
            return response.json()["text"]
        except Exception as e:
            raise Exception(response.text) from e
