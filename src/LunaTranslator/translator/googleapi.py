from translator.basetranslator import basetrans
from language import Languages
from html import unescape


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
        if not self.is_src_auto:
            params["source"] = self.srclang
        response = self.proxysession.get(
            "https://translation.googleapis.com/language/translate/v2/", params=params
        )

        try:
            return unescape(
                response.json()["data"]["translations"][0]["translatedText"]
            )
        except:
            raise Exception(response)
