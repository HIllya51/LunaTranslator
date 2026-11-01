import base64, json, os, time
import queue, threading
import urllib.request
from translator.gptcommon import gptcommon
from translator.basetranslator import GptTextWithDict
from myutils.proxy import getproxy
import requests

# opencode serve --service 会把 url/password 写进该文件（自动发现用，
# 恒定启用；文件不存在时回退手动配置——如远端实例或非 service 模式）
STATE_FILE = os.path.join(
    os.path.expanduser("~"), ".local", "state", "opencode", "service.json"
)


def _resolve_service(url, password):
    try:
        with open(STATE_FILE, "r", encoding="utf8") as ff:
            svc = json.load(ff)
        url, password = svc["url"], svc["password"]
    except:
        pass
    return (url or "").rstrip("/"), password


def _headers(password):
    # Basic auth：用户名必须是 opencode（服务端校验）
    if not password:
        return {}
    return {
        "Authorization": "Basic "
        + base64.b64encode(("opencode:" + password).encode()).decode()
    }


def _raise(resp):
    # opencode 的错误是 {"message": ...}（如 free 模型限流的 503），
    # 带上服务端原话，别只给个 HTTP 状态码
    try:
        raise Exception(resp.json()["message"])
    except Exception:
        resp.raise_for_status()
        raise


def list_models(typename, regist):
    url, password = _resolve_service(
        regist.get("API接口地址", lambda: "")(),
        regist.get("SECRET_KEY", lambda: "")(),
    )
    if not url:
        raise Exception("no opencode service url")
    resp = requests.get(
        url + "/api/model",
        headers=_headers(password),
        proxies=getproxy(("fanyi", typename)),
        timeout=10,
    )
    if resp.status_code != 200:
        _raise(resp)
    return [m["id"] for m in resp.json()["data"]]


class _SSEBus:
    """/api/event 的常驻订阅（opencode 的事件流是服务器级订阅、不会自己
    结束，每词建一条必漏连接）——后台线程收事件，按 sessionID 分发；
    断线自动重连。直连不走代理（本地服务）。"""

    def __init__(self, url, headers):
        self._url = url
        self._headers = headers
        self._queues = {}
        self._lock = threading.Lock()
        self._started = False

    def ensure(self):
        with self._lock:
            if not self._started:
                self._started = True
                threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        while True:
            resp = None
            try:
                req = urllib.request.Request(
                    self._url + "/api/event",
                    headers=dict(self._headers, Accept="text/event-stream"),
                )
                resp = opener.open(req, timeout=330)
                for raw in resp:
                    line = raw.decode("utf8", errors="replace").strip()
                    if not line.startswith("data: "):
                        continue
                    try:
                        ev = json.loads(line[6:])
                    except:
                        continue
                    sid = (ev.get("data") or {}).get("sessionID")
                    with self._lock:
                        q = self._queues.get(sid)
                    if q is not None:
                        q.put(ev)
            except:
                pass
            finally:
                if resp is not None:
                    try:
                        resp.close()
                    except:
                        pass
            time.sleep(1)

    def subscribe(self, sid):
        q = queue.Queue()
        with self._lock:
            self._queues[sid] = q
        return q

    def unsubscribe(self, sid):
        with self._lock:
            self._queues.pop(sid, None)


_buses = {}


def _getbus(url, headers):
    key = (url, headers.get("Authorization", ""))
    if key not in _buses:
        _buses[key] = _SSEBus(url, headers)
    bus = _buses[key]
    bus.ensure()
    return bus


class TS(gptcommon):
    def translate(self, query_2: GptTextWithDict):
        if isinstance(query_2, str):
            query_2 = GptTextWithDict(query_2)
        messages, query, query_1 = self.commoncreatemessages(query_2)
        url, password = _resolve_service(
            self.config.get("API接口地址", "").strip(),
            self.multiapikeycurrent.get("SECRET_KEY", ""),
        )
        if not url:
            raise Exception("no opencode service url")
        headers = _headers(password)
        # opencode 的 prompt 只有 text：系统提示/历史/用户输入拼成一条
        prompt = "\n\n".join(_["content"] for _ in messages if _.get("content"))
        # 不指定 agent（默认 build）：title 等一次性 agent 会被自身的
        # 系统提示带偏（只输出标题），build 稳定按指令翻译
        body = {"title": "LunaTranslator"}
        model = self.config.get("model", "")
        if model:
            body["model"] = {"id": model, "providerID": "opencode"}
        resp = self.proxysession.post(
            url + "/api/session", headers=headers, json=body, timeout=30
        )
        if resp.status_code != 200:
            _raise(resp)
        sid = resp.json()["data"]["id"]
        try:
            if self.config.get("流式输出", True):
                # 先订阅事件流再发 prompt：session.text.delta 即增量文本
                # （delta 已增量 yield，结束后不再重复输出完整结果）
                bus = _getbus(url, headers)
                q = bus.subscribe(sid)
                try:
                    self.__sendprompt(url, headers, sid, prompt)
                    respmessage = yield from self.__stream(q, url, headers, sid)
                finally:
                    bus.unsubscribe(sid)
            else:
                self.__sendprompt(url, headers, sid, prompt)
                respmessage = self.__waitresult(url, headers, sid)
                yield respmessage
        finally:
            # 会话用完即删（否则留在 opencode 的会话列表里）
            try:
                self.proxysession.delete(
                    url + "/api/session/{}".format(sid), headers=headers, timeout=15
                )
            except:
                pass
        if not (respmessage and query_1.strip() and respmessage.strip()):
            return
        self._context.append(
            {"role": "user", "content": query, "query_1": query_1}
        )
        self._context.append({"role": "assistant", "content": respmessage})

    def __sendprompt(self, url, headers, sid, prompt):
        resp = self.proxysession.post(
            url + "/api/session/{}/prompt".format(sid),
            headers=headers,
            json={"text": prompt},
            timeout=30,
        )
        if resp.status_code != 200:
            _raise(resp)

    def __stream(self, q, url, headers, sid, timeout=300):
        respmessage = ""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                ev = q.get(timeout=1)
            except queue.Empty:
                continue
            data = ev.get("data") or {}
            ty = ev.get("type")
            if ty == "session.text.delta":
                delta = data.get("delta")
                if not delta:
                    continue
                respmessage += delta
                yield delta
            elif ty == "session.execution.failed":
                raise Exception("opencode execution failed")
            elif ty == "session.execution.succeeded":
                break
        if not respmessage:
            # 事件流里没拿到文本（订阅晚了/纯 reasoning）：取最终消息兜底
            return self.__waitresult(url, headers, sid)
        return respmessage

    def __waitresult(self, url, headers, sid, timeout=300):
        deadline = time.time() + timeout
        while time.time() < deadline:
            resp = self.proxysession.get(
                url + "/api/session/{}/message".format(sid),
                headers=headers,
                timeout=30,
            )
            if resp.status_code != 200:
                _raise(resp)
            msgs = resp.json()["data"]
            assistants = [
                _ for _ in msgs if _.get("type") == "assistant" and _.get("finish")
            ]
            if assistants:
                msg = assistants[-1]
                result = "\n".join(
                    _["text"]
                    for _ in msg.get("content", [])
                    if _.get("type") == "text"
                )
                if msg["finish"] == "error" or not result:
                    raise Exception(result or msg["finish"])
                return result
            time.sleep(0.5)
        raise Exception("opencode timeout")
