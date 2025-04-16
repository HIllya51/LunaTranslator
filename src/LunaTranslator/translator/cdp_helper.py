from translator.basetranslator import basetrans
import json, requests, threading, hashlib
from myutils.config import _TR
from myutils.wrapper import threader
from myutils.utils import checkportavailable
import websocket, time, queue, os, subprocess


class Commonloadchromium:
    def __init__(self) -> None:
        self.task = queue.Queue()
        self.waittaskthread()

    def maybeload(self, config):
        self.task.put(config)

    @threader
    def waittaskthread(self):
        while True:
            self.__waittaskthread()

    def __waittaskthread(self):
        config = self.task.get()
        if not self.task.empty():
            return
        time.sleep(0.2)
        if not self.task.empty():
            return

        port = config["debugport"]
        _path = self.getpath(config)
        if not _path:
            print("No Chromium Found")
            return
        try:
            requests.get("http://127.0.0.1:{}/json/list".format(port)).json()
            print("连接成功")
        except:
            if checkportavailable(port):
                print("连接失败")
                call = self.gencmd(_path, port)
                subprocess.Popen(call)
            else:
                print("端口冲突")

    def gencmd(self, path, port):
        hash_ = hashlib.md5(path.encode("utf8")).hexdigest()
        cache = os.path.abspath(os.path.join("chrome_cache", hash_))
        fmt = '"%s" --no-first-run --remote-debugging-port=%d --user-data-dir="%s"'
        call = fmt % (path, port, cache)
        return call

    def getpath(self, config):
        for syspath in [
            config["chromepath"],
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]:
            if os.path.exists(syspath) and os.path.isfile(syspath):
                return syspath
        return None


class cdp_helper:
    target_url = None

    @property
    def config(self):
        return self.ref.config

    @property
    def using(self):
        return self.ref.using

    def check_url_is_translator_url(self, url: str):
        return url.startswith(self.target_url)

    def Page_navigate(self, url):
        self._SendRequest("Page.navigate", {"url": url})
        self._wait_document_ready()

    def Runtime_evaluate(self, expression):
        return self._SendRequest("Runtime.evaluate", {"expression": expression})

    def wait_for_result(self, expression):
        for i in range(10000):
            if self.using == False:
                return
            state = self.Runtime_evaluate(expression)
            try:
                value = state["result"]["value"]
                if value:
                    return value
            except:
                pass
            time.sleep(0.1)

    #########################################

    def __init__(self, ref: basetrans) -> None:
        self.ref = ref
        cdp_helper.commonloadchromium.maybeload(self.config)
        self._id = 1
        self.sendrecvlock = threading.Lock()
        self._createtarget()

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
                cdp_helper.commonloadchromium.maybeload(self.config)
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
        port = self.config["debugport"]
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

    def clear_input(self):
        self._SendRequest(
            "Input.dispatchKeyEvent",
            {
                "type": "keyDown",
                "modifiers": 2,
                "timestamp": 0,
                "windowsVirtualKeyCode": 65,
                "autoRepeat": False,
                "isKeypad": False,
                "isSystemKey": False,
                "location": 0,
            },
        )
        self._SendRequest(
            "Input.dispatchKeyEvent",
            {
                "type": "keyUp",
                "modifiers": 2,
                "timestamp": 0,
                "windowsVirtualKeyCode": 65,
                "autoRepeat": False,
                "isKeypad": False,
                "isSystemKey": False,
                "location": 0,
            },
        )
        self._SendRequest(
            "Input.dispatchKeyEvent",
            {
                "type": "keyDown",
                "timestamp": 0,
                "windowsVirtualKeyCode": 8,
                "autoRepeat": False,
                "isKeypad": False,
                "isSystemKey": False,
                "location": 0,
            },
        )
        self._SendRequest(
            "Input.dispatchKeyEvent",
            {
                "type": "keyUp",
                "timestamp": 0,
                "windowsVirtualKeyCode": 8,
                "autoRepeat": False,
                "isKeypad": False,
                "isSystemKey": False,
                "location": 0,
            },
        )

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

    commonloadchromium = Commonloadchromium()


class cdp_helperllm(cdp_helper):
    jsfile = ...
    textarea_selector = ...
    button_selector = ...
    function1 = ...
    function2 = ...

    def injectjs(self):
        with open(
            os.path.join(os.path.dirname(__file__), self.jsfile),
            "r",
            encoding="utf8",
        ) as ff:
            js = ff.read() % (
                self.function1,
                self.function2,
            )
        self.Runtime_evaluate(js)

    def translate(self, content):
        self.injectjs()
        prompt = self.ref._gptlike_createsys("use_custom_prompt", "custom_prompt")
        content = prompt + content
        self.Runtime_evaluate(
            "document.querySelector(`{}`).foucs()".format(repr(self.textarea_selector))
        )
        self.clear_input()
        self.send_keys(content)
        # chatgpt网站没有焦点时，用这个也可以。
        self.Runtime_evaluate(
            'textarea=document.querySelector({});textarea.value="";event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);textarea.value=`{}`;event = new Event("input", {{bubbles: true, cancelable: true }});textarea.dispatchEvent(event);'.format(
                repr(self.textarea_selector), content
            )
        )

        try:
            # 月之暗面
            while self.Runtime_evaluate(
                "document.querySelector({}).disabled".format(repr(self.button_selector))
            )["result"]["value"]:
                time.sleep(0.1)
        except:
            pass
        self.Runtime_evaluate(
            "document.querySelector({}).click()".format(repr(self.button_selector))
        )
        if self.config["usingstream"]:
            __ = [""]

            def ___(__):
                time.sleep(0.1)
                thistext = self.Runtime_evaluate("thistext")["result"]["value"]

                if thistext.startswith(__[0]):
                    yield thistext[len(__[0]) :]
                else:
                    yield "\0"
                    yield thistext
                __[0] = thistext

            while not self.Runtime_evaluate("hasdone")["result"]["value"]:
                yield from ___(__)
            yield from ___(__)
        else:
            while not self.Runtime_evaluate("hasdone")["result"]["value"]:
                time.sleep(0.1)
                continue
            yield self.Runtime_evaluate("thistext")["result"]["value"]
