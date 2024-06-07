from traceback import print_exc
import requests
import base64
from tts.basettsclass import TTSbase


class TTS(TTSbase):
    def getvoicelist(self):
        return [
            "jp_male_satoshi",
            "jp_female_mai",
            "zh_male_rap",
            "zh_female_sichuan",
            "zh_male_xiaoming",
            "zh_male_zhubo",
            "zh_female_zhubo",
            "zh_female_qingxin",
            "zh_female_story",
            "en_male_adam",
            "en_male_bob",
            "en_female_sarah",
        ]

    def speak(self, content, rate, voice, voiceidx):

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
        response = requests.post(
            "https://translate.volcengine.com/crx/tts/v1/",
            headers=headers,
            json=json_data,
            proxies=self.proxy,
        )
        b64 = base64.b64decode(response.json()["audio"]["data"])

        return b64
