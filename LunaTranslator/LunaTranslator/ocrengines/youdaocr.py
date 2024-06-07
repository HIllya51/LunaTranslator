import base64
import base64
import uuid
import time
import hashlib
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    def langmap(self):
        return {"zh": "zh-CHS", "cht": "zh-CHT"}

    def freetest(self, imagebinary):
        headers = {
            "authority": "aidemo.youdao.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://ai.youdao.com",
            "referer": "https://ai.youdao.com/",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }
        b64 = base64.b64encode(imagebinary)
        data = {
            "imgBase": "data:image/jpeg;base64," + str(b64, encoding="utf8"),
            "lang": "",
            "company": "",
        }

        response = self.proxysession.post(
            "https://aidemo.youdao.com/ocrapi1", headers=headers, data=data
        )

        try:
            return self.common_solve_text_orientation(
                [
                    [int(_) for _ in l["boundingBox"].split(",")]
                    for l in response.json()["lines"]
                ],
                [l["words"] for l in response.json()["lines"]],
            )
        except:
            raise Exception(response.text)

    def ocrapi(self, imagebinary):
        def truncate(q):
            if q is None:
                return None
            size = len(q)
            return q if size <= 20 else q[0:10] + str(size) + q[size - 10 : size]

        def encrypt(signStr):
            hash_algorithm = hashlib.sha256()
            hash_algorithm.update(signStr.encode("utf-8"))
            return hash_algorithm.hexdigest()

        self.checkempty(["APP_KEY", "APP_SECRET"])
        APP_KEY, APP_SECRET = self.config["APP_KEY"], self.config["APP_SECRET"]
        YOUDAO_URL = "https://openapi.youdao.com/ocrapi"
        content = base64.b64encode(imagebinary).decode("utf-8")

        data = {}
        data["img"] = content
        data["detectType"] = "10012"
        data["imageType"] = "1"
        data["langType"] = self.srclang
        data["docType"] = "json"
        data["signType"] = "v3"
        curtime = str(int(time.time()))
        data["curtime"] = curtime
        salt = str(uuid.uuid1())
        signStr = APP_KEY + truncate(content) + salt + curtime + APP_SECRET
        sign = encrypt(signStr)
        data["appKey"] = APP_KEY
        data["salt"] = salt
        data["sign"] = sign

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.proxysession.post(YOUDAO_URL, data=data, headers=headers)
        self.countnum()
        try:
            _ = []
            for l in response.json()["Result"]["regions"]:
                _ += l["lines"]
            return self.common_solve_text_orientation(
                [[int(_) for _ in l["boundingBox"].split(",")] for l in _],
                [l["text"] for l in _],
            )
        except:
            raise Exception(response.text)

    def ocr(self, imagebinary):
        interfacetype = self.config["接口"]
        if interfacetype == 0:
            return self.freetest(imagebinary)
        elif interfacetype == 1:
            return self.ocrapi(imagebinary)
        raise Exception("unknown")
