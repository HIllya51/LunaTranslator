 
import re
from socket import timeout
import time
from urllib.parse import quote 
from translator.basetranslator import basetrans
import random
import urllib
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
import requests
import base64
class Caiyun(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://fanyi.caiyunapp.com'
        self.api_url = 'https://api.interpreter.caiyunai.com/v1/translator'
        # self.old_get_tk_url = 'https://fanyi.caiyunapp.com/static/js/app.1312348c1a3d00422dd1.js'
        self.get_tk_pattern = '/static/js/app.(.*?).js'
        self.get_tk_url = None
        self.get_jwt_url = 'https://api.interpreter.caiyunai.com/v1/user/jwt/generate'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_referer_for_host=True)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=False, if_json_for_api=True)
        self.language_map = None
        self.browser_pool = [
            'd8bab270cec5dc600525d424be1da0bb',
            '2c011fd3dbab6f3f763c5e7406317fdf',
            '74231a3a95c91c2fa8eba3082a8cc4d6'
        ]
        self.browser_id = random.choice(self.browser_pool)
        self.tk = None
        self.jwt = None
        self.decrypt_dictionary = self.crypt(if_de=True)
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = 5000
 
    def get_tk(self, ss, timeout, proxies):
        js_html = ss.get(self.get_tk_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
        return re.compile('t.headers\["X-Authorization"\]="(.*?)",').findall(js_html)[0]

    def get_jwt(self, browser_id, api_headers, ss, timeout, proxies):
        data = {"browser_id": browser_id}
        _ = ss.options(self.get_jwt_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
        return ss.post(self.get_jwt_url, headers=api_headers, json=data, timeout=timeout, proxies=proxies).json()['jwt']

    def crypt(self, if_de=True):
        normal_key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' + '0123456789' + '=.+-_/'
        cipher_key = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm' + '0123456789' + '=.+-_/'
        if if_de:
            return {k: v for k, v in zip(cipher_key, normal_key)}
        return {v: k for k, v in zip(cipher_key, normal_key)}

    def encrypt(self, plain_text):
        encrypt_dictionary = self.crypt(if_de=False)
        _cipher_text = base64.b64encode(plain_text.encode()).decode()
        return ''.join(list(map(lambda k: encrypt_dictionary[k], _cipher_text)))

    def decrypt(self, cipher_text):
        _ciphertext = ''.join(list(map(lambda k: self.decrypt_dictionary[k], cipher_text)))
        return base64.b64decode(_ciphertext).decode()

    # @Tse.time_stat
    def caiyun_api(self, query_text ) :
        """
        https://fanyi.caiyunapp.com
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param professional_field: str, default None, choose from ("medicine","law","machinery")
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
            if self._ is None:
                host_html = ss.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies).text
                if not self.get_tk_url:
                    self.get_tk_url = self.host_url + re.compile(self.get_tk_pattern).search(host_html).group()
                self.tk = self.get_tk(ss, timeout, proxies)
                 
            self.api_headers.update({
                "app-name": "xy",
                "device-id": "",
                "os-type": "web",
                "os-version": "",
                "version": "1.8.0",
                "X-Authorization": self.tk,
            })
            if self._ is None:
                self.jwt = self.get_jwt(self.browser_id, self.api_headers, ss, timeout, proxies)
                 
                self._=1
            self.api_headers.update({"T-Authorization": self.jwt}) 
            form_data = {
                "browser_id": self.browser_id,
                "cached": "true",
                "dict": "true",
                "media": "text",
                "os_type": "web",
                "replaced": "true",
                "request_id": "web_fanyi",
                "source": query_text,
                "trans_type": 'ja2zh',
            } 
            _ = ss.options(self.api_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
            r = ss.post(self.api_url, headers=self.api_headers, json=form_data, timeout=timeout, proxies=proxies)
            r.raise_for_status()
            data = r.json() 
        self.query_count += 1
        self.api_headers.pop('T-Authorization')
        data['target'] = self.decrypt(data['target'])
        return   data['target']

from traceback import print_exc

class TS(basetrans):
    def inittranslator(self):  
        self.engine=Caiyun()
        self.engine._=None
    def translate(self,content): 
        try:
            return self.engine.caiyun_api(content)
        except:
            print_exc()
            
            self.inittranslator()
            return '出错了'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')