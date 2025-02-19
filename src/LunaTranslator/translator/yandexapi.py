from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):

    def translate(self, content):
        self.checkempty(["key"])

        key = self.multiapikeycurrent["key"]

        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        js = {
            "targetLanguageCode": self.tgtlang,
            "texts": [content],
        }
        if self.srclang != Languages.Auto:
            js["sourceLanguageCode"] = self.srclang
        response = self.proxysession.post(
            url, json=js, headers={"Authorization": "Api-Key " + key}
        )

        try:
            return response.json()["translations"][0]["text"]
        except:
            raise Exception(response)
