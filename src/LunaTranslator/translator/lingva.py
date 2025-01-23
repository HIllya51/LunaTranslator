from urllib.parse import quote_plus
from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.TradChinese: "zh_HANT"}

    def translate(self, content):

        x = self.proxysession.get(
            "https://"
            + self.config["host"]
            + "/api/v1/%s/%s/%s" % (self.srclang, self.tgtlang, quote_plus(content)),
        ).json()
        return x["translation"]
