import base64, hashlib
from ocrengines.baseocrclass import baseocr, OCRResult
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from language import Languages
from urllib.parse import urlencode
import json


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3 :]
    schema = requset_url[: stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    # date = "Mon, 22 Aug 2022 03:26:45 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(
        host, date, method, path
    )
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding="utf-8")
    authorization_origin = (
        'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
        % (api_key, "hmac-sha256", "host date request-line", signature_sha)
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
        encoding="utf-8"
    )
    values = {"host": host, "date": date, "authorization": authorization}

    return requset_url + "?" + urlencode(values)


class OCR(baseocr):
    def get_result(self, url, bina, appid, apisecret, apikey):
        request_url = assemble_ws_auth_url(url, "POST", apikey, apisecret)
        headers = {
            "host": "api.xf-yun.com",
            "appid": "APPID",
        }
        body = {
            "header": {"app_id": appid, "status": 3},
            "parameter": {
                "hh_ocr_recognize_doc": {
                    "recognizeDocumentRes": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json",
                    }
                }
            },
            "payload": {
                "image": {
                    "encoding": "jpg",
                    "image": str(base64.b64encode(bina), "utf-8"),
                    "status": 3,
                }
            },
        }
        response = self.proxysession.post(request_url, json=body, headers=headers)
        re = response.content.decode("utf8")
        try:
            str_result = json.loads(re)
            renew_text = str_result["payload"]["recognizeDocumentRes"]["text"]
            result = json.loads(str(base64.b64decode(renew_text), "utf-8"))["lines"]
            boxs = []
            texts = []
            for line in result:
                boxs.append(line["position"])
                texts.append(line["text"])
            return boxs, texts
        except:
            raise Exception(response)

    def get_result2(self, url, appid, apisecret, apikey, bina):
        request_url = assemble_ws_auth_url(url, "POST", apikey, apisecret)
        headers = {
            "host": "cn-east-1.api.xf-yun.com",
            "app_id": appid,
        }
        body = {
            "header": {"app_id": appid, "status": 3},
            "parameter": {
                "ocr": {
                    "language": self.srclang,
                    "ocr_output_text": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json",
                    },
                }
            },
            "payload": {
                "image": {
                    "encoding": "jpg",
                    "image": str(base64.b64encode(bina), "utf-8"),
                    "status": 3,
                }
            },
        }
        response = self.proxysession.post(request_url, json=body, headers=headers)

        re = response.content.decode("utf8")
        try:
            str_result = json.loads(re)
            renew_text = str_result["payload"]["ocr_output_text"]["text"]
            pages = json.loads(str(base64.b64decode(renew_text), "utf-8"))["pages"]
            boxs = []
            texts = []
            for page in pages:
                for line in page.get("lines", []):
                    texts.append(line["content"])
                    boxs.append(
                        [
                            line["coord"][0]["x"],
                            line["coord"][0]["y"],
                            line["coord"][1]["x"],
                            line["coord"][1]["y"],
                            line["coord"][2]["x"],
                            line["coord"][2]["y"],
                            line["coord"][3]["x"],
                            line["coord"][3]["y"],
                        ]
                    )
            return boxs, texts
        except:
            raise Exception(response)

    def langmap(self):
        return {
            Languages.Chinese: "ch_en",
            Languages.English: "ch_en",
            Languages.TradChinese: "ch_en",
        }

    def ocr(self, imagebinary):
        self.checkempty(["APPId", "APISecret", "APIKey"])
        appid = self.multiapikeycurrent["APPId"]
        apisecret = self.multiapikeycurrent["APISecret"]
        apikey = self.multiapikeycurrent["APIKey"]
        if self.config["interface"] == "hh_ocr_recognize_doc":
            boxs, texts = self.get_result(
                "http://api.xf-yun.com/v1/private/hh_ocr_recognize_doc",
                imagebinary,
                appid,
                apisecret,
                apikey,
            )
        elif self.config["interface"] == "ocr":
            if self.is_src_auto:
                self.raise_cant_be_auto_lang()
            boxs, texts = self.get_result2(
                "https://cn-east-1.api.xf-yun.com/v1/ocr",
                appid,
                apisecret,
                apikey,
                imagebinary,
            )

        return OCRResult(boxs=boxs, texts=texts)
