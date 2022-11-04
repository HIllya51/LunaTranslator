import requests
import re
import urllib
import random
import time

from utils.config import globalconfig
import js2py
def srclang( ):
        return ['jp','en'][globalconfig['srclang']]
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
class Tencent(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://fanyi.qq.com'
        self.api_url = 'https://fanyi.qq.com/api/translate'
        self.get_language_url = 'https://fanyi.qq.com/js/index.js'
        self.get_qt_url = 'https://fanyi.qq.com/api/reauth12f'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True)
        self.qt_headers = self.get_headers(self.host_url, if_api=True, if_json_for_api=True)
        self.language_map = None
        self.qtv_qtk = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = 2000

    def get_language_map(self, ss, language_url, timeout, proxies):
        r = ss.get(language_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
      
        lang_map_str = re.compile(pattern='C={(.*?)}|languagePair = {(.*?)}', flags=re.S).search(r.text).group(0)  # C=
        return js2py.eval(lang_map_str)

    def get_qt(self, ss, timeout, proxies, if_session=False):
        if if_session:
            return ss.post(self.get_qt_url, headers=self.qt_headers, json=self.qtv_qtk, timeout=timeout, proxies=proxies).json()
        return requests.post(self.get_qt_url, headers=self.qt_headers, json=self.qtv_qtk, timeout=timeout, proxies=proxies).json()

    # @Tse.time_stat
    def tencent_api(self, query_text: str, from_language: str = 'jp', to_language: str = 'zh', **kwargs)  :
        from_language=srclang()
        timeout=  globalconfig['translatortimeout']
        proxies={'http': None,'https': None}
        with requests.Session() as ss:
            if self._ is None:
                self._ = ss.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
            self.qtv_qtk = self.get_qt(ss, timeout, proxies, if_session=False)
            form_data = {
                'source': from_language,
                'target': to_language,
                'sourceText': query_text,
                'qtv': self.qtv_qtk.get('qtv', ''),
                'qtk': self.qtv_qtk.get('qtk', ''),
                'ticket': '',
                'randstr': '',
                'sessionUuid': 'translate_uuid' + str(int(time.time() * 1000)),
            }
            r = ss.post(self.api_url, headers=self.api_headers, data=form_data, timeout=timeout, proxies=proxies)
            
            data = r.json() 
        self.query_count += 1
        return  ''.join(item['targetText'] for item in data['translate']['records'])  # auto whitespace

from traceback import print_exc

from translator.basetranslator import basetrans
class TS(basetrans):
    def inittranslator(self):  
        self.engine=Tencent()
        self.engine._=None
    def translate(self,content):  
            return self.engine.tencent_api(content)
        