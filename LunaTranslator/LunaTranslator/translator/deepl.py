from myutils.config import static_data
import time
from translator.basetranslator import basetrans
import random
import urllib


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
        host_url,
        if_api=False,
        if_referer_for_host=True,
        if_ajax_for_api=True,
        if_json_for_api=False,
    ):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
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
        return host_headers if not if_api else api_headers


import requests


class Deepl(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://www.deepl.com/translator"
        self.api_url = "https://www2.deepl.com/jsonrpc"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url, if_api=True, if_ajax_for_api=False, if_json_for_api=True
        )
        self.params = {
            "split": {"method": "LMT_split_text"},
            "handle": {"method": "LMT_handle_jobs"},
        }
        self.request_id = int(random.randrange(100, 10000) * 10000 + 4)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = "zh"
        self.input_limit = int(5e3)
        self.session = requests.Session()

    def split_sentences_param(self, query_text, from_language):
        data = {
            "id": self.request_id,
            "jsonrpc": "2.0",
            "params": {
                "texts": query_text.split("\n"),
                "commonJobParams": {"mode": "translate"},
                "lang": {
                    "lang_user_selected": from_language,
                    "preference": {
                        "weight": {},
                        "default": "default",
                    },
                },
            },
        }
        return {**self.params["split"], **data}

    def context_sentences_param(self, sentences, from_language, to_language):
        sentences = [""] + sentences + [""]
        data = {
            "id": self.request_id + 1,
            "jsonrpc": " 2.0",
            "params": {
                "priority": 1,  # -1 if 'quality': 'fast'
                "timestamp": int(time.time() * 1e3),
                "commonJobParams": {
                    # 'regionalVariant': 'en-US',
                    "browserType": 1,
                    "mode": "translate",
                },
                "jobs": [
                    {
                        "kind": "default",
                        # 'quality': 'fast', # -1
                        "sentences": [
                            {"id": i - 1, "prefix": "", "text": sentences[i]}
                        ],
                        "raw_en_context_before": (
                            sentences[1:i] if sentences[i - 1] else []
                        ),
                        "raw_en_context_after": (
                            [sentences[i + 1]] if sentences[i + 1] else []
                        ),
                        "preferred_num_beams": (
                            1 if len(sentences) >= 4 else 4
                        ),  # 1 if two sentences else 4, len>=2+2
                    }
                    for i in range(1, len(sentences) - 1)
                ],
                "lang": {
                    "preference": {
                        "weight": {},
                        "default": "default",
                    },
                    "source_lang_user_selected": from_language,  # "source_lang_computed"
                    "target_lang": to_language,
                },
            },
        }
        return {**self.params["handle"], **data}

    # @Tse.time_stat
    def deepl_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
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

        from_language = (
            from_language.upper() if from_language != "auto" else from_language
        )
        to_language = to_language.upper() if to_language != "auto" else to_language

        ssp_data = self.split_sentences_param(query_text, from_language)
        r_s = self.session.post(
            self.api_url,
            params=self.params["split"],
            json=ssp_data,
            headers=self.api_headers,
            timeout=timeout,
            proxies=proxies,
        )
        r_s.raise_for_status()
        s_data = r_s.json()
        try:
            s_sentences = [
                it["sentences"][0]["text"]
                for item in s_data["result"]["texts"]
                for it in item["chunks"]
            ]
        except:
            raise Exception(s_data)
        h_data = self.context_sentences_param(s_sentences, from_language, to_language)

        r_cs = self.session.post(
            self.api_url,
            params=self.params["handle"],
            json=h_data,
            headers=self.api_headers,
            timeout=timeout,
            proxies=proxies,
        )
        r_cs.raise_for_status()
        data = r_cs.json()
        time.sleep(sleep_seconds)
        self.request_id += 3
        self.query_count += 1
        try:
            return (
                data
                if is_detail_result
                else "\n".join(
                    item["beams"][0]["sentences"][0]["text"]
                    for item in data["result"]["translations"]
                )
            )
        except:
            raise Exception(data)


class TS(basetrans):
    def langmap(self):
        x = {_: _.upper() for _ in static_data["language_list_translator_inner"]}
        x.pop("cht")
        return x  # {"zh":"ZH","ja":"JA","en":"EN","es":"ES","fr":"FR","ru":"RU"}

    def inittranslator(self):
        self.engine = Deepl()

    def translate(self, content):

        return self.engine.deepl_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
