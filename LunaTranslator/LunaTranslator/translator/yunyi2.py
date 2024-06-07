import json
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-cn", "en": "en-us", "cht": "zh-tw"}

    def translate(self, content):

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Origin": "https://online.cloudtranslation.com",
            "Pragma": "no-cache",
            "Referer": "https://online.cloudtranslation.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42",
            "sec-ch-ua": '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        response = self.proxysession.post(
            "https://online.cloudtranslation.com/api/v1.0/request_translate/try_translate",
            data={
                "type": "text",
                "text": content,
                "src_lang": self.srclang,
                "tgt_lang": self.tgtlang,
                "domain": "general",
            },
            headers=headers,
        )
        try:
            return json.loads(response.json()["data"]["data"])["translation"]
        except:
            raise Exception(json.dumps(response.json(), ensure_ascii=False))
