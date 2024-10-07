from urllib import parse
from myutils.config import static_data
from translator.basetranslator import basetrans


class TS(basetrans):

    @property
    def srclang(self):
        if self.srclang_1 == "cht":
            return "ZH"
        return self.srclang_1.upper()

    @property
    def tgtlang(self):
        if self.tgtlang_1 == "cht":
            return "ZH-HANT"
        return self.tgtlang_1.upper()

    def translate(self, query):
        if self.config["usewhich"] == 0:
            self.checkempty(["DeepL-Auth-Key"])
            appid = self.multiapikeycurrent["DeepL-Auth-Key"]
            endpoint = "https://api-free.deepl.com/v2/translate"
        elif self.config["usewhich"] == 1:
            self.checkempty(["DeepL-Auth-Key-2"])
            appid = self.multiapikeycurrent["DeepL-Auth-Key-2"]
            endpoint = "https://api.deepl.com/v2/translate"

        headers = {
            "Authorization": "DeepL-Auth-Key " + appid,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = (
            "text="
            + parse.quote(query)
            + "&target_lang="
            + self.tgtlang
            + "&source_lang="
            + self.srclang
        )

        response = self.proxysession.post(
            endpoint, headers=headers, verify=False, data=data
        )

        try:
            return response.json()["translations"][0]["text"]
        except:
            raise Exception(response.text)
