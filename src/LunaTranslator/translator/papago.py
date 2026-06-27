from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CN", Languages.TradChinese: "zh-TW"}

    def translate(self, content):
        data = {
            "dict": "true",
            "dictDisplay": "30",
            "honorific": "false",
            "useGlossary": "false",
            "source": self.srclang,
            "target": self.tgtlang,
            "text": content,
        }

        r = self.proxysession.post(
            "https://papago.naver.com/api/text/translation", data=data
        )

        data = r.json()
        try:
            return data["translatedText"]
        except:
            raise Exception(data)
