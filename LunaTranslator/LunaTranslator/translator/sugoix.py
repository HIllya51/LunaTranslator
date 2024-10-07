import requests, os
from translator.basetranslator import basetrans
from myutils.subproc import subproc_w, autoproc


class TS(basetrans):
    def translate(self, query):

        json_data = {
            "content": query,
            "message": "translate sentences",
        }

        response = self.proxysession.post(self.config["api"], json=json_data)
        try:
            return response.json()
        except:
            raise Exception(response.text)
