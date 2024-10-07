import requests, re, uuid
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


class QQTranSmart(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://transmart.qq.com"
        self.api_url = "https://transmart.qq.com/api/imt"
        self.get_lang_url = None
        self.get_lang_url_pattern = "/assets/vendor.(.*?).js"  # e4c6831c
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url, if_api=True, if_json_for_api=True
        )
        self.language_map = None
        self.session = None
        self.uuid = str(uuid.uuid4())
        self.query_count = 0
        self.output_zh = "zh"
        self.input_limit = int(5e3)

    def get_clientKey(self):
        return "browser-firefox-110.0.0-Windows 10-{}-{}".format(
            self.uuid, int(time.time() * 1e3)
        )

    def split_sentence(self, data):
        index_pair_list = [
            [item["start"], item["start"] + item["len"]]
            for item in data["sentence_list"]
        ]
        index_list = [i for ii in index_pair_list for i in ii]
        return [
            data["text"][index_list[i] : index_list[i + 1]]
            for i in range(len(index_list) - 1)
        ]

    def qqTranSmart_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        """
        https://transmart.qq.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default 0.
                :param is_detail_result: boolean, default False.
                :param if_ignore_limit_of_length: boolean, default False.
                :param limit_of_length: int, default 5000.
                :param if_ignore_empty_query: boolean, default False.
                :param update_session_after_freq: int, default 1000.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: boolean, default False.
                :param show_time_stat_precision: int, default 4.
                :param if_print_warning: bool, default True.
        :return: str or dict
        """

        timeout = kwargs.get("timeout", None)
        proxies = kwargs.get("proxies", None)
        sleep_seconds = kwargs.get("sleep_seconds", 0)
        if_print_warning = kwargs.get("if_print_warning", True)
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
            host_html = self.session.get(
                self.host_url,
                headers=self.host_headers,
                timeout=timeout,
                proxies=proxies,
            ).text

            if not self.get_lang_url:
                self.get_lang_url = (
                    self.host_url
                    + re.compile(self.get_lang_url_pattern).search(host_html).group()
                )

        client_key = self.get_clientKey()
        self.api_headers.update({"Cookie": "client_key={}".format(client_key)})

        split_form_data = {
            "header": {
                "fn": "text_analysis",
                "client_key": client_key,
            },
            "type": "plain",
            "text": query_text,
            "normalize": {"merge_broken_line": "false"},
        }
        split_data = self.session.post(
            self.api_url,
            json=split_form_data,
            headers=self.api_headers,
            timeout=timeout,
            proxies=proxies,
        ).json()
        text_list = self.split_sentence(split_data)

        api_form_data = {
            "header": {
                "fn": "auto_translation",
                "client_key": client_key,
            },
            "type": "plain",
            "model_category": "normal",
            "source": {
                "lang": from_language,
                "text_list": [""] + text_list + [""],
            },
            "target": {"lang": to_language},
        }
        r = self.session.post(
            self.api_url,
            json=api_form_data,
            headers=self.api_headers,
            timeout=timeout,
            proxies=proxies,
        )
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else "".join(data["auto_translation"])


class TS(basetrans):
    def langmap(self):
        return {"cht": "zh-tw"}

    def inittranslator(self):
        self.engine = QQTranSmart()

    def translate(self, content):

        return self.engine.qqTranSmart_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
