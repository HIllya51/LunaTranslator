import base64
from tts.basettsclass import TTSbase, TTSResult


class TTS(TTSbase):
    def getvoicelist(self):
        _ = [
            "jp_male_satoshi",
            "jp_female_mai",
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
            "en_male_adam",
            "tts.other.BV027_streaming",
            "en_male_bob",
            "tts.other.BV032_TOBI_streaming",
            "tts.other.BV516_streaming",
            "en_female_sarah",
            "fr_male_enzo",
            "tts.other.BV078_streaming",
        ]
        _v = [
            "jp_日语男声",
            "jp_日语女声",
            "zh_嘻哈歌手",
            "zh_男主播",
            "zh_女主播",
            "zh_东北男声",
            "zh_粤语男声",
            "zh_台湾女声",
            "zh_四川女声",
            "zh_影视配音",
            "zh_清新女声",
            "zh_少儿故事",
            "en_美式男声",
            "en_美式女声",
            "en_英式男声",
            "en_英式女声",
            "en_澳洲男声",
            "en_澳洲女声",
            "fr_法语男声",
            "fr_法语女声",
        ]
        return _, _v

    def speak(self, content, voice, _):

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
