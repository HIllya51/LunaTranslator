from ocrengines.baseocrclass import baseocr
import base64
from language import Languages
from myutils.utils import createurl, common_list_models, common_parse_normal_response
from myutils.proxy import getproxy


def list_models(typename, regist):
    return common_list_models(
        getproxy(("ocr", typename)),
        regist["apiurl"](),
        regist["SECRET_KEY"]().split("|")[0],
    )


class OCR(baseocr):

    def langmap(self):
        return Languages.createenglishlangmap()

    def createdata(self, message):
        temperature = self.config["Temperature"]

        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            # n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
        )
        if "api.mistral.ai" not in self.config["apiurl"]:
            data.update(dict(frequency_penalty=self.config["frequency_penalty"]))
        return data

    def createheaders(self):
        return {"Authorization": "Bearer " + self.multiapikeycurrent["SECRET_KEY"]}

    def ocr_mistral(self, _, base64_image):
        payload = {
            "model": self.config["model"],
            "document": {
                "type": "image_url",
                "image_url": "data:image/jpeg;base64,{}".format(base64_image),
            },
        }
        response = self.proxysession.post(
            "https://api.mistral.ai/v1/ocr",
            headers=self.createheaders(),
            json=payload,
        )
        try:
            texts = []
            for pages in response.json()["pages"]:
                texts.append(pages["markdown"])
            return {"text": texts}
        except:
            raise Exception(response)

    def ocr_gemini(self, prompt, base64_image):
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": base64_image,
                            }
                        },
                    ]
                }
            ]
        }
        safety = {
            "safety_settings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_CIVIC_INTEGRITY",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        }
        payload.update(safety)
        response = self.proxysession.post(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(
                self.config["model"], self.multiapikeycurrent["SECRET_KEY"]
            ),
            json=payload,
        )
        return response

    def ocr_normal(self, prompt, base64_image):

        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + base64_image,
                            "detail": "low",
                        },
                    },
                ],
            }
        ]

        response = self.proxysession.post(
            createurl(self.config["apiurl"]),
            headers=self.createheaders(),
            json=self.createdata(message),
        )
        return response

    def ocr(self, imagebinary):

        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = "Recognize the {} text in the picture.".format(self.srclang)

        base64_image = base64.b64encode(imagebinary).decode("utf-8")

        if self.config["apiurl"].startswith(
            "https://generativelanguage.googleapis.com"
        ):
            response = self.ocr_gemini(prompt, base64_image)
        elif self.config["apiurl"].startswith("https://api.mistral.ai/v1"):
            return self.ocr_mistral(prompt, base64_image)
        else:
            response = self.ocr_normal(prompt, base64_image)
        return common_parse_normal_response(response, self.config["apiurl"])
