from .winhttp import *
from requests import ResponseBase, Timeout, Requester_common
from traceback import print_exc
import gzip, zlib
from ctypes import pointer, create_string_buffer, create_unicode_buffer

try:
    from .brotli_dec import decompress
except:
    from traceback import print_exc

    print_exc()


class Response(ResponseBase):
    def iter_content_impl(self, chunk_size=1):
        availableSize = DWORD()
        downloadedSize = DWORD()
        downloadeddata = b""
        while True:
            succ = WinHttpQueryDataAvailable(self.hreq, pointer(availableSize))
            if succ == 0:
                raise WinhttpException(GetLastError())
            if availableSize.value == 0:
                break
            buff = create_string_buffer(availableSize.value)
            succ = WinHttpReadData(
                self.hreq, buff, availableSize, pointer(downloadedSize)
            )
            if succ == 0:
                raise WinhttpException(GetLastError())

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

    def raise_for_status(self):
        error = GetLastError()
        if error:
            raise WinhttpException(error)


def ExceptionFilter(func):
    def _wrapper(*args, **kwargs):
        try:
            _ = func(*args, **kwargs)
            return _
        except WinhttpException as e:
            if e.errorcode == WinhttpException.ERROR_WINHTTP_TIMEOUT:
                raise Timeout(e)
            else:
                raise e

    return _wrapper


class Requester(Requester_common):

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
            error = GetLastError()
            if error:
                raise WinhttpException(error)
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
            raise WinhttpException(GetLastError())

    @ExceptionFilter
    def request(
        self,
        method,
        scheme,
        server,
        port,
        param,
        url,
        _headers,
        cookies,
        dataptr,
        datalen,
        proxy,
        stream,
        verify,
        timeout,
        allow_redirects,
    ):
        headers = self._parseheader(_headers, cookies)
        flag = WINHTTP_FLAG_SECURE if scheme == "https" else 0
        # print(server,port,param,dataptr)
        headers = "\r\n".join(headers)

        hConnect = AutoWinHttpHandle(WinHttpConnect(self.hSession, server, port, 0))
        if hConnect == 0:
            raise WinhttpException(GetLastError())
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
        if timeout:
            WinHttpSetTimeouts(hRequest, timeout, timeout, timeout, timeout)
        if hRequest == 0:
            raise WinhttpException(GetLastError())
        self._set_verify(hRequest, verify)
        self._set_proxy(hRequest, proxy)
        self._set_allow_redirects(hRequest, allow_redirects)
        succ = WinHttpSendRequest(
            hRequest, headers, -1, dataptr, datalen, datalen, None
        )
        if succ == 0:
            raise WinhttpException(GetLastError())

        succ = WinHttpReceiveResponse(hRequest, None)
        if succ == 0:
            raise WinhttpException(GetLastError())
        resp = Response()
        resp.headers, resp.cookies = self._parseheader2dict(self._getheaders(hRequest))

        resp.status_code = self._getStatusCode(hRequest)
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
                raise WinhttpException(GetLastError())
            if availableSize.value == 0:
                break
            buff = create_string_buffer(availableSize.value)
            succ = WinHttpReadData(
                hRequest, buff, availableSize, pointer(downloadedSize)
            )
            if succ == 0:
                raise WinhttpException(GetLastError())
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
