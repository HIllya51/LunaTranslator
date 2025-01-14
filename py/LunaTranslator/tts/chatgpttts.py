from tts.basettsclass import TTSbase, SpeechParam
from myutils.utils import urlpathjoin, createurl
from myutils.proxy import getproxy
import requests


def list_models(typename, regist):
    resp = requests.get(
        urlpathjoin(
            createurl(regist["API接口地址"]().strip(), checkend="/audio/speech")[
                : -len("audio/speech")
            ],
            "models",
        ),
        headers={
            "Authorization": "Bearer " + regist["SECRET_KEY"]().split("|")[0].strip()
        },
        proxies=getproxy(("reader", typename)),
    )
    try:
        return sorted([_["id"] for _ in resp.json()["data"]])
    except:
        raise Exception(resp)


class TTS(TTSbase):
    def getvoicelist(self):
        voice = self.config["voice_list"]
        return voice, voice

    def createheaders(self):
        _ = {}
        curkey = self.config["SECRET_KEY"]
        if curkey:
            # 部分白嫖接口可以不填，填了反而报错
            _.update({"Authorization": "Bearer " + curkey})
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            _.update({"api-key": curkey})

        return _

    @property
    def apiurl(self):
        return self.config["API接口地址"].strip()

    def createurl(self):
        if "openai.azure.com/openai/deployments/" in self.apiurl:
            return self.apiurl
        return createurl(self.apiurl, checkend="/audio/speech")

    def speak(self, content, voice, param: SpeechParam):

        headers = self.createheaders()
        if param.speed > 0:
            speed = 1 + 3 * param.speed / 10
        else:
            speed = 1 + 0.75 * param.speed / 10
        json_data = {
            "model": self.config["model"],
            "input": content,
            "voice": voice,
            "speed": speed,  # 0.25 to 4.0. 1.0 is the default.
        }

        response = requests.post(self.createurl(), headers=headers, json=json_data)
        return response.content
