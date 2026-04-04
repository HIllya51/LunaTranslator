from myutils.config import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
import json
from urllib.parse import quote

# https://github.com/chromium/chromium/blob/main/chrome/browser/resources/network_speech_synthesis/tts_extension.js


class TTS(TTSbase):
    arg_support_pitch = False

    def getvoicelist(self):
        voices = r"""
[
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "de-DE",
        "voice_name": "Google Deutsch",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "en-US",
        "voice_name": "Google US English",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "en-GB",
        "voice_name": "Google UK English Female",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "male",
        "lang": "en-GB",
        "voice_name": "Google UK English Male",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "es-ES",
        "voice_name": "Google español",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "es-US",
        "voice_name": "Google español de Estados Unidos",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "fr-FR",
        "voice_name": "Google français",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "hi-IN",
        "voice_name": "Google हिन्दी",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "id-ID",
        "voice_name": "Google Bahasa Indonesia",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "it-IT",
        "voice_name": "Google italiano",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "ja-JP",
        "voice_name": "Google 日本語",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "ko-KR",
        "voice_name": "Google 한국의",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "nl-NL",
        "voice_name": "Google Nederlands",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "pl-PL",
        "voice_name": "Google polski",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "pt-BR",
        "voice_name": "Google português do Brasil",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "ru-RU",
        "voice_name": "Google русский",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "zh-CN",
        "voice_name": "Google 普通话（中国大陆）",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "zh-HK",
        "voice_name": "Google 粤語（香港）",
        "remote": true
      },
      {
        "event_types": [ "start", "end", "error" ],
        "gender": "female",
        "lang": "zh-TW",
        "voice_name": "Google 國語（臺灣）",
        "remote": true
      }
    ]
"""
        voices = json.loads(voices)
        voicelist = []
        internal = []
        for _ in voices:
            internal.append((_["lang"], _["gender"]))
            voicelist.append(_["voice_name"])
        return internal, voicelist

    def init(self):
        self.SPEECH_SERVER_URL_ = (
            "https://www.google.com/speech-api/v2/synthesize?"
            + "enc=mpeg&client=chromium"
        )

        self.LANG_AND_GENDER_TO_VOICE_NAME_ = {
            "en-gb-male": "rjs",
            "en-gb-female": "fis",
        }

    def speak(self, content, voice: "tuple[str, str]", param: SpeechParam):
        lang, gender = voice
        key = f"{lang.lower()}-{gender}"
        voiceName = self.LANG_AND_GENDER_TO_VOICE_NAME_.get(key)

        url = self.SPEECH_SERVER_URL_

        url += "&key=" + self.config["key"]  # 可以chrome里调用js api，然后抓包
        url += "&text=" + quote(content)
        url += "&lang=" + lang.lower()

        if voiceName:
            url += "&name=" + voiceName

        # Input rate is between 0.1 and 10.0 with a default of 1.0.
        # Output speed is between 0.0 and 1.0 with a default of 0.5.
        url += "&speed=" + str(0.5 + param.speed)

        # Input pitch is between 0.0 and 2.0 with a default of 1.0.
        # Output pitch is between 0.0 and 1.0 with a default of 0.5.
        url += "&pitch=" + str(0.5 + param.pitch)

        response = self.proxysession.get(url, stream=True)

        return response
