from language import Languages
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {
            Languages.Spanish: "spa",
            Languages.Korean: "kor",
            Languages.French: "fra",
            Languages.Japanese: "jp",
            Languages.TradChinese: "cht",
            Languages.Vietnamese: "vie",
            Languages.Ukrainian: "ukr",
            Languages.Arabic: "ara",
            Languages.Swedish: "swe",
            Languages.Latin: "lat",
        }

    def inittranslator(self):
        u = "https://fanyi.baidu.com"
        _ = self.proxysession.get(u)
        _ = self.proxysession.get(u)

    def translate(self, query):
        form_data = {
            "from": self.srclang,
            "to": self.tgtlang,
            "query": query,
            "source": "txt",
        }
        u = "https://fanyi.baidu.com/transapi"
        r = self.proxysession.post(u, data=form_data)
        try:
            return "\n".join([item["dst"] for item in r.json()["data"]])
        except:
            raise Exception(r)
