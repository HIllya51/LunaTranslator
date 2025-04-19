from .winhttp import *
from requests import Response, Requester_common
from traceback import print_exc
import gzip, zlib, platform
from ctypes import pointer, create_string_buffer, create_unicode_buffer


class Response_1(Response):
    def __init__(self, stream):
        super().__init__(stream)
        self.hreq = None
        self.hSession = None
        self.hconn = None

    def iter_content_impl(self, chunk_size=1):
        availableSize = DWORD()
        downloadedSize = DWORD()
        downloadeddata = b""
        while True:
            MaybeRaiseException0(
                WinHttpQueryDataAvailable(self.hreq, pointer(availableSize))
            )
            if availableSize.value == 0:
                break
            buff = create_string_buffer(availableSize.value)
            MaybeRaiseException0(
                WinHttpReadData(self.hreq, buff, availableSize, pointer(downloadedSize))
            )
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

    @staticmethod
    def _getheaders(hreq):
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

    @staticmethod
    def _getStatusCode(hreq):
        dwSize = DWORD(sizeof(DWORD))
        dwStatusCode = DWORD()
        MaybeRaiseException0(
            WinHttpQueryHeaders(
                hreq,
                WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                None,
                pointer(dwStatusCode),
                pointer(dwSize),
                None,
            )
        )
        return dwStatusCode.value

    @staticmethod
    def _set_proxy(hsess, proxy):
        if proxy:
            winhttpsetproxy(hsess, proxy)

    @staticmethod
    def _set_verify(hRequest, verify):
        if verify == False:
            dwFlags = DWORD(SECURITY_FLAG_IGNORE_ALL_CERT_ERRORS)
            WinHttpSetOption(
                hRequest,
                WINHTTP_OPTION_SECURITY_FLAGS,
                pointer(dwFlags),
                sizeof(dwFlags),
            )

    @staticmethod
    def _set_allow_redirects(hRequest, allow_redirects):
        if allow_redirects:
            dwFlags = DWORD(WINHTTP_OPTION_REDIRECT_POLICY_ALWAYS)
        else:
            dwFlags = DWORD(WINHTTP_OPTION_REDIRECT_POLICY_NEVER)
        WinHttpSetOption(
            hRequest, WINHTTP_OPTION_REDIRECT_POLICY, pointer(dwFlags), sizeof(dwFlags)
        )

    @staticmethod
    def _set_auto_decompress(hRequest):
        if tuple(int(_) for _ in platform.version().split(".")[:2]) <= (6, 2):
            return

        dwFlags = DWORD(
            WINHTTP_DECOMPRESSION_FLAG_GZIP | WINHTTP_DECOMPRESSION_FLAG_DEFLATE
        )
        return WinHttpSetOption(
            hRequest, WINHTTP_OPTION_DECOMPRESSION, pointer(dwFlags), sizeof(dwFlags)
        )

    def __init__(self) -> None:
        self.hSession = WinHttpOpen(
            self.default_UA,
            WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
            WINHTTP_NO_PROXY_NAME,
            WINHTTP_NO_PROXY_BYPASS,
            0,
        )
        MaybeRaiseException0(self.hSession)

    @staticmethod
    def queryurl(hreq):
        dwSize = DWORD(0)
        WinHttpQueryOption(hreq, WINHTTP_OPTION_URL, NULL, pointer(dwSize))
        pwszUrl = create_unicode_buffer(dwSize.value + 1)
        MaybeRaiseException0(
            WinHttpQueryOption(hreq, WINHTTP_OPTION_URL, pwszUrl, pointer(dwSize))
        )
        return pwszUrl.value

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
        flag = WINHTTP_FLAG_SECURE if scheme == "https" else 0

        hConnect = WinHttpConnect(self.hSession, server, port, 0)
        MaybeRaiseException0(hConnect)
        hRequest = WinHttpOpenRequest(
            hConnect,
            method,
            param,
            None,
            WINHTTP_NO_REFERER,
            WINHTTP_DEFAULT_ACCEPT_TYPES,
            flag,
        )
        tconnect = timeout[0]
        tsendrecv = timeout[1]
        WinHttpSetTimeouts(hRequest, tconnect, tconnect, tsendrecv, tsendrecv)
        MaybeRaiseException0(hRequest)
        self._set_verify(hRequest, verify)
        self._set_proxy(hRequest, proxy)
        self._set_allow_redirects(hRequest, allow_redirects)
        autodec = self._set_auto_decompress(hRequest)
        headers = self._parseheader(_headers, cookies)
        headers = "\r\n".join(headers)
        MaybeRaiseException0(
            WinHttpSendRequest(
                hRequest, headers, -1, databytes, len(databytes), len(databytes), None
            )
        )
        MaybeRaiseException0(WinHttpReceiveResponse(hRequest, None))
        resp = Response_1(stream)
        resp.headers, resp.cookies, resp.reason = self._parseheader2dict(
            self._getheaders(hRequest)
        )
        resp.status_code = self._getStatusCode(hRequest)
        resp.url = self.queryurl(hRequest)
        if stream:
            resp.hSession = self.hSession
            resp.hconn = hConnect
            resp.hreq = hRequest
            return resp
        availableSize = DWORD()
        downloadedSize = DWORD()
        downloadeddata = b""
        while True:
            MaybeRaiseException0(
                WinHttpQueryDataAvailable(hRequest, pointer(availableSize))
            )
            if availableSize.value == 0:
                break
            buff = create_string_buffer(availableSize.value)
            MaybeRaiseException0(
                WinHttpReadData(hRequest, buff, availableSize, pointer(downloadedSize))
            )
            downloadeddata += buff[: downloadedSize.value]
        if autodec:
            resp.content = downloadeddata
        else:
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
            return data
        except:
            print_exc()
            raise Exception("unenable to decompress {}".format(encode))
