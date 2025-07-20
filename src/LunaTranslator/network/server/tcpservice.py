from traceback import print_exc
import socket
from base64 import encodebytes as base64encode
import hashlib, os
import types
import io, json, struct
from urllib.parse import parse_qsl, urlsplit
from network.structures import CaseInsensitiveDict
from myutils.wrapper import threader
from myutils.mimehelper import query_mime


class ResponseWithHeader:
    def __init__(self, data, headers):
        self.headers = headers
        self.data = data


class FileResponse:

    def __init__(self, filename):
        self.filename = filename
        if not os.path.isfile(filename):
            raise Exception()
        self.length = os.stat(filename).st_size
        self.type = query_mime(filename)


class RedirectResponse:
    def __init__(self, target):
        self.target = target


class ResponseInfo:
    @staticmethod
    def _404(sock: socket.socket):
        ResponseInfo(404, "Not Found", body="Not Found").write(sock)
        sock.close()

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
        self.headers["Access-Control-Allow-Origin"] = "*"
        if isinstance(body, ResponseWithHeader):
            self.headers.update(body.headers)
            body = body.data
        if isinstance(body, bytes):
            self.headers["Content-Length"] = len(body)
        elif isinstance(body, str):
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
        elif isinstance(body, RedirectResponse):
            self.code = 302
            self.headers["Location"] = body.target
            body = None
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
            client_socket.send(self.body)
        elif isinstance(self.body, FileResponse):
            with open(self.body.filename, "rb") as ff:
                while True:
                    bs = ff.read(1024)
                    if not bs:
                        break
                    client_socket.send(bs)
        elif isinstance(self.body, types.GeneratorType):
            for body in self.body:
                if isinstance(body, str):
                    body: bytes = body.encode()
                elif isinstance(body, (dict, list, tuple)):
                    body: bytes = json.dumps(body, ensure_ascii=False).encode()
                client_socket.send(b"data: " + body + b"\n\n")


class RequestBody:
    def __init__(self, bs: bytes):
        self.bs = bs

    @property
    def json(self):
        return json.loads(self.bs.decode())


