from libcurl import *
import threading, functools, queue
from ctypes import c_long, cast, pointer, POINTER, c_char
from network.requests_common import *
from traceback import print_exc


class autostatus:
    def __init__(self, ref) -> None:
        self.ref = ref
        ref._status = 1

    def __del__(self):
        self.ref._status = 0


class Response(ResponseBase):
    def __init__(self):
        super().__init__()
        self.last_error = 0

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

    def raise_for_status(self):
        if self.last_error:
            raise CURLException(self.last_error)


def ExceptionFilter(func):
    def _wrapper(*args, **kwargs):
        try:
            _ = func(*args, **kwargs)
            return _
        except CURLException as e:
            if e.errorcode == CURLcode.CURLE_OPERATION_TIMEDOUT:
                raise Timeout(e)
            else:
                raise e

    return _wrapper


class Session(Sessionbase):

    def __init__(self) -> None:
        super().__init__()
        self._status = 0
        self.curl = AutoCURLHandle(curl_easy_init())
        curl_easy_setopt(self.curl, CURLoption.CURLOPT_COOKIEJAR, "")
        curl_easy_setopt(
            self.curl, CURLoption.CURLOPT_USERAGENT, self.UA.encode("utf8")
        )

    def raise_for_status(self):
        if self.last_error:
            raise CURLException(self.last_error)

    def _getStatusCode(self, curl):
        status_code = c_long()
        self.last_error = curl_easy_getinfo(
            curl, CURLINFO.CURLINFO_RESPONSE_CODE, pointer(status_code)
        )
        self.raise_for_status()
        return status_code.value

    def _set_proxy(self, curl, proxy):
        if proxy:
            self.last_error = curl_easy_setopt(
                curl, CURLoption.CURLOPT_PROXY, proxy.encode("utf8")
            )
            self.raise_for_status()

    def _set_verify(self, curl, verify):
        if verify == False:
            curl_easy_setopt(curl, CURLoption.CURLOPT_SSL_VERIFYPEER, 0)
            curl_easy_setopt(curl, CURLoption.CURLOPT_SSL_VERIFYHOST, 0)
        else:
            curl_easy_setopt(curl, CURLoption.CURLOPT_SSL_VERIFYPEER, 1)
            curl_easy_setopt(curl, CURLoption.CURLOPT_SSL_VERIFYHOST, 2)

    def _perform(self, curl):
        self.last_error = curl_easy_perform(curl)
        self.raise_for_status()

    @ExceptionFilter
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
        dataptr,
        datalen,
        proxy,
        stream,
        verify,
        timeout,
    ):

        if self._status == 0:
            curl = self.curl
            __ = autostatus(self)
        else:
            # 不能多线程同时复用同一个curl对象
            curl = AutoCURLHandle(curl_easy_duphandle(self.curl))
            if cookies:
                cookies.update(self.cookies)
            else:
                cookies = self.cookies
        if cookies:
            cookie = self._parsecookie(cookies)
            curl_easy_setopt(curl, CURLoption.CURLOPT_COOKIE, cookie.encode("utf8"))
        if timeout:
            curl_easy_setopt(curl, CURLoption.CURLOPT_TIMEOUT_MS, timeout)
            curl_easy_setopt(curl, CURLoption.CURLOPT_CONNECTTIMEOUT_MS, timeout)
        curl_easy_setopt(
            curl,
            CURLoption.CURLOPT_ACCEPT_ENCODING,
            headers["Accept-Encoding"].encode("utf8"),
        )

        curl_easy_setopt(
            curl, CURLoption.CURLOPT_CUSTOMREQUEST, method.upper().encode("utf8")
        )

        self.last_error = curl_easy_setopt(
            curl, CURLoption.CURLOPT_URL, url.encode("utf8")
        )
        self.raise_for_status()
        curl_easy_setopt(curl, CURLoption.CURLOPT_PORT, port)

        lheaders = Autoslist()
        for _ in self._parseheader(headers, None):
            lheaders = curl_slist_append(
                cast(lheaders, POINTER(curl_slist)), _.encode("utf8")
            )
        self.last_error = curl_easy_setopt(
            curl, CURLoption.CURLOPT_HTTPHEADER, lheaders
        )
        self.raise_for_status()

        self._set_verify(curl, verify)
        self._set_proxy(curl, proxy)
        if datalen:
            curl_easy_setopt(curl, CURLoption.CURLOPT_POSTFIELDS, dataptr)
            curl_easy_setopt(curl, CURLoption.CURLOPT_POSTFIELDSIZE, datalen)

        resp = Response()

        if stream:

            def WriteMemoryCallback(queue, contents, size, nmemb, userp):
                realsize = size * nmemb
                queue.put(cast(contents, POINTER(c_char))[:realsize])
                return realsize

            _content = []
            _headers = []
            resp.queue = queue.Queue()
            headerqueue = queue.Queue()
            resp.keepref1 = WRITEFUNCTION(
                functools.partial(WriteMemoryCallback, resp.queue)
            )
            resp.keepref2 = WRITEFUNCTION(
                functools.partial(WriteMemoryCallback, headerqueue)
            )
            curl_easy_setopt(
                curl,
                CURLoption.CURLOPT_WRITEFUNCTION,
                cast(resp.keepref1, c_void_p).value,
            )

            curl_easy_setopt(
                curl,
                CURLoption.CURLOPT_HEADERFUNCTION,
                cast(resp.keepref2, c_void_p).value,
            )

            def ___perform():
                try:
                    self._perform(curl)
                except:
                    print_exc()
                    self.raise_for_status()
                    headerqueue.put(None)
                curl_easy_reset(curl)
                resp.queue.put(None)

            threading.Thread(target=___perform, daemon=True).start()

            headerb = b""
            while True:
                _headerb = headerqueue.get()
                if _headerb is None:
                    self.raise_for_status()
                headerb += _headerb
                if _headerb == b"\r\n":
                    break
            resp.headers = self._update_header_cookie(headerb.decode("utf8"))

            if proxy:
                resp.status_code = int(
                    headerb.decode("utf8").split("\r\n")[0].split(" ")[1]
                )
            else:
                resp.status_code = self._getStatusCode(curl)
        else:

            def WriteMemoryCallback(saver, contents, size, nmemb, userp):
                realsize = size * nmemb
                saver.append(cast(contents, POINTER(c_char))[:realsize])
                return realsize

            _content = []
            _headers = []
            resp.keepref1 = WRITEFUNCTION(
                functools.partial(WriteMemoryCallback, _content)
            )
            resp.keepref2 = WRITEFUNCTION(
                functools.partial(WriteMemoryCallback, _headers)
            )

            curl_easy_setopt(
                curl,
                CURLoption.CURLOPT_WRITEFUNCTION,
                cast(resp.keepref1, c_void_p).value,
            )
            curl_easy_setopt(
                curl,
                CURLoption.CURLOPT_HEADERFUNCTION,
                cast(resp.keepref2, c_void_p).value,
            )

            self._perform(curl)
            resp.content = b"".join(_content)
            resp.headers = self._update_header_cookie(b"".join(_headers).decode("utf8"))
            resp.status_code = self._getStatusCode(curl)
            curl_easy_reset(curl)
        resp.last_error = self.last_error
        resp.cookies = self.cookies
        return resp


Sessionimpl[0] = Session
