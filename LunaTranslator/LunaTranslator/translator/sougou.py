import hashlib
import requests
from translator.basetranslator import basetrans
import random
import urllib


class Tse:
    def __init__(self):
        self.author = "Ulion.Tse"

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


class Sogou(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = "https://fanyi.sogou.com"
        # self.old_api_url = 'https://fanyi.sogou.com/reventondc/translateV3'
        self.api_url = "https://fanyi.sogou.com/api/transpc/text/result"
        self.get_language_url = (
            "https://dlweb.sogoucdn.com/translate/pc/static/js/app.7016e0df.js"
        )
        # self.get_language_pattern = '//dlweb.sogoucdn.com/translate/pc/static/js/app.(.*?).js'
        # self.get_language_url = None
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.form_data = None
        self.query_count = 0
        self.input_limit = 5000

    def get_form(self, query_text, from_language, to_language):
        uuid = ""
        for i in range(8):
            uuid += hex(int(65536 * (1 + random.random())))[2:][1:]
            if i in range(1, 5):
                uuid += "-"
        sign_text = (
            "" + from_language + to_language + query_text + "109984457"
        )  # window.__INITIAL_STATE__.common.CONFIG.secretCode
        sign = hashlib.md5(sign_text.encode()).hexdigest()
        form = {
            "from": from_language,
            "to": to_language,
            "text": query_text,
            "uuid": uuid,
            "s": sign,
            "client": "pc",  # wap
            "fr": "browser_pc",  # browser_wap
            "needQc": "1",
        }
        return form

    # @Tse.time_stat
    def sogou_api(self, query_text, src, tgt, proxy):

        with requests.Session() as ss:
            _ = ss.get(self.host_url, headers=self.host_headers, proxies=proxy).text
            from_language, to_language = src, tgt
            self.form_data = self.get_form(query_text, from_language, to_language)
            r = ss.post(
                self.api_url,
                headers=self.api_headers,
                data=self.form_data,
                proxies=proxy,
            )

            data = r.json()
        return data["data"]["translate"]["dit"]


class TS(basetrans):
    def inittranslator(self):
        self.engine = Sogou()

    def translate(self, content):
        ss = self.engine.sogou_api(content, self.srclang, self.tgtlang, self.proxy)
        return ss

    def langmap(self):
        return {"zh": "zh-CHS"}
