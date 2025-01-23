from .winhttp import *
from requests import Response, Timeout, Requester_common
from traceback import print_exc
import windows
import gzip, zlib
from ctypes import pointer, create_string_buffer, create_unicode_buffer

try:
    from .brotli_dec import decompress
except:
    from traceback import print_exc

    print_exc()


class Response(Response):
    def iter_content_impl(self, chunk_size=1):
        availableSize = DWORD()
        downloadedSize = DWORD()
        downloadeddata = b""
        while True:
            succ = WinHttpQueryDataAvailable(self.hreq, pointer(availableSize))
            if succ == 0:
                MaybeRaiseException()
            if availableSize.value == 0:
                break
            buff = create_string_buffer(availableSize.value)
            succ = WinHttpReadData(
                self.hreq, buff, availableSize, pointer(downloadedSize)
            )
            if succ == 0:
                MaybeRaiseException()

            if chunk_size:
                downloadeddata += buff[: downloadedSize.value]
                while len(downloadeddata) > chunk_size:
                    yield downloadeddata[:chunk_size]
                    downloadeddata = downloadeddata[chunk_size:]
            else:
                yield buff[: downloadedSize.value]
        while len(downloadeddata):
            yield downloadeddata[:chunk_size]
            downloadeddata = downloadeddata[chunk_size:]


class Requester(Requester_common):
    def request(self, *argc, **kwarg) -> Response:
        if kwarg["stream"]:
            # winhttp流式时，没办法判断解压边界
            kwarg["headers"].pop("Accept-Encoding")
        return super().request(*argc, **kwarg)

    def _getheaders(self, hreq):
        dwSize = DWORD()
        WinHttpQueryHeaders(
            hreq,
            WINHTTP_QUERY_RAW_HEADERS_CRLF,
            WINHTTP_HEADER_NAME_BY_INDEX,
            None,
            pointer(dwSize),
            WINHTTP_NO_HEADER_INDEX,
        )

        pszCookies = create_unicode_buffer(dwSize.value // 2 + 1)
        succ = WinHttpQueryHeaders(
            hreq,
            WINHTTP_QUERY_RAW_HEADERS_CRLF,
            WINHTTP_HEADER_NAME_BY_INDEX,
            pszCookies,
            pointer(dwSize),
            WINHTTP_NO_HEADER_INDEX,
        )
        if succ == 0:
            return ""
        return pszCookies.value

    def _getStatusCode(self, hreq):
        dwSize = DWORD(sizeof(DWORD))
        dwStatusCode = DWORD()
        bResults = WinHttpQueryHeaders(
            hreq,
            WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
            None,
            pointer(dwStatusCode),
            pointer(dwSize),
            None,
        )
        if bResults == 0:
            MaybeRaiseException()
        return dwStatusCode.value

    def _set_proxy(self, hsess, proxy):
        if proxy:
            winhttpsetproxy(hsess, proxy)

    def _set_verify(self, hRequest, verify):
        if verify == False:
            dwFlags = DWORD(SECURITY_FLAG_IGNORE_ALL_CERT_ERRORS)
            WinHttpSetOption(
                hRequest,
                WINHTTP_OPTION_SECURITY_FLAGS,
                pointer(dwFlags),
                sizeof(dwFlags),
            )

    def _set_allow_redirects(self, hRequest, allow_redirects):
        if allow_redirects:
            dwFlags = DWORD(WINHTTP_OPTION_REDIRECT_POLICY_ALWAYS)
        else:
            dwFlags = DWORD(WINHTTP_OPTION_REDIRECT_POLICY_NEVER)
        WinHttpSetOption(
            hRequest, WINHTTP_OPTION_REDIRECT_POLICY, pointer(dwFlags), sizeof(dwFlags)
        )

    def __init__(self) -> None:
        self.hSession = AutoWinHttpHandle(
            WinHttpOpen(
                self.default_UA,
                WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                WINHTTP_NO_PROXY_NAME,
                WINHTTP_NO_PROXY_BYPASS,
                0,
            )
        )
        if self.hSession == 0:
            MaybeRaiseException()

    def request_impl(
        self,
        method,
        scheme,
        server,
        port,
        param,
        url,
        _headers,
        cookies,
        databytes,
        proxy,
        stream,
        verify,
        timeout,
        allow_redirects,
    ):
        headers = self._parseheader(_headers, cookies)
        flag = WINHTTP_FLAG_SECURE if scheme == "https" else 0
        headers = "\r\n".join(headers)

        hConnect = AutoWinHttpHandle(WinHttpConnect(self.hSession, server, port, 0))
        if hConnect == 0:
            MaybeRaiseException()
        hRequest = AutoWinHttpHandle(
            WinHttpOpenRequest(
                hConnect,
                method,
                param,
                None,
                WINHTTP_NO_REFERER,
                WINHTTP_DEFAULT_ACCEPT_TYPES,
                flag,
            )
        )
        tconnect = timeout[0]
        tsendrecv = timeout[1]
        WinHttpSetTimeouts(hRequest, tconnect, tconnect, tsendrecv, tsendrecv)
        if hRequest == 0:
            MaybeRaiseException()
        self._set_verify(hRequest, verify)
        self._set_proxy(hRequest, proxy)
        self._set_allow_redirects(hRequest, allow_redirects)
        succ = WinHttpSendRequest(
            hRequest, headers, -1, databytes, len(databytes), len(databytes), None
        )
        if succ == 0:
            MaybeRaiseException()

        succ = WinHttpReceiveResponse(hRequest, None)
        if succ == 0:
            MaybeRaiseException()
        resp = Response(stream)
        resp.headers, resp.cookies, resp.reason = self._parseheader2dict(
            self._getheaders(hRequest)
        )

        resp.status_code = self._getStatusCode(hRequest)
        resp.url = url
        if stream:
            resp.hSession = self.hSession
            resp.hconn = hConnect
            resp.hreq = hRequest
            return resp
        availableSize = DWORD()
        downloadedSize = DWORD()
        downloadeddata = b""
        while True:
            succ = WinHttpQueryDataAvailable(hRequest, pointer(availableSize))
            if succ == 0:
                MaybeRaiseException()
            if availableSize.value == 0:
                break
            buff = create_string_buffer(availableSize.value)
            succ = WinHttpReadData(
                hRequest, buff, availableSize, pointer(downloadedSize)
            )
            if succ == 0:
                MaybeRaiseException()
            downloadeddata += buff[: downloadedSize.value]
        resp.content = self.decompress(downloadeddata, resp.headers)

        return resp

    def decompress(self, data, headers):
        # WINHTTP_OPTION_DECOMPRESSION
        # 支持gzip和deflate，WINHTTP_DECOMPRESSION_FLAG_GZIP|WINHTTP_DECOMPRESSION_FLAG_DEFLATE
        # 但只支持win8.1+,不支持br
        encode = headers.get("Content-Encoding", None)
        try:
            if encode == "gzip":
                data = gzip.decompress(data)
            elif encode == "deflate":
                data = zlib.decompress(data, -zlib.MAX_WBITS)
            elif encode == "br":
                data = decompress(data)
            return data
        except:
            print_exc()
            raise Exception("unenable to decompress {}".format(encode))
