import requests
import re
import urllib
import random
import time
 
class Tse:
    def __init__(self):
        self.author = 'Ulion.Tse'
        self.begin_time = time.time()
        self.default_session_seconds = 1.5e3
        self.transform_en_translator_pool = ('Itranslate', 'Lingvanex',)
        self.auto_pool = ('auto', 'auto-detect',)
        self.zh_pool = ('zh', 'zh-CN', 'zh-CHS', 'zh-Hans', 'zh-Hans_CN', 'cn', 'chi',)
 
    @staticmethod
    def get_headers(host_url: str,
                    if_api: bool = False,
                    if_referer_for_host: bool = True,
                    if_ajax_for_api: bool = True,
                    if_json_for_api: bool = False,
                    if_multipart_for_api: bool = False
                    ) -> dict:

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
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
        if if_api and if_multipart_for_api:
            api_headers.pop('Content-Type')
        return host_headers if not if_api else api_headers
 
class Lingvanex(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://lingvanex.com/demo/'
        self.api_url = None
        self.language_url = None
        self.auth_url = 'https://lingvanex.com/lingvanex_demo_page/js/api-base.js'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=False)
        self.session = None
        self.language_map = None
        self.detail_language_map = None
        self.auth_info = None
        self.mode = None
        self.model_pool = ('B2B', 'B2C',)
        self.query_count = 0
        self.output_zh = 'zh-Hans_CN'
        self.input_limit = 10000
 
    def get_d_lang_map(self, lang_url, ss, headers, timeout, proxies):
        params = {'all': 'true', 'code': 'en_GB', 'platform': 'dp', '_': int(time.time() * 1000)}
        return ss.get(lang_url, params=params, headers=headers, timeout=timeout, proxies=proxies).json()

    def get_auth(self, auth_url, ss, headers, timeout, proxies):
        js_html = ss.get(auth_url, headers=headers, timeout=timeout, proxies=proxies).text
        return {k: v for k, v in re.compile(',(.*?)="(.*?)"').findall(js_html)}
 
    def lingvanex_api(self, query_text: str, from_language: str = 'auto', to_language: str = 'en', **kwargs)  :
        """
        https://lingvanex.com/demo/
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'zh'.
        :param **kwargs:
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default `random.random()`.
                :param is_detail_result: boolean, default False.
                :param if_ignore_limit_of_length: boolean, default False.
                :param limit_of_length: int, default 5000.
                :param if_ignore_empty_query: boolean, default False.
                :param update_session_after_seconds: float, default 1500.
                :param if_show_time_stat: boolean, default False.
                :param show_time_stat_precision: int, default 4.
                :param lingvanex_mode: str, default "B2C", choose from ("B2B", "B2C").
        :return: str or dict
        """
        print(query_text,from_language,to_language)
        mode = kwargs.get('lingvanex_mode', 'B2C')
        timeout = kwargs.get('timeout', None)
        proxies = kwargs.get('proxies', None)
        is_detail_result = kwargs.get('is_detail_result', False)
        sleep_seconds = kwargs.get('sleep_seconds', random.random())
        update_session_after_seconds = kwargs.get('update_session_after_seconds', self.default_session_seconds)
 

        not_update_cond_time = 1 if time.time() - self.begin_time < update_session_after_seconds else 0
        if not (self.session and not_update_cond_time and self.language_map and self.auth_info and self.mode == mode):
            self.session = requests.Session()
            _ = self.session.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            self.auth_info = self.get_auth(self.auth_url, self.session, self.host_headers, timeout, proxies)

            if mode != self.mode:
                self.mode = mode
                self.api_url = ''.join([self.auth_info[f'{mode}_BASE_URL'], self.auth_info['TRANSLATE_URL']])
                self.language_url = ''.join([self.auth_info[f'{mode}_BASE_URL'], self.auth_info['GET_LANGUAGES_URL']])
                self.host_headers.update({'authorization': self.auth_info[f'{mode}_AUTH_TOKEN']})
                self.api_headers.update({'authorization': self.auth_info[f'{mode}_AUTH_TOKEN']})
                self.api_headers.update({'referer': urllib.parse.urlparse(self.auth_info[f'{mode}_BASE_URL']).netloc})
 
            self.detail_language_map = self.get_d_lang_map(self.language_url, self.session, self.host_headers, timeout, proxies)
  

        form_data = {
            'from': from_language,
            'to': to_language,
            'text': query_text,
            'platform': 'dp',
            'is_return_text_split_ranges': 'true'
        }
        
        form_data = urllib.parse.urlencode(form_data)
        r = self.session.post(self.api_url, data=form_data, headers=self.api_headers, timeout=timeout, proxies=proxies)
         
        data = r.json()
        time.sleep(sleep_seconds)
        self.query_count += 1
        #return data if is_detail_result else data['result'] if self.mode == 'B2C' else data['result']['text']
        print(data if is_detail_result else data['result'] if self.mode == 'B2C' else data['result']['text'])
        return data['result']['text']
from traceback import print_exc

from translator.basetranslator import basetrans
class TS(basetrans):
    def langmap(self):
        return {"zh":"zh-Hans_CN","cht":"zh-Hant_TW","en":"en_GB","es":"es_ES","fr":"fr_FR","ko":"ko_KR","ru":"ru_RU","ja":"ja_JP"}
    def inittranslator(self):  
        self.engine=Lingvanex()
        self.engine._=None
    def translate(self,content):  
            return self.engine.lingvanex_api(content,self.srclang,self.tgtlang,proxies=self.proxy)
        