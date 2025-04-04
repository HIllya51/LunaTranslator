import uuid
from translator.basetranslator import basetrans
import time
from language import Languages


class TS(basetrans):
    def get_clientKey(self):
        return "browser-firefox-110.0.0-Windows 10-{}-{}".format(
            uuid.uuid4(), int(time.time() * 1e3)
        )

    def split_sentence(self, data):
        index_pair_list = [
            [item["start"], item["start"] + item["len"]]
            for item in data["sentence_list"]
        ]
        index_list = [i for ii in index_pair_list for i in ii]
        return [
            data["text"][index_list[i] : index_list[i + 1]]
            for i in range(len(index_list) - 1)
        ]

    def init(self):
        self.host_url = "https://transmart.qq.com"
        self.api_url = "https://transmart.qq.com/api/imt"
        _ = self.proxysession.get(self.host_url).text

    def translate(self, content):

        client_key = self.get_clientKey()
        api_headers = {"Cookie": "client_key={}".format(client_key)}

        split_form_data = {
            "header": {
                "fn": "text_analysis",
                "client_key": client_key,
            },
            "type": "plain",
            "text": content,
            "normalize": {"merge_broken_line": "false"},
        }
        split_data = self.proxysession.post(self.api_url, json=split_form_data).json()
        text_list = self.split_sentence(split_data)

        api_form_data = {
            "header": {
                "fn": "auto_translation",
                "client_key": client_key,
            },
            "type": "plain",
            "model_category": "normal",
            "source": {
                "lang": self.srclang,
                "text_list": [""] + text_list + [""],
            },
            "target": {"lang": self.tgtlang},
        }
        r = self.proxysession.post(
            self.api_url, json=api_form_data, headers=api_headers
        )
        try:
            data = r.json()
            return "".join(data["auto_translation"])
        except:
            raise Exception(r)

    def langmap(self):
        return {Languages.TradChinese: "zh-tw"}
