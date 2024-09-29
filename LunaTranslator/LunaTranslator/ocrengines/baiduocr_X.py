import base64
from myutils.config import globalconfig
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    def langmap(self):
        return {
            "zh": "CHN_ENG",
            "en": "ENG",
            "ja": "JAP",
            "en": "ENG",
            "ko": "KOR",
            "fr": "FRE",
            "es": "SPA",
        }

    def initocr(self):
        self.appid, self.secretKey, self.accstoken = None, None, None
        self.checkchange()

    def checkchange(self):
        self.checkempty(["API Key", "Secret Key"])
        if (self.config["API Key"], self.config["Secret Key"]) != (
            self.appid,
            self.secretKey,
        ):
            self.appid, self.secretKey = (
                self.config["API Key"],
                self.config["Secret Key"],
            )
            self.accstoken = self.proxysession.get(
                "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id="
                + self.appid
                + "&client_secret="
                + self.secretKey
            ).json()["access_token"]

    def ocr(self, imagebinary):
        self.checkchange()
        if self.accstoken == "":
            return ""
        headers = {
            "authority": "aip.baidubce.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "origin": "chrome-extension://hmpjibmn1ncjokocepchnea",
            "pragma": "no-cache",
            "sec-ch-ua": '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53",
        }

        params = {"access_token": self.accstoken}  # '',

        b64 = base64.b64encode(imagebinary)

        data = {
            "image": b64,
            "detect_direction": int(globalconfig["verticalocr"]) != 0,
            "language_type": self.srclang,
        }
        interfacetype = self.config["接口"]

        url = [
            "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic",
            "https://aip.baidubce.com/rest/2.0/ocr/v1/general",
            "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic",
            "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate",
        ][interfacetype]
        response = self.proxysession.post(
            url, params=params, headers=headers, data=data
        )
        try:

            self.countnum()
            if interfacetype in [0, 2]:
                return {"text": [x["words"] for x in response.json()["words_result"]]}
            else:
                texts = [x["words"] for x in response.json()["words_result"]]
                boxs = [
                    (
                        x["location"]["left"],
                        x["location"]["top"],
                        x["location"]["left"] + x["location"]["width"],
                        x["location"]["top"] + x["location"]["height"],
                    )
                    for x in response.json()["words_result"]
                ]
                return {"box": boxs, "text": texts}
        except:
            raise Exception(response.text)
