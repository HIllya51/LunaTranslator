from ctypes import c_size_t, pointer, create_string_buffer, POINTER
from .libcurl import *
from urllib.parse import urlsplit
import time


class WebSocket:
    def send(self, data):
        if isinstance(data, str):
            _t = CURLWS_TEXT
            data = data.encode("utf8")
        else:
            _t = CURLWS_BINARY
        sent = c_size_t()
        error = curl_ws_send(self.curl, data, len(data), pointer(sent), 0, _t)
        MaybeRaiseException(error)

    def recv(self):
        time.sleep(0.01)
        rlen = c_size_t()
        meta = POINTER(curl_ws_frame)()
        buffer = create_string_buffer(10240)
        while 1:
            error = curl_ws_recv(
                self.curl, buffer, (10240), pointer(rlen), pointer(meta)
            )
            if error == CURLException.AGAIN:
                time.sleep(0.01)
            elif error:
                MaybeRaiseException(error)
            else:
                break
        if meta.contents.flags & CURLWS_TEXT:
            ret = buffer[: rlen.value].decode("utf8")
        elif meta.contents.flags & CURLWS_BINARY:
            ret = buffer[: rlen.value]
        else:
            # unknown
            ret = buffer[: rlen.value]
        return ret

    def close(self):
        if self.curl:
            sent = c_size_t()
            curl_ws_send(self.curl, "", 0, pointer(sent), 0, CURLWS_CLOSE)
            self.curl = 0

    def __del__(self):
        self.close()

    def __init__(self) -> None:
        self.curl = 0

    def _setproxy(self, curl, http_proxy_host, http_proxy_port):
        if http_proxy_host is None or http_proxy_port is None:
            return
        proxy = "{}:{}".format(http_proxy_host, http_proxy_port)
        curl_easy_setopt(curl, CURLoption.PROXY, proxy.encode("utf8"))

    def _parseurl2serverandpath(self, url: str):
        url = url.strip()
        scheme, server, path, query, _ = urlsplit(url)
        if scheme == "wss":
            ishttps = True
        elif scheme == "ws":
            ishttps = False
        else:
            raise requests.exceptions.RequestException("unknown scheme {} for invalid url {}".format(scheme, url))
        spl = server.split(":")
        if len(spl) == 2:
            server = spl[0]
            port = int(spl[1])
        elif len(spl) == 1:
            spl[0]
            if ishttps:
                port = 443
            else:
                port = 80
        else:
            raise requests.exceptions.RequestException("invalid url " + url)
        if len(query):
            path += "?" + query
        return ishttps, server, port, path

    def _set_verify(self, curl, verify):
        if verify == False:
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYPEER, 0)
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYHOST, 0)
        else:
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYPEER, 1)
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYHOST, 2)

    def connect(
        self, url: str, header=None, http_proxy_host=None, http_proxy_port=None
    ):
        https, server, port, path = self._parseurl2serverandpath(url)
        if server == "127.0.0.1":
            # libcurl在本地地址走代理时有时会谜之502
            http_proxy_host = http_proxy_port = None
        self.curl = curl_easy_init()
        curl_easy_setopt(self.curl, CURLoption.CONNECT_ONLY, 2)
        curl_easy_setopt(self.curl, CURLoption.URL, url.encode("utf8"))
        curl_easy_setopt(self.curl, CURLoption.PORT, port)
        self._setproxy(self.curl, http_proxy_host, http_proxy_port)
        self._set_verify(self.curl, False)

        lheaders = auto_curl_slist()
        if header:
            for _ in header:
                lheaders.append(_)
        curl_easy_setopt(self.curl, CURLoption.HTTPHEADER, lheaders.ptr)

        curl_easy_perform(self.curl)
