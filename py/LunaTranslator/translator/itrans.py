import requests
import re
import urllib
import time
from language import Languages


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


class Itranslate(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://itranslate.com/webapp"
        self.api_url = "https://web-api.itranslateapp.com/v3/texts/translate"
        self.language_url = "https://itranslate-webapp-production.web.app/main.js"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url, if_api=True, if_json_for_api=True
        )
        self.session = None
        self.language_map = None
        self.language_description = None
        self.api_key = None
        self.query_count = 0
        self.output_zh = "zh-CN"
        self.input_limit = 1000

    def get_d_lang_map(self, lang_html):

        lang_str = re.compile("d=\[{(.*?)}\]").search(lang_html).group()[2:]
        dialect = "dialect"
        dataImage = "dataImage"
        label = "label"
        return eval(lang_str)

    def get_apikey(self, lang_html):
        return re.compile('"API-KEY":"(.*?)"').findall(lang_html)[0]

    def itranslate_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        if not (self.session):
            self.session = requests.Session()
            mainjsurl = self.session.get(
                "https://itranslate-webapp-production.web.app/manifest.json",
                proxies=kwargs["proxies"],
            ).json()["main.js"]
            mainjs = self.session.get(mainjsurl, proxies=kwargs["proxies"]).text
            self.api_key = re.compile('"API-KEY":"(.*?)"').findall(mainjs)[0]
            self.api_headers.update({"API-KEY": self.api_key})
        form_data = {
            "source": {
                "dialect": from_language,
                "text": query_text,
                "with": ["synonyms"],
            },
            "target": {"dialect": to_language},
        }
        r = self.session.post(
            self.api_url,
            headers=self.api_headers,
            json=form_data,
            proxies=kwargs["proxies"],
        )
        r.raise_for_status()
        self.query_count += 1
        try:
            return r.json()["target"]["text"]
        except:
            raise Exception(r)


from traceback import print_exc

from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {
            Languages.English: "en-UK",
            Languages.Chinese: "zh-CN",
            Languages.Spanish: "es-ES",
            Languages.French: "fr-FR",
            Languages.TradChinese: "zh-TW",
        }

    def inittranslator(self):
        self.engine = Itranslate()
        self.engine._ = None

    def translate(self, content):
        return self.engine.itranslate_api(
            content, self.srclang, self.tgtlang, proxies=self.proxy
        )
