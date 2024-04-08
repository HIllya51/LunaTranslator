from textoutput.outputerbase import Base
from traceback import print_exc
import socket
from base64 import encodebytes as base64encode
import hashlib
from myutils.wrapper import threader


class websocketserver:
    def stop(self):
        self.server_socket.close()
        for sock in self.connectedsockets:
            try:
                sock.close()
            except:
                pass

    def __init__(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", port))
        self.connectedsockets = []
        self.errorsocks = []
        self.listen()

    @threader
    def listen(self):

        self.server_socket.listen(1)
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Client connected: {address}")

            self.handle_client(client_socket)

    @threader
    def handle_client(self, client_socket: socket.socket):
        # 接收客户端的握手请求
        request = client_socket.recv(1024).decode()

        # 解析握手请求中的 WebSocket 关键信息
        key = ""
        for line in request.split("\r\n"):
            if "Sec-WebSocket-Key:" in line:
                key = line.split(":")[1].strip()
                break
        value = f"{key}258EAFA5-E914-47DA-95CA-C5AB0DC85B11".encode("utf-8")
        hashed = base64encode(hashlib.sha1(value).digest()).strip().lower().decode()
        # 构造握手响应
        response = "HTTP/1.1 101 Switching Protocols\r\n"
        response += "Upgrade: websocket\r\n"
        response += "Connection: Upgrade\r\n"
        response += "sec-websocket-protocol: 111\r\n"
        response += f"Sec-WebSocket-Accept: {hashed}\r\n\r\n"

        # 发送握手响应给客户端
        client_socket.send(response.encode())
        self.connectedsockets.append(client_socket)

    def maketextframe(self, message):

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

    def sendtext(self, text):
        frame = self.maketextframe(text)
        for i, sock in enumerate(self.connectedsockets):
            if i in self.errorsocks:
                continue
            try:
                sock.send(frame)
            except:
                self.errorsocks.append(i)


class Outputer(Base):
    def init(self):

        try:
            self.server.stop()
        except:
            pass
        if not self.config["use"]:
            return
        try:
            self.server = websocketserver(self.config["port"])
        except:
            print_exc()

    def dispatch(self, text):
        self.server.sendtext(text)
