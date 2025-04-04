import re
from language import Languages
from translator.basetranslator import basetrans


class TS(basetrans):

    def init(self):
        mainjsurl = self.proxysession.get(
            "https://itranslate-webapp-production.web.app/manifest.json"
        ).json()["main.js"]
        mainjs = self.proxysession.get(mainjsurl).text
        self.api_key = re.compile('"API-KEY":"(.*?)"').findall(mainjs)[0]

    def translate(self, content):
        form_data = {
            "source": {
                "dialect": self.srclang,
                "text": content,
                "with": ["synonyms"],
            },
            "target": {"dialect": self.tgtlang},
        }
        r = self.proxysession.post(
            "https://web-api.itranslateapp.com/v3/texts/translate",
            headers={"API-KEY": self.api_key},
            json=form_data,
        )
        try:
            return r.json()["target"]["text"]
        except:
            raise Exception(r)

    def langmap(self):
        return {
            Languages.English: "en-UK",
            Languages.Chinese: "zh-CN",
            Languages.Spanish: "es-ES",
            Languages.French: "fr-FR",
            Languages.TradChinese: "zh-TW",
        }
