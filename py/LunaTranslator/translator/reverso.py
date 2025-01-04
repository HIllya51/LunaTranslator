import requests
import urllib
from translator.basetranslator import basetrans
from language import Languages


class Tse:
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
        self.language_pattern = r"https://cdn.reverso.net/trans/v(\d).(\d).(\d)/main.js"
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(
            self.host_url, if_api=True, if_json_for_api=True
        )
        self.session = None

    def reverso_api(
        self,
        __,
        query_text: str,
        from_language: str = "auto",
        to_language: str = "en",
        **kwargs
    ):
        proxies = kwargs.get("proxies", None)
        if not (self.session):
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
                "origin": ["translation.web", "contextweb"][__],
            },
        }
        r = self.session.post(
            self.api_url,
            json=form_data,
            headers=self.api_headers,
            proxies=proxies,
        )
        return r.json()


class TS(basetrans):

    def langmap(self):
        return {
            Languages.Chinese: "chi",
            Languages.English: "eng",
            Languages.Spanish: "spa",
            Languages.French: "fra",
            Languages.Korean: "kor",
            Languages.Russian: "rus",
            Languages.Japanese: "jpn",
        }

    def inittranslator(self):
        self.engine = Reverso()
        self.mostmaybelang = "jpn"

    def translate(self, content):
        if self.srclang == Languages.Auto:
            src = self.mostmaybelang
        else:
            src = self.srclang

        data = self.engine.reverso_api(
            self.config["origin"],
            content,
            src,
            self.tgtlang,
            proxies=self.proxy,
        )
        if self.srclang == Languages.Auto:
            det = data["languageDetection"]["detectedLanguage"]
            if det == src:
                return "".join(data["translation"])
            else:
                self.mostmaybelang = det
                data = self.engine.reverso_api(
                    self.config["origin"],
                    content,
                    det,
                    self.tgtlang,
                    proxies=self.proxy,
                )
                return "".join(data["translation"])
        else:
            return "".join(data["translation"])
