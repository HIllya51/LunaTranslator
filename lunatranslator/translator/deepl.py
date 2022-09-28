 
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


class Deepl(Tse):
    def __init__(self):
        super().__init__()
        self.host_url = 'https://www.deepl.com/translator'
        self.api_url = 'https://www2.deepl.com/jsonrpc'
        self.host_headers = self.get_headers(self.host_url, if_api=False)
        self.api_headers = self.get_headers(self.host_url, if_api=True, if_ajax_for_api=False, if_json_for_api=True)
        self.api_headers.update({'TE': 'trailers'})
        self.request_id = random.randrange(100, 10000) * 10000 + 4
        self.language_map = None
        self.query_count = 0
        self.output_zh = 'zh'
        self.input_limit = 5000
 
    def split_sentences_param(self, query_text, from_language):
        params = {'method': 'LMT_split_into_sentences'}
        data = {
            'id': self.request_id + 0,
            'jsonrpc': '2.0',
            'params': {
                'texts': [query_text],
                'lang': {
                    'lang_user_selected': from_language,
                    'preference': {
                        'weight': {},
                        'default': 'default',
                    },
                },
            },
        }
        data.update(params)
        return params, data

    def context_sentences_param(self, sentences, from_language, to_language):
        sentences = [''] + sentences + ['']
        params = {'method': 'LMT_handle_jobs'}
        data = {
            'id': self.request_id + 1,
            'jsonrpc': ' 2.0',
            'params': {
                'priority': 1,  # -1 if 'quality': 'fast'
                'commonJobParams': {
                    # 'regionalVariant': 'en-US',
                    'browserType': 1,
                    'formality': None,
                },
                'timestamp': int(time.time() * 1000),
                'jobs': [
                    {
                        'kind': 'default',
                        # 'quality': 'fast', # -1
                        'raw_en_sentence': sentences[i],
                        'raw_en_context_before': [sentences[i - 1]] if sentences[i - 1] else [],
                        'raw_en_context_after': [sentences[i + 1]] if sentences[i + 1] else [],
                        'preferred_num_beams': 1 if len(sentences) >= 4 else 4,  # 1 if two sentences else 4, len>=2+2
                    } for i in range(1, len(sentences) - 1)
                ],
                'lang': {
                    'preference': {
                        'weight': {},
                        'default': 'default',
                    },
                    'source_lang_computed': from_language,
                    'target_lang': to_language,
                },
            },
        }
        data.update(params)
        return params, data

    # @Tse.time_stat
    def deepl_api(self, query_text): 
        timeout = 5
        proxies ={'http': None,'https': None}   
        delete_temp_language_map_label = 0
        if not query_text:
            return ''

        with requests.Session() as ss:
            
            from_language, to_language='ja','zh'

            ss_params, ss_data = self.split_sentences_param(query_text, from_language)
            # _ = ss.options(self.api_url, params=ss_params, headers=self.api_headers, timeout=timeout, proxies=proxies)
            r_ss = ss.post(self.api_url, params=ss_params, json=ss_data, headers=self.api_headers, timeout=timeout, proxies=proxies)
            r_ss.raise_for_status()
            ss_data = r_ss.json()
            ss_sentences = ss_data['result']['splitted_texts'][0]

            cs_params, cs_data = self.context_sentences_param(ss_sentences, from_language, to_language)
            # _ = ss.options(self.api_url, params=cs_params, headers=self.api_headers, timeout=timeout, proxies=proxies)
            r_cs = ss.post(self.api_url, params=cs_params, json=cs_data, headers=self.api_headers, timeout=timeout, proxies=proxies)
            r_cs.raise_for_status()
            data = r_cs.json()

        if delete_temp_language_map_label != 0:
            self.language_map = None 
        self.request_id += 3
        self.query_count += 1
        return   ' '.join(item['beams'][0]['postprocessed_sentence'] for item in data['result']['translations'])

from traceback import print_exc

class TS(basetrans):
    def inittranslator(self): 
        self.typename='deepl'
        self.engine=Deepl()
        self.engine._=None
    def realfy(self,content): 
        try:
            return self.engine.deepl_api(content)
        except:
            print_exc()
            return '出错了'
if __name__=='__main__':
    a=BINGFY()
    a.gettask('はーい、おやすみなさい')