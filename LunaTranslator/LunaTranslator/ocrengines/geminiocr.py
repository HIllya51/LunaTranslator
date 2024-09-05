import base64
import requests
from ocrengines.baseocrclass import baseocr
from myutils.utils import createenglishlangmap
from myutils.proxy import getproxy


def list_models(typename, regist):
    js = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": regist["key"]().split("|")[0]},
        proxies=getproxy(("ocr", typename)),
    ).json()
    try:
        models = js["models"]
    except:
        raise Exception(js)
    mm = []
    for m in models:
        name: str = m["name"]
        supportedGenerationMethods: list = m["supportedGenerationMethods"]
        if "generateContent" not in supportedGenerationMethods:
            continue
        if name.startswith("models/"):
            name = name[7:]
        mm.append(name)
    return mm


class OCR(baseocr):
    def langmap(self):
        return createenglishlangmap()

    def ocr(self, imagebinary):
        self.checkempty(["key"])
        self.checkempty(["url"])
        self.checkempty(["model"])
        api_key = self.config["key"]
        url = self.config["url"]
        model = self.config["model"]
        image_data = base64.b64encode(imagebinary).decode("utf-8")

        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = f"Recognize the {self.srclang} text in the picture."
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
        url = f"{url}/models/{model}:generateContent?key={api_key}"

        # Send the request
        response = requests.post(url, headers=headers, json=payload, proxies=self.proxy)
        try:
            # Handle the response
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception(response.text)
        except Exception as e:
            raise Exception(response.text) from e
