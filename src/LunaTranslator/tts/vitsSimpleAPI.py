from myutils.utils import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
import functools
from gui.customparams import customparams, getcustombodyheaders

vitsparams = functools.partial(customparams, stringonly=True)


class TTS(TTSbase):
    def getvoicelist(self):
        responseVits: dict = self.proxysession.get(
            urlpathjoin(self.config["URL"], "voice/speakers"),
            headers={"ngrok-skip-browser-warning": "true"},
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
        extrabody, _ = getcustombodyheaders(self.config.get("customparams"))
        query.update(extrabody)
        response = self.proxysession.get(
            urlpathjoin(self.config["URL"], "voice/" + model.lower()),
            params=query,
            headers={"ngrok-skip-browser-warning": "true"},
        ).content

        return response
