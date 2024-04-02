import json
from collections import OrderedDict
import requests


import requests
from urllib.parse import urlencode
from functools import reduce
import hmac, base64
import datetime
import pytz
import hashlib, os
import sys, threading
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
    def hmac_sha1(key, content):
        # type(key) == <class 'bytes'>
        if sys.version_info[0] == 3:
            return hmac.new(
                key, bytes(content, encoding="utf-8"), hashlib.sha1
            ).digest()
        else:
            return hmac.new(key, bytes(content.encode("utf-8")), hashlib.sha1).digest()

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

    @staticmethod
    def pad(plain_text):
        block_size = AES.block_size

        number_of_bytes_to_pad = block_size - len(plain_text) % block_size
        ascii_string = chr(0)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding_str
        return padded_plain_text

    @staticmethod
    def generate_access_key_id(prefix):
        uid = str(uuid.uuid4())
        uid_base64 = base64.b64encode(uid.replace("-", "").encode(encoding="utf-8"))

        s = (
            uid_base64.decode()
            .replace("=", "")
            .replace("/", "")
            .replace("+", "")
            .replace("-", "")
        )
        return prefix + s

    @staticmethod
    def rand_string_runes(length):
        return "".join(random.sample(list(LETTER_RUNES), length))

    @staticmethod
    def aes_encrypt_cbc_with_base64(orig_data, key):
        # type(orig_data) == <class 'str'>
        # type(key) == <class 'bytes'>
        generator = AES.new(key, AES.MODE_CBC, key)
        if sys.version_info[0] == 3:
            crypt = generator.encrypt(Util.pad(orig_data).encode("utf-8"))
            return base64.b64encode(crypt).decode()
        else:
            crypt = generator.encrypt(Util.pad(orig_data))
            return base64.b64encode(crypt)

    @staticmethod
    def generate_secret_key():
        rand_str = Util.rand_string_runes(32)
        return Util.aes_encrypt_cbc_with_base64(
            rand_str, "bytedance-isgood".encode("utf-8")
        )

    @staticmethod
    def crc32(file_path):
        prev = 0
        for eachLine in open(file_path, "rb"):
            prev = crc32(eachLine, prev)
        return prev & 0xFFFFFFFF


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
    def sign_url(request, credentials):
        format_date = SignerV4.get_current_format_date()
        date = format_date[:8]

        md = MetaData()
        md.set_date(date)
        md.set_service(credentials.service)
        md.set_region(credentials.region)
        md.set_signed_headers("")
        md.set_algorithm("HMAC-SHA256")
        md.set_credential_scope("/".join([md.date, md.region, md.service, "request"]))

        query = request.query
        query["X-Date"] = format_date
        query["X-NotSignBody"] = ""
        query["X-Credential"] = credentials.ak + "/" + md.credential_scope
        query["X-Algorithm"] = md.algorithm
        query["X-SignedHeaders"] = md.signed_headers
        query["X-SignedQueries"] = ""
        query["X-SignedQueries"] = ";".join(sorted(query.keys()))
        if credentials.session_token != "":
            query["X-Security-Token"] = credentials.session_token

        hashed_canon_req = SignerV4.hashed_simple_canonical_request_v4(request, md)
        signing_str = "\n".join(
            [md.algorithm, format_date, md.credential_scope, hashed_canon_req]
        )
        signing_key = SignerV4.get_signing_secret_key_v4(
            credentials.sk, md.date, md.region, md.service
        )
        sign = SignerV4.signature_v4(signing_key, signing_str)

        query["X-Signature"] = sign
        return urlencode(query)

    @staticmethod
    def sign_only(param, credentials):
        request = Request()
        request.host = param.host
        request.method = param.method
        request.path = param.path
        request.body = param.body
        request.query = param.query
        request.headers = param.header_list

        format_date = param.date.strftime("%Y%m%dT%H%M%SZ")
        date = format_date[:8]
        request.headers["X-Date"] = format_date
        md = MetaData()
        md.set_algorithm("HMAC-SHA256")
        md.set_service(credentials.service)
        md.set_region(credentials.region)
        md.set_date(date)
        md.set_credential_scope("/".join([md.date, md.region, md.service, "request"]))

        if param.is_sign_url:
            md.set_signed_headers("")
            md.set_credential_scope(
                "/".join([md.date, md.region, md.service, "request"])
            )
            query = request.query
            query["X-Date"] = format_date
            query["X-NotSignBody"] = ""
            query["X-Credential"] = credentials.ak + "/" + md.credential_scope
            query["X-Algorithm"] = md.algorithm
            query["X-SignedHeaders"] = md.signed_headers
            query["X-SignedQueries"] = ""
            query["X-SignedQueries"] = ";".join(sorted(query.keys()))
            if credentials.session_token != "":
                query["X-Security-Token"] = credentials.session_token
            hashed_canon_req = SignerV4.hashed_simple_canonical_request_v4(request, md)
        else:
            if credentials.session_token != "":
                request.headers["X-Security-Token"] = credentials.session_token
            hashed_canon_req = SignerV4.hashed_canonical_request_v4(request, md)

        signing_str = "\n".join(
            [md.algorithm, format_date, md.credential_scope, hashed_canon_req]
        )
        signing_key = SignerV4.get_signing_secret_key_v4(
            credentials.sk, md.date, md.region, md.service
        )
        sign = SignerV4.signature_v4(signing_key, signing_str)

        result = SignResult()
        result.xdate = format_date
        result.xAlgorithm = md.algorithm
        if param.is_sign_url:
            result.xSignedQueries = request.query["X-SignedQueries"]
        result.xSignedHeaders = md.signed_headers
        result.xCredential = credentials.ak + "/" + md.credential_scope
        result.xSignature = sign
        result.xContextSha256 = request.headers["X-Content-Sha256"]
        result.authorization = (
            result.xAlgorithm
            + " Credential="
            + result.xCredential
            + ", SignedHeaders="
            + md.signed_headers
            + ", Signature="
            + result.xSignature
        )
        result.xSecurityToken = credentials.session_token

        return result

    @staticmethod
    def hashed_simple_canonical_request_v4(request, meta):
        body = bytes()
        # if sys.version_info[0] == 3:
        #     body_hash = Util.sha256(body.decode('utf-8'))
        # else:
        body_hash = Util.sha256(body)

        if request.path == "":
            request.path = "/"

        canoncial_request = "\n".join(
            [
                request.method,
                Util.norm_uri(request.path),
                Util.norm_query(request.query),
                "\n",
                meta.signed_headers,
                body_hash,
            ]
        )
        # if sys.version_info[0] == 3:
        #     return Util.sha256(canoncial_request.decode('utf-8'))
        # else:
        return Util.sha256(canoncial_request)

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
        self.session = requests.session()
        self.init()

    def init(self):
        if "VOLC_ACCESSKEY" in os.environ and "VOLC_SECRETKEY" in os.environ:
            self.service_info.credentials.set_ak(os.environ["VOLC_ACCESSKEY"])
            self.service_info.credentials.set_sk(os.environ["VOLC_SECRETKEY"])
        else:
            if os.environ.get("HOME", None) is None:
                return
            # 先尝试从credentials中读取ak、sk，credentials不存在则从config中读取
            path_ini = os.environ["HOME"] + "/.volc/credentials"
            path_json = os.environ["HOME"] + "/.volc/config"
            if os.path.isfile(path_ini):
                conf = configparser.ConfigParser()
                conf.read(path_ini)
                default_section, ak_option, sk_option = (
                    "default",
                    "access_key_id",
                    "secret_access_key",
                )
                if conf.has_section(default_section):
                    if conf.has_option(default_section, ak_option):
                        ak = conf.get(default_section, ak_option)
                        self.service_info.credentials.set_ak(ak)
                    if conf.has_option(default_section, sk_option):
                        sk = conf.get(default_section, sk_option)
                        self.service_info.credentials.set_sk(sk)
            elif os.path.isfile(path_json):
                with open(path_json, "r") as f:
                    try:
                        j = json.load(f)
                    except Exception:
                        logging.warning("%s is not json file", path_json)
                        return
                    if "ak" in j:
                        self.service_info.credentials.set_ak(j["ak"])
                    if "sk" in j:
                        self.service_info.credentials.set_sk(j["sk"])

    def set_ak(self, ak):
        self.service_info.credentials.set_ak(ak)

    def set_sk(self, sk):
        self.service_info.credentials.set_sk(sk)

    def set_session_token(self, session_token):
        self.service_info.credentials.set_session_token(session_token)

    def set_host(self, host):
        self.service_info.host = host

    def set_scheme(self, scheme):
        self.service_info.scheme = scheme

    def get_sign_url(self, api, params):
        if not (api in self.api_info):
            raise Exception("no such api")
        api_info = self.api_info[api]

        mquery = self.merge(api_info.query, params)
        r = Request()
        r.set_shema(self.service_info.scheme)
        r.set_method(api_info.method)
        r.set_path(api_info.path)
        r.set_query(mquery)

        return SignerV4.sign_url(r, self.service_info.credentials)

    def get(self, api, params, doseq=0):
        if not (api in self.api_info):
            raise Exception("no such api")
        api_info = self.api_info[api]

        r = self.prepare_request(api_info, params, doseq)

        SignerV4.sign(r, self.service_info.credentials)

        url = r.build(doseq)
        resp = self.session.get(
            url,
            headers=r.headers,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
        )
        if resp.status_code == 200:
            return resp.text
        else:
            raise Exception(resp.text)

    def post(self, api, params, form, proxy):
        if not (api in self.api_info):
            raise Exception("no such api")
        api_info = self.api_info[api]
        r = self.prepare_request(api_info, params)
        r.headers["Content-Type"] = "application/x-www-form-urlencoded"
        r.form = self.merge(api_info.form, form)
        r.body = urlencode(r.form, True)
        SignerV4.sign(r, self.service_info.credentials)

        url = r.build()

        resp = self.session.post(
            url,
            headers=r.headers,
            data=r.form,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
            proxies=proxy,
        )
        if resp.status_code == 200:
            return resp.text
        else:
            raise Exception(resp.text)

    def json(self, api, params, body):
        if not (api in self.api_info):
            raise Exception("no such api")
        api_info = self.api_info[api]
        r = self.prepare_request(api_info, params)
        r.headers["Content-Type"] = "application/json"
        r.body = body

        SignerV4.sign(r, self.service_info.credentials)

        url = r.build()
        resp = self.session.post(
            url,
            headers=r.headers,
            data=r.body,
            timeout=(
                self.service_info.connection_timeout,
                self.service_info.socket_timeout,
            ),
        )
        if resp.status_code == 200:
            return json.dumps(resp.json())
        else:
            raise Exception(resp.text.encode("utf-8"))

    def put(self, url, file_path, headers):
        with open(file_path, "rb") as f:
            resp = self.session.put(url, headers=headers, data=f)
            if resp.status_code == 200:
                return True, resp.text.encode("utf-8")
            else:
                return False, resp.text.encode("utf-8")

    def put_data(self, url, data, headers):
        resp = self.session.put(url, headers=headers, data=data)
        if resp.status_code == 200:
            return True, resp.text.encode("utf-8")
        else:
            return False, resp.text.encode("utf-8")

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
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(VisualService, "_instance"):
            with VisualService._instance_lock:
                if not hasattr(VisualService, "_instance"):
                    VisualService._instance = object.__new__(cls)
        return VisualService._instance

    def __init__(self):
        self.service_info = VisualService.get_service_info()
        self.api_info = VisualService.get_api_info()
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

    @staticmethod
    def get_api_info():
        api_info = {
            "JPCartoonCut": ApiInfo(
                "POST", "/", {"Action": "JPCartoonCut", "Version": "2020-08-26"}, {}, {}
            ),
            "JPCartoon": ApiInfo(
                "POST", "/", {"Action": "JPCartoon", "Version": "2020-08-26"}, {}, {}
            ),
            "IDCard": ApiInfo(
                "POST", "/", {"Action": "IDCard", "Version": "2020-08-26"}, {}, {}
            ),
            "FaceSwap": ApiInfo(
                "POST", "/", {"Action": "FaceSwap", "Version": "2020-08-26"}, {}, {}
            ),
            "OCRNormal": ApiInfo(
                "POST", "/", {"Action": "OCRNormal", "Version": "2020-08-26"}, {}, {}
            ),
            "BankCard": ApiInfo(
                "POST", "/", {"Action": "BankCard", "Version": "2020-08-26"}, {}, {}
            ),
            "HumanSegment": ApiInfo(
                "POST", "/", {"Action": "HumanSegment", "Version": "2020-08-26"}, {}, {}
            ),
            "GeneralSegment": ApiInfo(
                "POST",
                "/",
                {"Action": "GeneralSegment", "Version": "2020-08-26"},
                {},
                {},
            ),
            "EnhancePhoto": ApiInfo(
                "POST", "/", {"Action": "EnhancePhoto", "Version": "2020-08-26"}, {}, {}
            ),
            "ConvertPhoto": ApiInfo(
                "POST", "/", {"Action": "ConvertPhoto", "Version": "2020-08-26"}, {}, {}
            ),
            "VideoSceneDetect": ApiInfo(
                "POST",
                "/",
                {"Action": "VideoSceneDetect", "Version": "2020-08-26"},
                {},
                {},
            ),
            "OverResolution": ApiInfo(
                "POST",
                "/",
                {"Action": "OverResolution", "Version": "2020-08-26"},
                {},
                {},
            ),
            "GoodsSegment": ApiInfo(
                "POST", "/", {"Action": "GoodsSegment", "Version": "2020-08-26"}, {}, {}
            ),
            "ImageOutpaint": ApiInfo(
                "POST",
                "/",
                {"Action": "ImageOutpaint", "Version": "2020-08-26"},
                {},
                {},
            ),
            "ImageInpaint": ApiInfo(
                "POST", "/", {"Action": "ImageInpaint", "Version": "2020-08-26"}, {}, {}
            ),
            "ImageCut": ApiInfo(
                "POST", "/", {"Action": "ImageCut", "Version": "2020-08-26"}, {}, {}
            ),
            "EntityDetect": ApiInfo(
                "POST", "/", {"Action": "EntityDetect", "Version": "2020-08-26"}, {}, {}
            ),
            "GoodsDetect": ApiInfo(
                "POST", "/", {"Action": "GoodsDetect", "Version": "2020-08-26"}, {}, {}
            ),
            "VideoSummarizationSubmitTask": ApiInfo(
                "POST",
                "/",
                {"Action": "VideoSummarizationSubmitTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoSummarizationQueryTask": ApiInfo(
                "GET",
                "/",
                {"Action": "VideoSummarizationQueryTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoOverResolutionSubmitTask": ApiInfo(
                "POST",
                "/",
                {"Action": "VideoOverResolutionSubmitTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoOverResolutionQueryTask": ApiInfo(
                "GET",
                "/",
                {"Action": "VideoOverResolutionQueryTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoRetargetingSubmitTask": ApiInfo(
                "POST",
                "/",
                {"Action": "VideoRetargetingSubmitTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoRetargetingQueryTask": ApiInfo(
                "GET",
                "/",
                {"Action": "VideoRetargetingQueryTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoInpaintSubmitTask": ApiInfo(
                "POST",
                "/",
                {"Action": "VideoInpaintSubmitTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoInpaintQueryTask": ApiInfo(
                "GET",
                "/",
                {"Action": "VideoInpaintQueryTask", "Version": "2020-08-26"},
                {},
                {},
            ),
            "CarPlateDetection": ApiInfo(
                "POST",
                "/",
                {"Action": "CarPlateDetection", "Version": "2020-08-26"},
                {},
                {},
            ),
            "DistortionFree": ApiInfo(
                "POST",
                "/",
                {"Action": "DistortionFree", "Version": "2020-08-26"},
                {},
                {},
            ),
            "StretchRecovery": ApiInfo(
                "POST",
                "/",
                {"Action": "StretchRecovery", "Version": "2020-08-26"},
                {},
                {},
            ),
            "ImageFlow": ApiInfo(
                "POST", "/", {"Action": "ImageFlow", "Version": "2020-08-26"}, {}, {}
            ),
            "ImageScore": ApiInfo(
                "POST", "/", {"Action": "ImageScore", "Version": "2020-08-26"}, {}, {}
            ),
            "PoemMaterial": ApiInfo(
                "POST", "/", {"Action": "PoemMaterial", "Version": "2020-08-26"}, {}, {}
            ),
            "EmoticonEdit": ApiInfo(
                "POST", "/", {"Action": "EmoticonEdit", "Version": "2020-08-26"}, {}, {}
            ),
            "EyeClose2Open": ApiInfo(
                "POST",
                "/",
                {"Action": "EyeClose2Open", "Version": "2020-08-26"},
                {},
                {},
            ),
            "CarSegment": ApiInfo(
                "POST", "/", {"Action": "CarSegment", "Version": "2020-08-26"}, {}, {}
            ),
            "CarDetection": ApiInfo(
                "POST", "/", {"Action": "CarDetection", "Version": "2020-08-26"}, {}, {}
            ),
            "SkySegment": ApiInfo(
                "POST", "/", {"Action": "SkySegment", "Version": "2020-08-26"}, {}, {}
            ),
            "ImageSearchImageAdd": ApiInfo(
                "POST",
                "/",
                {"Action": "ImageSearchImageAdd", "Version": "2020-08-26"},
                {},
                {},
            ),
            "ImageSearchImageDelete": ApiInfo(
                "POST",
                "/",
                {"Action": "ImageSearchImageDelete", "Version": "2020-08-26"},
                {},
                {},
            ),
            "ImageSearchImageSearch": ApiInfo(
                "POST",
                "/",
                {"Action": "ImageSearchImageSearch", "Version": "2020-08-26"},
                {},
                {},
            ),
            "ProductSearchAddImage": ApiInfo(
                "POST",
                "/",
                {"Action": "ProductSearchAddImage", "Version": "2022-06-16"},
                {},
                {},
            ),
            "ProductSearchDeleteImage": ApiInfo(
                "POST",
                "/",
                {"Action": "ProductSearchDeleteImage", "Version": "2022-06-16"},
                {},
                {},
            ),
            "ProductSearchSearchImage": ApiInfo(
                "POST",
                "/",
                {"Action": "ProductSearchSearchImage", "Version": "2022-06-16"},
                {},
                {},
            ),
            "ClueLicense": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrClueLicense", "Version": "2020-08-26"},
                {},
                {},
            ),
            "DrivingLicense": ApiInfo(
                "POST",
                "/",
                {"Action": "DrivingLicense", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VehicleLicense": ApiInfo(
                "POST",
                "/",
                {"Action": "VehicleLicense", "Version": "2020-08-26"},
                {},
                {},
            ),
            "TaxiInvoice": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrTaxiInvoice", "Version": "2020-08-26"},
                {},
                {},
            ),
            "TrainTicket": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrTrainTicket", "Version": "2020-08-26"},
                {},
                {},
            ),
            "FlightInvoice": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrFlightInvoice", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VatInvoice": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrVatInvoice", "Version": "2020-08-26"},
                {},
                {},
            ),
            "QuotaInvoice": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrQuotaInvoice", "Version": "2020-08-26"},
                {},
                {},
            ),
            "HairStyle": ApiInfo(
                "POST", "/", {"Action": "HairStyle", "Version": "2020-08-26"}, {}, {}
            ),
            "FacePretty": ApiInfo(
                "POST", "/", {"Action": "FacePretty", "Version": "2020-08-26"}, {}, {}
            ),
            "ImageAnimation": ApiInfo(
                "POST",
                "/",
                {"Action": "ImageAnimation", "Version": "2020-08-26"},
                {},
                {},
            ),
            "CoverVideo": ApiInfo(
                "POST", "/", {"Action": "CoverVideo", "Version": "2020-08-26"}, {}, {}
            ),
            "DollyZoom": ApiInfo(
                "POST", "/", {"Action": "DollyZoom", "Version": "2020-08-26"}, {}, {}
            ),
            "PotraitEffect": ApiInfo(
                "POST",
                "/",
                {"Action": "PotraitEffect", "Version": "2020-08-26"},
                {},
                {},
            ),
            "ImageStyleConversion": ApiInfo(
                "POST",
                "/",
                {"Action": "ImageStyleConversion", "Version": "2020-08-26"},
                {},
                {},
            ),
            "3DGameCartoon": ApiInfo(
                "POST",
                "/",
                {"Action": "3DGameCartoon", "Version": "2020-08-26"},
                {},
                {},
            ),
            "HairSegment": ApiInfo(
                "POST", "/", {"Action": "HairSegment", "Version": "2020-08-26"}, {}, {}
            ),
            "OcrSeal": ApiInfo(
                "POST", "/", {"Action": "OcrSeal", "Version": "2021-08-23"}, {}, {}
            ),
            "OcrPassInvoice": ApiInfo(
                "POST",
                "/",
                {"Action": "OcrPassInvoice", "Version": "2021-08-23"},
                {},
                {},
            ),
            "OCRTrade": ApiInfo(
                "POST", "/", {"Action": "OCRTrade", "Version": "2020-12-21"}, {}, {}
            ),
            "OCRRuanzhu": ApiInfo(
                "POST", "/", {"Action": "OCRRuanzhu", "Version": "2020-12-21"}, {}, {}
            ),
            "OCRCosmeticProduct": ApiInfo(
                "POST",
                "/",
                {"Action": "OCRCosmeticProduct", "Version": "2020-12-21"},
                {},
                {},
            ),
            "OCRPdf": ApiInfo(
                "POST", "/", {"Action": "OCRPdf", "Version": "2021-08-23"}, {}, {}
            ),
            "OCRTable": ApiInfo(
                "POST", "/", {"Action": "OCRTable", "Version": "2021-08-23"}, {}, {}
            ),
            "VideoCoverSelection": ApiInfo(
                "POST",
                "/",
                {"Action": "VideoCoverSelection", "Version": "2020-08-26"},
                {},
                {},
            ),
            "VideoHighlightExtractionSubmitTask": ApiInfo(
                "POST",
                "/",
                {
                    "Action": "VideoHighlightExtractionSubmitTask",
                    "Version": "2020-08-26",
                },
                {},
                {},
            ),
            "VideoHighlightExtractionQueryTask": ApiInfo(
                "GET",
                "/",
                {
                    "Action": "VideoHighlightExtractionQueryTask",
                    "Version": "2020-08-26",
                },
                {},
                {},
            ),
            "CertToken": ApiInfo(
                "POST", "/", {"Action": "CertToken", "Version": "2022-08-31"}, {}, {}
            ),
            "CertVerifyQuery": ApiInfo(
                "POST",
                "/",
                {"Action": "CertVerifyQuery", "Version": "2022-08-31"},
                {},
                {},
            ),
            "T2ILDM": ApiInfo(
                "POST", "/", {"Action": "T2ILDM", "Version": "2022-08-31"}, {}, {}
            ),
            "Img2ImgStyle": ApiInfo(
                "POST", "/", {"Action": "Img2ImgStyle", "Version": "2022-08-31"}, {}, {}
            ),
            "Img2ImgAnime": ApiInfo(
                "POST", "/", {"Action": "Img2ImgAnime", "Version": "2022-08-31"}, {}, {}
            ),
        }
        return api_info

    def common_handler(self, api, form, proxy):
        params = dict()
        try:
            res = self.post(api, params, form, proxy)
            res_json = json.loads(res)
            return res_json
        except Exception as e:
            res = str(e)
            try:
                res_json = json.loads(res)
                return res_json
            except:
                raise Exception(str(e))

    def common_get_handler(self, api, params):
        try:
            res = self.get(api, params)
            res_json = json.loads(res)
            return res_json
        except Exception as e:
            res = str(e)
            try:
                res_json = json.loads(res)
                return res_json
            except:
                raise Exception(str(e))

    def common_json_handler(self, api, form):
        params = dict()
        try:
            res = self.json(api, params, json.dumps(form))
            res_json = json.loads(res)

            return res_json
        except Exception as e:
            res = str(e)
            try:
                res_json = json.loads(res)
                return res_json
            except:
                raise Exception(str(e))

    def jpcartoon_cut(self, form):
        try:
            res_json = self.common_handler("JPCartoonCut", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def jpcartoon(self, form):
        try:
            res_json = self.common_handler("JPCartoon", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def id_card(self, form):
        try:
            res_json = self.common_handler("IDCard", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def face_swap(self, form):
        try:
            res_json = self.common_handler("FaceSwap", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_normal(self, form):
        try:
            res_json = self.common_handler("OCRNormal", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def bank_card(self, form):
        try:
            res_json = self.common_handler("BankCard", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def human_segment(self, form):
        try:
            res_json = self.common_handler("HumanSegment", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def general_segment(self, form):
        try:
            res_json = self.common_handler("GeneralSegment", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def enhance_photo(self, form):
        try:
            res_json = self.common_handler("EnhancePhoto", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def convert_photo(self, form):
        try:
            res_json = self.common_handler("ConvertPhoto", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_scene_detect(self, form):
        try:
            res_json = self.common_handler("VideoSceneDetect", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def over_resolution(self, form):
        try:
            res_json = self.common_handler("OverResolution", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def goods_segment(self, form):
        try:
            res_json = self.common_handler("GoodsSegment", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_outpaint(self, form):
        try:
            res_json = self.common_handler("ImageOutpaint", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_inpaint(self, form):
        try:
            res_json = self.common_handler("ImageInpaint", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_cut(self, form):
        try:
            res_json = self.common_handler("ImageCut", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def entity_detect(self, form):
        try:
            res_json = self.common_handler("EntityDetect", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def goods_detect(self, form):
        try:
            res_json = self.common_handler("GoodsDetect", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_summarization_submit_task(self, form):
        try:
            res_json = self.common_handler("VideoSummarizationSubmitTask", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_summarization_query_task(self, params):
        try:
            res_json = self.common_get_handler("VideoSummarizationQueryTask", params)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_over_resolution_submit_task(self, form):
        try:
            res_json = self.common_handler("VideoOverResolutionSubmitTask", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_over_resolution_query_task(self, params):
        try:
            res_json = self.common_get_handler("VideoOverResolutionQueryTask", params)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_retargeting_submit_task(self, form):
        try:
            res_json = self.common_handler("VideoRetargetingSubmitTask", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_retargeting_query_task(self, params):
        try:
            res_json = self.common_get_handler("VideoRetargetingQueryTask", params)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_inpaint_submit_task(self, form):
        try:
            res_json = self.common_handler("VideoInpaintSubmitTask", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_inpaint_query_task(self, params):
        try:
            res_json = self.common_get_handler("VideoInpaintQueryTask", params)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def car_plate_detection(self, form):
        try:
            res_json = self.common_handler("CarPlateDetection", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def distortion_free(self, form):
        try:
            res_json = self.common_handler("DistortionFree", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def stretch_recovery(self, form):
        try:
            res_json = self.common_handler("StretchRecovery", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_flow(self, form):
        try:
            res_json = self.common_handler("ImageFlow", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_score(self, form):
        try:
            res_json = self.common_handler("ImageScore", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def poem_material(self, form):
        try:
            res_json = self.common_handler("PoemMaterial", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def emoticon_edit(self, form):
        try:
            res_json = self.common_handler("EmoticonEdit", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def eye_close2open(self, form):
        try:
            res_json = self.common_handler("EyeClose2Open", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def car_segment(self, form):
        try:
            res_json = self.common_handler("CarSegment", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def car_detection(self, form):
        try:
            res_json = self.common_handler("CarDetection", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def sky_segment(self, form):
        try:
            res_json = self.common_handler("SkySegment", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_search_image_add(self, form):
        try:
            res_json = self.common_handler("ImageSearchImageAdd", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_search_image_delete(self, form):
        try:
            res_json = self.common_handler("ImageSearchImageDelete", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_search_image_search(self, form):
        try:
            res_json = self.common_handler("ImageSearchImageSearch", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def product_search_add_image(self, params):
        try:
            res_json = self.json("ProductSearchAddImage", [], json.dumps(params))
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def product_search_delete_image(self, params):
        try:
            res_json = self.json("ProductSearchDeleteImage", [], json.dumps(params))
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def product_search_search_image(self, params):
        try:
            res_json = self.json("ProductSearchSearchImage", [], json.dumps(params))
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def clue_license(self, form):
        try:
            res_json = self.common_handler("ClueLicense", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def driving_license(self, form):
        try:
            res_json = self.common_handler("DrivingLicense", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def vehicle_license(self, form):
        try:
            res_json = self.common_handler("VehicleLicense", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def taxi_invoice(self, form):
        try:
            res_json = self.common_handler("TaxiInvoice", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def train_ticket(self, form):
        try:
            res_json = self.common_handler("TrainTicket", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def flight_invoice(self, form):
        try:
            res_json = self.common_handler("FlightInvoice", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def vat_invoice(self, form):
        try:
            res_json = self.common_handler("VatInvoice", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def quota_invoice(self, form):
        try:
            res_json = self.common_handler("QuotaInvoice", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def hair_style(self, form):
        try:
            res_json = self.common_handler("HairStyle", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def face_pretty(self, form):
        try:
            res_json = self.common_handler("FacePretty", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_animation(self, form):
        try:
            res_json = self.common_handler("ImageAnimation", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def cover_video(self, form):
        try:
            res_json = self.common_handler("CoverVideo", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def dolly_zoom(self, form):
        try:
            res_json = self.common_handler("DollyZoom", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def potrait_effect(self, form):
        try:
            res_json = self.common_handler("PotraitEffect", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def image_style_conversion(self, form):
        try:
            res_json = self.common_handler("ImageStyleConversion", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def three_d_game_cartoon(self, form):
        try:
            res_json = self.common_handler("3DGameCartoon", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def hair_segment(self, form):
        try:
            res_json = self.common_handler("HairSegment", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_seal(self, form):
        try:
            res_json = self.common_handler("OcrSeal", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_pass_invoice(self, form):
        try:
            res_json = self.common_handler("OcrPassInvoice", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_trade(self, form):
        try:
            res_json = self.common_handler("OCRTrade", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_ruanzhu(self, form):
        try:
            res_json = self.common_handler("OCRRuanzhu", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_cosmetic_product(self, form):
        try:
            res_json = self.common_handler("OCRCosmeticProduct", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_pdf(self, form):
        try:
            res_json = self.common_handler("OCRPdf", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_table(self, form):
        try:
            res_json = self.common_handler("OCRTable", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_cover_selection(self, form):
        try:
            res_json = self.common_handler("VideoCoverSelection", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_highlight_extraction_submit_task(self, form):
        try:
            res_json = self.common_handler("VideoHighlightExtractionSubmitTask", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def video_highlight_extraction_query_task(self, params):
        try:
            res_json = self.common_get_handler(
                "VideoHighlightExtractionQueryTask", params
            )
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def cert_token(self, form):
        try:
            res_json = self.common_json_handler("CertToken", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def cert_verify_query(self, form):
        try:
            res_json = self.common_json_handler("CertVerifyQuery", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def t2i_ldm(self, form):
        try:
            res_json = self.common_json_handler("T2ILDM", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def img2img_style(self, form):
        try:
            res_json = self.common_json_handler("Img2ImgStyle", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def img2img_anime(self, form):
        try:
            res_json = self.common_json_handler("Img2ImgAnime", form)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def ocr_api(self, action, form, proxy):
        try:
            res_json = self.common_handler(action, form, proxy)
            return res_json
        except Exception as e:
            raise Exception(str(e))

    def set_api_info(self, action, version):
        self.api_info[action] = ApiInfo(
            "POST", "/", {"Action": action, "Version": version}, {}, {}
        )


import requests
import base64
from ocrengines.baseocrclass import baseocr


class OCR(baseocr):

    def ocr(self, imgfile):
        visual_service = VisualService()
        self.checkempty(["Access Key ID", "Secret Access Key"])
        # call below method if you dont set ak and sk in $HOME/.volc/config
        visual_service.set_ak(self.config["Access Key ID"])
        visual_service.set_sk(self.config["Secret Access Key"])

        visual_service.set_api_info("MultiLanguageOCR", "2022-08-31")

        # below shows the sdk usage for all common apis,
        # if you cannot find the needed one, please check other example files in the same dir
        # or contact us for further help
        form = dict()
        import base64

        with open(imgfile, "rb") as ff:
            f = ff.read()
        b64 = base64.b64encode(f)
        form["image_base64"] = b64
        resp = visual_service.ocr_api("MultiLanguageOCR", form, self.proxy)
        try:
            texts = [box["text"] for box in resp["data"]["ocr_infos"]]
            boxs = self.flatten4point(
                [box["rect"] for box in resp["data"]["ocr_infos"]]
            )
            return self.common_solve_text_orientation(boxs, texts)
        except:
            raise Exception(resp)
