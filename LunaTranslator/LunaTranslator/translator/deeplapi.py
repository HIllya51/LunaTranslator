from urllib import parse
from myutils.config import static_data
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        x = {_: _.upper() for _ in static_data["language_list_translator_inner"]}
        x.pop("cht")
        return x

    def translate(self, query):
        self.checkempty(["DeepL-Auth-Key"])

        appid = self.multiapikeycurrent["DeepL-Auth-Key"]

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
            "https://api.deepl.com/v2/translate",
            headers=headers,
            verify=False,
            data=data,
        )

        try:
            _ = response.json()["translations"][0]["text"]

            self.countnum(query)
            return _
        except:
            raise Exception(response.text)
