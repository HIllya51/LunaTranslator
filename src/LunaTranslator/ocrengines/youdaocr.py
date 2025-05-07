import base64
import uuid
import time
import hashlib
from ocrengines.baseocrclass import baseocr, OCRResult
from language import Languages


class OCR(baseocr):
    def langmap(self):
        return {Languages.Chinese: "zh-CHS", Languages.TradChinese: "zh-CHT"}

    def freetest(self, imagebinary):
        headers = {
            "authority": "aidemo.youdao.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://ai.youdao.com",
            "referer": "https://ai.youdao.com/",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
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

            return OCRResult(
                boxs=[
                    [int(_) for _ in l["boundingBox"].split(",")]
                    for l in response.json()["lines"]
                ],
                texts=[l["words"] for l in response.json()["lines"]],
            )
        except:
            raise Exception(response)

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
        APP_KEY, APP_SECRET = (
            self.multiapikeycurrent["APP_KEY"],
            self.multiapikeycurrent["APP_SECRET"],
        )
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
        try:
            _ = []
            for l in response.json()["Result"]["regions"]:
                _ += l["lines"]
            return OCRResult(
                boxs=[[int(_) for _ in l["boundingBox"].split(",")] for l in _],
                texts=[l["text"] for l in _],
            )
        except:
            raise Exception(response)

    def freetest_ts(self, imagebinary):

        headers = {
            "authority": "aidemo.youdao.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://ai.youdao.com",
            "referer": "https://ai.youdao.com/",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
        b64 = base64.b64encode(imagebinary)
        data = {
            "imgBase": "data:image/jpeg;base64," + str(b64, encoding="utf8"),
            "lang": "",
            "company": "",
        }

        response = self.proxysession.post(
            "https://aidemo.youdao.com/ocrtransapi1", headers=headers, data=data
        )

        try:
            return OCRResult(
                texts=[l["tranContent"] for l in response.json()["lines"]],
                isocrtranslate=True,
            )
        except:
            raise Exception(response)

    def ocrapi_ts(self, imagebinary):

        self.checkempty(["APP_KEY", "APP_SECRET"])
        APP_KEY, APP_SECRET = (
            self.multiapikeycurrent["APP_KEY"],
            self.multiapikeycurrent["APP_SECRET"],
        )

        """
        添加鉴权相关参数 -
            appKey : 应用ID
            salt : 随机值
            curtime : 当前时间戳(秒)
            signType : 签名版本
            sign : 请求签名
            
            @param appKey    您的应用ID
            @param appSecret 您的应用密钥
            @param paramsMap 请求参数表
        """

        def addAuthParams(appKey, appSecret, params):
            q = params.get("q")
            if q is None:
                q = params.get("img")
            salt = str(uuid.uuid1())
            curtime = str(int(time.time()))
            sign = calculateSign(appKey, appSecret, q, salt, curtime)
            params["appKey"] = appKey
            params["salt"] = salt
            params["curtime"] = curtime
            params["signType"] = "v3"
            params["sign"] = sign

        """
            计算鉴权签名 -
            计算方式 : sign = sha256(appKey + input(q) + salt + curtime + appSecret)
            @param appKey    您的应用ID
            @param appSecret 您的应用密钥
            @param q         请求内容
            @param salt      随机值
            @param curtime   当前时间戳(秒)
            @return 鉴权签名sign
        """

        def calculateSign(appKey, appSecret, q, salt, curtime):
            strSrc = appKey + getInput(q) + salt + curtime + appSecret
            return encrypt(strSrc)

        def encrypt(strSrc):
            hash_algorithm = hashlib.sha256()
            hash_algorithm.update(strSrc.encode("utf-8"))
            return hash_algorithm.hexdigest()

        def getInput(input):
            if input is None:
                return input
            inputLen = len(input)
            return (
                input
                if inputLen <= 20
                else input[0:10] + str(inputLen) + input[inputLen - 10 : inputLen]
            )

        def createRequest():
            """
            note: 将下列变量替换为需要请求的参数
            取值参考文档: https://ai.youdao.com/DOCSIRMA/html/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E7%BF%BB%E8%AF%91/API%E6%96%87%E6%A1%A3/%E5%9B%BE%E7%89%87%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1/%E5%9B%BE%E7%89%87%E7%BF%BB%E8%AF%91%E6%9C%8D%E5%8A%A1-API%E6%96%87%E6%A1%A3.html
            """
            lang_from = self.srclang
            lang_to = self.tgtlang
            render = "0"  #'是否需要服务端返回渲染的图片'
            type = "1"

            # 数据的base64编码
            q = readFileAsBase64(imagebinary)
            data = {
                "q": q,
                "from": lang_from,
                "to": lang_to,
                "render": render,
                "type": type,
            }

            addAuthParams(APP_KEY, APP_SECRET, data)

            header = {"Content-Type": "application/x-www-form-urlencoded"}
            res = doCall("https://openapi.youdao.com/ocrtransapi", header, data, "post")
            return res

        def doCall(url, header, params, method):
            if "get" == method:
                return self.proxysession.get(url, params)
            elif "post" == method:
                return self.proxysession.post(url, params, header)

        def readFileAsBase64(imagebinary):
            return str(base64.b64encode(imagebinary), "utf-8")

        response = createRequest()
        try:

            text = [_["tranContent"] for _ in response.json()["resRegions"]]
            box = [
                [int(_) for _ in l["boundingBox"].split(",")]
                for l in response.json()["resRegions"]
            ]
            return OCRResult(boxs=box, texts=text, isocrtranslate=True)
        except:
            raise Exception(response)

    def ocr(self, imagebinary):
        interfacetype = self.config["interface"]
        if interfacetype == 1:
            return self.freetest(imagebinary)
        elif interfacetype == 0:
            return self.ocrapi(imagebinary)
        elif interfacetype == 2:
            return self.ocrapi_ts(imagebinary)
        elif interfacetype == 3:
            return self.freetest_ts(imagebinary)
        raise Exception("unknown")
