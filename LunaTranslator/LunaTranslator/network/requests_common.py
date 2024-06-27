import json, base64, re
from collections.abc import Mapping, MutableMapping
from collections import OrderedDict
from urllib.parse import urlencode, urlsplit
from functools import partial


class NetWorkException(Exception):
    pass


class Timeout(NetWorkException):
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
    def __init__(self):
        self.headers = CaseInsensitiveDict()
        self.cookies = {}
        self.status_code = 0
        self.content = b"{}"

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

    def json(self):
        return json.loads(self.text)

    def iter_content(self, chunk_size=1, decode_unicode=False):
        for chunk in self.iter_content_impl(chunk_size):
            if decode_unicode:
                yield chunk.decode("utf8")
            else:
                yield chunk

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


class Sessionbase:
    def __init__(self) -> None:
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.last_error = 0
        self.cookies = {}
        self.headers = CaseInsensitiveDict(
            {
                "User-Agent": self.UA,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

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

    def _parsedata(self, data, headers, js):

        if data is None and js is None:
            dataptr = None
            datalen = 0
        else:
            if data:
                dataptr = self._encode_params(data)

                if isinstance(dataptr, str):
                    dataptr = (dataptr).encode("utf8")
                datalen = len(dataptr)
                # print('dataptr',dataptr)
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
            elif js:
                dataptr = json.dumps(js).encode("utf8")
                datalen = len(dataptr)
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
        if datalen:
            headers["Content-Length"] = str(datalen)
        # print(headers,dataptr,datalen)
        return headers, dataptr, datalen

    def _parseurl(self, url, param):
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

    def _parseheader(self, headers, cookies):
        _x = []

        if cookies:
            cookie = self._parsecookie(cookies)
            headers.update({"Cookie": cookie})
        for k in sorted(headers.keys()):
            _x.append("{}: {}".format(k, headers[k]))
        return _x

    def _parsecookie(self, cookie):
        _c = []
        for k, v in cookie.items():
            _c.append("{}={}".format(k, v))
        return "; ".join(_c)

    def _update_header_cookie(self, headerstr):
        headers, cookies = self._parseheader2dict(headerstr)
        self.cookies.update(cookies)
        return headers

    def _parseheader2dict(self, headerstr):
        # print(headerstr)
        header = CaseInsensitiveDict()
        cookie = {}
        for line in headerstr.split("\r\n")[1:]:
            idx = line.find(": ")
            if line[:idx].lower() == "set-cookie":
                _c = line[idx + 2 :].split("; ")[0]
                _idx = _c.find("=")
                cookie[_c[:_idx]] = _c[_idx + 1 :]
            else:
                header[line[:idx]] = line[idx + 2 :]
        return CaseInsensitiveDict(header), cookie

    def request_impl(self, *args):
        pass

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
        timeout=None,
        allow_redirects=True,
        hooks=None,
        stream=None,
        verify=False,
        cert=None,
    ):
        _h = self.headers.copy()
        if headers:
            _h.update(headers)
        headers = _h

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
        headers, dataptr, datalen = self._parsedata(data, headers, json)
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
        _ = self.request_impl(
            method,
            scheme,
            server,
            port,
            param,
            url,
            headers,
            cookies,
            dataptr,
            datalen,
            proxy,
            stream,
            verify,
            timeout,
        )

        if allow_redirects and (
            _.status_code == 301 or _.status_code == 302 or _.status_code == 307
        ):
            location = _.headers["Location"]
            if location.startswith("/"):  # vndb
                url = url = scheme + "://" + server + location
                param = location
            elif location.startswith(
                "http"
            ):  # https://api.github.com/repos/XXX/XXX/zipball
                scheme, server, port, param, url = self._parseurl(location, None)
            else:
                raise Exception("redirect {}: {}".format(_.status_code, location))
            _ = self.request_impl(
                method,
                scheme,
                server,
                port,
                param,
                url,
                headers,
                cookies,
                dataptr,
                datalen,
                proxy,
                stream,
                verify,
                timeout,
            )

        return _

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


Sessionimpl = [Sessionbase]


def request(method, url, **kwargs):
    with Sessionimpl[0]() as session:
        return session.request(method=method, url=url, **kwargs)


def session():
    with Sessionimpl[0]() as session:
        return session


get = partial(request, "GET")
post = partial(request, "POST")
options = partial(request, "OPTIONS")
patch = partial(request, "PATCH")
delete = partial(request, "DELETE")
