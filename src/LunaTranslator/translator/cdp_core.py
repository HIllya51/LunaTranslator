import os
import sys
import time
import json
import re
import socket
import struct
import base64
import urllib.parse
import subprocess
import threading

def cdp_log(msg: str):
    """CDP console logging."""
    print(f"[CDP] {msg}")

_job_object = None

def _init_job_object():
    global _job_object
    if sys.platform != "win32" or _job_object is not None:
        return
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        hJob = kernel32.CreateJobObjectW(None, None)
        if not hJob:
            return

        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
        JobObjectExtendedLimitInformation = 9

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_uint64),
                ("WriteOperationCount", ctypes.c_uint64),
                ("OtherOperationCount", ctypes.c_uint64),
                ("ReadTransferCount", ctypes.c_uint64),
                ("WriteTransferCount", ctypes.c_uint64),
                ("OtherTransferCount", ctypes.c_uint64),
            ]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryLimit", ctypes.c_size_t),
                ("PeakJobMemoryLimit", ctypes.c_size_t),
            ]

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        kernel32.SetInformationJobObject(
            hJob, JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info)
        )
        _job_object = hJob
    except Exception:
        pass

def assign_proc_to_job(proc):
    if sys.platform != "win32" or not proc or not _job_object:
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        proc_handle = getattr(proc, "_handle", None)
        if proc_handle:
            kernel32.AssignProcessToJobObject(_job_object, proc_handle)
    except Exception:
        pass

_init_job_object()


class SimpleWebSocket:
    def __init__(self, url: str, timeout: float = 30.0):
        self.url = url
        self.timeout = timeout
        self.sock = None
        self._connect()

    def _connect(self):
        parsed = urllib.parse.urlparse(self.url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme in ("wss", "https") else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((host, port))

        if parsed.scheme in ("wss", "https"):
            import ssl
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(self.sock, server_hostname=host)

        sec_key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode("ascii"))

        header_data = bytearray()
        while b"\r\n\r\n" not in header_data:
            chunk = self.sock.recv(1024)
            if not chunk:
                raise ConnectionResetError("Server closed connection during handshake.")
            header_data.extend(chunk)

        headers_text = header_data.decode("latin1")
        if " 101 " not in headers_text.splitlines()[0]:
            raise ConnectionError(f"WebSocket upgrade failed: {headers_text.splitlines()[0]}")

    def send(self, message: str):
        payload = message.encode("utf-8")
        length = len(payload)
        header = bytearray([0x81])
        if length <= 125:
            header.append(length | 0x80)
        elif length <= 65535:
            header.append(126 | 0x80)
            header.extend(struct.pack("!H", length))
        else:
            header.append(127 | 0x80)
            header.extend(struct.pack("!Q", length))

        mask = os.urandom(4)
        header.extend(mask)
        masked_payload = bytearray(length)
        for i in range(length):
            masked_payload[i] = payload[i] ^ mask[i % 4]

        self.sock.sendall(header + masked_payload)

    def recv(self) -> str:
        message_bytes = bytearray()
        while True:
            b1, b2 = self._read_exact(2)
            fin = bool(b1 & 0x80)
            opcode = b1 & 0x0F
            if opcode == 0x8:
                raise ConnectionResetError("Remote server sent Close frame.")

            payload_len = b2 & 0x7F
            if payload_len == 126:
                payload_len = struct.unpack("!H", self._read_exact(2))[0]
            elif payload_len == 127:
                payload_len = struct.unpack("!Q", self._read_exact(8))[0]

            is_masked = bool(b2 & 0x80)
            if is_masked:
                mask = self._read_exact(4)
                data = bytearray(self._read_exact(payload_len))
                for i in range(payload_len):
                    data[i] ^= mask[i % 4]
                payload_bytes = bytes(data)
            else:
                payload_bytes = self._read_exact(payload_len)

            if opcode == 0x9:
                pong = bytearray([0x8A, 0x00])
                self.sock.sendall(pong)
                continue
            elif opcode == 0xA:
                continue
            elif opcode in (0x1, 0x0):
                message_bytes.extend(payload_bytes)
                if fin:
                    return message_bytes.decode("utf-8", errors="replace")
            else:
                if fin:
                    return payload_bytes.decode("utf-8", errors="replace")

    def _read_exact(self, num_bytes: int) -> bytes:
        data = bytearray()
        while len(data) < num_bytes:
            chunk = self.sock.recv(num_bytes - len(data))
            if not chunk:
                raise ConnectionResetError("Socket closed prematurely while reading data.")
            data.extend(chunk)
        return bytes(data)

    def close(self):
        if self.sock:
            try:
                self.sock.sendall(bytearray([0x88, 0x00]))
                self.sock.close()
            except Exception:
                pass
            finally:
                self.sock = None


