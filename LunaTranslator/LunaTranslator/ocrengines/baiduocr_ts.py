import random
from hashlib import md5
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    isocrtranslate = True

    def langmap(self):
        return {
            "es": "spa",
            "ko": "kor",
            "fr": "fra",
            "ja": "jp",
            "cht": "cht",
            "vi": "vie",
            "uk": "ukr",
            "ar": "ara",
        }

    def ocr(self, imagebinary):
        self.checkempty(["app_id", "app_key"])
        endpoint = "http://api.fanyi.baidu.com"
        path = "/api/trans/sdk/picture"
        url = endpoint + path

        from_lang = self.srclang
        to_lang = self.tgtlang

        # Set your own appid/appkey.
        app_id = self.config["app_id"]
        app_key = self.config["app_key"]

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
            text = [_["src"] for _ in js["data"]["content"]]
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
            return self.common_solve_text_orientation(box, text)
        except:
            raise Exception(response.text)
