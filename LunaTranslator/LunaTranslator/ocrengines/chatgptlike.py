from ocrengines.baseocrclass import baseocr
import base64


class OCR(baseocr):

    def langmap(self):
        return {
            "zh": "Simplified Chinese",
            "ja": "Japanese",
            "en": "English",
            "ru": "Russian",
            "es": "Spanish",
            "ko": "Korean",
            "fr": "French",
            "cht": "Traditional Chinese",
            "vi": "Vietnamese",
            "tr": "Turkish",
            "pl": "Polish",
            "uk": "Ukrainian",
            "it": "Italian",
            "ar": "Arabic",
            "th": "Thai",
        }

    def createdata(self, message):
        temperature = self.config["Temperature"]

        data = dict(
            model=self.config["model"],
            messages=message,
            # optional
            max_tokens=self.config["max_tokens"],
            n=1,
            # stop=None,
            top_p=self.config["top_p"],
            temperature=temperature,
            frequency_penalty=self.config["frequency_penalty"],
        )
        return data

    def createheaders(self):
        return {"Authorization": "Bearer " + self.config["SECRET_KEY"]}

    def checkv1(self, api_url: str):
        # 傻逼豆包大模型是非要v3，不是v1
        if api_url.endswith("/v3"):
            return api_url
        elif api_url.endswith("/v3/"):
            return api_url[:-1]
        # 智谱AI
        elif api_url.endswith("/v4"):
            return api_url
        elif api_url.endswith("/v4/"):
            return api_url[:-1]
        # 正常的
        elif api_url.endswith("/v1"):
            return api_url
        elif api_url.endswith("/v1/"):
            return api_url[:-1]
        elif api_url.endswith("/"):
            return api_url + "v1"
        else:
            return api_url + "/v1"

    def ocr(self, imagebinary):

        if self.config["use_custom_prompt"]:
            prompt = self.config["custom_prompt"]
        else:
            prompt = f"Recognize the {self.srclang} text in the picture."

        base64_image = base64.b64encode(imagebinary).decode("utf-8")
        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low",
                        },
                    },
                ],
            }
        ]

        response = self.proxysession.post(
            self.createurl(),
            headers=self.createheaders(),
            json=self.createdata(message),
        )
        try:
            message = (
                response.json()["choices"][0]["message"]["content"]
                .replace("\n\n", "\n")
                .strip()
            )
            return message
        except:
            raise Exception(response.text)

    def createurl(self):
        url = self.config["apiurl"]
        if url.endswith("/chat/completions"):
            pass
        else:
            url = self.checkv1(url) + "/chat/completions"
        return url
