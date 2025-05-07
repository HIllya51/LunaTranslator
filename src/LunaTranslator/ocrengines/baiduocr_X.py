import base64
from myutils.config import globalconfig
from ocrengines.baseocrclass import baseocr, OCRResult
import random, zhconv
from hashlib import md5
from language import Languages


class OCR(baseocr):

    def ocr_ts1(self, imagebinary):

        accstoken = self.getaccess()

        params = {
            "access_token": accstoken,
            "from": self.srclangx,
            "to": self.tgtlangx,
            "v": "3",
            "paste": "1",
        }  # '',
        image = {"image": ("shit.png", imagebinary, "multipart/form-data")}
        response = self.proxysession.post(
            "https://aip.baidubce.com/file/2.0/mt/pictrans/v1",
            params=params,
            files=image,
        )

        try:
            js = response.json()
            text = [
                (
                    zhconv.convert(_["dst"], "zh-tw")
                    if (Languages.TradChinese == self.tgtlang_1)
                    else _["dst"]
                )
                for _ in js["data"]["content"]
            ]
            box = [
                (
                    l["points"][0]["x"],
                    l["points"][0]["y"],
                    l["points"][1]["x"],
                    l["points"][1]["y"],
                    l["points"][2]["x"],
                    l["points"][2]["y"],
                    l["points"][3]["x"],
                    l["points"][3]["y"],
                )
                for l in js["data"]["content"]
            ]
            return OCRResult(boxs=box, texts=text, isocrtranslate=True)
        except:
            raise Exception(response)

    def ocr_ts2(self, imagebinary):
        self.checkempty(["app_id", "app_key"])
        endpoint = "http://api.fanyi.baidu.com"
        path = "/api/trans/sdk/picture"
        url = endpoint + path

        from_lang = self.srclangx
        to_lang = self.tgtlangx

        # Set your own appid/appkey.
        app_id = self.multiapikeycurrent["app_id"]
        app_key = self.multiapikeycurrent["app_key"]

        # cuid & mac
        cuid = "APICUID"
        mac = "mac"

        # Generate salt and sign
        def get_md5(string, encoding="utf-8"):
            return md5(string.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = get_md5(
            app_id + md5(imagebinary).hexdigest() + str(salt) + cuid + mac + app_key
        )

        # Build request
        payload = {
            "from": from_lang,
            "to": to_lang,
            "appid": app_id,
            "salt": salt,
            "sign": sign,
            "cuid": cuid,
            "mac": mac,
        }

        files = {"image": ("image.png", imagebinary, "multipart/form-data")}
        response = self.proxysession.post(url, params=payload, files=files)

        try:
            js = response.json()
            text = [
                (
                    zhconv.convert(_["dst"], "zh-tw")
                    if (Languages.TradChinese == self.tgtlang_1)
                    else _["dst"]
                )
                for _ in js["data"]["content"]
            ]
            box = [
                (
                    l["points"][0]["x"],
                    l["points"][0]["y"],
                    l["points"][1]["x"],
                    l["points"][1]["y"],
                    l["points"][2]["x"],
                    l["points"][2]["y"],
                    l["points"][3]["x"],
                    l["points"][3]["y"],
                )
                for l in js["data"]["content"]
            ]
            return OCRResult(boxs=box, texts=text, isocrtranslate=True)
        except:
            raise Exception(response)

    @property
    def __x(self):
        return {
            Languages.TradChinese: "zh",
            Languages.Spanish: "spa",
            Languages.Korean: "kor",
            Languages.French: "fra",
            Languages.Japanese: "jp",
            Languages.Vietnamese: "vie",
            Languages.Ukrainian: "ukr",
            Languages.Arabic: "ara",
            Languages.Swedish: "swe",
        }

    @property
    def srclangx(self):
        return self.__x.get(self.srclang_1, self.srclang_1)

    @property
    def tgtlangx(self):
        return self.__x.get(self.tgtlang_1, self.tgtlang_1)

    def langmap(self):
        return {
            Languages.Auto: "auto_detect",
            Languages.TradChinese: "CHN_ENG",
            Languages.Chinese: "CHN_ENG",
            Languages.English: "ENG",
            Languages.Japanese: "JAP",
            Languages.Korean: "KOR",
            Languages.French: "FRE",
            Languages.Spanish: "SPA",
            Languages.Portuguese: "POR",
            Languages.German: "GER",
            Languages.Italian: "ITA",
            Languages.Russian: "RUS",
            Languages.Dutch: "DUT",
            Languages.Swedish: "SWE",
            Languages.Polish: "POL",
            Languages.Turkish: "TUR",
            Languages.Thai: "THA",
            Languages.Vietnamese: "VIE",
            Languages.Arabic: "ARA",
        }

    def init(self):
        self.access = {}

    def get_access_token(self, API_KEY, SECRET_KEY):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": SECRET_KEY,
        }
        resp = self.proxysession.post(url, params=params)

        try:
            return resp.json()["access_token"]
        except:
            raise Exception(resp)

    def getaccess(self):
        self.checkempty(["API Key", "Secret Key"])
        SECRET_KEY, API_KEY = (
            self.multiapikeycurrent["Secret Key"],
            self.multiapikeycurrent["API Key"],
        )
        if not self.access.get((API_KEY, SECRET_KEY)):
            acss = self.get_access_token(API_KEY, SECRET_KEY)
            self.access[(API_KEY, SECRET_KEY)] = acss
        return self.access[(API_KEY, SECRET_KEY)]

    def ocr(self, imagebinary):
        if self.config["接口"] in [0, 1, 2, 3]:
            return self.ocr_x(imagebinary)
        elif self.config["接口"] == 4:
            return self.ocr_ts1(imagebinary)
        elif self.config["接口"] == 5:
            return self.ocr_ts2(imagebinary)
        raise Exception("unknown")

    def ocr_x(self, imagebinary):
        accstoken = self.getaccess()
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
        }

        params = {"access_token": accstoken}  # '',

        b64 = base64.b64encode(imagebinary)

        data = {
            "image": b64,
            "detect_direction": int(globalconfig["verticalocr"]) != 0,
            "language_type": self.srclang,
        }

        if self.config["接口"] in [0, 1]:
            if self.is_src_auto:
                data["detect_language"] = True
                data.pop("language_type")
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

            if interfacetype in [0, 2]:
                return OCRResult(
                    texts=[x["words"] for x in response.json()["words_result"]]
                )
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
                return OCRResult(boxs=boxs, texts=texts)
        except:
            raise Exception(response)
