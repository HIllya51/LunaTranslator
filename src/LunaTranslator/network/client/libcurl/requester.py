from .libcurl import *
import threading, functools, queue
from ctypes import c_long, cast
from requests import Response, Requester_common


class Response_1(Response):
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
    def __init__(self, ref: "Requester") -> None:
        self.ref = ref
        ref.occupied = True

    def __del__(self):
        self.ref.occupied = False


class Requester(Requester_common):

    def __init__(self) -> None:
        # 用tls不太行，因为为了防止阻塞，每次请求都是完全重新开的线程，会100%重新initcurl
        self.occupied = 0
        curl = curl_easy_init()
        curl_easy_setopt(curl, CURLoption.USERAGENT, self.default_UA.encode("utf8"))
        self.curl = curl

    def __WriteMemoryCallback(
        self, headerqueue: queue.Queue, que, contents, size, nmemb, userp
    ):
        if headerqueue:
            headerqueue.put(0)
        realsize = size * nmemb
        bs: bytes = contents[:realsize]
        if isinstance(que, queue.Queue):
            que.put(bs)
        elif isinstance(que, list):
            que.append(bs)
        return realsize

    def _filter_header(self, headertext: str):
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
        lheaders = auto_curl_slist()
        for _ in self._parseheader(headers, None):
            lheaders.append(_)
        curl_easy_setopt(curl, CURLoption.HTTPHEADER, lheaders.ptr)

        if cookies:
            cookie = self._parsecookie(cookies)
            curl_easy_setopt(curl, CURLoption.COOKIE, cookie.encode("utf8"))
        return lheaders

    def request_impl(
        self,
        method,
        scheme,
        server,
        port,
        param,
        url: str,
        headers: dict,
        cookies,
        databytes,
        proxy: str,
        stream,
        verify,
        timeout,
        allow_redirects,
    ):
        if self.occupied == False:
            curl = self.curl
            __ = autostatus(self)
        else:
            curl = curl_easy_duphandle(self.curl)
            __ = 0

        curl_easy_reset(curl)
        # curl_easy_setopt(curl, CURLoption.VERBOSE, 1)
        curl_easy_setopt(curl, CURLoption.COOKIEJAR, "")
        if timeout[0]:
            curl_easy_setopt(curl, CURLoption.CONNECTTIMEOUT_MS, timeout[0])
        if timeout[1]:
            curl_easy_setopt(curl, CURLoption.TIMEOUT_MS, sum(timeout))
        if method == "HEAD":
            curl_easy_setopt(curl, CURLoption.NOBODY, 1)
        encoding: str = headers.get("Accept-Encoding", libcurl_Accept_Encoding)
        if encoding:
            curl_easy_setopt(curl, CURLoption.ACCEPT_ENCODING, encoding.encode("utf8"))
        curl_easy_setopt(curl, CURLoption.CUSTOMREQUEST, method.encode("utf8"))
        curl_easy_setopt(curl, CURLoption.URL, url.encode("utf8"))
        curl_easy_setopt(curl, CURLoption.PORT, port)
        lheaders = self._setheaders(curl, headers, cookies)

        curl_set_verify(curl, verify)
        if proxy:
            curl_easy_setopt(curl, CURLoption.PROXY, proxy.encode("utf8"))
        curl_easy_setopt(curl, CURLoption.FOLLOWLOCATION, int(allow_redirects))
        # curl_easy_setopt(curl, CURLoption.MAXREDIRS, 100) #默认50够了
        try:
            curl_easy_setopt(curl, CURLoption.TCP_KEEPALIVE, 1)
            curl_easy_setopt(curl, CURLoption.TCP_KEEPIDLE, 30)
            curl_easy_setopt(curl, CURLoption.TCP_KEEPINTVL, 10)
        except Exception:
            pass
        if server in ("127.0.0.1", "localhost"):
            # 本地 llama.cpp 会在空闲后关掉 keep-alive。libcurl 对 POST 不会换新连接重试，
            # 且读超时为 0，下一次请求会永久卡住，CLI 也收不到新请求。
            try:
                curl_easy_setopt(curl, CURLoption.FRESH_CONNECT, 1)
                curl_easy_setopt(curl, CURLoption.FORBID_REUSE, 1)
            except Exception:
                pass
        if databytes:
            curl_easy_setopt(curl, CURLoption.POSTFIELDS, databytes)
            curl_easy_setopt(curl, CURLoption.POSTFIELDSIZE, len(databytes))

        resp = Response_1(stream)
        resp.keeprefs.append(curl)
        resp.keeprefs.append(__)
        resp.keeprefs.append(lheaders)
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
        curl_easy_setopt(curl, CURLoption.WRITEFUNCTION, cast(keepref1, c_void_p))
        curl_easy_setopt(curl, CURLoption.HEADERFUNCTION, cast(keepref2, c_void_p))
        resp.keeprefs += [keepref1, keepref2]

        if stream:
            # SSE 解析遇到 [DONE] 就会返回，早于 curl_easy_perform 结束。
            # Response 可能立刻被回收；回调和 handle 必须活到 perform 返回，
            # 且 occupied 不能提前放开，否则下一次请求会 reset 正在 perform 的 handle。
            perform_keep = [curl, __, lheaders, keepref1, keepref2]

            def ___perform():
                try:
                    curl_easy_perform(curl)
                except Exception as e:
                    headerqueue.put(e)
                finally:
                    resp.queue.put(None)
                    perform_keep.clear()

            threading.Thread(target=___perform, daemon=True).start()

        else:
            curl_easy_perform(curl)
        header = self.__getrealheader(headerqueue)
        if not stream:
            resp.content = b"".join(resp.queue)

        resp.headers, resp.cookies, resp.reason = self._parseheader2dict(header)
        if stream:
            # perform 仍在后台跑，不能对同一 easy handle 调 getinfo
            try:
                resp.status_code = int(header.split("\n", 1)[0].split()[1])
            except Exception:
                resp.status_code = 0
            resp.url = url
        else:
            resp.status_code = curl_easy_getinfo(curl, CURLINFO.RESPONSE_CODE, c_long)
            resp.url = curl_easy_getinfo(curl, CURLINFO.EFFECTIVE_URL, c_char_p).decode()

        return resp
