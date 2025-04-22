import base64
from tts.basettsclass import TTSbase, TTSResult


class TTS(TTSbase):
    langs = {
        "en": [
            "en_male_adam",
            "tts.other.BV027_streaming",
            "en_male_bob",
            "tts.other.BV032_TOBI_streaming",
            "tts.other.BV516_streaming",
            "en_female_sarah",
        ],
        "jp": ["jp_male_satoshi", "jp_female_mai"],
        "zh": [
            "zh_male_rap",
            "zh_male_zhubo",
            "zh_female_zhubo",
            "tts.other.BV021_streaming",
            "tts.other.BV026_streaming",
            "tts.other.BV025_streaming",
            "zh_female_sichuan",
            "zh_male_xiaoming",
            "zh_female_qingxin",
            "zh_female_story",
        ],
        "ko": ["kr_male_gye", "tts.other.BV059_streaming"],
        "br": ["pt_female_alice", "tts.other.BV531_streaming"],
        "pt": ["pt_female_alice", "tts.other.BV531_streaming"],
        "es": ["es_male_george", "tts.other.BV065_streaming"],
        "id": ["id_female_noor", "tts.other.BV160_streaming"],
        "de": ["de_female_sophie"],
        "fr": ["fr_male_enzo", "tts.other.BV078_streaming"],
        "ms": ["tts.other.BV092_streaming"],
        "vi": ["tts.other.BV075_streaming", "tts.other.BV074_streaming"],
        "ru": ["tts.other.BV068_streaming"],
        "tr": ["tts.other.BV083_streaming"],
        "it": ["tts.other.BV087_streaming"],
        "ar": ["tts.other.BV570_streaming"],
    }

    voicesnames = {
        "en_male_adam": "美式男声",
        "tts.other.BV027_streaming": "美式女声",
        "en_male_bob": "英式男声",
        "tts.other.BV032_TOBI_streaming": "英式女声",
        "tts.other.BV516_streaming": "澳洲男声",
        "en_female_sarah": "澳洲女声",
        "zh_male_rap": "嘻哈歌手",
        "zh_male_zhubo": "男主播",
        "zh_female_zhubo": "女主播",
        "tts.other.BV021_streaming": "东北男声",
        "tts.other.BV026_streaming": "粤语男声",
        "tts.other.BV025_streaming": "台湾女声",
        "zh_female_sichuan": "四川女声",
        "zh_male_xiaoming": "影视配音",
        "zh_female_qingxin": "清新女声",
        "zh_female_story": "少儿故事",
        "jp_male_satoshi": "日语男声",
        "jp_female_mai": "日语女声",
        "kr_male_gye": "韩语男声",
        "tts.other.BV059_streaming": "韩语女声",
        "es_male_george": "西语男声",
        "tts.other.BV065_streaming": "西语女声",
        "pt_female_alice": "葡语女声",
        "tts.other.BV531_streaming": "葡语男声",
        "id_female_noor": "印尼女声",
        "tts.other.BV160_streaming": "印尼男声",
        "de_female_sophie": "德语女声",
        "fr_male_enzo": "法语男声",
        "tts.other.BV078_streaming": "法语女声",
        "tts.other.BV092_streaming": "马来女声",
        "tts.other.BV075_streaming": "越南男声",
        "tts.other.BV074_streaming": "越南女声",
        "tts.other.BV068_streaming": "俄语女声",
        "tts.other.BV083_streaming": "土耳其男声",
        "tts.other.BV087_streaming": "意语男声",
        "tts.other.BV570_streaming": "阿语男声",
    }

    def getvoicelang(self, k):
        for lang, vv in self.langs.items():
            if k in vv:
                return lang
        return None

    def getvoicelist(self):

        ks = sorted(self.voicesnames.keys())
        vs = ["{} {}".format(self.getvoicelang(k), self.voicesnames[k]) for k in ks]
        zipped_lists = zip(vs, ks)
        sorted_pairs = sorted(zipped_lists)
        vs, ks = zip(*sorted_pairs)
        return ks, vs

    def speak(self, content, voice, _):
        vlang = self.getvoicelang(voice)
        if vlang and (self.srclang in self.langs) and (self.srclang != vlang):
            voice = self.langs[self.srclang][0]
        headers = {
            "authority": "translate.volcengine.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "chrome-extension://klgfhbdadaspgppeadghjjemk",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }

        json_data = {
            "text": content,
            "speaker": voice,
        }  #
        response = self.proxysession.post(
            "https://translate.volcengine.com/crx/tts/v1/",
            headers=headers,
            json=json_data,
        )
        try:
            b64 = base64.b64decode(response.json()["audio"]["data"])
            return TTSResult(b64, "mp3")
        except:
            raise Exception(response)
