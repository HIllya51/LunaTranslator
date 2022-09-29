import requests
import re
import urllib
import random
import time
import js2py
class Tse:
    def __init__(self):
        self.author = 'Ulion.Tse' 

    @staticmethod
    def get_headers(host_url, if_api=False, if_referer_for_host=True, if_ajax_for_api=True, if_json_for_api=False):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        url_path = urllib.parse.urlparse(host_url).path
        host_headers = {
            'Referer' if if_referer_for_host else 'Host': host_url,
            "User-Agent": user_agent,
        }
        api_headers = {
            'Origin': host_url.split(url_path)[0] if url_path else host_url,
            'Referer': host_url,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            "User-Agent": user_agent,
        }
        if if_api and not if_ajax_for_api:
            api_headers.pop('X-Requested-With')
            api_headers.update({'Content-Type': 'text/plain'})
        if if_api and if_json_for_api:
            api_headers.update({'Content-Type': 'application/json'})
        return host_headers if not if_api else api_headers

class IflytekV2(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://fanyi.xfyun.cn/console/trans/text'  # https://www.iflyrec.com/html/translate.html
        self.api_url = 'https://fanyi.xfyun.cn/api-tran/trans/its'
        self.detect_language_url = 'https://fanyi.xfyun.cn/api-tran/trans/detection'
        self.get_language_url = 'https://fanyi.xfyun.cn/js/trans-text/index.7da7fa2e.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.language_map = None
        self.query_count = 0
        self.output_zh = 'cn'
        self.input_limit = 2000

    def get_language_map(self, lang_url, ss, headers, timeout, proxies):
        js_html = ss.get(lang_url, headers=headers, timeout=timeout, proxies=proxies).text
        lang_list = re.compile('languageCode:"(.*?)",').findall(js_html)
        lang_list = sorted(list(set(lang_list)))
        return {}.fromkeys(lang_list, lang_list)

    # @Tse.time_stat
    def iflytek_api(self, query_text: str, from_language: str = 'ja', to_language: str = 'cn', **kwargs)  :
        """
        https://fanyi.xfyun.cn/console/trans/text
        :param query_text: str, must.
        :param from_language: str, default 'zh', unsupported 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param if_ignore_limit_of_length: boolean, default False.
                :param is_detail_result: boolean, default False.
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default `random.random()`.
        :return: str or dict
        """
        timeout=5
        proxies={'http': None,'https': None}
        with requests.Session() as ss:
            _ = ss.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
 
            form_data = {'from': from_language, 'to': to_language, 'text': query_text}
            r = ss.post(self.api_url, headers=self.api_headers, data=form_data, timeout=timeout, proxies=proxies)
            r.raise_for_status()
            data = r.json()
            print(data)
        return   eval(data['data'])['trans_result']['dst']



from traceback import print_exc

from translator.basetranslator import basetrans
class TS(basetrans):
    def inittranslator(self): 
        self.typename='ifly'
        self.engine=IflytekV2()
        self.engine._=None
    def realfy(self,content): 
        try:
            return self.engine.iflytek_api(content)
        except:
            print_exc()
            self.inittranslator()
            return '出错了'