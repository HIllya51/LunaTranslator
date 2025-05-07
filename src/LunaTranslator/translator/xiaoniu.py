from translator.basetranslator import basetrans

from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.TradChinese: "cht"}

    def translate(self, query):
        self.checkempty(["apikey"])

        apikey = self.multiapikeycurrent["apikey"]

        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
        }

        params = {
            "from": self.srclang,
            "to": self.tgtlang,
            "src_text": query,
            "apikey": apikey,
        }
        response = self.proxysession.post(
            "https://api.niutrans.com/NiuTransServer/translation",
            headers=headers,
            data=params,
            verify=False,
        )

        try:
            return response.json()["tgt_text"]
        except:
            raise Exception(response)
