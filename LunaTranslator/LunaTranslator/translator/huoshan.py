import json
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"cht": "zh-Hant"}

    def translate(self, content):

        headers = {
            "authority": "translate.volcengine.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,ar;q=0.8,sq;q=0.7",
            "content-type": "application/json",
            "origin": "chrome-extension://klgfhbiooeogdfodpopgppeadghjjemk",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }

        json_data = {
            "text": content,
            "source_language": self.srclang,
            "target_language": self.tgtlang,
            "enable_user_glossary": False,
            "glossary_list": [],
            "category": "",
        }
        response = self.session.post(
            "https://translate.volcengine.com/crx/translate/v1/",
            headers=headers,
            json=json_data,
        )

        try:
            return response.json()["translation"]
        except:
            raise Exception(json.dumps(response.json(), ensure_ascii=False))
