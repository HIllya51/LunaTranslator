from ocrengines.baseocrclass import baseocr, OCRResult
import base64


class OCR(baseocr):

    def ocr(self, imagebinary):
        # https://github.com/dmotz/thing-translator/blob/d1fec3f38d24e973af49766669f9ee00bd9e98a8/src/effects/snap.js
        # https://cloud.google.com/vision/docs/ocr?hl=zh-cn
        # https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#EntityAnnotation
        self.checkempty(["key"])
        ocr_url = "https://vision.googleapis.com/v1/images:annotate"
        params = {"key": self.multiapikeycurrent["key"]}
        encodestr = str(base64.b64encode(imagebinary), "utf-8")
        data = {
            "requests": [
                {
                    "image": {"content": encodestr},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }
        response = self.proxysession.post(ocr_url, json=data, params=params)
        try:
            boxs = []
            texts = []
            blocks = response.json()["responses"][0]["fullTextAnnotation"]["pages"][0][
                "blocks"
            ]
            for block in blocks:
                for paragraph in block["paragraphs"]:
                    ws = []
                    for word in paragraph["words"]:
                        for symbol in word["symbols"]:
                            ws.append(symbol["text"])
                    texts.append("".join(ws))
                    vertices = paragraph["boundingBox"]["vertices"]
                    boxs.append(
                        [
                            vertices[0]["x"],
                            vertices[0]["y"],
                            vertices[1]["x"],
                            vertices[1]["y"],
                            vertices[2]["x"],
                            vertices[2]["y"],
                            vertices[3]["x"],
                            vertices[3]["y"],
                        ]
                    )
            return OCRResult(boxs=boxs, texts=texts)
        except:
            raise Exception(response)
