from translator.basetranslator import basetrans
from myutils.utils import urlpathjoin


class TS(basetrans):

    def translate(self, query):
        self.checkempty(["apikey"])
        self.checkempty(["apiurl"])
        apikey = self.multiapikeycurrent["apikey"]
        url = urlpathjoin(self.config["apiurl"], "v3/translate?version=2018-05-01")
        data = {"text": [query], "target": self.tgtlang}
        if not self.is_src_auto:
            data.update({"source": self.srclang})

        response = self.proxysession.post(url, auth=("apikey", apikey), json=data)
        try:
            result = response.json()
            translation = result["translations"][0]["translation"]
            return translation
        except Exception as e:
            raise Exception(response)
