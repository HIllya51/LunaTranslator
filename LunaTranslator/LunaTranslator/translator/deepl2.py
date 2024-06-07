from myutils.config import static_data
import time
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        x = {_: _.upper() for _ in static_data["language_list_translator_inner"]}
        x.pop("cht")
        return x  # {"zh":"ZH","ja":"JA","en":"EN","es":"ES","fr":"FR","ru":"RU"}

    def translate(self, content):
        headers = {
            "authority": "www2.deepl.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7",
            "authorization": "None",
            "content-type": "application/json; charset=utf-8",
            "origin": "chrome-extension://cofdbpoegempjloogbagkncekinflcnj",
            "referer": "https://www.deepl.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "user-agent": "DeepLBrowserExtension/1.11.2 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        }

        json_data = {
            "jsonrpc": "2.0",
            "method": "LMT_handle_texts",
            "params": {
                "texts": [
                    {
                        "text": content,
                    },
                ],
                "splitting": "newlines",
                "lang": {
                    "target_lang": self.tgtlang,
                    "source_lang_user_selected": self.srclang,
                    # 'preference': {
                    #     'weight': {
                    #         'BG': 0.00088,
                    #         'CS': 0.03823,
                    #         'DA': 0.05825,
                    #         'DE': 0.02246,
                    #         'EL': 0.0015400000000000001,
                    #         'EN': 2.6768500000000004,
                    #         'ES': 0.08243,
                    #         'ET': 0.02381,
                    #         'FI': 0.01895,
                    #         'FR': 0.24500000000000002,
                    #         'HU': 0.02153,
                    #         'ID': 0.04993,
                    #         'IT': 0.057690000000000005,
                    #         'JA': 0.00354,
                    #         'KO': 0.0027400000000000002,
                    #         'LT': 0.01564,
                    #         'LV': 0.02577,
                    #         'NB': 0.03724,
                    #         'NL': 0.03622,
                    #         'PL': 0.02185,
                    #         'PT': 0.056060000000000006,
                    #         'RO': 0.044660000000000005,
                    #         'RU': 0.0012300000000000002,
                    #         'SK': 0.021070000000000002,
                    #         'SL': 0.023450000000000002,
                    #         'SV': 0.035730000000000005,
                    #         'TR': 0.010920000000000001,
                    #         'UK': 0.0017800000000000001,
                    #         'ZH': 0.0054600000000000004,
                    #     },
                    # },
                },
                "commonJobParams": {},
                "timestamp": int(time.time() * 1000),
            },
            "id": 3266547795,
        }

        response = self.proxysession.post(
            "https://www2.deepl.com/jsonrpc?client=chrome-extension,1.11.2",
            headers=headers,
            json=json_data,
        )

        try:
            return response.json()["result"]["texts"][0]["text"]
        except:
            raise Exception(response.json())
