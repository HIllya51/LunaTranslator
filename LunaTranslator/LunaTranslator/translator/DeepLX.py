from myutils.config import static_data
import time
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        x = {_: _.upper() for _ in static_data["language_list_translator_inner"]}
        x.pop("cht")
        return x  # {"zh":"ZH","ja":"JA","en":"EN","es":"ES","fr":"FR","ru":"RU"}

    def translate(self, query):
        self.checkempty(["api"])
        payload = {
            "text": query,
            "source_lang": self.srclang,
            "target_lang": self.tgtlang,
        }

        response = self.proxysession.post(self.config["api"], json=payload)

        try:
            return response.json()["data"]
        except:
            raise Exception(response.text)
