import requests
from urllib.parse import urljoin
from tts.basettsclass import TTSbase
from urllib.parse import quote


class TTS(TTSbase):
    def getvoicelist(self):
        if self.config["voices"] == "":
            return [(0, 0, 0)], []
        responseVits = requests.get(
            urljoin(self.config["URL"], self.config["voices"])
        ).json()
        voicelist = []
        internal = []
        modelTypes = responseVits.keys()
        for modelType in modelTypes:
            vits_data = responseVits[modelType]
            for item in vits_data:
                model_info = f'{modelType}_{item["id"]}_{item["name"]}'
                voicelist.append(model_info)
                internal.append((modelType, item["id"], item["name"]))
        return internal, voicelist

    def speak(self, content, rate, voice):
        encoded_content = quote(content)
        model, idx, _ = voice
        speak = self.config["speak"].format(
            model_lower=model.lower(), model=model, id=idx, text=encoded_content
        )
        response = requests.get(urljoin(self.config["URL"], speak)).content

        return response
