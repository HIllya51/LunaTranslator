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


class TranslateCom(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://www.translate.com/machine-translation"
        self.api_url = "https://www.translate.com/translator/translate_mt"
        self.lang_detect_url = (
            "https://www.translate.com/translator/ajax_lang_auto_detect"
        )
        self.language_url = "https://www.translate.com/ajax/language/ht/all"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url, if_api=True, if_json_for_api=False
        )
        self.session = None
        self.language_map = None
        self.language_description = None
        self.query_count = 0
        self.output_zh = "zh"
        self.input_limit = 15000  # fifteen thousand letters left today.

    def translateCom_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        """
        https://www.translate.com/machine-translation
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default `random.random()`.
                :param is_detail_result: boolean, default False.
                :param if_ignore_limit_of_length: boolean, default False.
                :param limit_of_length: int, default 5000.
                :param if_ignore_empty_query: boolean, default False.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: boolean, default False.
                :param show_time_stat_precision: int, default 4.
        :return: str or dict
        """

        timeout = kwargs.get("timeout", None)
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
            and self.language_description
        ):
            self.session = requests.Session()
            _ = self.session.get(
                self.host_url,
                headers=self.host_headers,
                timeout=timeout,
                proxies=proxies,
            )
            lang_r = self.session.get(
                self.language_url,
                headers=self.host_headers,
                timeout=timeout,
                proxies=proxies,
            )
            self.language_description = lang_r.json()

        if from_language == "auto":
            detect_form = {"text_to_translate": query_text}
            r_detect = self.session.post(
                self.lang_detect_url,
                data=detect_form,
                headers=self.api_headers,
                timeout=timeout,
                proxies=proxies,
            )
            from_language = r_detect.json()["language"]

        form_data = {
            "text_to_translate": query_text,
            "source_lang": from_language,
            "translated_lang": to_language,
            "use_cache_only": "false",
        }
        r = self.session.post(
            self.api_url,
            data=form_data,
            headers=self.api_headers,
            timeout=timeout,
            proxies=proxies,
        )
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return (
            data if is_detail_result else data["translated_text"]
        )  # translation_source is microsoft, wtf!


from traceback import print_exc

from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"cht": "zh-TW"}

    def inittranslator(self):
        self.engine = TranslateCom()
        self.engine._ = None

    def translate(self, content):
        return self.engine.translateCom_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
