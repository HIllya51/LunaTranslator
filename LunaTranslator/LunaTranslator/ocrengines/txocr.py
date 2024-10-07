from hashlib import sha1
import time, random, hmac, base64, uuid, hashlib, json
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    @property
    def region(self):
        try:
            return [
                "ap-beijing",
                "ap-guangzhou",
                "ap-hongkong",
                "ap-seoul",
                "ap-shanghai",
                "ap-singapore",
            ][self.config["Region"]]
        except:
            return "ap-beijing"

    @property
    def langocr(self):
        s = self.srclang_1
        return {
            "zh": "zh",
            "cht": "zh",
            "ja": "jap",
            "ko": "kor",
            "es": "spa",
            "fr": "fre",
            "de": "ger",
            "pt": "por",
            "vi": "vie",
            "ru": "rus",
            "it": "ita",
            "it": "hol",
            "sv": "swe",
            "hu": "hun",
            "th": "tha",
            "ar": "ara",
        }.get(s, "auto")

    def langmap(self):
        # https://cloud.tencent.com/document/product/551/17232
        return {"cht": "zh-TW"}

    def ocr_fy(self, imagebinary):
        self.checkempty(["SecretId", "SecretKey"])

        encodestr = str(base64.b64encode(imagebinary), "utf-8")
        req_para = {
            "Source": self.srclang,
            "Target": self.tgtlang,
            "ProjectId": int(self.config["ProjectId"]),
            "Data": encodestr,
            "SessionUuid": str(uuid.uuid4()),
            "Scene": "doc",
        }

        def sha256(message, secret=""):
            return hmac.new(secret, message, hashlib.sha256).digest()

        def getHash(message):
            return hashlib.sha256(message).hexdigest()

        version = "2018-03-21"
        action = "ImageTranslate"
        endpoint = "tmt.tencentcloudapi.com"
        httpRequestMethod = "POST"
        canonicalUri = "/"
        canonicalQueryString = ""
        canonicalHeaders = "content-type:application/json\n" + "host:" + endpoint + "\n"
        signedHeaders = "content-type;host"
        payload = json.dumps(req_para)
        hashedRequestPayload = getHash(payload.encode())
        canonicalRequest = (
            httpRequestMethod
            + "\n"
            + canonicalUri
            + "\n"
            + canonicalQueryString
            + "\n"
            + canonicalHeaders
            + "\n"
            + signedHeaders
            + "\n"
            + hashedRequestPayload
        )
        algorithm = "TC3-HMAC-SHA256"
        hashedCanonicalRequest = getHash(canonicalRequest.encode())
        date = time.strftime("%Y-%m-%d")
        timestamp = str(int(time.time()))
        service = "tmt"
        credentialScope = date + "/" + service + "/" + "tc3_request"
        stringToSign = (
            algorithm
            + "\n"
            + timestamp
            + "\n"
            + credentialScope
            + "\n"
            + hashedCanonicalRequest
        )
        kDate = sha256(date.encode(), ("TC3" + self.config["SecretKey"]).encode())
        kService = sha256(service.encode(), kDate)
        kSigning = sha256("tc3_request".encode(), kService)
        signature = sha256(stringToSign.encode(), kSigning).hex()
        authorization = (
            algorithm
            + " "
            + "Credential="
            + self.config["SecretId"]
            + "/"
            + credentialScope
            + ", "
            + "SignedHeaders="
            + signedHeaders
            + ", "
            + "Signature="
            + signature
        )

        r = self.proxysession.post(
            url="https://tmt.tencentcloudapi.com",
            headers={
                "Authorization": authorization,
                "content-type": "application/json",
                "Host": endpoint,
                "X-TC-Action": action,
                "X-TC-Timestamp": timestamp,
                "X-TC-Version": version,
                "X-TC-Region": self.region,
            },
            data=payload,
        )

        try:
            boxs = [
                (_["X"], _["Y"], _["X"] + _["W"], _["Y"] + _["H"])
                for _ in r.json()["Response"]["ImageRecord"]["Value"]
            ]
            texts = [
                _["TargetText"] for _ in r.json()["Response"]["ImageRecord"]["Value"]
            ]
            return {"box": boxs, "text": texts, "isocrtranslate": True}
        except:
            raise Exception(r.json())

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

    def ocr_ocr(self, imagebinary):
        self.checkempty(["SecretId", "SecretKey"])

        encodestr = str(base64.b64encode(imagebinary), "utf-8")
        req_para = {
            "LanguageType": self.langocr,
            "Action": "GeneralBasicOCR",
            "ImageBase64": encodestr,
            "Version": "2018-11-19",
            "Region": self.region,  # https://cloud.tencent.com/document/product/866/33526
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
            texts = [_["DetectedText"] for _ in r.json()["Response"]["TextDetections"]]
            return {"box": boxs, "text": texts}
        except:
            raise Exception(r.text)

    def ocr(self, imagebinary):
        interfacetype = self.config["interface"]
        if interfacetype == 0:
            return self.ocr_ocr(imagebinary)
        elif interfacetype == 1:
            return self.ocr_fy(imagebinary)
        raise Exception("unknown")
