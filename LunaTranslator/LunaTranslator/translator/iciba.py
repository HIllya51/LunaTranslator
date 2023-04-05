import requests
import re
import urllib
import random
import time 
import hashlib
import functools

from utils.config import globalconfig 
class TranslatorError(Exception):
    pass
class Tse:
    def __init__(self):
        self.author = 'Ulion.Tse'

    @staticmethod
    def time_stat(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            t1 = time.time()
            r = func(*args, **kwargs)
            t2 = time.time()
            
            return r
        return _wrapper

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

    @staticmethod
    def check_language(from_language, to_language, language_map, output_zh=None, output_auto='auto'):
        auto_pool = ('auto', 'auto-detect')
        zh_pool = ('zh', 'zh-CN', 'zh-CHS', 'zh-Hans', 'zh-Hans_CN', 'cn', 'chi')
        from_language = output_auto if from_language in auto_pool else from_language
        from_language = output_zh if output_zh and from_language in zh_pool else from_language
        to_language = output_zh if output_zh and to_language in zh_pool else to_language

        if from_language != output_auto and from_language not in language_map:
            raise TranslatorError('Unsupported from_language[{}] in {}.'.format(from_language, sorted(language_map.keys())))
        elif to_language not in language_map:
            raise TranslatorError('Unsupported to_language[{}] in {}.'.format(to_language, sorted(language_map.keys())))
        elif from_language != output_auto and to_language not in language_map[from_language]:
           
            raise TranslatorError('Unsupported translation: from [{0}] to [{1}]!'.format(from_language, to_language))
        elif from_language == to_language:
            raise TranslatorError(f'from_language[{from_language}] and to_language[{to_language}] should not be same.')
        return from_language, to_language

    @staticmethod
    def en_tran(from_lang, to_lang, default_lang='en-US', default_translator='Itranslate'):
        if default_translator not in ('Itranslate', 'Lingvanex'):
            return from_lang, to_lang

        from_lang = default_lang if from_lang == 'en' else from_lang
        to_lang = default_lang if to_lang == 'en' else to_lang
        from_lang = default_lang.replace('-', '_') if default_translator == 'Lingvanex' and '-' in from_lang else from_lang
        to_lang = default_lang.replace('-', '_') if default_translator == 'Lingvanex' and '-' in to_lang else to_lang
        warnings.warn(f'Unsupported [language=en] with [{default_translator}]! Please specify it.')
        warnings.warn(f'default languages: [{from_lang}, {to_lang}]')
        return from_lang, to_lang

    @staticmethod
    def make_temp_language_map(from_language, to_language):
        warnings.warn('Did not get a complete language map. And do not use `from_language="auto"`.')
        if not (to_language != 'auto' and from_language != to_language):
            raise TranslatorError("to_language != 'auto' and from_language != to_language")
        lang_list = [from_language, to_language]
        return {}.fromkeys(lang_list, lang_list) if from_language != 'auto' else {from_language: to_language, to_language: to_language}

    @staticmethod
    def check_query_text(query_text, if_ignore_limit_of_length=False, limit_of_length=5000):
        if not isinstance(query_text, str):
            raise TranslatorError('query_text is not string type.')
        query_text = query_text.strip()
        length = len(query_text)
        if length >= limit_of_length and not if_ignore_limit_of_length:
            raise TranslatorError('The length of the text to be translated exceeds the limit.')
        else:
            if length >= limit_of_length:
                warnings.warn(f'The translation ignored the excess[above {limit_of_length}]. Length of `query_text` is {length}.')
                warnings.warn('The translation result will be incomplete.')
                return query_text[:limit_of_length - 1]
        return query_text


class Iciba(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://www.iciba.com/fy'
        self.api_url = 'https://ifanyi.iciba.com/index.php'
        self.host_headers = self.get_headers(self.host_url, if_api=False, if_ajax_for_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=True, if_json_for_api=False)
        self.language_headers = self.get_headers(self.host_url, if_api=False, if_json_for_api=True)
        self.language_map = None
        self.s_y2 = 'ifanyiweb8hc9s98e'
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = 3000

    def get_language_map(self, api_url, ss, headers, timeout, proxies):
        params = {'c': 'trans', 'm': 'getLanguage', 'q': 0, 'type': 'en', 'str': ''}
        dd = ss.get(api_url, params=params, headers=headers, timeout=timeout, proxies=proxies).json()
        lang_list = sorted(list(set([lang for d in dd for lang in dd[d]])))
        return {}.fromkeys(lang_list, lang_list)

    # @Tse.time_stat
    def iciba_api(self, proxy,query_text: str, from_language: str = 'ja', to_language: str = 'zh-CN', **kwargs)  :
         
        """
        https://www.iciba.com/fy
        :param query_text: str, must.
        :param from_language: str, default 'auto'.
        :param to_language: str, default 'en'.
        :param **kwargs:
                :param if_ignore_limit_of_length: boolean, default False.
                :param is_detail_result: boolean, default False.
                :param timeout: float, default None.
                :param proxies: dict, default None.
                :param sleep_seconds: float, default `random.random()`.
        :return: str or dict
        """
        is_detail_result = kwargs.get('is_detail_result', False)
        timeout= globalconfig['translatortimeout'] 
        proxies=proxy
        sleep_seconds = kwargs.get('sleep_seconds', random.random())
        if_ignore_limit_of_length = kwargs.get('if_ignore_limit_of_length', False)
        query_text = self.check_query_text(query_text, if_ignore_limit_of_length, limit_of_length=self.input_limit)
        delete_temp_language_map_label = 0
        if not query_text:
            return ''

        with requests.Session() as ss:
            _ = ss.get(self.host_url, headers=self.host_headers, timeout=timeout, proxies=proxies)
             

            sign = hashlib.md5(f"6key_web_fanyi{self.s_y2}{query_text}".encode()).hexdigest()[:16]  # strip()
            params = {'c': 'trans', 'm': 'fy', 'client': 6, 'auth_user': 'key_web_fanyi', 'sign': sign}
            form_data = {'from': from_language, 'to': to_language, 'q': query_text}
            r = ss.post(self.api_url, headers=self.api_headers, params=params, data=form_data, timeout=timeout, proxies=proxies)
            
            data = r.json()

        if delete_temp_language_map_label != 0:
            self.language_map = None
        time.sleep(sleep_seconds)
        self.query_count += 1
        return data if is_detail_result else data['content'] if data.get('isSensitive') == 1 else data['content']['out']


from traceback import print_exc

from translator.basetranslator import basetrans
class TS(basetrans):
    def langmap(self):
        return {"cht":"cht"}
    def inittranslator(self):  
        self.engine=Iciba()
        self.engine._=None
    def translate(self,content):  
            return self.engine.iciba_api(self.proxy, content,self.srclang,self.tgtlang)
         