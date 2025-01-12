from myutils.utils import urlpathjoin
from tts.basettsclass import TTSbase, SpeechParam
from urllib.parse import quote


class TTS(TTSbase):
    def getvoicelist(self):
        responseVits = self.proxysession.get(
            urlpathjoin(self.config["URL"], self.config["voices"])
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
        encoded_content = quote(content)
        model, idx, _ = voice
        speak = self.config["speak2"].format(
            model_lower=model.lower(),
            model=model,
            id=idx,
            text=encoded_content,
            length=length,
        )
        response = self.proxysession.get(urlpathjoin(self.config["URL"], speak)).content

        return response
