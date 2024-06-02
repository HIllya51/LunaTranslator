import requests
import random
import json
import os
import sys
from hashlib import md5
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
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

        data = (
            '--6d94758aed493e27c73620d74ff01fc4\r\nContent-Disposition: form-data; name="image"; filename="2024-05-29 220022.png"\r\nContent-Type: multipart/form-data\r\n\r\n'.encode(
                "latin-1"
            )
            + imagebinary
            + "\r\n--6d94758aed493e27c73620d74ff01fc4--\r\n".encode("latin-1")
        )
        headers = {
            "content-type": "multipart/form-data; boundary=6d94758aed493e27c73620d74ff01fc4",
        }
        response = self.session.post(url, params=payload, headers=headers, data=data)

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
            return "<notrans>" + self.common_solve_text_orientation(box, text)
        except:
            raise Exception(response.text)
