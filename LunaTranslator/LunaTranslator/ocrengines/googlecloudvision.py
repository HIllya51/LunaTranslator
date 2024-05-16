from ocrengines.baseocrclass import baseocr
import base64


class OCR(baseocr):

    def ocr(self, imagebinary):
        # https://github.com/dmotz/thing-translator/blob/d1fec3f38d24e973af49766669f9ee00bd9e98a8/src/effects/snap.js
        # https://cloud.google.com/vision/docs/ocr?hl=zh-cn
        # https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#EntityAnnotation
        self.checkempty(["googlecloudvision"])
        ocr_url = (
            "https://vision.googleapis.com/v1/images:annotate?key=" + self.config["key"]
        )
        encodestr = str(base64.b64encode(imagebinary), "utf-8")
        data = {
            "requests": [
                {
                    "image": {"content": encodestr},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }
        response = self.session.post(ocr_url, json=data)
        try:
            boxs = []
            texts = []
            for anno in response.json()["responses"][0]["textAnnotations"]:

                texts.append(anno["description"])
                boxs.append(
                    [
                        anno["boundingPoly"]["vertices"][0]["x"],
                        anno["boundingPoly"]["vertices"][0]["y"],
                        anno["boundingPoly"]["vertices"][1]["x"],
                        anno["boundingPoly"]["vertices"][1]["y"],
                        anno["boundingPoly"]["vertices"][2]["x"],
                        anno["boundingPoly"]["vertices"][2]["y"],
                        anno["boundingPoly"]["vertices"][3]["x"],
                        anno["boundingPoly"]["vertices"][3]["y"],
                    ]
                )
            return self.common_solve_text_orientation(boxs, texts)
        except:
            raise Exception(response.text)
