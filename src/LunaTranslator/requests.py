import json, base64, re, string, random, threading, codecs
from collections.abc import Mapping, MutableMapping
from collections import OrderedDict
from urllib.parse import urlencode, urlsplit
from functools import partial
from myutils.config import globalconfig

default_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

default_timeout = 10


class RequestException(Exception):
    pass


class Timeout(RequestException):
    pass


class HTTPError(RequestException):
    pass


class CaseInsensitiveDict(MutableMapping):

    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


class ResponseBase:
    def __init__(self, stream):
        self.headers = CaseInsensitiveDict()
        self.stream = stream
        self.url = ""
        self.cookies = {}
        self.status_code = 0
        self.status_text = ""
        self.__content = b""
        self.__content_s = []
        self.content_prepared = threading.Event()
        self.iter_once = True

    @property
    def content(self):
        if self.stream:
            if self.iter_once:
                for _ in self.iter_content():
                    pass
            self.content_prepared.wait()
            return b"".join(self.__content_s)
        else:
            return self.__content

    @content.setter
    def content(self, c):
        if self.stream:
            raise RequestException()
        self.__content = c

    @property
    def text(self):
        try:
            return self.content.decode(self.charset)
        except:
            raise Exception("unenable to decode with {}".format(self.charset))

    @property
    def charset(self):
        content_type = self.headers.get("Content-Type", "")
        m = re.search(r"charset=([\w-]+)", content_type)
        charset = m.group(1) if m else "utf-8"
        return charset

    @property
    def maybejson(self):
        try:
            return self.json()
        except:
            return self.text

    def json(self):
        return json.loads(self.text)

    def stream_decode_response_unicode(self, iterator):

        decoder = codecs.getincrementaldecoder(self.charset)(errors="replace")
        for chunk in iterator:
            rv = decoder.decode(chunk)
            if rv:
                yield rv
        rv = decoder.decode(b"", final=True)
        if rv:
            yield rv

    def iter_content(self, chunk_size=1, decode_unicode=False):
        if not self.stream:
            raise RequestException()

        if not self.iter_once:
            raise RequestException()
        self.iter_once = False

        def __generate():
            for chunk in self.iter_content_impl(chunk_size):
                self.__content_s.append(chunk)
                yield chunk
            self.content_prepared.set()

        stream_chunks = __generate()

        chunks = stream_chunks

        if decode_unicode:
            chunks = self.stream_decode_response_unicode(chunks)

        return chunks

    def iter_content_impl(self, chunk_size=1):
        pass

    def iter_lines(self, chunk_size=512, decode_unicode=False, delimiter=None):
        pending = None
        size = 0
        for chunk in self.iter_content(
            chunk_size=chunk_size, decode_unicode=decode_unicode
        ):
            size += len(chunk)
            if pending is not None:
                chunk = pending + chunk

            if delimiter:
                lines = chunk.split(delimiter)
            else:
                lines = chunk.splitlines()

            if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            else:
                pending = None

            yield from lines

        if pending is not None:
            yield pending

    def raise_for_status(self):
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error: {self.status_text} for url: {self.url}"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error: {self.status_text} for url: {self.url}"

        if http_error_msg:
            raise HTTPError(http_error_msg)


