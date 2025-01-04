import re

from language import Languages
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CHS"}

    def translate(self, content):

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        params = {
            "keyword": content,
            "transfrom": self.srclang,
            "transto": self.tgtlang,
            "model": "general",
        }

        res = self.proxysession.get(
            "https://fanyi.sogou.com/text", params=params, headers=headers
        )
        res = re.search(
            '<p id="trans-result" class="output-val" style="white-space: pre-line">([\\s\\S]*?)</p>',
            res.text,
        )

        res = res.groups()[0]

        return res
