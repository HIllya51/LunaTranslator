import requests
import urllib
import random
import time


class Tse:
    def __init__(self):
        self.author = "Ulion.Tse"
        self.begin_time = time.time()
        self.default_session_seconds = 1.5e3
        self.transform_en_translator_pool = (
            "Itranslate",
            "Lingvanex",
        )
        self.auto_pool = (
            "auto",
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
        return host_headers if not if_api else api_headers


class Reverso(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://www.reverso.net/text-translation"
        self.api_url = "https://api.reverso.net/translate/v1/translation"
        self.language_url = None
        self.language_pattern = "https://cdn.reverso.net/trans/v(\d).(\d).(\d)/main.js"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url, if_api=True, if_json_for_api=True
        )
        self.session = None
        self.language_map = None
        self.decrypt_language_map = None
        self.query_count = 0
        self.output_zh = "zh"  # 'chi', because there are self.language_tran
        self.input_limit = 2000

    def reverso_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        proxies = kwargs.get("proxies", None)
        is_detail_result = kwargs.get("is_detail_result", False)
        sleep_seconds = kwargs.get("sleep_seconds", random.random())
        update_session_after_seconds = kwargs.get(
            "update_session_after_seconds", self.default_session_seconds
        )

        not_update_cond_time = (
            1 if time.time() - self.begin_time < update_session_after_seconds else 0
        )
        if not (
            self.session
            and not_update_cond_time
            and self.language_map
            and self.decrypt_language_map
        ):
            self.session = requests.Session()
            host_html = self.session.get(
                self.host_url,
                headers=self.host_headers,
                proxies=proxies,
            ).text

        form_data = {
            "format": "text",
            "from": from_language,
            "to": to_language,
            "input": query_text,
            "options": {
                "contextResults": "true",
                "languageDetection": "true",
                "sentenceSplitter": "true",
                "origin": "contextweb",
            },
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
        return data if is_detail_result else "".join(data["translation"])


from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {
            "zh": "chi",
            "en": "eng",
            "es": "spa",
            "fr": "fra",
            "ko": "kor",
            "ru": "rus",
            "ja": "jpn",
        }

    def inittranslator(self):
        self.engine = Reverso()
        self.engine._ = None

    def translate(self, content):
        return self.engine.reverso_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
