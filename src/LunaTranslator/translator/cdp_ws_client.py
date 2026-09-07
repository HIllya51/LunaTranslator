import time
import json
import collections
import threading
import urllib.parse
from translator.basetranslator import basetrans, GptTextWithDict
from language import Languages

from translator.cdp_core import (
    close_duplicate_tabs,
    CDPSession,
    TranslationTask,
    load_selectors,
    ensure_browser_launched,
    connect_to_tab,
    set_window_visibility,
    kill_browser,
    format_prompt,
    clean_response,
)


class BaseCDPTranslator(basetrans):
    PROVIDER_KEY = ""

    def langmap(self):
        return Languages.createenglishlangmap()

    def init(self):
        self.selectors = load_selectors(self.PROVIDER_KEY)
        self.provider_name = self.selectors.get("name", self.PROVIDER_KEY.capitalize() + " Web")
        self.profile_name = self.selectors.get("profile", f"{self.PROVIDER_KEY}_profile")
        self.send_key_modifiers = self.selectors.get("send_key_modifiers", 0)

        self._update_target_endpoint()

        cfg_port = self.config.get("debugport")
        self.debug_port = int(cfg_port) if cfg_port else self.selectors.get("default_port", 9222)

        self.cdp = CDPSession(self.provider_name)
        self.is_ready = False
        self.browser_proc = None
        self.task_queue = collections.deque()
        self.queue_lock = threading.Lock()
        self.max_queue_size = 3
        self._current_window_visible = None
        self._connect_lock = threading.Lock()
        self.queue_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._queue_worker, daemon=True)
        self.worker_thread.start()
        self.start_game_watcher()

    def _update_target_endpoint(self):
        custom = self.config.get("custom_url", "").strip()
        if custom:
            self.target_url = custom
            parsed = urllib.parse.urlparse(custom)
            self.target_domain = parsed.netloc or parsed.path
        else:
            self.target_url = self.selectors.get("url", "")
            self.target_domain = self.selectors.get("domain", "")

    def warmup(self):
        if not getattr(self, "using", True):
            return
        def _bg():
            try:
                if not getattr(self, "using", True):
                    return
                self.connect_cdp()
                self.wait_for_ready_and_login(timeout_sec=15)
            except Exception as e:
                print(f"[{self.provider_name}] Warmup notice: {e}")
        threading.Thread(target=_bg, daemon=True).start()

    def start_game_watcher(self):
        def _watch():
            import gobject
            warmed_gameuid = None
            while True:
                try:
                    if not getattr(self, "using", True):
                        time.sleep(2.0)
                        continue
                    current_game = getattr(gobject.base, "gameuid", None) or getattr(gobject.base, "hwnd", None)
                    if current_game and current_game != warmed_gameuid:
                        warmed_gameuid = current_game
                        self.warmup()
                    elif not current_game:
                        warmed_gameuid = None
                except Exception:
                    pass
                time.sleep(1.0)
        threading.Thread(target=_watch, daemon=True).start()

    def close_browser(self):
        if not self.cdp.connected and not self.browser_proc:
            return
        try:
            if self.cdp.is_alive(self.debug_port):
                self.cdp.execute("Browser.close", timeout=2.0)
        except Exception:
            pass
        self.cdp.disconnect()
        self.is_ready = False
        proc_pid = getattr(self.browser_proc, "pid", None)
        kill_browser(pid=proc_pid, port=self.debug_port)
        self.browser_proc = None
        self._current_window_visible = None

    def __del__(self):
        try:
            self.close_browser()
        except Exception:
            pass

    def connect_cdp(self):
        with self._connect_lock:
            if self.cdp.is_alive(self.debug_port):
                return
            proc, port = ensure_browser_launched(self.debug_port, self.profile_name, self.config.get("chromepath", ""), self.target_url)
            self.debug_port = port
            if proc:
                self.browser_proc = proc
            ws_url = connect_to_tab(self.debug_port, self.target_domain, self.target_url)
            self.cdp.connect(ws_url)
            for _ in range(15):
                try:
                    cur_url = self.cdp.evaluate_js("window.location.href") or ""
                    if self.target_domain in cur_url:
                        break
                    elif "about:blank" in cur_url or "chrome://" in cur_url or not cur_url:
                        self.cdp.execute("Page.navigate", {"url": self.target_url})
                except Exception:
                    pass
                time.sleep(0.4)

            try:
                keep_id = ws_url.split('/')[-1] if ws_url else ""
                close_duplicate_tabs(self.debug_port, keep_id)
            except Exception:
                pass

            target_visible = bool(self.config.get("show_browser", True))
            proc_pid = getattr(self.browser_proc, "pid", None)
            if not target_visible:
                set_window_visibility(provider_name=self.provider_name, visible=target_visible, pid=proc_pid, port=self.debug_port)
            self._current_window_visible = target_visible

    def wait_for_ready_and_login(self, timeout_sec=25):
        self._refresh_selectors()
        input_sel = json.dumps(self.selectors.get("input_selector", "textarea"))
        ready_js = (
            "(() => {"
            f"const candidates = Array.from(document.querySelectorAll({input_sel}));"
            "const el = candidates.find(c => (c.offsetWidth > 0 || c.offsetHeight > 0) && !c.className.includes('fallback')) || candidates[0];"
            "if (el) {"
            "const s = window.getComputedStyle(el);"
            "if (s.display !== 'none' && s.visibility !== 'hidden') return 'ready';"
            "}"
            "const url = window.location.href.toLowerCase();"
            "if (url.includes('/login') || url.includes('/auth/') || url.includes('/sign_in')) return 'login_needed';"
            "return 'waiting';"
            "})()"
        )
        start = time.time()
        while time.time() - start < timeout_sec:
            try:
                status = self.cdp.evaluate_js(ready_js)
                if status == "ready":
                    self.is_ready = True
                    self.cdp.evaluate_js(
                        "(() => {"
                        f"const candidates = Array.from(document.querySelectorAll({input_sel}));"
                        "const el = candidates.find(c => (c.offsetWidth > 0 || c.offsetHeight > 0) && !c.className.includes('fallback')) || candidates[0];"
                        "if (el) {"
                        "if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') el.value = '';"
                        "else el.innerHTML = '<p><br></p>';"
                        "el.dispatchEvent(new Event('input', { bubbles: true }));"
                        "}"
                        "})()"
                    )
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        return False

    def wait_until_idle(self, timeout=6.0):
        stop_sel_val = self.selectors.get("stop_btn_selector", "")
        if not stop_sel_val:
            return True
        stop_sel = json.dumps(stop_sel_val)
        stop_js = f"Boolean(document.querySelector({stop_sel}))"
        start = time.time()
        while time.time() - start < timeout:
            try:
                if not self.cdp.evaluate_js(stop_js):
                    return True
            except Exception:
                pass
            time.sleep(0.3)
        return True

    def _queue_worker(self):
        while True:
            if not self.using:
                if self.cdp.connected or self.browser_proc:
                    self.close_browser()
                while not self.using:
                    time.sleep(1.0)
                continue

            target_visible = bool(self.config.get("show_browser", True))
            if self._current_window_visible is not None and self._current_window_visible != target_visible:
                proc_pid = getattr(self.browser_proc, "pid", None)
                set_window_visibility(provider_name=self.provider_name, visible=target_visible, pid=proc_pid, port=self.debug_port)
                self._current_window_visible = target_visible

            self.queue_event.wait(timeout=1.0)
            self.queue_event.clear()
            with self.queue_lock:
                if self.task_queue:
                    self.queue_event.set()

            if not self.using:
                continue

            while True:
                with self.queue_lock:
                    task = self.task_queue.popleft() if self.task_queue else None
                if not task:
                    break
                if task.cancelled:
                    task.done_event.set()
                    continue

                task_age = time.time() - getattr(task, "created_at", time.time())
                if task_age > 20.0:
                    print(f"[{self.provider_name}] Dropping stale queued task ({task_age:.1f}s old)")
                    task.cancelled = True
                    task.result = ""
                    task.done_event.set()
                    continue

                try:
                    alive = self.cdp.is_alive(self.debug_port)
                    if not alive:
                        self.cdp.disconnect()
                        self.is_ready = False
                        try:
                            self.connect_cdp()
                        except Exception as e:
                            print(f"[{self.provider_name}] Connect error: {e}")
                            task.result = ""
                            continue

                    if not self.is_ready:
                        ready_ok = False
                        try:
                            ready_ok = self.wait_for_ready_and_login(timeout_sec=3)
                        except Exception as e:
                            print(f"[{self.provider_name}] Not ready: {e}")

                        if not ready_ok:
                            task.result = ""
                            continue

                    self.cdp.disable_interaction()
                    self.wait_until_idle()
                    if task.cancelled:
                        continue
                    task.result = self._do_translate(task.content, task.srclang_obj, task.tgtlang_obj)
                except Exception as e:
                    print(f"[{self.provider_name}] Worker error: {e}")
                    task.result = ""
                finally:
                    task.done_event.set()
                    with self.queue_lock:
                        if not self.task_queue:
                            self.cdp.enable_interaction()


    def _focus_input(self):
        input_sel = json.dumps(self.selectors.get("input_selector", "textarea"))
        js = (
            "(() => {"
            f"const candidates = Array.from(document.querySelectorAll({input_sel}));"
            "const el = candidates.find(c => (c.offsetWidth > 0 || c.offsetHeight > 0) && !c.className.includes('fallback')) || candidates[0];"
            "if (el) {"
            "el.focus();"
            "try { el.click(); } catch(e) {}"
            "if (el.isContentEditable) {"
            "const sel = window.getSelection();"
            "if (sel) {"
            "const r = document.createRange();"
            "r.selectNodeContents(el);"
            "r.collapse(false);"
            "sel.removeAllRanges();"
            "sel.addRange(r);"
            "}"
            "} else if (el.setSelectionRange) {"
            "const len = el.value ? el.value.length : 0;"
            "el.setSelectionRange(len, len);"
            "}"
            "return true;"
            "}"
            "return false;"
            "})()"
        )
        for _ in range(5):
            if self.cdp.evaluate_js(js):
                return True
            time.sleep(0.12)
        return False

    def _clear_input(self):
        input_sel = json.dumps(self.selectors.get("input_selector", "textarea"))
        js = (
            "(() => {"
            f"const candidates = Array.from(document.querySelectorAll({input_sel}));"
            "const el = candidates.find(c => (c.offsetWidth > 0 || c.offsetHeight > 0) && !c.className.includes('fallback')) || candidates[0];"
            "if (el) {"
            "el.focus();"
            "try { document.execCommand('selectAll', false, null); } catch(e) {}"
            "try { document.execCommand('delete', false, null); } catch(e) {}"
            "if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') el.value = '';"
            "else el.innerHTML = '<p><br></p>';"
            "el.dispatchEvent(new Event('input', { bubbles: true }));"
            "}"
            "})()"
        )
        self.cdp.evaluate_js(js)

    def _verify_input(self):
        input_sel = json.dumps(self.selectors.get("input_selector", "textarea"))
        js = (
            "(() => {"
            f"const candidates = Array.from(document.querySelectorAll({input_sel}));"
            "const el = candidates.find(c => (c.offsetWidth > 0 || c.offsetHeight > 0) && !c.className.includes('fallback')) || candidates[0];"
            "if (!el) return false;"
            "const val = (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') ? el.value : (el.innerText || el.textContent);"
            "return Boolean(val && val.trim().length > 0);"
            "})()"
        )
        return self.cdp.evaluate_js(js)

    def _send_message(self):
        send_sel_val = self.selectors.get("send_btn_selector", "")
        btn_clicked = False
        if send_sel_val:
            send_sel = json.dumps(send_sel_val)
            send_js = (
                "(() => {"
                f"const btn = document.querySelector({send_sel});"
                "if (btn && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true' && !btn.className.includes('disabled') && !btn.className.includes('floating')) {"
                "btn.click();"
                "return true;"
                "}"
                "return false;"
                "})()"
            )
            # Allow reactive frameworks (React/ProseMirror) up to 0.8s to mount the active send button
            start_t = time.time()
            while time.time() - start_t < 0.8:
                if self.cdp.evaluate_js(send_js):
                    btn_clicked = True
                    break
                time.sleep(0.08)

        time.sleep(0.12)
        if not btn_clicked or self._verify_input():
            self._focus_input()
            self.cdp.execute("Input.dispatchKeyEvent", {
                "type": "rawKeyDown",
                "windowsVirtualKeyCode": 13,
                "modifiers": self.send_key_modifiers,
                "unmodifiedText": "\r",
                "text": "\r"
            })
            self.cdp.execute("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "windowsVirtualKeyCode": 13,
                "modifiers": self.send_key_modifiers,
                "unmodifiedText": "\r",
                "text": "\r"
            })
            time.sleep(0.15)
            if self._verify_input():
                self._focus_input()
                self.cdp.execute("Input.dispatchKeyEvent", {
                    "type": "rawKeyDown",
                    "windowsVirtualKeyCode": 13,
                    "modifiers": self.send_key_modifiers,
                    "unmodifiedText": "\r",
                    "text": "\r"
                })
                self.cdp.execute("Input.dispatchKeyEvent", {
                    "type": "keyUp",
                    "windowsVirtualKeyCode": 13,
                    "modifiers": self.send_key_modifiers,
                    "unmodifiedText": "\r",
                    "text": "\r"
                })

    def _refresh_selectors(self):
        base_sel = load_selectors(self.PROVIDER_KEY)
        self.selectors = dict(base_sel)
        if self.config.get("use_custom_dom", False):
            for k in ["input_selector", "send_btn_selector", "msg_selector", "stop_btn_selector"]:
                val = (self.config.get(f"dom_{k}") or "").strip()
                if val:
                    self.selectors[k] = val

    def build_prompt(self, content: str, srclang_obj, tgtlang_obj) -> str:
        if self.config.get("use_custom_prompt", False) and self.config.get("custom_prompt", "").strip():
            return format_prompt(
                content,
                srclang_obj,
                tgtlang_obj,
                template=self.config.get("custom_prompt", "")
            )
        return format_prompt(content, srclang_obj, tgtlang_obj)

    def _do_translate(self, content, srclang_obj, tgtlang_obj):
        self._refresh_selectors()
        full_prompt = self.build_prompt(content, srclang_obj, tgtlang_obj)
        mq = json.dumps(self.selectors.get("msg_selector", "article"))

        prev_state = self.cdp.evaluate_js(
            "(() => {"
            f"const msgs = document.querySelectorAll({mq});"
            "return { count: msgs.length, last_text: msgs.length > 0 ? msgs[msgs.length - 1].innerText.trim() : '' };"
            "})()"
        ) or {}
        prev_count = prev_state.get("count", 0)
        prev_text = prev_state.get("last_text", "")

        self._focus_input()
        self._clear_input()
        time.sleep(0.06)

        # Insert text via execCommand
        input_sel = json.dumps(self.selectors.get("input_selector", "textarea"))
        insert_js = (
            "(() => {"
            f"const candidates = Array.from(document.querySelectorAll({input_sel}));"
            "const el = candidates.find(c => (c.offsetWidth > 0 || c.offsetHeight > 0) && !c.className.includes('fallback')) || candidates[0];"
            "if (!el) return false;"
            "el.focus();"
            "try { document.execCommand('selectAll', false, null); } catch(e) {}"
            f"const ok = document.execCommand('insertText', false, {json.dumps(full_prompt)});"
            "const val = (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') ? el.value : (el.innerText || el.textContent);"
            "if (!val || val.trim().length === 0) {"
            f"    if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') el.value = {json.dumps(full_prompt)};"
            f"    else el.innerText = {json.dumps(full_prompt)};"
            "    el.dispatchEvent(new Event('input', { bubbles: true }));"
            "    el.dispatchEvent(new Event('change', { bubbles: true }));"
            "}"
            "return true;"
            "})()"
        )
        self.cdp.evaluate_js(insert_js)
        time.sleep(0.12)

        if not self._verify_input():
            self._focus_input()
            self.cdp.execute("Input.insertText", {"text": full_prompt})
            time.sleep(0.15)

        self._send_message()
        time.sleep(1.0)

        extract_js = (
            "(() => {"
            f"const msgs = document.querySelectorAll({mq});"
            "return msgs.length > 0 ? msgs[msgs.length - 1].innerText.trim() : '';"
            "})()"
        )
        return self._poll_response(extract_js, prev_count, prev_text)

    def _poll_response(self, extract_js, prev_count, prev_text, max_wait=30):
        mq = json.dumps(self.selectors.get("msg_selector", "article"))
        stop_sel_val = self.selectors.get("stop_btn_selector", "")
        stop_sel = json.dumps(stop_sel_val)
        stop_js = f"Boolean(document.querySelector({stop_sel}))" if stop_sel_val else "false"

        start = time.time()
        last_text = ""
        unchanged = 0
        detected = False

        while time.time() - start < max_wait:
            is_gen = bool(self.cdp.evaluate_js(stop_js))
            cur_text = (self.cdp.evaluate_js(extract_js) or "").strip()
            cur_count = self.cdp.evaluate_js(f"document.querySelectorAll({mq}).length") or 0

            if is_gen or (cur_count > prev_count) or (cur_text and cur_text != prev_text):
                detected = True
            if detected:
                if cur_text and cur_text != prev_text:
                    if cur_text == last_text:
                        unchanged += 1
                    else:
                        unchanged = 0
                        last_text = cur_text
                    if not is_gen and unchanged >= 2:
                        break
                elif not is_gen and (time.time() - start > 8.0):
                    break
            if not detected and (time.time() - start > 8.0):
                break
            time.sleep(0.4)

        raw = (self.cdp.evaluate_js(extract_js) or last_text or "").strip()
        return "" if raw == prev_text else clean_response(raw)

    def translate(self, content):
        if isinstance(content, GptTextWithDict):
            content = content.parsedtext or content.rawtext
        content = str(content).strip() if content else ""
        if not content:
            return ""
        task = TranslationTask(content, self.srclang_1, self.tgtlang_1)
        with self.queue_lock:
            while len(self.task_queue) >= self.max_queue_size:
                dropped = self.task_queue.popleft()
                dropped.cancelled = True
                dropped.done_event.set()
            self.task_queue.append(task)
            self.queue_event.set()
        if not task.done_event.wait(timeout=25.0):
            task.cancelled = True
            print(f"[{self.provider_name}] Translation timed out for: {content[:50]}...")
        return task.result