class TranslationTask:
    def __init__(self, content: str, srclang_obj, tgtlang_obj):
        self.content = content
        self.srclang_obj = srclang_obj
        self.tgtlang_obj = tgtlang_obj
        self.done_event = threading.Event()
        self.result = ""
        self.cancelled = False
        self.created_at = time.time()


SHIELD_JS = (
    "(() => {"
    "let shield = document.getElementById('__cdp_shield__');"
    "if (!shield) {"
    "shield = document.createElement('div');"
    "shield.id = '__cdp_shield__';"
    "shield.style.cssText = 'position:fixed!important;top:0!important;left:0!important;"
    "width:100vw!important;height:100vh!important;z-index:2147483647!important;"
    "background:rgba(0,0,0,0.001)!important;cursor:wait!important;"
    "pointer-events:all!important;user-select:none!important;';"
    "document.documentElement.appendChild(shield);"
    "}"
    "})()"
)

UNSHIELD_JS = (
    "(() => {"
    "const shield = document.getElementById('__cdp_shield__');"
    "if (shield) shield.remove();"
    "})()"
)


def get_child_pids(parent_pid: int) -> set:
    """Get child process IDs via Toolhelp32Snapshot."""
    pids = {parent_pid}
    if sys.platform != "win32":
        return pids
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        TH32CS_SNAPPROCESS = 0x00000002  # Snapshot all processes
        h_snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if h_snap == -1 or h_snap == 0:
            return pids

        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_char * 260),
            ]

        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        if kernel32.Process32First(h_snap, ctypes.byref(entry)):
            entries = []
            while True:
                entries.append((entry.th32ProcessID, entry.th32ParentProcessID))
                if not kernel32.Process32Next(h_snap, ctypes.byref(entry)):
                    break
            kernel32.CloseHandle(h_snap)

            changed = True
            while changed:
                changed = False
                for pid, ppid in entries:
                    if ppid in pids and pid not in pids:
                        pids.add(pid)
                        changed = True
    except Exception:
        pass
    return pids


def get_browser_path(custom: str = "") -> str:
    candidates = [
        custom,
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return "chrome.exe"


def get_pid_from_port(port: int) -> int:
    try:
        out = subprocess.check_output("netstat -ano", shell=True).decode()
        port_str = f":{port}"
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and "LISTENING" in parts:
                local_addr = parts[1]
                if local_addr.endswith(port_str):
                    return int(parts[-1])
    except Exception:
        pass
    return None


def find_browser_hwnds_by_pid_or_port(pid: int = None, port: int = None, provider_name: str = "") -> list:
    if sys.platform != "win32":
        return []
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32

        target_pid = pid or (get_pid_from_port(port) if port else None)
        if not target_pid:
            return []
        pids = get_child_pids(target_pid)
        if not pids:
            return []

        found_hwnds = []
        my_pid = os.getpid()

        def enum_windows_callback(hwnd, extra):
            w_pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(w_pid))
            if w_pid.value == my_pid:
                return 1
            if w_pid.value not in pids:
                return 1

            buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, buf, 256)
            if buf.value != "Chrome_WidgetWin_1":
                return 1

            if hwnd not in found_hwnds:
                found_hwnds.append(hwnd)
            return 1

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
        return found_hwnds
    except Exception:
        return []


