from translator.basetranslator import basetrans
import json


class TS(basetrans):
    def translate(self, query):
        self.checkempty(["Token"])

        token = self.multiapikeycurrent["Token"]

        url = "http://api.interpreter.caiyunai.com/v1/translator"
        # WARNING, this token is a test token for new developers,
        # and it should be replaced by your token

        payload = {
            "source": query,
            "trans_type": self.srclang + "2" + self.tgtlang,
            "request_id": "demo",
            "detect": True,
        }
        headers = {
            "x-authorization": "token " + token,
        }
        response = self.proxysession.request("POST", url, json=payload, headers=headers)
        try:
            return response.json()["target"]
        except:
            raise Exception(response)
