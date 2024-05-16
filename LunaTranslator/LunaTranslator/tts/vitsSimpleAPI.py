import requests
import time, os
from tts.basettsclass import TTSbase
from urllib.parse import quote


class TTS(TTSbase):
    def getvoicelist(self):
        responseVits = requests.get(
            f"http://127.0.0.1:{self.config['Port']}/voice/speakers"
        ).json()
        self.voicelist = []

        # 获取所有模型类型，对于每个模型类型下的模型信息，将其 modelType、id、name 合成一个字符串
        modelTypes = responseVits.keys()
        for modelType in modelTypes:
            vits_data = responseVits[modelType]
            for item in vits_data:
                model_info = f'{modelType}_{item["id"]}_{item["name"]}'
                self.voicelist.append(model_info)
        return self.voicelist

    def voiceshowmap(self, voice):
        return voice

    def speak(self, content, rate, voice, voiceidx):
        encoded_content = quote(content)
        idx = int(voice.split("_")[1])
        model = str.lower(voice.split("_")[0])
        response = requests.get(
            f"http://127.0.0.1:{self.config['Port']}/voice/{model}?text={encoded_content}&id={idx}&lang=auto&prompt_lang=auto&format=wav&preset={self.config['preset']}"
        ).content
        fname = str(time.time())
        os.makedirs("./cache/tts/", exist_ok=True)
        with open("./cache/tts/" + fname + ".wav", "wb") as ff:
            ff.write(response)

        return "./cache/tts/" + fname + ".wav"