_saved_window_positions = {}


def set_window_visibility(provider_name: str = "", visible: bool = True, pid: int = None, port: int = None):
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        hwnds = find_browser_hwnds_by_pid_or_port(pid=pid, port=port, provider_name=provider_name)
        SW_SHOWNOACTIVATE = 4
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040

        for hwnd in hwnds:
            if visible:
                user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
                pos = _saved_window_positions.get(hwnd)
                if pos and pos[0] > -10000:
                    x, y, w, h = pos
                    user32.SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOACTIVATE | SWP_SHOWWINDOW)
            else:
                rect = wintypes.RECT()
                if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    w = rect.right - rect.left
                    h = rect.bottom - rect.top
                    if rect.left > -10000 and w > 0 and h > 0:
                        _saved_window_positions[hwnd] = (rect.left, rect.top, w, h)
                user32.SetWindowPos(hwnd, 0, -32000, -32000, 1024, 768, SWP_NOACTIVATE | SWP_SHOWWINDOW)
    except Exception:
        pass


def kill_browser(pid: int = None, port: int = None):
    target_pid = pid or (get_pid_from_port(port) if port else None)
    if target_pid:
        try:
            subprocess.run(f"taskkill /F /PID {target_pid} /T", shell=True, capture_output=True)
        except Exception:
            pass


def clean_response(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    text = text.strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith('“') and text.endswith('”')):
        text = text[1:-1].strip()
    return text


DEFAULT_PROMPT_TEMPLATE = (
    "You are an expert Visual Novel translator. Translate the following text from {srclang} to {tgtlang}:\n"
    "\u300c{content}\u300d\n"
    "Output ONLY the direct translation text without quotation marks, notes, or explanations."
)


def format_prompt(content: str, srclang_obj, tgtlang_obj, template: str = None) -> str:
    src_name = getattr(srclang_obj, "name", "Japanese")
    tgt_name = getattr(tgtlang_obj, "name", "Vietnamese")
    tmpl = (template or "").strip() or DEFAULT_PROMPT_TEMPLATE

    if "{content}" not in tmpl and "{sentence}" not in tmpl:
        tmpl = tmpl + "\n\u300c{content}\u300d"

    return (
        tmpl.replace("{content}", content)
        .replace("{sentence}", content)
        .replace("{srclang}", src_name)
        .replace("{tgtlang}", tgt_name)
        .replace("{src_lang}", src_name)
        .replace("{tgt_lang}", tgt_name)
    )


