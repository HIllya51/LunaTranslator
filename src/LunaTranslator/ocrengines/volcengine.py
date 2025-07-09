from collections import OrderedDict
from urllib.parse import urlencode
from functools import reduce
import hmac, base64
import datetime
import pytz
import hashlib
import sys
from urllib.parse import quote

VERSION = "v1.0.75"


class MetaData(object):
    def __init__(self):
        self.algorithm = ""
        self.credential_scope = ""
        self.signed_headers = ""
        self.date = ""
        self.region = ""
        self.service = ""

    def set_date(self, date):
        self.date = date

    def set_service(self, service):
        self.service = service

    def set_region(self, region):
        self.region = region

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def set_credential_scope(self, credential_scope):
        self.credential_scope = credential_scope

    def set_signed_headers(self, signed_headers):
        self.signed_headers = signed_headers


class Request(object):
    def __init__(self):
        self.schema = ""
        self.method = ""
        self.host = ""
        self.path = ""
        self.headers = OrderedDict()
        self.query = OrderedDict()
        self.body = ""
        self.form = dict()
        self.connection_timeout = 0
        self.socket_timeout = 0

    def set_shema(self, schema):
        self.schema = schema

    def set_method(self, method):
        self.method = method

    def set_host(self, host):
        self.host = host

    def set_path(self, path):
        self.path = path

    def set_headers(self, headers):
        self.headers = headers

    def set_query(self, query):
        self.query = query

    def set_body(self, body):
        self.body = body

    def set_connection_timeout(self, connection_timeout):
        self.connection_timeout = connection_timeout

    def set_socket_timeout(self, socket_timeout):
        self.socket_timeout = socket_timeout

    def build(self, doseq=0):
        return (
            self.schema
            + "://"
            + self.host
            + self.path
            + "?"
            + urlencode(self.query, doseq)
        )


class Util(object):
    @staticmethod
    def norm_uri(path):
        return quote(path).replace("%2F", "/").replace("+", "%20")

    @staticmethod
    def norm_query(params):
        query = ""
        for key in sorted(params.keys()):
            if type(params[key]) == list:
                for k in params[key]:
                    query = (
                        query
                        + quote(key, safe="-_.~")
                        + "="
                        + quote(k, safe="-_.~")
                        + "&"
                    )
            else:
                query = (
                    query
                    + quote(key, safe="-_.~")
                    + "="
                    + quote(params[key], safe="-_.~")
                    + "&"
                )
        query = query[:-1]
        return query.replace("+", "%20")

    @staticmethod
    def hmac_sha256(key, content):
        # type(key) == <class 'bytes'>
        if sys.version_info[0] == 3:
            return hmac.new(
                key, bytes(content, encoding="utf-8"), hashlib.sha256
            ).digest()
        else:
            return hmac.new(
                key, bytes(content.encode("utf-8")), hashlib.sha256
            ).digest()

    @staticmethod
    def sha256(content):
        # type(content) == <class 'str'>
        if sys.version_info[0] == 3:
            if isinstance(content, str) is True:
                return hashlib.sha256(content.encode("utf-8")).hexdigest()
            else:
                return hashlib.sha256(content).hexdigest()
        else:
            if isinstance(content, (str, unicode)) is True:
                return hashlib.sha256(content.encode("utf-8")).hexdigest()
            else:
                return hashlib.sha256(content).hexdigest()

    @staticmethod
    def to_hex(content):
        lst = []
        for ch in content:
            if sys.version_info[0] == 3:
                hv = hex(ch).replace("0x", "")
            else:
                hv = hex(ord(ch)).replace("0x", "")
            if len(hv) == 1:
                hv = "0" + hv
            lst.append(hv)
        return reduce(lambda x, y: x + y, lst)


class Credentials(object):
    def __init__(self, ak, sk, service, region, session_token=""):
        self.ak = ak
        self.sk = sk
        self.service = service
        self.region = region
        self.session_token = session_token

    def set_ak(self, ak):
        self.ak = ak

    def set_sk(self, sk):
        self.sk = sk

    def set_session_token(self, session_token):
        self.session_token = session_token


