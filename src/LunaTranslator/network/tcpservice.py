from traceback import print_exc
import socket, re
from base64 import encodebytes as base64encode
import hashlib, os
import time, types
import io, json

if __name__ == "__main__":
    import sys

    sys.path.append(".")
from network.structures import CaseInsensitiveDict
from myutils.wrapper import threader
from myutils.mimehelper import query_mime


class FileResponse:

    def __init__(self, filename):
        self.filename = filename
        if not os.path.isfile(filename):
            raise Exception("")
        self.length = os.stat(filename).st_size
        self.type = query_mime(filename)


class ResponseInfo:
    def __init__(
        self,
        code: int = 200,
        reason: str = "",
        version="HTTP/1.1",
        headers: CaseInsensitiveDict = {},
        body=None,
    ):
        self.code, self.reason, self.headers = (
            code,
            reason,
            CaseInsensitiveDict(headers),
        )
        self.version = version

        if isinstance(body, str):
            body: bytes = body.encode()
            self.headers["Content-Type"] = "text/html; charset=utf-8"
            self.headers["Content-Length"] = len(body)
        elif isinstance(body, (dict, list, tuple)):
            body: bytes = json.dumps(body, ensure_ascii=False).encode()
            self.headers["Content-Type"] = "application/json; charset=utf-8"
            self.headers["Content-Length"] = len(body)
        elif isinstance(body, FileResponse):
            self.headers["Content-Type"] = body.type
            self.headers["Content-Length"] = body.length
        elif isinstance(body, types.GeneratorType):
            self.headers["Content-Type"] = "text/event-stream; charset=utf-8"
        self.body = body

    def write(self, client_socket: socket.socket):
        resp = "{} {} {}\r\n".format(self.version, self.code, self.reason)
        for k, v in self.headers.items():
            resp += "{}: {}\r\n".format(k, v)
        resp += "\r\n"
        client_socket.send(resp.encode())
        if not self.body:
            return
        if isinstance(self.body, bytes):
            return client_socket.send(self.body)
        if isinstance(self.body, FileResponse):
            with open(self.body.filename, "rb") as ff:
                while True:
                    bs = ff.read(1024)
                    if not bs:
                        break
                    client_socket.send(bs)
        if isinstance(self.body, types.GeneratorType):
            for body in self.body:
                if isinstance(body, str):
                    body: bytes = body.encode()
                elif isinstance(body, (dict, list, tuple)):
                    body: bytes = json.dumps(body, ensure_ascii=False).encode()
                client_socket.send(b"data: " + body + b"\n\n")


class RequestInfo:
    def __str__(self):
        vis = dict(
            method=self.method,
            path=self.path,
            version=self.version,
            headers=self.headers,
        )
        return str(vis)

    @staticmethod
    def readfrom(client_socket: socket.socket):
        return RequestInfo._parseheader(
            RequestInfo._read_headers(client_socket.makefile("rb"))
        )

    def __init__(
        self, method: str, path: str, version: str, headers: CaseInsensitiveDict
    ):
        self.method, self.path, self.version = (method, path, version)
        self.headers = headers

    @staticmethod
    def _parseheader(lines: str):
        header = CaseInsensitiveDict()
        method, path, version = lines[0].split(" ")
        for line in lines[1:]:
            idx = line.find(": ")
            if idx == -1:
                continue
            header[line[:idx]] = line[idx + 2 :]
        return RequestInfo(method, path, version, CaseInsensitiveDict(header))

    @staticmethod
    def _read_headers(fp: io.TextIOWrapper):
        """Reads potential header lines into a list from a file pointer.

        Length of line is limited by _MAXLINE, and number of
        headers is limited by _MAXHEADERS.
        """
        headers = []
        while True:
            line: bytes = fp.readline(65536 + 1)
            if len(line) > 65536:
                raise Exception("")
            if len(headers) > 65536:
                raise Exception("")
            if line in (b"\r\n", b"\n", b""):
                break
            line = line.decode("iso-8859-1")
            if line.endswith("\r\n"):
                line = line[:-2]
            if line:
                headers.append(line)
        return headers


class HandlerBase:
    path: str = ...

    def __init__(self, info: RequestInfo, sock: socket.socket): ...

    def parse(self, info: RequestInfo): ...


