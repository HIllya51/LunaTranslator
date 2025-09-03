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

        response = self.proxysession.get(
            "http://127.0.0.1:{}/image".format(self.port), params=params
        )
        try:
            os.remove(absolute_img_path)
        except:
            pass
        try:
            return response.json()["text"]
        except Exception as e:
            raise Exception(response) from e
