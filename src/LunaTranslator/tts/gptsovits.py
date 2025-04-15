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
        js = dict(text=content)
        if self.config["apiv"] == "v2":
            url = urlpathjoin(self.config["URL"], "tts")
            js.update(text_lang=self.srclang, speed_factor=speed)
        else:
            url = self.config["URL"]
            js.update(text_language=self.srclang, speed=speed)
        extrabody, extraheader = getcustombodyheaders(self.config.get("customparams"))

        js.update(extrabody)
        response = self.proxysession.post(url, headers=extraheader, json=js).content
        return response
