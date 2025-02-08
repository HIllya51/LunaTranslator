from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CN", Languages.TradChinese: "zh-TW"}

    def translate(self, query):
        self.checkempty(["key"])

        key = self.multiapikeycurrent["key"]
        params = {
            "key": key,
            "target": self.tgtlang,
            "q": (query),
        }
        if self.srclang != Languages.Auto:
            params["source"] = self.srclang
        response = self.proxysession.get(
            "https://translation.googleapis.com/language/translate/v2/", params=params
        )

        try:
            return response.json()["data"]["translations"][0]["translatedText"]
        except:
            raise Exception(response)
