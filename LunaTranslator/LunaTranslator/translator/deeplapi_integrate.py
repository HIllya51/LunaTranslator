from urllib import parse
from myutils.config import static_data
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        x = {_: _.upper() for _ in static_data["language_list_translator_inner"]}
        x.pop("cht")
        return x

    def translate(self, query):
        if self.config["usewhich"] == 0:
            appid = self.multiapikeycurrent["DeepL-Auth-Key-1"]
            endpoint = "https://api-free.deepl.com/v2/translate"
            self.checkempty(["DeepL-Auth-Key-1"])
        elif self.config["usewhich"] == 1:
            appid = self.multiapikeycurrent["DeepL-Auth-Key-2"]
            endpoint = "https://api.deepl.com/v2/translate"
            self.checkempty(["DeepL-Auth-Key-2"])

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
            _ = response.json()["translations"][0]["text"]

            self.countnum(query)
            return _
        except:
            raise Exception(response.text)
