from myutils.utils import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
from gui.customparams import customparams, getcustombodyheaders


class TTS(TTSbase):
    def getvoicelist(self):
        return [""], [""]

    def speak(self, content, voice, param: SpeechParam):
        js = dict(text=content)
        if self.config["apiv"] == "v2":
            url = urlpathjoin(self.config["URL"], "tts")
            js.update(text_lang=self.srclang)
        else:
            url = self.config["URL"]
            js.update(text_language=self.srclang)
        extrabody, extraheader = getcustombodyheaders(self.config.get("customparams"))

        js.update(extrabody)
        response = self.proxysession.get(url, headers=extraheader, json=js).content
        return response
