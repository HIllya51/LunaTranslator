from translator.basetranslator import basetrans


class TS(basetrans):
    needzhconv = True

    def translate(self, content):
        self.checkempty(["key"])

        key = self.multiapikeycurrent["key"]

        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        js = {
            "targetLanguageCode": self.tgtlang,
            "texts": [content],
        }
        if not self.is_src_auto:
            js["sourceLanguageCode"] = self.srclang
        response = self.proxysession.post(
            url, json=js, headers={"Authorization": "Api-Key " + key}
        )

        try:
            return response.json()["translations"][0]["text"]
        except:
            raise Exception(response)
