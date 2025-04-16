from myutils.utils import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
import functools
from gui.customparams import customparams, getcustombodyheaders

vitsparams = functools.partial(customparams, stringonly=True)


class TTS(TTSbase):
    def getvoicelist(self):
        extrabody, extraheader = getcustombodyheaders(self.config.get("customparams"))
        headers = {"ngrok-skip-browser-warning": "true"}
        headers.update(extraheader)
        responseVits: dict = self.proxysession.get(
            urlpathjoin(self.config["URL"], "voice/speakers"), headers=headers
        ).json()
        voicelist = []
        internal = []
        modelTypes = responseVits.keys()
        for modelType in modelTypes:
            vits_data = responseVits[modelType]
            for item in vits_data:
                lang_str = "/".join(item["lang"])
                model_info = "{}_{}_{}_{}".format(
                    modelType, item["id"], item["name"], lang_str
                )
                voicelist.append(model_info)
                internal.append((modelType, item["id"], item["name"]))
        return internal, voicelist

    def speak(self, content, voice, param: SpeechParam):
        if param.speed > 0:
            length = 1 - param.speed / 15
        else:
            length = 1 - param.speed / 5
        model, idx, _ = voice
        query = dict(text=content, id=idx, length=length)
        extrabody, extraheader = getcustombodyheaders(self.config.get("customparams"))
        headers = {"ngrok-skip-browser-warning": "true"}
        headers.update(extraheader)
        query.update(extrabody)
        response = self.proxysession.get(
            urlpathjoin(self.config["URL"], "voice/" + model.lower()),
            params=query,
            headers=headers,
        )

        return response
