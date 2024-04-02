import hashlib
import time, hmac, base64, uuid, json
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):
    def langmap(self):
        # https://cloud.tencent.com/document/product/551/17232
        return {"cht": "zh-TW"}

    def ocr(self, imgfile):
        self.checkempty(["SecretId", "SecretKey"])

        with open(imgfile, "rb") as f:
            data = f.read()
            encodestr = str(base64.b64encode(data), "utf-8")
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

        region = [
            "ap-beijing",
            "ap-shanghai",
            "ap-chengdu",
            "ap-chongqing",
            "ap-guangzhou",
            "ap-hongkong",
            "ap-mumbai",
            "ap-seoul",
            "ap-shanghai-fsi",
            "ap-shenzhen-fsi",
            "ap-singapore",
            "ap-tokyo",
            "ap-bangkok",
            "eu-frankfurt",
            "na-ashburn",
            "na-siliconvalley",
            "na-toronto",
        ][self.config["Region"]]
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

        r = self.session.post(
            url="https://tmt.tencentcloudapi.com",
            headers={
                "Authorization": authorization,
                "content-type": "application/json",
                "Host": endpoint,
                "X-TC-Action": action,
                "X-TC-Timestamp": timestamp,
                "X-TC-Version": version,
                "X-TC-Region": region,
            },
            data=payload,
            timeout=10,
        )

        try:
            boxs = [
                (_["X"], _["Y"], _["X"] + _["W"], _["Y"] + _["H"])
                for _ in r.json()["Response"]["ImageRecord"]["Value"]
            ]
            texts = [
                _["TargetText"] for _ in r.json()["Response"]["ImageRecord"]["Value"]
            ]
            return "<notrans>" + self.common_solve_text_orientation(boxs, texts)
        except:
            raise Exception(r.json())