class WSHandler(HandlerBase):
    path = ...

    def _upgrade(self, headers: dict):
        Upgrade: str = headers.get("Upgrade")
        if not (Upgrade and Upgrade.lower() == "websocket"):
            return
        key = headers.get("Sec-WebSocket-Key")
        if not key:
            return
        value = "{}258EAFA5-E914-47DA-95CA-C5AB0DC85B11".format(key).encode("utf-8")
        hashed = base64encode(hashlib.sha1(value).digest()).strip().decode()

        headers = {
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-WebSocket-Accept": hashed,
        }
        return headers

    def __init__(self, info: RequestInfo, sock: socket.socket):
        self.sock = sock
        ResponseInfo(
            101, "Switching Protocols", headers=self._upgrade(info.headers)
        ).write(sock)
        self.parse(info)

    def _maketextframe(self, message: str):

        fin = 1
        opcode = 0x1
        payload = message.encode("utf-8")
        length = len(payload)

        frame = bytearray()
        frame.append((fin << 7) | opcode)

        if length <= 125:
            frame.append(length)
        elif length <= 65535:
            frame.extend([126, (length >> 8) & 0xFF, length & 0xFF])
        else:
            frame.extend([127] + [(length >> (8 * i)) & 0xFF for i in range(7, -1, -1)])

        frame.extend(payload)
        return frame

    def sendtext(self, text: str):
        frame = self._maketextframe(text)
        try:
            self.sock.send(frame)
        except:
            self.sock = None


class HTTPHandler(HandlerBase):
    path = ...
    method = None

    def __init__(self, info: RequestInfo, client_socket: socket.socket):
        try:
            if not self._checkmethod(info.method):
                raise Exception("")
            ret = self.parse(info)
            resp = ResponseInfo(body=ret)
            try:
                resp.write(client_socket)
            except:
                print_exc()
        except Exception as e:
            print_exc()
            self._404(client_socket)
        client_socket.close()

    def _checkmethod(self, method: str):
        method = method.lower()
        if not self.method:
            return True
        if isinstance(self.method, str):
            return self.method.lower() == method.lower()
        if isinstance(self.method, (list, tuple)):
            return method.lower() in (_.lower() for _ in self.method)
        return True

    def _404(self, client_socket):
        ResponseInfo(404).write(client_socket)


class TCPService:
    def __init__(self):
        self.server_socket = None
        self.handlers: list[HandlerBase] = []

    def register(self, Handler):
        self.handlers.append(Handler)

    def stop(self):
        if self.server_socket:
            self.server_socket.close()

    def init(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.listen()

    @threader
    def listen(self):

        self.server_socket.listen(1)
        while True:
            client_socket, _ = self.server_socket.accept()
            self.handle_client(client_socket)

    def __checkifwebsocket(self, headers: dict):
        Upgrade: str = headers.get("Upgrade")
        return Upgrade and Upgrade.lower() == "websocket"

    @threader
    def handle_client(self, client_socket: socket.socket):
        info = RequestInfo.readfrom(client_socket)

        iswsreq = self.__checkifwebsocket(info.headers)
        matchlen = 0
        matchclass = None
        for handler in self.handlers:
            if (iswsreq and issubclass(handler, HTTPHandler)) or (
                (not iswsreq) and issubclass(handler, WSHandler)
            ):
                continue
            m = re.match(handler.path, info.path)
            if not m:
                continue
            if m.span()[1] > matchlen:
                matchlen = m.span()[1]
                matchclass = handler
        if not matchclass:
            return
        matchclass(info, client_socket)


if __name__ == "__main__":
    ws = TCPService()

    class TextOutput(WSHandler):
        path = "/"

        def parse(self, info: RequestInfo):
            while True:
                time.sleep(1)
                self.sendtext(str(time.time()))

    class APItest(HTTPHandler):
        path = "/"

        def parse(self, info: RequestInfo):
            # return FileResponse(r"C:\Users\11737\Music\12eve\天門 - Again.mp3")

            # for i in range(100):
            #     yield str(i)

            return {"shit": 1}

    ws.register(TextOutput)
    ws.register(APItest)
    ws.init(8011)
