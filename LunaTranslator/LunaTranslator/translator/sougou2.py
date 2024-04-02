import re
from urllib.parse import quote
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CHS"}

    def translate(self, content):

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50",
            "sec-ch-ua": '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        res = self.session.get(
            "https://fanyi.sogou.com/text?keyword="
            + quote(content)
            + "&transfrom="
            + self.srclang
            + "&transto"
            + self.tgtlang
            + "&model=general",
            headers=headers,
        )
        res = re.search(
            '<p id="trans-result" class="output-val" style="white-space: pre-line">([\\s\\S]*?)</p>',
            res.text,
        )

        res = res.groups()[0]

        return res
