import base64, hashlib
from ocrengines.baseocrclass import baseocr
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json


class OCR(baseocr):
    def ocr(self, imagebinary):
        self.checkempty(["APPId", "APISecret", "APIKey"])

        APPId = self.config["APPId"]
        APISecret = self.config["APISecret"]
        APIKey = self.config["APIKey"]
        SRCLANG = self.srclang

        class AssembleHeaderException(Exception):
            def __init__(self, msg):
                self.message = msg

        class Url:
            def __init__(this, host, path, schema):
                this.host = host
                this.path = path
                this.schema = schema
                pass

        class printed_word_recognition(object):

            def __init__(self):
                self.appid = APPId
                self.apikey = APIKey
                self.apisecret = APISecret
                self.url = "https://cn-east-1.api.xf-yun.com/v1/ocr"

            def parse_url(self, requset_url):
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

            def get_body(self, imagebinary):
                buf = imagebinary
                body = {
                    "header": {"app_id": self.appid, "status": 3},
                    "parameter": {
                        "ocr": {
                            "language": SRCLANG,
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
                            "image": str(base64.b64encode(buf), "utf-8"),
                            "status": 3,
                        }
                    },
                }
                return body

        # build websocket auth request url
        def assemble_ws_auth_url(requset_url, method="POST", api_key="", api_secret=""):
            u = printed_word_recognition.parse_url(requset_url)
            host = u.host
            path = u.path
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))
            # print(date)
            # date = "Thu, 12 Dec 2019 01:57:27 GMT"
            signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(
                host, date, method, path
            )
            # print(signature_origin)
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
            authorization = base64.b64encode(
                authorization_origin.encode("utf-8")
            ).decode(encoding="utf-8")
            # print(authorization_origin)
            values = {"host": host, "date": date, "authorization": authorization}

            return requset_url + "?" + urlencode(values)

        printed_word_recognition = printed_word_recognition()
        request_url = assemble_ws_auth_url(
            printed_word_recognition.url,
            "POST",
            printed_word_recognition.apikey,
            printed_word_recognition.apisecret,
        )
        headers = {
            "content-type": "application/json",
            "host": "cn-east-1.api.xf-yun.com",
            "app_id": APPId,
        }
        # print("request_url:", request_url)

        body = printed_word_recognition.get_body(file_path=imagebinary)
        response = self.session.post(
            request_url, data=json.dumps(body), headers=headers
        )

        re = response.content.decode("utf8")
        str_result = json.loads(re)
        # print("\nresponse-content:", re)
        try:
            renew_text = str_result["payload"]["ocr_output_text"]["text"]
            finalResult = json.loads(str(base64.b64decode(renew_text), "utf-8"))
        except:
            raise Exception(str_result)
        try:
            res = finalResult["pages"][0]
            if "lines" not in res:
                return ""
            boxs = []
            texts = []
            for line in res["lines"]:
                coord = line["coord"]
                boxs.append(
                    [
                        coord[0]["x"],
                        coord[0]["y"],
                        coord[1]["x"],
                        coord[1]["y"],
                        coord[2]["x"],
                        coord[2]["y"],
                        coord[3]["x"],
                        coord[3]["y"],
                    ]
                )
                texts.append(line["content"])
            return self.common_solve_text_orientation(boxs, texts)
        except:
            raise Exception(finalResult)
