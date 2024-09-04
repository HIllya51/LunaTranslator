from .libcurl import *
import threading, functools, queue
from ctypes import c_long, cast, pointer, POINTER, c_char
from requests import ResponseBase, Timeout, Requester_common
from traceback import print_exc


class Response(ResponseBase):
    def __init__(self, stream=False):
        super().__init__(stream)
        self.keeprefs = []
        self.queue = queue.Queue()

    def iter_content_impl(self, chunk_size=1):

        downloadeddata = b""
        canend = False
        allbs = 0
        while not (self.queue.empty() and canend):
            buff = self.queue.get()
            if buff is None:
                canend = True
                continue
            allbs += len(buff)
            if chunk_size:
                downloadeddata += buff
                while len(downloadeddata) > chunk_size:
                    yield downloadeddata[:chunk_size]
                    downloadeddata = downloadeddata[chunk_size:]
            else:
                yield buff
        while len(downloadeddata):
            yield downloadeddata[:chunk_size]
            downloadeddata = downloadeddata[chunk_size:]


class autostatus:
    def __init__(self, ref) -> None:
        self.ref = ref
        ref.occupied = True

    def __del__(self):
        self.ref.occupied = False


class Requester(Requester_common):

    Accept_Encoding = "gzip, deflate, br, zstd"

    def __init__(self) -> None:
        # 用tls不太行，因为为了防止阻塞，每次请求都是完全重新开的线程，会100%重新initcurl
        self.occupied = 0
        self.curl = self.initcurl()

    def initcurl(self):
        curl = AutoCURLHandle(curl_easy_init())
        curl_easy_setopt(curl, CURLoption.USERAGENT, self.default_UA.encode("utf8"))
        return curl

    def _getStatusCode(self, curl):
        status_code = c_long()
        MaybeRaiseException(
            curl_easy_getinfo(curl, CURLINFO.RESPONSE_CODE, pointer(status_code))
        )
        return status_code.value

    def _set_proxy(self, curl, proxy):
        if proxy:
            MaybeRaiseException(
                curl_easy_setopt(curl, CURLoption.PROXY, proxy.encode("utf8"))
            )

    def _set_verify(self, curl, verify):
        if verify == False:
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYPEER, 0)
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYHOST, 0)
        else:
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYPEER, 1)
            curl_easy_setopt(curl, CURLoption.SSL_VERIFYHOST, 2)

    def _perform(self, curl):
        MaybeRaiseException(curl_easy_perform(curl))

    def _set_allow_redirects(self, curl, allow_redirects):

        curl_easy_setopt(curl, CURLoption.FOLLOWLOCATION, int(allow_redirects))
        # curl_easy_setopt(curl, CURLoption.MAXREDIRS, 100) #默认50够了

    def __WriteMemoryCallback(self, headerqueue, que, contents, size, nmemb, userp):
        if headerqueue:
            headerqueue.put(0)
        realsize = size * nmemb
        bs = cast(contents, POINTER(c_char))[:realsize]
        if isinstance(que, queue.Queue):
            que.put(bs)
        elif isinstance(que, list):
            que.append(bs)
        return realsize

    def _filter_header(self, headertext):
        header = []
        for line in headertext.split("\n"):
            if line.startswith("HTTP/"):
                header = []
            header.append(line)
        return "\n".join(header)

    def __getrealheader(self, headerqueue):
        if isinstance(headerqueue, queue.Queue):
            header = []
            while True:
                _headerb = headerqueue.get()
                if _headerb == 0:
                    break
                elif isinstance(_headerb, Exception):
                    raise _headerb
                header.append(_headerb)

        elif isinstance(headerqueue, list):
            header = headerqueue
        return self._filter_header(b"".join(header).decode("utf8"))

    def _setheaders(self, curl, headers, cookies):
        lheaders = Autoslist()
        for _ in self._parseheader(headers, None):
            lheaders = curl_slist_append(
                cast(lheaders, POINTER(curl_slist)), _.encode("utf8")
            )
        MaybeRaiseException(curl_easy_setopt(curl, CURLoption.HTTPHEADER, lheaders))

        if cookies:
            cookie = self._parsecookie(cookies)
            curl_easy_setopt(curl, CURLoption.COOKIE, cookie.encode("utf8"))

    def request_impl(
        self,
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
    ):
        if self.occupied == False:
            curl = self.curl
            __ = autostatus(self)
        else:
            curl = AutoCURLHandle(curl_easy_duphandle(self.curl))
            __ = 0

        curl_easy_reset(curl)
        curl_easy_setopt(curl, CURLoption.COOKIEJAR, "")
        if timeout:
            curl_easy_setopt(curl, CURLoption.TIMEOUT_MS, timeout)
            curl_easy_setopt(curl, CURLoption.CONNECTTIMEOUT_MS, timeout)
        curl_easy_setopt(
            curl,
            CURLoption.ACCEPT_ENCODING,
            headers["Accept-Encoding"].encode("utf8"),
        )

        if method == "HEAD":
            curl_easy_setopt(curl, CURLoption.NOBODY, 1)
        curl_easy_setopt(curl, CURLoption.CUSTOMREQUEST, method.encode("utf8"))
        MaybeRaiseException(curl_easy_setopt(curl, CURLoption.URL, url.encode("utf8")))
        curl_easy_setopt(curl, CURLoption.PORT, port)

        self._setheaders(curl, headers, cookies)

        self._set_verify(curl, verify)
        self._set_proxy(curl, proxy)
        self._set_allow_redirects(curl, allow_redirects)
        if len(databytes):
            curl_easy_setopt(curl, CURLoption.POSTFIELDS, databytes)
            curl_easy_setopt(curl, CURLoption.POSTFIELDSIZE, len(databytes))

        resp = Response(stream)
        resp.keeprefs.append(curl)
        resp.keeprefs.append(__)
        if stream:
            headerqueue = queue.Queue()
            _notif = headerqueue
        else:
            headerqueue = []
            _notif = None
            resp.queue = []
        keepref1 = WRITEFUNCTION(
            functools.partial(self.__WriteMemoryCallback, _notif, resp.queue)
        )
        keepref2 = WRITEFUNCTION(
            functools.partial(self.__WriteMemoryCallback, None, headerqueue)
        )
        curl_easy_setopt(
            curl,
            CURLoption.WRITEFUNCTION,
            cast(keepref1, c_void_p).value,
        )

        curl_easy_setopt(
            curl,
            CURLoption.HEADERFUNCTION,
            cast(keepref2, c_void_p).value,
        )
        resp.keeprefs += [keepref1, keepref2]

        if stream:

            def ___perform():
                try:
                    self._perform(curl)
                except Exception as e:
                    headerqueue.put(e)
                resp.queue.put(None)

            threading.Thread(target=___perform, daemon=True).start()

        else:

            self._perform(curl)
        header = self.__getrealheader(headerqueue)
        if not stream:
            resp.content = b"".join(resp.queue)

        resp.headers, resp.cookies, resp.status_text = self._parseheader2dict(header)
        resp.status_code = self._getStatusCode(curl)
        resp.url = url

        return resp
