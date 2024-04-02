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
        """
        https://bing.com/Translator, https://cn.bing.com/Translator.
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
                :param if_use_cn_host: boolean, default None.
        :return: str or dict
        """

        use_cn_condition = (
            kwargs.get("if_use_cn_host", None) or self.server_region == "CN"
        )
        self.host_url = self.cn_host_url if use_cn_condition else self.en_host_url
        self.api_url = self.host_url.replace("Translator", "ttranslatev3")
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)

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
            and self.tk
            and self.ig_iid
        ):
            self.session = requests.Session()
            host_html = self.session.get(
                self.host_url,
                headers=self.host_headers,
                timeout=timeout,
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
            timeout=timeout,
            proxies=proxies,
        )
        r.raise_for_status()
        data = r.json()
        print(r.text)
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data[0] if is_detail_result else data[0]["translations"][0]["text"]


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-Hans", "cht": "zh-Hant"}

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


# class TS(basetrans):
#     def langmap(self):
#          return  {"zh":"zh-Hans","cht":"zh-Hant"}
#     def inittranslator(self):
#         self.ss=requests.session()
#         headers = {
#                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#                 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
#                 'cache-control': 'no-cache',
#                 'pragma': 'no-cache',
#                 'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
#                 'sec-ch-ua-arch': '"x86"',
#                 'sec-ch-ua-bitness': '"64"',
#                 'sec-ch-ua-full-version': '"105.0.1343.53"',
#                 'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-model': '""',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-ch-ua-platform-version': '"10.0.0"',
#                 'sec-ch-ua-wow64': '?0',
#                 'sec-fetch-dest': 'document',
#                 'sec-fetch-mode': 'navigate',
#                 'sec-fetch-site': 'same-origin',
#                 'sec-fetch-user': '?1',
#                 'upgrade-insecure-requests': '1',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
#             }

#         response = self.ss.get('https://cn.bing.com/translator/' ,headers=headers)
#         text=response.text

#         res=re.compile('var params_AbusePreventionHelper = (.*?);').findall(text)[0]

#         self.key=str(eval(res)[0])
#         self.token=str(eval(res)[1])

#         iid = 'translator.5028'
#         ig = re.compile('IG:"(.*?)"').findall(text)[0]

#         self.IG=ig


#         self.iid=iid

#     def translate(self,content):
#             print(content)

#             headers = {
#                 'authority': 'cn.bing.com',
#                 'accept': '*/*',
#                 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
#                 'cache-control': 'no-cache',
#                 'content-type': 'application/x-www-form-urlencoded',
#                 'origin': 'https://cn.bing.com',
#                 'pragma': 'no-cache',
#                 'referer': 'https://cn.bing.com/translator/',
#                 'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
#                 'sec-ch-ua-arch': '"x86"',
#                 'sec-ch-ua-bitness': '"64"',
#                 'sec-ch-ua-full-version': '"105.0.1343.53"',
#                 'sec-ch-ua-full-version-list': '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-ch-ua-platform-version': '"10.0.0"',
#                 'sec-fetch-dest': 'empty',
#                 'sec-fetch-mode': 'cors',
#                 'sec-fetch-site': 'same-origin',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
#                 'x-edge-shopping-flag': '1',
#             }

#             response = self.ss.post('https://cn.bing.com/ttranslatev3?isVertical=1&&IG='+self.IG+'&IID='+self.iid,headers=headers, data={
#                  'fromLang':self.srclang,'text':content,'to':self.tgtlang,'token':self.token,'key':self.key
#             })#data=data )
#             js=response.json()
#             ch=js[0]['translations'][0]['text']

#             return ch
