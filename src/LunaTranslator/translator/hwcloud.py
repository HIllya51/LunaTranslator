from translator.basetranslator import basetrans
import hashlib, hmac, json
from datetime import datetime
from urllib.parse import quote, unquote


text_type = str
binary_type = bytes


def ensure_binary(s, encoding="utf-8", errors="strict"):
    """Coerce **s** to six.binary_type.

    For Python 2:
    - `unicode` -> encoded to `str`
    - `str` -> `str`

    For Python 3:
    - `str` -> encoded to `bytes`
    - `bytes` -> `bytes`
    """
    if isinstance(s, binary_type):
        return s
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    raise TypeError("not expecting type '%s'" % type(s))


class Req:
    def __init__(self) -> None:
        self.header_params = {}
        self.query_params = {}
        self.method = ""
        self.body = b""
        self.resource_path = ""
        self.host = ""


class Signer(object):
    _ENCODE_UTF8 = "utf-8"
    _ENCODE_ISO_8859_1 = "iso-8859-1"
    _BASIC_DATE_FORMAT = "%Y%m%dT%H%M%SZ"
    _ALGORITHM = "SDK-HMAC-SHA256"
    _HEADER_X_DATE = "X-Sdk-Date"
    _HEADER_HOST = "Host"
    _HEADER_AUTHORIZATION = "Authorization"
    _HEADER_CONTENT = "X-Sdk-Content-Sha256"
    _EMPTY_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def __init__(self, credentials):
        self._ak, self._sk = credentials
        self._hash_func = hashlib.sha256

    def _verify_required(self):
        if not self._ak:
            raise ValueError("ak is required in credentials")
        if not self._sk:
            raise ValueError("sk is required in credentials")

    def sign(self, request: Req):
        self._verify_required()
        if isinstance(request.body, text_type):
            request.body = ensure_binary(request.body)

        self._process_content_header(request)
        t = self._process_header_time(request)
        self._process_header_host(request)

        signed_headers = self._process_signed_headers(request)
        canonical_request = self._process_canonical_request(request, signed_headers)
        string_to_sign = self._process_string_to_sign(canonical_request, t)
        signature = self._sign_string_to_sign(string_to_sign, self._sk)
        auth_value = self._process_auth_header_value(
            signature, self._ak, signed_headers
        )
        request.header_params[self._HEADER_AUTHORIZATION] = auth_value

        self.process_request_uri(request)

        return request

    @classmethod
    def _process_content_header(cls, request: Req):
        content_type = request.header_params.get("Content-Type")
        if content_type and not content_type.startswith("application/json"):
            request.header_params[cls._HEADER_CONTENT] = "UNSIGNED-PAYLOAD"

    @classmethod
    def process_request_uri(cls, request: Req):
        canonical_query_string = cls._process_canonical_query_string(request)
        request.uri = (
            "%s?%s" % (request.resource_path, canonical_query_string)
            if canonical_query_string != ""
            else request.resource_path
        )

    @classmethod
    def _process_header_time(cls, request: Req):
        header_time = cls._get_header_ignore_case(request, cls._HEADER_X_DATE)
        if header_time is None:
            t = datetime.utcnow()
            request.header_params[cls._HEADER_X_DATE] = datetime.strftime(
                t, cls._BASIC_DATE_FORMAT
            )
        else:
            t = datetime.strptime(header_time, cls._BASIC_DATE_FORMAT)
        return t

    @classmethod
    def _process_header_host(cls, request: Req):
        has_host_header = False
        for key in request.header_params:
            if key.lower() == "host":
                has_host_header = True
                break
        if not has_host_header:
            request.header_params["Host"] = request.host

    def _hash_hex_string(self, data):
        # type: (bytes) -> str
        _hash = self._hash_func(data)
        return _hash.hexdigest()

    def _hmac(self, key, data):
        # type: (bytes, bytes) -> bytes
        return hmac.new(key, data, digestmod=self._hash_func).digest()

    def _process_string_to_sign(self, canonical_request, time):
        # type: (str, datetime) -> str
        return "%s\n%s\n%s" % (
            self._ALGORITHM,
            datetime.strftime(time, self._BASIC_DATE_FORMAT),
            self._hash_hex_string(ensure_binary(canonical_request)),
        )

    @classmethod
    def _url_encode(cls, s):
        # type: (str) -> str
        return quote(s, safe="~")

    @classmethod
    def _get_header_ignore_case(cls, r: Req, header):
        for k in r.header_params:
            if k.lower() == header.lower():
                return r.header_params[k]
        return None

    def _process_canonical_request(self, request: Req, signed_headers):
        canonical_headers = self._process_canonical_headers(request, signed_headers)

        hex_encode = self._process_hash_payload(request)
        canonical_uri = self._process_canonical_uri(request)
        canonical_query_string = self._process_canonical_query_string(request)

        return "%s\n%s\n%s\n%s\n%s\n%s" % (
            request.method.upper(),
            canonical_uri,
            canonical_query_string,
            canonical_headers,
            ";".join(signed_headers),
            hex_encode,
        )

    def _process_hash_payload(self, request: Req):
        if not request.body:
            return self._EMPTY_HASH

        hex_encode = self._get_header_ignore_case(request, self._HEADER_CONTENT)
        if hex_encode:
            return hex_encode

        return self._hash_hex_string(request.body)

    def _process_canonical_uri(self, request: Req):
        pattens = unquote(request.resource_path).split("/")
        uri = []
        for v in pattens:
            uri.append(self._url_encode(v))
        url_path = "/".join(uri)

        if url_path[-1] != "/":
            url_path = url_path + "/"

        return url_path

    @classmethod
    def process_canonical_query_string(cls, request):
        return cls._process_canonical_query_string(request)

    @classmethod
    def _process_canonical_query_string(cls, request: Req):
        params = []
        for param in request.query_params:
            params.append(param)
        params.sort()

        canonical_query_param = []
        for key, value in params:
            k = cls._url_encode(key)
            if isinstance(value, list):
                value.sort()
                for v in value:
                    kv = "%s=%s" % (k, cls._url_encode(str(v)))
                    canonical_query_param.append(kv)
            elif isinstance(value, bool):
                kv = "%s=%s" % (k, cls._url_encode(str(value).lower()))
                canonical_query_param.append(kv)
            else:
                kv = "%s=%s" % (k, cls._url_encode(str(value)))
                canonical_query_param.append(kv)

        return "&".join(canonical_query_param)

    def _process_canonical_headers(self, request: Req, signed_headers):
        canonical_headers = []
        __headers = {}
        for key in request.header_params:
            key_encoded = key.lower()
            value = request.header_params[key]
            value_encoded = str(value).strip()
            __headers[key_encoded] = value_encoded
            if 1:
                request.header_params[key] = value_encoded.encode(
                    self._ENCODE_UTF8
                ).decode("iso-8859-1")

        for key in signed_headers:
            canonical_headers.append(key + ":" + __headers.get(key))

        return "\n".join(canonical_headers) + "\n"

    @classmethod
    def _process_signed_headers(cls, request: Req):
        signed_headers = []
        for key in request.header_params:
            if "_" in key:
                continue
            signed_headers.append(key.lower())
        signed_headers.sort()
        return signed_headers

    def _sign_string_to_sign(self, string_to_sign, key):
        # type: (str, str) -> str
        return self._hex(self._hmac(ensure_binary(key), ensure_binary(string_to_sign)))

    def _process_auth_header_value(self, signature, app_key, signed_headers):
        # type: (str, str, list) -> str
        return "%s Access=%s, SignedHeaders=%s, Signature=%s" % (
            self._ALGORITHM,
            app_key,
            ";".join(signed_headers),
            signature,
        )

    def _hex(self, data):
        return "".join(format(c, "02x") for c in ensure_binary(data))


