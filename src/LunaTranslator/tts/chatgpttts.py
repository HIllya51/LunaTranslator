from tts.basettsclass import TTSbase, SpeechParam
from myutils.utils import APIType, common_list_models
from myutils.proxy import getproxy
import base64, ctypes
from gui.customparams import getcustombodyheaders, customparams


def list_models(typename, regist):
    return common_list_models(
        getproxy(("reader", typename)),
        APIType(regist["API接口地址"]()),
        regist["SECRET_KEY"]().split("|")[0],
        checkend="/audio/speech",
    )


class TTS(TTSbase):
    arg_support_pitch = False

    def getvoicelist(self):
        voice = self.config["voice_list"]
        return voice, voice

    def createheaders(self, apitype: APIType):
        _ = {}
        curkey = self.multiapikeycurrent["SECRET_KEY"]
        if curkey:
            # 部分白嫖接口可以不填，填了反而报错
            _.update({"Authorization": "Bearer " + curkey})
        if apitype == APIType.azure:
            _.update({"api-key": curkey})

        return _

    def speak(self, content, voice, param: SpeechParam):

        if param.speed > 0:
            speed = 1 + 3 * param.speed / 10
        else:
            speed = 1 + 0.75 * param.speed / 10

        extrabody, extraheader = getcustombodyheaders(
            self.config.get("customparams"), **locals()
        )
        apitype = APIType(self.config["API接口地址"])
        if apitype == APIType.gemini:
            return self.request_gemini(
                apitype, content, voice, speed, extrabody, extraheader
            )
        else:
            return self.requestnormal(content, voice, speed, extrabody, extraheader)

    def requestnormal(
        self, apitype: APIType, content, voice, speed, extrabody, extraheader
    ):

        json_data = {
            "model": self.config["model"],
            "input": content,
            "voice": voice,
            "speed": speed,  # 0.25 to 4.0. 1.0 is the default.
        }

        headers = self.createheaders(apitype)
        headers.update(extraheader)
        json_data.update(extrabody)
        response = self.proxysession.post(
            apitype.finalurl("/audio/speech"),
            headers=headers,
            json=json_data,
            stream=True,
        )
        return response

    def request_gemini(
        self, apitype: APIType, content, voice, speed, extrabody, extraheader
    ):

        body = {
            "contents": [{"parts": [{"text": content}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
                },
            },
            "model": self.config["model"],
        }
        body.update(extrabody)
        response = self.proxysession.post(
            "{}/{}:generateContent".format(apitype.url, self.config["model"]),
            params={"key": self.multiapikeycurrent["SECRET_KEY"]},
            headers=extraheader,
            json=body,
        )
        try:
            b64: str = response.json()["candidates"][0]["content"]["parts"][0][
                "inlineData"
            ]["data"]
            # https://ai.google.dev/gemini-api/docs/speech-generation
            voicebs = base64.b64decode(b64.encode())
            wavheader = (
                b"RIFF"
                + bytes(ctypes.c_int(len(voicebs) + 70))
                + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\xc0]\x00\x00\x80\xbb\x00\x00\x02\x00\x10\x00LIST\x1a\x00\x00\x00INFOISFT\r\x00\x00\x00Lavf60.5.100\x00\x00data"
                + bytes(ctypes.c_int(len(voicebs)))
            )
            return wavheader + voicebs
        except:
            raise Exception(response)
