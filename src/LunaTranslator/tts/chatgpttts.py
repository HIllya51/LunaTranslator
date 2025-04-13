from tts.basettsclass import TTSbase, SpeechParam
from myutils.utils import createurl, common_list_models
from myutils.proxy import getproxy
from gui.customparams import getcustombodyheaders, customparams


def list_models(typename, regist):
    return common_list_models(
        getproxy(("reader", typename)),
        regist["API接口地址"](),
        regist["SECRET_KEY"]().split("|")[0],
        checkend="/audio/speech",
    )


class TTS(TTSbase):
    def getvoicelist(self):
        voice = self.config["voice_list"]
        return voice, voice

    def createheaders(self):
        _ = {}
        curkey = self.multiapikeycurrent["SECRET_KEY"]
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

        extrabody, extraheader = getcustombodyheaders(self.config.get("customparams"))
        headers.update(extraheader)
        json_data.update(extrabody)
        response = self.proxysession.post(
            self.createurl(), headers=headers, json=json_data
        )
        if 400 <= response.status_code < 600:
            raise Exception(response)

        return response.content
