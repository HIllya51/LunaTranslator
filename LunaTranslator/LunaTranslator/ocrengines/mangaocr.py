import requests
from ocrengines.baseocrclass import baseocr
import os, uuid, gobject

class OCR(baseocr):

    def ocr(self, imagebinary):

        fname = gobject.gettempdir(str(uuid.uuid4()) + ".png")
        with open(fname, "wb") as ff:
            ff.write(imagebinary)
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
