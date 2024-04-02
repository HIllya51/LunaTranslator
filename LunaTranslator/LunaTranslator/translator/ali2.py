import requests, re
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


class AlibabaV1(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://translate.alibaba.com"
        self.api_url = "https://translate.alibaba.com/translationopenseviceapp/trans/TranslateTextAddAlignment.do"
        self.get_language_url = "https://translate.alibaba.com/translationopenseviceapp/trans/acquire_supportLanguage.do"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.professional_field = ("general", "message", "offer")
        self.dmtrack_pageid = None
        self.session = None
        self.query_count = 0
        self.output_zh = "zh"
        self.input_limit = int(5e3)

    def get_dmtrack_pageid(self, host_response):
        try:
            e = re.compile("dmtrack_pageid='(\w+)';").findall(host_response.text)[0]
        except:
            e = ""
        if not e:
            e = host_response.cookies.get("cna", "001")
            e = re.compile(pattern="[^a-z\d]").sub(repl="", string=e.lower())[:16]
        else:
            n, r = e[0:16], e[16:26]
            i = hex(int(r, 10))[2:] if re.compile("^[\-+]?[0-9]+$").match(r) else r
            e = n + i

        s = int(time.time() * 1000)
        o = "".join([e, hex(s)[2:]])
        for _ in range(1, 10):
            a = hex(int(0 * 1e10))[2:]  # int->str: 16, '0x'
            o += a
        return o[:42]

    def alibaba_api(
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
        if not (
            self.session
            and self.language_map
            and not_update_cond_freq
            and not_update_cond_time
            and self.dmtrack_pageid
        ):
            self.session = requests.Session()
            host_response = self.session.get(
                self.host_url,
                headers=self.host_headers,
                timeout=timeout,
                proxies=proxies,
            )
            self.dmtrack_pageid = self.get_dmtrack_pageid(host_response)

        use_domain = kwargs.get("professional_field", "message")
        form_data = {
            "srcLanguage": from_language,
            "tgtLanguage": to_language,
            "srcText": query_text,
            "bizType": use_domain,
            "viewType": "",
            "source": "",
        }
        params = {"dmtrack_pageid": self.dmtrack_pageid}
        r = self.session.post(
            self.api_url,
            headers=self.api_headers,
            params=params,
            data=form_data,
            timeout=timeout,
            proxies=proxies,
        )
        r.raise_for_status()
        self.query_count += 1
        try:
            return "\n".join(r.json()["listTargetText"])
        except:
            raise Exception(r.text)


class TS(basetrans):
    def langmap(self):
        return {"cht": "zh-tw"}

    def inittranslator(self):
        self.engine = AlibabaV1()

    def translate(self, content):

        return self.engine.alibaba_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
