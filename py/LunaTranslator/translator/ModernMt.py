import requests, re, hashlib
from translator.basetranslator import basetrans
import time, urllib


class Tse:
    def __init__(self):
        self.author = "Ulion.Tse"
        self.begin_time = time.time()
        self.default_session_freq = int(1e3)
        self.default_session_seconds = 1.5e3
        self.transform_en_translator_pool = ("Itranslate", "Lingvanex", "MyMemory")
        self.auto_pool = (
            "auto",
            "detect",
            "auto-detect",
        )
        self.zh_pool = (
            "zh",
            "zh-CN",
            "zh-CHS",
            "zh-Hans",
            "zh-Hans_CN",
            "cn",
            "chi",
        )

    @staticmethod
    def get_headers(
        host_url: str,
        if_api: bool = False,
        if_referer_for_host: bool = True,
        if_ajax_for_api: bool = True,
        if_json_for_api: bool = False,
        if_multipart_for_api: bool = False,
        if_http_override_for_api: bool = False,
    ) -> dict:

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        url_path = urllib.parse.urlparse(host_url).path
        host_headers = {
            "Referer" if if_referer_for_host else "Host": host_url,
            "User-Agent": user_agent,
        }
        api_headers = {
            "Origin": host_url.split(url_path)[0] if url_path else host_url,
            "Referer": host_url,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": user_agent,
        }
        if if_api and not if_ajax_for_api:
            api_headers.pop("X-Requested-With")
            api_headers.update({"Content-Type": "text/plain"})
        if if_api and if_json_for_api:
            api_headers.update({"Content-Type": "application/json"})
        if if_api and if_multipart_for_api:
            api_headers.pop("Content-Type")
        if if_api and if_http_override_for_api:
            api_headers.update({"X-HTTP-Method-Override": "GET"})
        return host_headers if not if_api else api_headers


class ModernMt(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://www.modernmt.com/translate"
        self.api_url = "https://webapi.modernmt.com/translate"
        self.language_url = "https://www.modernmt.com/scripts/app.bundle.js"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url,
            if_api=True,
            if_json_for_api=True,
            if_http_override_for_api=True,
        )
        self.session = None
        self.language_map = None
        self.query_count = 0
        self.output_zh = "zh-CN"
        self.input_limit = int(5e3)

    def modernMt_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):

        proxies = kwargs.get("proxies", None)
        sleep_seconds = kwargs.get("sleep_seconds", 0)
        is_detail_result = kwargs.get("is_detail_result", False)
        update_session_after_freq = kwargs.get(
            "update_session_after_freq", self.default_session_freq
        )
        update_session_after_seconds = kwargs.get(
            "update_session_after_seconds", self.default_session_seconds
        )

        not_update_cond_freq = 1 if self.query_count < update_session_after_freq else 0
        not_update_cond_time = (
            1 if time.time() - self.begin_time < update_session_after_seconds else 0
        )
        if not (
            self.session
            and self.language_map
            and not_update_cond_freq
            and not_update_cond_time
        ):
            self.session = requests.Session()
            _ = self.session.get(
                self.host_url,
                headers=self.host_headers,
                proxies=proxies,
            )

        time_stamp = int(time.time() * 1e3)
        form_data = {
            "q": query_text,
            "source": "" if from_language == "auto" else from_language,
            "target": to_language,
            "ts": time_stamp,
            "verify": hashlib.md5(
                "webkey_E3sTuMjpP8Jez49GcYpDVH7r#{}#{}".format(
                    time_stamp, query_text
                ).encode()
            ).hexdigest(),
            "hints": "",
            "multiline": "true",
        }
        r = self.session.post(
            self.api_url,
            json=form_data,
            headers=self.api_headers,
            proxies=proxies,
        )
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data["data"]["translation"]


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def inittranslator(self):
        self.engine = ModernMt()

    def translate(self, content):

        return self.engine.modernMt_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