class SignerV4(object):
    @staticmethod
    def sign(request, credentials):
        if request.path == "":
            request.path = "/"
        if request.method != "GET" and not ("Content-Type" in request.headers):
            request.headers["Content-Type"] = (
                "application/x-www-form-urlencoded; charset=utf-8"
            )

        format_date = SignerV4.get_current_format_date()
        request.headers["X-Date"] = format_date
        if credentials.session_token != "":
            request.headers["X-Security-Token"] = credentials.session_token

        md = MetaData()
        md.set_algorithm("HMAC-SHA256")
        md.set_service(credentials.service)
        md.set_region(credentials.region)
        md.set_date(format_date[:8])

        hashed_canon_req = SignerV4.hashed_canonical_request_v4(request, md)
        md.set_credential_scope("/".join([md.date, md.region, md.service, "request"]))

        signing_str = "\n".join(
            [md.algorithm, format_date, md.credential_scope, hashed_canon_req]
        )
        signing_key = SignerV4.get_signing_secret_key_v4(
            credentials.sk, md.date, md.region, md.service
        )
        sign = Util.to_hex(Util.hmac_sha256(signing_key, signing_str))
        request.headers["Authorization"] = SignerV4.build_auth_header_v4(
            sign, md, credentials
        )
        return

    @staticmethod
    def hashed_canonical_request_v4(request, meta):
        # if sys.version_info[0] == 3:
        #     body_hash = Util.sha256(request.body.decode('utf-8'))
        # else:
        body_hash = Util.sha256(request.body)
        request.headers["X-Content-Sha256"] = body_hash

        signed_headers = dict()
        for key in request.headers:
            if key in ["Content-Type", "Content-Md5", "Host"] or key.startswith("X-"):
                signed_headers[key.lower()] = request.headers[key]

        if "host" in signed_headers:
            v = signed_headers["host"]
            if v.find(":") != -1:
                split = v.split(":")
                port = split[1]
                if str(port) == "80" or str(port) == "443":
                    signed_headers["host"] = split[0]

        signed_str = ""
        for key in sorted(signed_headers.keys()):
            signed_str += key + ":" + signed_headers[key] + "\n"

        meta.set_signed_headers(";".join(sorted(signed_headers.keys())))

        canoncial_request = "\n".join(
            [
                request.method,
                Util.norm_uri(request.path),
                Util.norm_query(request.query),
                signed_str,
                meta.signed_headers,
                body_hash,
            ]
        )

        return Util.sha256(canoncial_request)

    @staticmethod
    def signature_v4(signing_key, signing_str):
        return Util.to_hex(Util.hmac_sha256(signing_key, signing_str))

    @staticmethod
    def get_signing_secret_key_v4(sk, date, region, service):
        if sys.version_info[0] == 3:
            kdate = Util.hmac_sha256(bytes(sk, encoding="utf-8"), date)
        else:
            kdate = Util.hmac_sha256(sk.encode("utf-8"), date)
        kregion = Util.hmac_sha256(kdate, region)
        kservice = Util.hmac_sha256(kregion, service)
        return Util.hmac_sha256(kservice, "request")

    @staticmethod
    def build_auth_header_v4(signature, meta, credentials):
        credential = credentials.ak + "/" + meta.credential_scope
        return (
            meta.algorithm
            + " Credential="
            + credential
            + ", SignedHeaders="
            + meta.signed_headers
            + ", Signature="
            + signature
        )

    @staticmethod
    def get_current_format_date():
        return datetime.datetime.now(tz=pytz.timezone("UTC")).strftime("%Y%m%dT%H%M%SZ")


class ServiceInfo(object):
    def __init__(
        self,
        host,
        header,
        credentials,
        connection_timeout,
        socket_timeout,
        scheme="http",
    ):
        self.host = host
        self.header = header
        self.credentials = credentials
        self.connection_timeout = connection_timeout
        self.socket_timeout = socket_timeout
        self.scheme = scheme


class ApiInfo(object):
    def __init__(self, method, path, query, form, header):
        self.method = method
        self.path = path
        self.query = query
        self.form = form
        self.header = header

    def __str__(self):
        return "method: " + self.method + ", path: " + self.path


