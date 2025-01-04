import base64
import requests
from ocrengines.baseocrclass import baseocr
from myutils.utils import urlpathjoin
from myutils.proxy import getproxy
from language import Languages


def list_models(typename, regist):
    resp = requests.get(
        urlpathjoin(regist["BASE_URL"]().strip(), "v1beta/models"),
        params={"key": regist["key"]().split("|")[0].strip()},
        proxies=getproxy(("ocr", typename)),
    )
    try:
        models = resp.json()["models"]
    except:
        raise Exception(resp)
    mm = []
    for m in models:
        name: str = m["name"]
        supportedGenerationMethods: list = m["supportedGenerationMethods"]
        if "generateContent" not in supportedGenerationMethods:
            continue
        if name.startswith("models/"):
            name = name[7:]
        mm.append(name)
    return sorted(mm)


class OCR(baseocr):
    def langmap(self):
        return Languages.createenglishlangmap()

    def ocr(self, imagebinary):
        self.checkempty(["key"])
        self.checkempty(["BASE_URL"])
        self.checkempty(["model"])
        api_key = self.config["key"]
        model = self.config["model"]
        image_data = base64.b64encode(imagebinary).decode("utf-8")

        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = "Recognize the {} text in the picture.".format(self.srclang)
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": "image/png", "data": image_data}},
                    ]
                }
            ]
        }

        # Set up the request headers and URL
        headers = {"Content-Type": "application/json"}
        # by default https://generativelanguage.googleapis.com/v1
        # Send the request
        response = requests.post(
            urlpathjoin(
                self.config["BASE_URL"],
                "v1beta/models/{}:generateContent?key={}".format(model, api_key),
            ),
            headers=headers,
            json=payload,
            proxies=self.proxy,
        )
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise Exception(response) from e
