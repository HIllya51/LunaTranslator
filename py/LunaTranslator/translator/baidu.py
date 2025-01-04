import requests
from language import Languages
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


class BaiduV1(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://fanyi.baidu.com"
        self.api_url = "https://fanyi.baidu.com/transapi"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.session = None
        self.query_count = 0
        self.output_zh = "zh"
        self.input_limit = int(5e3)

    # @Tse.debug_language_map
    # def get_language_map(self, host_html, **kwargs):
    #     lang_str = re.compile('langMap: {(.*?)}').search(host_html.replace('\n', '').replace('  ', '')).group()[8:]
    #     return execjs.eval(lang_str)

    def baidu_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        proxies = kwargs.get("proxies", None)
        sleep_seconds = kwargs.get("sleep_seconds", 0)

        if not (self.session):
            self.session = requests.Session()
            _ = self.session.get(
                self.host_url,
                headers=self.host_headers,
                proxies=proxies,
            )  # must twice, send cookies.
            host_html = self.session.get(
                self.host_url,
                headers=self.host_headers,
                proxies=proxies,
            ).text
            # self.language_map = self.get_language_map(host_html, from_language=from_language, to_language=to_language)

        form_data = {
            "from": from_language,
            "to": to_language,
            "query": query_text,
            "source": "txt",
        }
        r = self.session.post(
            self.api_url,
            data=form_data,
            headers=self.api_headers,
            proxies=proxies,
        )
        r.raise_for_status()
        time.sleep(sleep_seconds)
        self.query_count += 1
        try:
            return "\n".join([item["dst"] for item in r.json()["data"]])
        except:
            raise Exception(r)


class TS(basetrans):
    def langmap(self):
        return {
            Languages.Spanish: "spa",
            Languages.Korean: "kor",
            Languages.French: "fra",
            Languages.Japanese: "jp",
            Languages.TradChinese: "cht",
            Languages.Vietnamese: "vie",
            Languages.Ukrainian: "ukr",
            Languages.Arabic: "ara",
            Languages.Swedish : "swe",
            Languages.Latin: "lat",
        }

    def inittranslator(self):

        self.engine = BaiduV1()

    def translate(self, query):
        return self.engine.baidu_api(
            query, self.srclang, self.tgtlang, proxies=self.proxy
        )