class Service(object):
    def __init__(self, service_info, api_info):
        self.service_info = service_info
        self.api_info = api_info

    def set_ak(self, ak):
        self.service_info.credentials.set_ak(ak)

    def set_sk(self, sk):
        self.service_info.credentials.set_sk(sk)

    def set_session_token(self, session_token):
        self.service_info.credentials.set_session_token(session_token)

    def set_host(self, host):
        self.service_info.host = host

    def post(self, api, params, form, session):
        if not (api in self.api_info):
            raise Exception("no such api")
        api_info = self.api_info[api]
        r = self.prepare_request(api_info, params)
        r.headers["Content-Type"] = "application/x-www-form-urlencoded"
        r.form = self.merge(api_info.form, form)
        r.body = urlencode(r.form, True)
        SignerV4.sign(r, self.service_info.credentials)

        url = r.build()

        resp = session.post(
            url,
            headers=r.headers,
            data=r.form,
        )
        return resp

    def prepare_request(self, api_info, params, doseq=0):
        for key in params:
            if (
                type(params[key]) == int
                or type(params[key]) == float
                or type(params[key]) == bool
            ):
                params[key] = str(params[key])
            elif sys.version_info[0] != 3:
                if type(params[key]) == unicode:
                    params[key] = params[key].encode("utf-8")
            elif type(params[key]) == list:
                if not doseq:
                    params[key] = ",".join(params[key])

        connection_timeout = self.service_info.connection_timeout
        socket_timeout = self.service_info.socket_timeout

        r = Request()
        r.set_shema(self.service_info.scheme)
        r.set_method(api_info.method)
        r.set_connection_timeout(connection_timeout)
        r.set_socket_timeout(socket_timeout)

        mheaders = self.merge(api_info.header, self.service_info.header)
        mheaders["Host"] = self.service_info.host
        mheaders["User-Agent"] = "volc-sdk-python/" + VERSION
        r.set_headers(mheaders)

        mquery = self.merge(api_info.query, params)
        r.set_query(mquery)

        r.set_host(self.service_info.host)
        r.set_path(api_info.path)

        return r

    def merge(self, param1, param2):
        od = OrderedDict()
        for key in param1:
            od[key] = param1[key]

        for key in param2:
            od[key] = param2[key]

        return od


class VisualService(Service):

    def __init__(self):
        self.service_info = VisualService.get_service_info()
        self.api_info = {}
        super(VisualService, self).__init__(self.service_info, self.api_info)

    @staticmethod
    def get_service_info():
        service_info = ServiceInfo(
            "visual.volcengineapi.com",
            {},
            Credentials("", "", "cv", "cn-north-1"),
            10,
            30,
        )
        return service_info

    def ocr_api(self, action, form, session):
        try:
            resp = self.post(action, {}, form, session)
            return resp.json()
        except Exception as e:
            raise Exception(resp)

    def set_api_info(self, action, version):
        self.api_info[action] = ApiInfo(
            "POST", "/", {"Action": action, "Version": version}, {}, {}
        )


import base64
from ocrengines.baseocrclass import baseocr, OCRResult


class OCR(baseocr):

    def ocr(self, imagebinary):
        visual_service = VisualService()
        self.checkempty(["Access Key ID", "Secret Access Key"])
        # call below method if you dont set ak and sk in $HOME/.volc/config
        visual_service.set_ak(self.multiapikeycurrent["Access Key ID"])
        visual_service.set_sk(self.multiapikeycurrent["Secret Access Key"])

        visual_service.set_api_info("MultiLanguageOCR", "2022-08-31")

        # below shows the sdk usage for all common apis,
        # if you cannot find the needed one, please check other example files in the same dir
        # or contact us for further help
        form = dict()

        b64 = base64.b64encode(imagebinary)
        form["image_base64"] = b64
        resp = visual_service.ocr_api("MultiLanguageOCR", form, self.proxysession)
        try:
            texts = [box["text"] for box in resp["data"]["ocr_infos"]]
            boxs = self.flatten4point(
                [box["rect"] for box in resp["data"]["ocr_infos"]]
            )
            return OCRResult(boxs=boxs, texts=texts)
        except:
            raise Exception(resp)
