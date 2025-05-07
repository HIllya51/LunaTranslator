from language import Languages
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {Languages.TradChinese: "zh-Hant"}

    def translate(self, content):

        headers = {
            "authority": "translate.volcengine.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7",
            "origin": "chrome-extension://klgfhbiooeogdfodpopgppeadghjjemk",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
        }

        json_data = {
            "text": content,
            "target_language": self.tgtlang,
            "enable_user_glossary": False,
            "glossary_list": [],
            "category": "",
        }
        if not self.is_src_auto:
            json_data["source_language"] = self.srclang
        response = self.proxysession.post(
            "https://translate.volcengine.com/crx/translate/v1/",
            headers=headers,
            json=json_data,
        )

        try:
            return response.json()["translation"]
        except:
            raise Exception(response)
