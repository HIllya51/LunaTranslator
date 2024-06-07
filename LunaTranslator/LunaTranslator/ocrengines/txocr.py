from hashlib import sha1
import time, random, hmac, base64
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    def langmap(self):
        # https://cloud.tencent.com/document/product/866/33526
        return {
            "ja": "jap",
            "ko": "kor",
            "en": "auto",
            "ru": "rus",
            "es": "spa",
            "fr": "fre",
            "vi": "vie",
            "it": "ita",
            "ar": "ara",
            "th": "tha",
        }

    def ocr(self, imagebinary):
        self.checkempty(["SecretId", "SecretKey"])

        encodestr = str(base64.b64encode(imagebinary), "utf-8")
        req_para = {
            "LanguageType": self.srclang,
            "Action": "GeneralBasicOCR",
            "ImageBase64": encodestr,
            "Version": "2018-11-19",
            "Region": [
                "ap-beijing",
                "ap-guangzhou",
                "ap-hongkong",
                "ap-seoul",
                "ap-shanghai",
                "ap-singapore",
                "na-toronto",
            ][
                self.config["Region"]
            ],  # https://cloud.tencent.com/document/product/866/33526
            "Timestamp": int(time.time()),
            "Nonce": random.randint(1, 100000),
            "SecretId": self.config["SecretId"],
        }
        raw_msg = "&".join(
            [
                "{}={}".format(kv[0], kv[1])
                for kv in sorted(req_para.items(), key=lambda x: x[0])
            ]
        )
        raw_msg = "GETocr.tencentcloudapi.com/?" + raw_msg
        raw = raw_msg.encode()
        key = self.config["SecretKey"].encode()
        hashed = hmac.new(key, raw, sha1)
        b64output = base64.encodebytes(hashed.digest()).decode("utf-8")
        req_para.update({"Signature": b64output})
        r = self.proxysession.get(
            url="https://ocr.tencentcloudapi.com/", params=req_para, timeout=10
        )
        # print(r.text)
        if r.status_code == 200:
            try:
                boxs = [
                    [
                        _["Polygon"][0]["X"],
                        _["Polygon"][0]["Y"],
                        _["Polygon"][1]["X"],
                        _["Polygon"][1]["Y"],
                        _["Polygon"][2]["X"],
                        _["Polygon"][2]["Y"],
                        _["Polygon"][3]["X"],
                        _["Polygon"][3]["Y"],
                    ]
                    for _ in r.json()["Response"]["TextDetections"]
                ]
                texts = [
                    _["DetectedText"] for _ in r.json()["Response"]["TextDetections"]
                ]
                return self.common_solve_text_orientation(boxs, texts)
            except:
                raise Exception(r.json())
        return r.text