class RequestInfo:
    @property
    def log(self):
        return "{} {}".format(self.method, self.rawpath)

    def __str__(self):
        vis = dict(
            method=self.method,
            path=self.rawpath,
            version=self.version,
            headers=self.headers,
        )
        return str(vis)

    @staticmethod
    def readfrom(client_socket: socket.socket):
        fp = client_socket.makefile("rb")
        info = RequestInfo._parseheader(RequestInfo._read_headers(fp))
        clen = info.headers.get("Content-Length")
        if clen:
            try:
                clen = int(clen)
                info.body = RequestBody(fp.read(clen))
            except:
                pass
        return info

    def __init__(
        self, method: str, rawpath: str, version: str, headers: CaseInsensitiveDict
    ):
        self.rawpath = rawpath
        spls = urlsplit(rawpath)
        self.path = spls.path
        self.query = dict(parse_qsl(spls.query))
        self.method, self.version = (method.upper(), version)
        self.headers = headers
        self.body: RequestBody = None

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
                raise Exception()
            if len(headers) > 65536:
                raise Exception()
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
        self.__recv()

    @threader
    def __recv(self):
        while True:
            msg = self.__readstr()
            if not msg:
                break
            self.onmessage(msg)
        self.sock.close()

    @staticmethod
    def receive_frame(client_socket: socket.socket):
        """接收并解析WebSocket帧"""
        try:
            # 读取前2字节
            header = client_socket.recv(2)
            if len(header) < 2:
                return None, None

            first_byte, second_byte = header[0], header[1]
            fin = (first_byte & 0x80) >> 7
            opcode = first_byte & 0x0F
            mask = (second_byte & 0x80) >> 7
            payload_length = second_byte & 0x7F

            # 处理扩展长度
            if payload_length == 126:
                extended_length = client_socket.recv(2)
                if len(extended_length) < 2:
                    return None, None
                payload_length = struct.unpack(">H", extended_length)[0]
            elif payload_length == 127:
                extended_length = client_socket.recv(8)
                if len(extended_length) < 8:
                    return None, None
                payload_length = struct.unpack(">Q", extended_length)[0]

            # 读取掩码键
            masking_key = client_socket.recv(4) if mask else None

            # 读取载荷数据
            payload = client_socket.recv(payload_length)
            if len(payload) < payload_length:
                return None, None

            # 如果有掩码，解码数据
            if mask and masking_key:
                payload = bytearray(payload)
                for i in range(len(payload)):
                    payload[i] ^= masking_key[i % 4]

            # 如果是文本帧，解码为字符串
            if opcode == 0x1:
                return opcode, payload.decode("utf-8")
            else:
                return opcode, payload

        except Exception as e:
            return None, None

    def __readstr(self):
        # 读取WebSocket帧
        opcode, payload = self.receive_frame(self.sock)

        if not opcode:
            return

        if opcode == 0x1:  # 文本帧
            return payload

        elif opcode == 0x8:  # 关闭帧
            status_code = (payload[0] << 8) + payload[1] if len(payload) >= 2 else None
            reason = (
                payload[2:].decode("utf-8", errors="ignore")
                if len(payload) > 2
                else None
            )
            self.send_close_frame(self.sock, status_code, reason)

        elif opcode == 0x9:  # Ping 帧
            pong_frame = self.build_frame(0xA, payload)
            self.sock.send(pong_frame)

    def send_close_frame(
        self, client_socket: socket.socket, status_code=1000, reason=""
    ):
        payload = struct.pack(">H", status_code) + (
            reason.encode("utf-8") if reason else b""
        )
        frame = self.build_frame(0x8, payload)
        client_socket.send(frame)

    def build_frame(self, opcode, payload):
        """构建WebSocket帧"""
        fin = 0x80
        frame = bytearray()

        # 第一个字节: FIN + opcode
        frame.append(fin | opcode)

        # 第二个字节: MASK + 载荷长度
        mask = 0  # 服务器发送不需要掩码
        payload_length = len(payload)

        if payload_length <= 125:
            frame.append(mask << 7 | payload_length)
        elif payload_length <= 65535:
            frame.append(mask << 7 | 126)
            frame.extend(struct.pack(">H", payload_length))
        else:
            frame.append(mask << 7 | 127)
            frame.extend(struct.pack(">Q", payload_length))

        # 添加载荷
        frame.extend(payload)

        return frame

    def onmessage(self, message: str): ...

    def send_text(self, message: str):
        payload = message.encode("utf-8")
        frame = self.build_frame(0x1, payload)
        self.sock.send(frame)


class HTTPHandler(HandlerBase):
    path = ...
    method: "str|list[str]|tuple[str]" = None

    def __init__(self, info: RequestInfo, client_socket: socket.socket):
        try:
            if not self._checkmethod(info.method):
                raise Exception()
            ret = self.parse(info)
            resp = ResponseInfo(body=ret)
            try:
                resp.write(client_socket)
            except:
                print_exc()
            client_socket.close()
        except Exception as e:
            print_exc()
            self._404(client_socket)

    def _checkmethod(self, method: str):
        if not self.method:
            return True
        if isinstance(self.method, str):
            return self.method == method
        if isinstance(self.method, (list, tuple)):
            return method in self.method
        return True

    def _404(self, client_socket):
        ResponseInfo._404(client_socket)


class TCPService:
    def __init__(self):
        self.server_socket = None
        self.handlers: "list[HandlerBase]" = []

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
            try:
                client_socket, _ = self.server_socket.accept()
            except OSError:
                break
            self.handle_client(client_socket)

    def __checkifwebsocket(self, headers: dict):
        Upgrade: str = headers.get("Upgrade")
        return Upgrade and Upgrade.lower() == "websocket"

    @threader
    def handle_client(self, client_socket: socket.socket):
        info = RequestInfo.readfrom(client_socket)
        print(info.log)
        iswsreq = self.__checkifwebsocket(info.headers)
        for handler in self.handlers:
            if (iswsreq and issubclass(handler, HTTPHandler)) or (
                (not iswsreq) and issubclass(handler, WSHandler)
            ):
                continue
            if info.path == handler.path:
                return handler(info, client_socket)
        return ResponseInfo._404(client_socket)
