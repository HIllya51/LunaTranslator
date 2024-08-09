from translator.basetranslator import basetrans
import json, requests, threading, hashlib
from myutils.config import globalconfig, _TR
from myutils.wrapper import threader
from myutils.utils import checkportavailable
from myutils.subproc import subproc_w
import websocket, time, queue, os
from gui.setting_translate import statuslabelsettext


class Commonloadchromium:
    def __init__(self) -> None:
        self.task = queue.Queue()
        self.waittaskthread()

    def maybeload(self):
        self.task.put(0)

    @threader
    def waittaskthread(self):
        while True:
            self.__waittaskthread()

    def __waittaskthread(self):
        _ = self.task.get()
        if not self.task.empty():
            return
        time.sleep(0.2)
        if not self.task.empty():
            return

        port = globalconfig["debugport"]
        _path = self.getpath()
        if not _path:
            statuslabelsettext(self, "No Chromium Found")
            return
        try:
            requests.get("http://127.0.0.1:{}/json/list".format(port)).json()
            statuslabelsettext(self, "连接成功")
        except:
            if checkportavailable(port):
                statuslabelsettext(self, "连接失败")
                call = self.gencmd(_path, port)
                self.engine = subproc_w(call)
            else:
                statuslabelsettext(self, "端口冲突")

    def gencmd(self, path, port):
        hash_ = hashlib.md5(path.encode("utf8")).hexdigest()
        cache = os.path.abspath(os.path.join("chrome_cache", hash_))
        fmt = '"%s" --disable-extensions --remote-allow-origins=* --disable-gpu --no-first-run --remote-debugging-port=%d --user-data-dir="%s"'
        call = fmt % (path, port, cache)
        return call

    def getpath(self):
        for syspath in [
            globalconfig["chromepath"],
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]:
            if os.path.exists(syspath) and os.path.isfile(syspath):
                return syspath
        return None


class basetransdev(basetrans):
    target_url = None
    commonloadchromium = Commonloadchromium()

    def check_url_is_translator_url(self, url):
        return url.startswith(self.target_url)

    def Page_navigate(self, url):
        self._SendRequest("Page.navigate", {"url": url})
        self._wait_document_ready()

    def Runtime_evaluate(self, expression):
        return self._SendRequest("Runtime.evaluate", {"expression": expression})

    def wait_for_result(self, expression, badresult="", multi=False):
        for i in range(10000):
            if self.using == False:
                return
            state = self.Runtime_evaluate(expression)
            try:
                value = state["result"]["value"]
                if multi:
                    if not (value in badresult):
                        return value
                else:
                    if value != badresult:
                        return value
            except:
                pass
            time.sleep(0.1)

    #########################################
    def _private_init(self):
        self.commonloadchromium.maybeload()
        self._id = 1
        self.sendrecvlock = threading.Lock()
        self._createtarget()
        super()._private_init()

    def _SendRequest(self, method, params, ws=None):
        if self.using == False:
            return
        with self.sendrecvlock:
            self._id += 1

            if ws is None:
                ws = self.ws
            try:
                ws.send(
                    json.dumps({"id": self._id, "method": method, "params": params})
                )
                res = ws.recv()
            except requests.RequestException:
                self.commonloadchromium.maybeload()
                raise Exception(_TR("连接失败"))

            res = json.loads(res)
            try:
                return res["result"]
            except:
                print(res)
                raise Exception(res)

    def _createtarget(self):
        if self.using == False:
            return
        port = globalconfig["debugport"]
        url = self.target_url
        try:
            infos = requests.get("http://127.0.0.1:{}/json/list".format(port)).json()
        except:
            time.sleep(1)
            self._createtarget()
            return
        use = None
        for info in infos:
            if self.check_url_is_translator_url(info["url"]):
                use = info["webSocketDebuggerUrl"]
                break
        if use is None:
            ws = websocket.create_connection(infos[0]["webSocketDebuggerUrl"])
            a = self._SendRequest("Target.createTarget", {"url": url}, ws=ws)

            use = "ws://127.0.0.1:{}/devtools/page/".format(port) + a["targetId"]
        self.ws = websocket.create_connection(use)
        self._wait_document_ready()

    def _wait_document_ready(self):
        for i in range(10000):
            if self.using == False:
                return
            state = self.Runtime_evaluate("document.readyState")
            try:
                if state["result"]["value"] == "complete":
                    break
            except:
                pass
            time.sleep(0.1)

    def send_keys(self, text):
        # self._SendRequest("Input.setIgnoreInputEvents", {"ignore": False})
        try:
            self._SendRequest("Input.insertText", {"text": text})
        except:
            for char in text:
                # self._SendRequest('Input.dispatchKeyEvent', {'type': 'keyDown', 'modifiers': 0, 'timestamp': 0, 'text': char, 'unmodifiedText': char, 'keyIdentifier': '', 'code': f'Key{char.upper()}', 'key': char, 'windowsVirtualKeyCode': code, 'nativeVirtualKeyCode': code, 'autoRepeat': False, 'isKeypad': False, 'isSystemKey': False, 'location': 0})
                self._SendRequest(
                    "Input.dispatchKeyEvent",
                    {
                        "type": "char",
                        "modifiers": 0,
                        "timestamp": 0,
                        "text": char,
                        "unmodifiedText": char,
                        "keyIdentifier": "",
                        "code": "Unidentified",
                        "key": "",
                        "windowsVirtualKeyCode": 0,
                        "nativeVirtualKeyCode": 0,
                        "autoRepeat": False,
                        "isKeypad": False,
                        "isSystemKey": False,
                        "location": 0,
                    },
                )
                # self._SendRequest('Input.dispatchKeyEvent', {'type': 'keyUp', 'modifiers': 0, 'timestamp': 0, 'text': '', 'unmodifiedText': '', 'keyIdentifier': '', 'code': f'Key{char.upper()}', 'key': char, 'windowsVirtualKeyCode': code, 'nativeVirtualKeyCode': code, 'autoRepeat': False, 'isKeypad': False, 'isSystemKey': False, 'location': 0})

        # self._SendRequest("Input.setIgnoreInputEvents", {"ignore": True})
