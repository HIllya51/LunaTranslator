import re
import requests, time, urllib
from translator.basetranslator import basetrans


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


class Bing(Tse):
    def __init__(self, server_region="EN"):
        super().__init__()
        self.host_url = None
        self.cn_host_url = "https://cn.bing.com/Translator"
        self.en_host_url = "https://www.bing.com/Translator"
        self.server_region = server_region
        self.api_url = None
        self.host_headers = None
        self.api_headers = None
        self.language_map = None
        self.session = None
        self.tk = None
        self.ig_iid = None
        self.query_count = 0
        self.output_auto = "auto-detect"
        self.output_zh = "zh-Hans"
        self.input_limit = int(1e3)

    def get_ig_iid(self, host_html):

        # iid = et.xpath('//*[@id="tta_outGDCont"]/@data-iid')[0]  # browser page is different between request page.
        # iid = 'translator.5028'
        iid = re.search(
            '<div[ ]+id="tta_outGDCont"[ ]+data-iid="(.*?)">', host_html
        ).groups()[0]
        ig = re.compile('IG:"(.*?)"').findall(host_html)[0]
        return {"iid": iid, "ig": ig}

    def get_tk(self, host_html):
        result_str = re.compile("var params_AbusePreventionHelper = (.*?);").findall(
            host_html
        )[0]
        print(result_str)
        result = eval(result_str)
        return {"key": result[0], "token": result[1]}

    def bing_api(
        self,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        use_cn_condition = (
            kwargs.get("if_use_cn_host", None) or self.server_region == "CN"
        )
        self.host_url = self.cn_host_url if use_cn_condition else self.en_host_url
        self.api_url = self.host_url.replace("Translator", "ttranslatev3")
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)

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
            and self.tk
            and self.ig_iid
        ):
            self.session = requests.Session()
            host_html = self.session.get(
                self.host_url,
                headers=self.host_headers,
                proxies=proxies,
            ).text
            self.tk = self.get_tk(host_html)
            self.ig_iid = self.get_ig_iid(host_html)

        form_data = {
            "text": query_text,
            "fromLang": from_language,
            "to": to_language,
            "tryFetchingGenderDebiasedTranslations": "true",
        }
        form_data = {**form_data, **self.tk}
        api_url_param = "?isVertical=1&&IG={}&IID={}".format(
            self.ig_iid["ig"], self.ig_iid["iid"]
        )
        api_url = "".join([self.api_url, api_url_param])

        r = self.session.post(
            api_url,
            headers=self.host_headers,
            data=form_data,
            proxies=proxies,
        )
        r.raise_for_status()
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        try:
            return data[0] if is_detail_result else data[0]["translations"][0]["text"]
        except:
            raise Exception(r.maybejson)


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-Hans", "cht": "zh-Hant", "auto": "auto-detect"}

    def inittranslator(self):
        self.engine = Bing()

    def translate(self, content):
        try:
            return self.engine.bing_api(
                content,
                self.srclang,
                self.tgtlang,
                proxies=self.proxy,
                if_use_cn_host=True,
            )
        except:
            return self.engine.bing_api(
                content, self.srclang, self.tgtlang, proxies=self.proxy
            )