class TS(basetrans):
    def init(self):
        self.cacheproject = {}

    def translate(self, query):
        self.checkempty(["ak", "endpoint", "sk"])

        ak, sk = self.multiapikeycurrent["ak"], self.multiapikeycurrent["sk"]

        endpoint = self.multiapikeycurrent["endpoint"].strip()
        ends = {"cn-north-4": "nlp-ext.cn-north-4.myhuaweicloud.com"}
        end = ends.get(endpoint, ends["cn-north-4"])
        if (end, ak, sk) not in self.cacheproject:
            params = {
                "name": "cn-north-4",
            }
            r = Req()
            r.query_params = params.items()
            r.host = "iam.myhuaweicloud.com"
            r.resource_path = "/v3/projects"
            r.method = "GET"
            r = Signer((ak, sk)).sign(r)
            response = self.proxysession.get(
                "https://iam.myhuaweicloud.com/v3/projects",
                params=params,
                headers=r.header_params,
            )
            try:
                project_id = response.json()["projects"][0]["id"]
            except:
                raise Exception(response)
            self.cacheproject[(end, ak, sk)] = project_id
        project_id = self.cacheproject.get((end, ak, sk))
        url = "https://{}/v1/{}/machine-translation/text-translation".format(
            end, project_id
        )
        body = {
            "text": query,
            "from": self.srclang,
            "to": self.tgtlang,
            "scene": "common",
        }
        body = json.dumps(body).encode("utf8")
        r = Req()
        r.header_params = {
            "Content-Type": "application/json",
            "X-Project-Id": project_id,
            "User-Agent": "huaweicloud-usdk-python/3.0",
        }
        r.host = end
        r.resource_path = "/v1/{}/machine-translation/text-translation".format(
            project_id
        )
        r.method = "POST"
        r.body = body
        r = Signer((ak, sk)).sign(r)

        request = self.proxysession.post(url, headers=r.header_params, data=body)
        response = request.json()
        try:
            return response["translated_text"]
        except:
            raise Exception(response)
