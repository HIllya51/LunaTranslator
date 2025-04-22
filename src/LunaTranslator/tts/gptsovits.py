from myutils.utils import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
from gui.customparams import customparams, getcustombodyheaders


class TTS(TTSbase):
    def getvoicelist(self):
        return [""], [""]

    def speak(self, content, voice, param: SpeechParam):
        if param.speed > 0:
            speed = 1 + param.speed / 5
        else:
            speed = 1 + param.speed / 15
        query = dict(text=content)
        if self.config["apiv"] == "v2":
            url = urlpathjoin(self.config["URL"], "tts")
            query.update(text_lang=self.srclang, speed_factor=speed)
        else:
            url = self.config["URL"]
            query.update(text_language=self.srclang, speed=speed)
        extrabody, extraheader = getcustombodyheaders(self.config.get("customparams"), **locals())
        headers = {"ngrok-skip-browser-warning": "true"}
        headers.update(extraheader)
        query.update(extrabody)
        response = self.proxysession.get(url, headers=headers, params=query)
        return response