class Requester_common:
    Accept_Encoding = "gzip, deflate, br"
    default_UA = default_UA

    @staticmethod
    def _encode_params(data):
        if isinstance(data, (str, bytes)):
            return data
        elif hasattr(data, "read"):
            return data
        elif hasattr(data, "__iter__"):
            result = []
            for k, vs in list(data.items()):
                if isinstance(vs, (str, bytes)) or not hasattr(vs, "__iter__"):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (
                                k.encode("utf-8") if isinstance(k, str) else k,
                                v.encode("utf-8") if isinstance(v, str) else v,
                            )
                        )
            return urlencode(result, doseq=True)
        else:
            return data

    def _parseurl(self, url: str, param):
        url = url.strip()
        scheme, server, path, query, _ = urlsplit(url)
        if scheme not in ["https", "http"]:
            raise Exception("unknown scheme " + scheme)
        spl = server.split(":")
        if len(spl) == 2:
            server = spl[0]
            port = int(spl[1])
        elif len(spl) == 1:
            spl[0]
            if scheme == "https":
                port = 443
            else:
                port = 80
        else:
            raise Exception("invalid url")
        if param:
            param = self._encode_params(param)
            query += ("&" if len(query) else "") + param
        if len(query):
            path += "?" + query
        url = scheme + "://" + server + path
        return scheme, server, port, path, url

    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        proxies=None,
        json=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=default_timeout,
        allow_redirects=True,
        hooks=None,
        stream=None,
        verify=False,
        cert=None,
    ) -> ResponseBase:

        if auth and isinstance(auth, tuple) and len(auth) == 2:
            headers["Authorization"] = (
                "Basic "
                + (
                    base64.b64encode(
                        b":".join((auth[0].encode("latin1"), auth[1].encode("latin1")))
                    ).strip()
                ).decode()
            )

        scheme, server, port, param, url = self._parseurl(url, params)
        databytes = b""
        contenttype = None
        if files:
            contenttype, databytes = self._parsefilesasmultipart(files, headers)
        elif data:
            contenttype, databytes = self._parsedata(data)
        elif json:
            contenttype, databytes = self._parsejson(json)
        if len(databytes):
            headers["Content-Length"] = str(len(databytes))
        if contenttype and ("Content-Type" not in headers):
            headers["Content-Type"] = contenttype
        proxy = proxies.get(scheme, None) if proxies else None
        proxy = None if proxy == "" else proxy
        if timeout:
            if isinstance(timeout, (float, int)):
                timeout = int(timeout * 1000)  # convert to milliseconds
            else:
                try:
                    timeout = max(int(_ * 1000) for _ in timeout)
                except:
                    print("Error invalid timeout", timeout)
                    timeout = None
        return self.request_impl(
            method,
            scheme,
            server,
            port,
            param,
            url,
            headers,
            cookies,
            databytes,
            proxy,
            stream,
            verify,
            timeout,
            allow_redirects,
        )

    def request_impl(self, *argc) -> ResponseBase: ...

    def _parseheader(self, headers: CaseInsensitiveDict, cookies: dict):
        _x = []

        if cookies:
            cookie = self._parsecookie(cookies)
            headers.update({"Cookie": cookie})
        for k in sorted(headers.keys()):
            _x.append("{}: {}".format(k, headers[k]))
        return _x

    def _parsecookie(self, cookie: dict):
        _c = []
        for k, v in cookie.items():
            _c.append("{}={}".format(k, v))
        return "; ".join(_c)

    def _parsecookiestring(self, cookiestr: str):
        if not cookiestr:
            return {}
        cookies = cookiestr.split("; ")
        cookie = {}
        for _c in cookies:
            _idx = _c.find("=")
            cookie[_c[:_idx]] = _c[_idx + 1 :]
        return cookie

    def _parseheader2dict(self, headerstr: str):
        header = CaseInsensitiveDict()
        cookie = {}
        lines = headerstr.split("\r\n")
        status_text = " ".join(lines[0].split(" ")[2:])
        for line in lines[1:]:
            idx = line.find(": ")
            if idx == -1:
                continue
            if line[:idx].lower() == "set-cookie":
                cookie.update(self._parsecookiestring(line[idx + 2 :]))
            else:
                header[line[:idx]] = line[idx + 2 :]
        return CaseInsensitiveDict(header), cookie, status_text

    def _parsejson(self, _json):
        databytes = json.dumps(_json).encode("utf8")
        contenttype = "application/json"
        return contenttype, databytes

    def _parsedata(self, data):
        contenttype = None
        databytes = self._encode_params(data)
        if isinstance(databytes, str):
            databytes = (databytes).encode("utf8")
        if isinstance(data, (str, bytes)):
            pass
        else:
            contenttype = "application/x-www-form-urlencoded"
        return contenttype, databytes

    def _parsefilesasmultipart(self, files: dict, header: dict):
        def generate_random_string(length=16):
            characters = string.ascii_letters + string.digits
            return "".join(random.choices(characters, k=length))

        _ct = header.get("Content-Type", None)
        _ct_start = "multipart/form-data; boundary="
        if _ct and _ct.lower().startswith(_ct_start):
            boundary = _ct[len(_ct_start) :]
        else:
            boundary = "----WebKitFormBoundary" + generate_random_string()
            _ct = _ct_start + boundary
        boundary = boundary.encode()
        items = []
        for name, data in files.items():
            items.append(b"--" + boundary)
            disposition = b'Content-Disposition: form-data; name="'
            disposition += name.encode("utf8")
            disposition += b'"'
            if isinstance(data, (tuple, list)):
                if len(data) == 3:
                    filename, data, type_ = data
                elif len(data) == 2:
                    filename, data = data
                    type_ = None
            else:
                filename = None
                type_ = None
            if filename:
                disposition += b'; filename="'
                disposition += filename.encode("utf8")
                disposition += b'"'
            items.append(disposition)
            if type_:
                Type = b"Content-Type: "
                Type += type_.encode("utf8")
                items.append(Type)
            items.append(b"")
            if isinstance(data, str):
                data = data.encode("utf8")
            items.append(data)
        items.append(b"--" + boundary + b"--")
        return _ct, b"".join(_ + b"\r\n" for _ in items)


class Session:
    def __init__(self):

        self.cookies = {}
        self._requester = None
        self._libidx = -1

        self.headers = CaseInsensitiveDict(
            {
                # "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @property
    def requester(self) -> Requester_common:
        if self._libidx == globalconfig["network"]:
            return self._requester
        if globalconfig["network"] == 1:
            from network.libcurl.requester import Requester
        elif globalconfig["network"] == 0:
            from network.winhttp.requester import Requester
        self._requester = Requester()
        self._libidx = globalconfig["network"]

        self.headers.update({"Accept-Encoding": self.requester.Accept_Encoding})
        self.headers.update({"User-Agent": self.requester.default_UA})
        return self._requester

    def request(
        self,
        method: str,
        url: str,
        params=None,
        data=None,
        headers=None,
        proxies=None,
        json=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=default_timeout,
        allow_redirects=True,
        hooks=None,
        stream=None,
        verify=False,
        cert=None,
    ):
        requester = self.requester

        _h = self.headers.copy()
        if headers:
            _h.update(headers)
            self.cookies.update(requester._parsecookiestring(_h.get("cookie", "")))
        if cookies:
            self.cookies.update(cookies)
        response = requester.request(
            method.upper(),
            url,
            params=params,
            data=data,
            headers=_h,
            proxies=proxies,
            json=json,
            cookies=self.cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
        )
        self.cookies.update(response.cookies)
        response.cookies.update(self.cookies)
        return response

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def options(self, url, **kwargs):
        return self.request("OPTIONS", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def head(self, url, **kwargs):
        return self.request("HEAD", url, **kwargs)


def request(method, url, **kwargs):
    with Session() as session:
        return session.request(method=method, url=url, **kwargs)


def session():
    with Session() as session:
        return session


get = partial(request, "GET")
post = partial(request, "POST")
options = partial(request, "OPTIONS")
patch = partial(request, "PATCH")
delete = partial(request, "DELETE")
head = partial(request, "HEAD")
