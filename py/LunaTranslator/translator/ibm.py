from translator.basetranslator import basetrans
import json
from language import Languages


class TS(basetrans):

    def translate(self, query):
        self.checkempty(["apikey"])
        self.checkempty(["apiurl"])
        apikey = self.multiapikeycurrent["apikey"]
        url = self.config["apiurl"] + "/v3/translate?version=2018-05-01"
        headers = {"Content-Type": "application/json"}
        data = {"text": [query], "target": self.tgtlang}
        if self.srclang != Languages.Auto:
            data.update({"source": self.srclang})

        response = self.proxysession.post(
            url, auth=("apikey", apikey), headers=headers, data=json.dumps(data)
        )
        try:
            result = response.json()
            translation = result["translations"][0]["translation"]
            return translation
        except Exception as e:
            raise Exception(response)