def is_port_listening(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def cdp_http_get_json(port: int, path: str, timeout: float = 2.0):
    """HTTP GET JSON request via raw socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect(("127.0.0.1", port))
            req = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\nUser-Agent: LunaTranslator-CDP\r\n\r\n"
            s.sendall(req.encode("ascii"))
            data = bytearray()
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data.extend(chunk)
                except Exception:
                    break
        idx = data.find(b"\r\n\r\n")
        if idx == -1:
            return None
        body_part = data[idx + 4:].decode("utf-8", errors="replace")
        return json.loads(body_part)
    except Exception:
        return None


def is_browser_alive_on_port(port: int) -> bool:
    """Check if debug port is listening."""
    if not is_port_listening(port):
        return False
    data = cdp_http_get_json(port, "/json/version", timeout=1.5)
    return data is not None and "Browser" in data


_browser_launch_lock = threading.RLock()


def ensure_browser_launched(debug_port: int, profile_name: str, chrome_path: str = "", target_url: str = "") -> tuple:
    """Ensure browser is running on debug port."""
    with _browser_launch_lock:
        if is_port_listening(debug_port):
            return None, debug_port

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "browser_profile"))
        os.makedirs(base_dir, exist_ok=True)
        profile_path = os.path.join(base_dir, profile_name)
        os.makedirs(profile_path, exist_ok=True)

        browser_exe = get_browser_path(chrome_path)
        cdp_log(f"Starting browser on port {debug_port} (profile={profile_name})")
        cmd = [
            browser_exe,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-restore-session-state",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=CalculateNativeWinOcclusion",
            "--disable-extensions",
            "--disable-default-apps"
        ]
        if target_url:
            cmd.append(target_url)
        flags = 0x00000008 if sys.platform == "win32" else 0
        proc = subprocess.Popen(cmd, creationflags=flags)
        assign_proc_to_job(proc)

        start_time = time.time()
        while time.time() - start_time < 15:
            if is_port_listening(debug_port):
                cdp_log(f"Browser ready on port {debug_port} (PID {getattr(proc, 'pid', None)})")
                return proc, debug_port
            time.sleep(0.4)
        cdp_log(f"WARNING: port {debug_port} not listening after 15s timeout")
        return proc, debug_port


def _close_tab(debug_port: int, tab_id: str):
    """Close browser tab by ID."""
    if not tab_id:
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect(("127.0.0.1", debug_port))
            req = f"GET /json/close/{tab_id} HTTP/1.1\r\nHost: 127.0.0.1:{debug_port}\r\nConnection: close\r\n\r\n"
            s.sendall(req.encode("ascii"))
            s.recv(1024)
    except Exception:
        pass


def connect_to_tab(debug_port: int, target_domain: str, target_url: str) -> str:
    """Connect or navigate to target domain tab."""
    target_tab = None
    start_wait = time.time()
    navigated = False

    while time.time() - start_wait < 15:
        try:
            tabs = cdp_http_get_json(debug_port, "/json/list", timeout=2.5)
            if not tabs or not isinstance(tabs, list):
                time.sleep(0.4)
                continue

            page_tabs = [t for t in tabs if t.get("type") == "page"]
            matched_tabs = [t for t in page_tabs if target_domain in t.get("url", "")]
            if matched_tabs:
                target_tab = matched_tabs[0]
                for extra in page_tabs:
                    if extra.get("id") != target_tab.get("id"):
                        _close_tab(debug_port, extra.get("id"))
                break

            if page_tabs:
                if not navigated:
                    target_tab = page_tabs[0]
                    ws_url = target_tab.get("webSocketDebuggerUrl")
                    if ws_url:
                        try:
                            temp_ws = SimpleWebSocket(ws_url, timeout=2.5)
                            temp_ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": target_url}}))
                            temp_ws.recv()
                            temp_ws.close()
                            navigated = True
                        except Exception:
                            pass
                    for extra in page_tabs[1:]:
                        _close_tab(debug_port, extra.get("id"))
                time.sleep(0.4)
                continue
        except Exception:
            pass
        time.sleep(0.4)

    if not target_tab:
        cdp_log(f"Could not locate browser tab for {target_domain} on port {debug_port}")
        raise RuntimeError(f"Could not locate a browser tab for {target_domain} on port {debug_port}")

    ws_url = target_tab.get("webSocketDebuggerUrl")
    if not ws_url:
        raise RuntimeError(f"Browser tab lacks webSocketDebuggerUrl for {target_domain}")

    return ws_url


def close_duplicate_tabs(debug_port: int, keep_tab_id: str):
    """Close extra page tabs."""
    if not keep_tab_id:
        return
    try:
        tabs = cdp_http_get_json(debug_port, "/json/list", timeout=1.5)
        if not tabs or not isinstance(tabs, list):
            return
        for t in tabs:
            if t.get("type") == "page" and t.get("id") != keep_tab_id:
                _close_tab(debug_port, t.get("id"))
    except Exception:
        pass
# =========================================================================
# Web UI Maintenance & DOM Selector Configuration
# =========================================================================
# When AI web interfaces (DeepSeek, ChatGPT, Gemini) change:
# 1. Update selectors directly in: defaultconfig/cdp_selectors.json
#    (Changes take effect immediately without modifying Python code).
# 2. To inspect and test selectors in browser DevTools Console (F12):
#    Boolean(document.querySelector('your_new_selector'))
# 3. Key selector fields:
#    - input_selector:     Target chat textbox (textarea or [contenteditable='true']).
#    - send_btn_selector:  Target send/submit button.
#    - stop_btn_selector:  Target stop response button during streaming.
#    - msg_selector:       Target AI response message elements.
#    - send_key_modifiers: Key combo to trigger send (0 = Enter, 2 = Ctrl+Enter).
# =========================================================================

DEFAULT_SELECTORS = {
    "chatgpt": {
        "name": "ChatGPT Web",
        "domain": "chatgpt.com",
        "url": "https://chatgpt.com/",
        "profile": "chatgpt_profile",
        "default_port": 9223,
        "input_selector": "#prompt-textarea, [contenteditable='true'], textarea:not([class*='fallback'])",
        "send_btn_selector": "#composer-submit-button, button[data-testid='send-button'], button[aria-label*='Send' i], button[aria-label*='Gửi' i], button.wm-composer-submitButton, button[type='submit']",
        "stop_btn_selector": "button[data-testid='stop-button'], button[aria-label*='Stop' i]",
        "msg_selector": "[data-message-author-role='assistant'], article [data-message-author-role='assistant'], div[class*='messageCopy'], .markdown",
        "send_key_modifiers": 0
    },
    "gemini": {
        "name": "Gemini Web",
        "domain": "gemini.google.com",
        "url": "https://gemini.google.com/app",
        "profile": "gemini_profile",
        "default_port": 9224,
        "input_selector": ".ql-editor, rich-textarea div[contenteditable='true'], [contenteditable='true']",
        "send_btn_selector": ".send-button-container button, button[aria-label*='Send message' i], button[aria-label*='Gửi' i], button.send-button",
        "stop_btn_selector": "button[aria-label*='Stop' i], .stop-button, mat-icon[data-mat-icon-name='stop']",
        "msg_selector": "model-response, [class*='model-response'], message-content",
        "send_key_modifiers": 2
    },
    "deepseek": {
        "name": "DeepSeek Web",
        "domain": "chat.deepseek.com",
        "url": "https://chat.deepseek.com/",
        "profile": "deepseek_profile",
        "default_port": 9222,
        "input_selector": "textarea.chat-input, textarea[placeholder*='DeepSeek'], textarea",
        "send_btn_selector": "div[class*='ds-button--primary'][class*='ds-button--circle']:not([class*='floating']):not([class*='disabled']), div[class*='ds-button--primary']:not([class*='floating']), div[class*='send-button'], button[type='submit']",
        "stop_btn_selector": "button[aria-label*='Stop' i], button[aria-label*='Dừng' i]",
        "msg_selector": ".ds-markdown, article",
        "send_key_modifiers": 0
    }
}


def load_selectors(provider_key: str) -> dict:
    """Load selectors configuration."""
    cfg_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "defaultconfig", "cdp_selectors.json"
    ))
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                all_cfg = json.load(f)
                if provider_key in all_cfg:
                    return all_cfg[provider_key]
        except Exception:
            pass
    return DEFAULT_SELECTORS.get(provider_key, {})


def diagnose_selectors(cdp_session, selectors: dict) -> dict:
    """Verify selector match on current page."""
    report = {}
    for key in ("input_selector", "send_btn_selector", "msg_selector"):
        sel = selectors.get(key, "")
        if sel:
            found = cdp_session.evaluate_js(f"Boolean(document.querySelector({json.dumps(sel)}))")
            report[key] = bool(found)
    return report


class CDPSession:

    def __init__(self, provider_name: str = ""):
        self.provider_name = provider_name
        self.ws = None
        self._msg_id = 0
        self._lock = threading.Lock()

    def connect(self, ws_url: str, timeout: float = 30):
        self.disconnect()
        self.ws = SimpleWebSocket(ws_url, timeout=timeout)
        self.execute("Page.enable")
        self.execute("Runtime.enable")
        time.sleep(0.3)
        cdp_log(f"[{self.provider_name}] CDP connected")

    def disconnect(self):
        with self._lock:
            if self.ws:
                try:
                    self.ws.close()
                except Exception:
                    pass
                self.ws = None

    @property
    def connected(self) -> bool:
        return self.ws is not None

    def execute(self, method: str, params: dict = None, timeout: float = 25.0) -> dict:
        """Send CDP command and return result."""
        with self._lock:
            if not self.ws:
                raise ConnectionResetError(f"CDP WebSocket for {self.provider_name} is not connected.")
            self._msg_id += 1
            call_id = self._msg_id
            cmd = {"id": call_id, "method": method, "params": params or {}}
            self.ws.send(json.dumps(cmd))
            start_t = time.time()
            while time.time() - start_t < timeout:
                raw = self.ws.recv()
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                except Exception:
                    continue
                if data.get("id") == call_id:
                    if "error" in data:
                        raise RuntimeError(f"CDP Error ({method}): {data['error']}")
                    return data.get("result", {})
            cdp_log(f"[{self.provider_name}] CDP call {method} timed out (call_id={call_id})")
            raise TimeoutError(f"CDP call {method} timed out on {self.provider_name}.")

    def evaluate_js(self, expression: str, await_promise: bool = False):
        for _ in range(6):
            try:
                res = self.execute("Runtime.evaluate", {
                    "expression": expression,
                    "returnByValue": True,
                    "awaitPromise": await_promise
                })
                val = res.get("result", {})
                return val.get("value")
            except Exception as e:
                err_str = str(e).lower()
                if "execution context" in err_str or "context was destroyed" in err_str or "-32000" in err_str:
                    time.sleep(0.2)
                    continue
                raise
        return None

    def is_alive(self, debug_port: int) -> bool:
        if not self.ws:
            return False
        try:
            return self.evaluate_js("1+1") == 2
        except Exception:
            return False

    def disable_interaction(self):
        try:
            self.evaluate_js(SHIELD_JS)
        except Exception:
            pass

    def enable_interaction(self):
        try:
            self.evaluate_js(UNSHIELD_JS)
        except Exception:
            pass

try:
    from qtsymbols import (
        QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton,
        QMessageBox, QApplication, QLabel, QLineEdit, Qt, QFileDialog
    )
except ImportError:
    QWidget = object


class DOMToolsWidget(QWidget):
    """DOM selector settings panel widget."""
    def __init__(self, _dict, key, provider_key="chatgpt"):
        super().__init__()
        self._dict = _dict or {}
        self._key = key
        self.provider_key = provider_key

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 4, 0, 4)
        main_layout.setSpacing(8)

        # --- Header row: Title + Switch ---
        header_layout = QHBoxLayout()
        header_label = QLabel("Advanced Mode (Self-Maintenance)")
        header_label.setStyleSheet("font-weight: bold; font-size: 11pt;")

        init_checked = bool(self._dict.get("use_custom_dom", False))
        try:
            from gui.usefulwidget import MySwitch
            self.switch = MySwitch(sign=init_checked)
        except Exception:
            from qtsymbols import QCheckBox
            self.switch = QCheckBox()
            self.switch.setChecked(init_checked)
        self.switch.setToolTip("Toggle to show/hide and enable custom DOM selectors")

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.switch)
        main_layout.addLayout(header_layout)

        # --- Subtitle hint ---
        hint_label = QLabel("Enable this only if the AI website updated its UI layout and broke translations.")
        hint_label.setStyleSheet("color: gray; font-size: 9pt;")
        main_layout.addWidget(hint_label)

        # --- Collapsible Container ---
        self.container = QWidget()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 6, 0, 4)
        container_layout.setSpacing(8)

        # 1. Guideline Box
        guide_text = (
            "<b>📖 How to get CSS Selectors via DevTools (F12):</b><br>"
            "1. Press <b>F12</b> on the web translation page (or Right-Click → <i>Inspect</i>).<br>"
            "2. Click the <b>Inspect Element Icon</b> ↖ (top-left of DevTools, or Ctrl+Shift+C).<br>"
            "3. Click on the target element (Input box, Send button, or AI reply bubble).<br>"
            "4. In the HTML Elements tree, right-click the highlighted tag → <b>Copy → Copy selector</b>.<br>"
            "5. Paste the selector into the corresponding field below.<br>"
            "<i>• Tips: You can use IDs (<code>#id</code>), classes (<code>.class</code>), or attributes (<code>button[type='submit']</code>).</i><br>"
            "<i>• Leave any field empty to fall back to built-in system default.</i>"
        )
        self.guide_label = QLabel(guide_text)
        self.guide_label.setTextFormat(Qt.TextFormat.RichText)
        self.guide_label.setWordWrap(True)
        self.guide_label.setStyleSheet(
            "padding: 8px 10px; border-radius: 5px; "
            "border: 1px solid rgba(128, 128, 128, 0.35); "
            "background-color: rgba(128, 128, 128, 0.08); font-size: 9pt;"
        )
        container_layout.addWidget(self.guide_label)

        # 2. Form Layout for 4 Selectors
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 4, 0, 4)
        form_layout.setSpacing(6)

        from translator.cdp_core import DEFAULT_SELECTORS
        p_sel = DEFAULT_SELECTORS.get(self.provider_key, {})

        def_in = p_sel.get("input_selector", "")
        def_snd = p_sel.get("send_btn_selector", "")
        def_msg = p_sel.get("msg_selector", "")
        def_stp = p_sel.get("stop_btn_selector", "")

        self.edit_input = QLineEdit(self._dict.get("dom_input_selector") or def_in)
        self.edit_input.setPlaceholderText(def_in)

        self.edit_send = QLineEdit(self._dict.get("dom_send_btn_selector") or def_snd)
        self.edit_send.setPlaceholderText(def_snd)

        self.edit_msg = QLineEdit(self._dict.get("dom_msg_selector") or def_msg)
        self.edit_msg.setPlaceholderText(def_msg)

        self.edit_stop = QLineEdit(self._dict.get("dom_stop_btn_selector") or def_stp)
        self.edit_stop.setPlaceholderText(def_stp)

        form_layout.addRow("Input Box Selector:", self.edit_input)
        form_layout.addRow("Send Button Selector:", self.edit_send)
        form_layout.addRow("Message Selector:", self.edit_msg)
        form_layout.addRow("Stop Button Selector:", self.edit_stop)
        container_layout.addLayout(form_layout)

        # 3. Action Buttons (Row 1: Save as Default, Reset Default)
        row1 = QHBoxLayout()
        self.btn_save = QPushButton("💾 Save as Default")
        self.btn_save.setToolTip("Save current custom selectors as system default in cdp_selectors.json")
        self.btn_save.clicked.connect(self.on_save_as_default)

        self.btn_reset = QPushButton("🔄 Reset to Default")
        self.btn_reset.setToolTip("Reset selector input fields to factory defaults")
        self.btn_reset.clicked.connect(self.on_reset_default)

        row1.addWidget(self.btn_save)
        row1.addWidget(self.btn_reset)
        container_layout.addLayout(row1)

        # 4. Sharing Buttons (Row 2: Export JSON File, Import JSON File)
        row2 = QHBoxLayout()
        self.btn_copy = QPushButton("📤 Export JSON File")
        self.btn_copy.setToolTip("Export selector settings to a .json file to easily share with others")
        self.btn_copy.clicked.connect(self.on_copy_json)

        self.btn_import = QPushButton("📥 Import JSON File")
        self.btn_import.setToolTip("Import selector settings from a .json file")
        self.btn_import.clicked.connect(self.on_import_json)

        row2.addWidget(self.btn_copy)
        row2.addWidget(self.btn_import)
        container_layout.addLayout(row2)

        main_layout.addWidget(self.container)

        # Initial visibility
        self.container.setVisible(init_checked)
        self.switch.clicked.connect(self.on_toggle_switch)

    def on_toggle_switch(self, *args):
        self.container.setVisible(self.switch.isChecked())
        win = self.window()
        if win:
            win.adjustSize()

    def updateValues(self):
        """Save selector configuration."""
        return {
            "use_custom_dom": self.switch.isChecked(),
            "dom_input_selector": self.edit_input.text().strip(),
            "dom_send_btn_selector": self.edit_send.text().strip(),
            "dom_msg_selector": self.edit_msg.text().strip(),
            "dom_stop_btn_selector": self.edit_stop.text().strip(),
        }

    def on_save_as_default(self):
        input_sel = self.edit_input.text().strip()
        send_sel = self.edit_send.text().strip()
        msg_sel = self.edit_msg.text().strip()
        stop_sel = self.edit_stop.text().strip()

        sel_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "defaultconfig", "cdp_selectors.json")
        )
        try:
            with open(sel_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        cfg = data.setdefault(self.provider_key, {})
        if input_sel:
            cfg["input_selector"] = input_sel
        if send_sel:
            cfg["send_btn_selector"] = send_sel
        if msg_sel:
            cfg["msg_selector"] = msg_sel
        if stop_sel:
            cfg["stop_btn_selector"] = stop_sel

        try:
            with open(sel_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(
                self,
                "Saved as Default",
                f"Successfully saved selectors for {self.provider_key.upper()} as system default in cdp_selectors.json!",
            )
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save default selectors: {e}")

    def on_reset_default(self):
        from translator.cdp_core import DEFAULT_SELECTORS
        factory = DEFAULT_SELECTORS.get(self.provider_key, {})
        if not factory:
            return

        self.edit_input.setText(factory.get("input_selector", ""))
        self.edit_send.setText(factory.get("send_btn_selector", ""))
        self.edit_msg.setText(factory.get("msg_selector", ""))
        self.edit_stop.setText(factory.get("stop_btn_selector", ""))

        QMessageBox.information(
            self,
            "Reset Selectors",
            f"Selectors for {self.provider_key.upper()} have been reset to factory defaults!",
        )

    def on_copy_json(self):
        default_filename = f"{self.provider_key}_dom_config.json"
        try:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save DOM Config File",
                default_filename,
                "JSON Files (*.json);;All Files (*.*)"
            )
            if not save_path:
                return  # Cancelled: do nothing, do not touch clipboard or show popup

            data = {
                "provider": self.provider_key,
                "input_selector": self.edit_input.text().strip(),
                "send_btn_selector": self.edit_send.text().strip(),
                "msg_selector": self.edit_msg.text().strip(),
                "stop_btn_selector": self.edit_stop.text().strip(),
            }
            json_str = json.dumps(data, ensure_ascii=False, indent=2)

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Configuration exported successfully to:\n{save_path}",
            )
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export file: {e}")

    def on_import_json(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select DOM Config File to Import",
                "",
                "JSON Files (*.json);;All Files (*.*)"
            )
            if not file_path:
                return  # Cancelled: do nothing, do not touch clipboard or show popup

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Read File Error", f"Failed to read file: {e}")
            return

        if not isinstance(data, dict):
            QMessageBox.warning(self, "Import Failed", "Selected file is not a valid JSON configuration object.")
            return

        matched = False
        if "input_selector" in data and data["input_selector"]:
            self.edit_input.setText(str(data["input_selector"]))
            matched = True
        if "send_btn_selector" in data and data["send_btn_selector"]:
            self.edit_send.setText(str(data["send_btn_selector"]))
            matched = True
        if "msg_selector" in data and data["msg_selector"]:
            self.edit_msg.setText(str(data["msg_selector"]))
            matched = True
        if "stop_btn_selector" in data and data["stop_btn_selector"]:
            self.edit_stop.setText(str(data["stop_btn_selector"]))
            matched = True

        if matched:
            self.switch.setChecked(True)
            self.on_toggle_switch(True)
            QMessageBox.information(
                self,
                "Import Successful",
                f"Successfully imported selectors for {self.provider_key.upper()} from file:\n{os.path.basename(file_path)}\n\nCustom DOM Mode has been enabled.",
            )
        else:
            QMessageBox.warning(
                self,
                "Import Error",
                "JSON file does not contain recognized selector keys:\n(input_selector, send_btn_selector, msg_selector)",
            )
