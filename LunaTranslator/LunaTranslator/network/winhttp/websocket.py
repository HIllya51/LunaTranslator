from .winhttp import *
from urllib.parse import urlsplit
from ctypes import pointer, create_string_buffer


class WebSocket:
    def send(self, data):
        if isinstance(data, str):
            _t = WINHTTP_WEB_SOCKET_UTF8_MESSAGE_BUFFER_TYPE
            data = data.encode("utf8")
        elif isinstance(data, bytes):
            _t = WINHTTP_WEB_SOCKET_BINARY_MESSAGE_BUFFER_TYPE
        datalen = len(data)
        dwError = WinHttpWebSocketSend(self.hWebSocketHandle, _t, data, datalen)

        if ERROR_SUCCESS != dwError:
            raise WinhttpException(dwError)

    def recv(self):
        eBufferType = DWORD(0)
        dwBytesTransferred = DWORD()
        newBufferSize = DWORD(10240)

        pbCurrentBufferPointer = create_string_buffer(10240)

        dwError = WinHttpWebSocketReceive(
            self.hWebSocketHandle,
            pbCurrentBufferPointer,
            newBufferSize,
            pointer(dwBytesTransferred),
            pointer(eBufferType),
        )
        if dwError == ERROR_SUCCESS:
            if eBufferType.value in [
                WINHTTP_WEB_SOCKET_UTF8_MESSAGE_BUFFER_TYPE,
                WINHTTP_WEB_SOCKET_UTF8_FRAGMENT_BUFFER_TYPE,
            ]:
                return pbCurrentBufferPointer[: dwBytesTransferred.value].decode("utf8")
            elif eBufferType.value in [
                WINHTTP_WEB_SOCKET_BINARY_MESSAGE_BUFFER_TYPE,
                WINHTTP_WEB_SOCKET_BINARY_FRAGMENT_BUFFER_TYPE,
            ]:
                return pbCurrentBufferPointer[: dwBytesTransferred.value]
        else:
            raise WinhttpException(dwError)

    def close(self):
        if self.hWebSocketHandle:
            WinHttpWebSocketClose(
                self.hWebSocketHandle,
                WINHTTP_WEB_SOCKET_SUCCESS_CLOSE_STATUS,
                NULL,
                None,
            )
            self.hWebSocketHandle = 0

    def __del__(self):
        self.close()

    def __init__(self) -> None:
        self.hWebSocketHandle = 0
        self.hConnect = 0
        self.hSession = 0

    def _parseurl2serverandpath(self, url):
        url = url.strip()
        scheme, server, path, query, _ = urlsplit(url)
        if scheme == "wss":
            ishttps = True
        elif scheme == "ws":
            ishttps = False
        else:
            raise WinhttpException("unknown scheme " + scheme)
        spl = server.split(":")
        if len(spl) == 2:
            server = spl[0]
            port = int(spl[1])
        elif len(spl) == 1:
            spl[0]
            if ishttps:
                port = INTERNET_DEFAULT_HTTPS_PORT
            else:
                port = INTERNET_DEFAULT_HTTP_PORT
        else:
            raise WinhttpException("invalid url")
        if len(query):
            path += "?" + query
        return ishttps, server, port, path

    def _parseheader(self, header):
        if header is None:
            return WINHTTP_NO_ADDITIONAL_HEADERS
        return "\r\n".join(header)

    def _setproxy(self, hsess, http_proxy_host, http_proxy_port):
        if http_proxy_host is None or http_proxy_port is None:
            return
        proxy = "{}:{}".format(http_proxy_host, http_proxy_port)
        winhttpsetproxy(hsess, proxy)

    def connect(self, url, header=None, http_proxy_host=None, http_proxy_port=None):
        https, server, port, path = self._parseurl2serverandpath(url)
        if https:
            flag = WINHTTP_FLAG_SECURE
        else:
            flag = 0
        self.hSession = AutoWinHttpHandle(
            WinHttpOpen(
                "WebSocket Client",
                WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                WINHTTP_NO_PROXY_NAME,
                WINHTTP_NO_PROXY_BYPASS,
                0,
            )
        )
        if self.hSession == 0:
            raise WinhttpException(GetLastError())
        self._setproxy(self.hSession, http_proxy_host, http_proxy_port)
        self.hConnect = AutoWinHttpHandle(
            WinHttpConnect(self.hSession, server, port, 0)
        )
        if self.hConnect == 0:
            raise WinhttpException(GetLastError())
        hRequest = AutoWinHttpHandle(
            WinHttpOpenRequest(
                self.hConnect,
                "GET",
                path,
                None,
                WINHTTP_NO_REFERER,
                WINHTTP_DEFAULT_ACCEPT_TYPES,
                flag,
            )
        )
        if hRequest == 0:
            raise WinhttpException(GetLastError())
        fStatus = WinHttpSetOption(
            hRequest, WINHTTP_OPTION_UPGRADE_TO_WEB_SOCKET, NULL, 0
        )

        if fStatus == 0:
            raise WinhttpException(GetLastError())
        fStatus = WinHttpSendRequest(
            hRequest, self._parseheader(header), -1, WINHTTP_NO_REQUEST_DATA, 0, 0, None
        )

        if fStatus == 0:
            raise WinhttpException(GetLastError())
        fStatus = WinHttpReceiveResponse(hRequest, 0)

        if fStatus == 0:
            raise WinhttpException(GetLastError())
        self.hWebSocketHandle = AutoWinHttpHandle(
            WinHttpWebSocketCompleteUpgrade(hRequest, NULL)
        )

        if self.hWebSocketHandle == 0:
            raise WinhttpException(GetLastError())
