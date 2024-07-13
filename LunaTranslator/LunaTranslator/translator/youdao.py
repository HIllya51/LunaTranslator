import time
import hashlib
from translator.basetranslator import basetrans
import random


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CHS"}

    def youdaoSIGN(self, useragent, e):
        t = hashlib.md5(bytes(useragent, encoding="utf-8")).hexdigest()

        r = int(1000 * time.time())
        i = r + int(10 * random.random())
        return {
            "ts": r,
            "bv": t,
            "salt": i,
            "sign": hashlib.md5(
                bytes(
                    "fanyideskweb" + str(e) + str(i) + "Ygy_4c=r#e#4EX^NUGUc5",
                    encoding="utf-8",
                )
            ).hexdigest(),
        }

    def inittranslator(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        # proxies = { "http": None, "https": None}

        self.proxysession.get("https://fanyi.youdao.com", headers=headers)

    def translate(self, content):

        params = {
            "smartresult": [
                "dict",
                "rule",
            ],
        }
        sign = self.youdaoSIGN(self.headers["User-Agent"], content)
        data = {
            "i": content,
            "from": self.srclang,
            "to": self.tgtlang,
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": sign["salt"],
            "sign": sign["sign"],
            "lts": sign["ts"],
            "bv": sign["bv"],
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_CLICKBUTTION",
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://fanyi.youdao.com",
            "Pragma": "no-cache",
            "Referer": "https://fanyi.youdao.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        response = self.proxysession.post(
            "https://fanyi.youdao.com/translate_o",
            params=params,
            headers=headers,
            data=data,
        )

        res = ""
        try:
            for js in response.json()["translateResult"]:
                if res != "":
                    res += "\n"
                for _ in js:
                    res += _["tgt"]

            return res
        except:
            raise Exception(response.text)

    def show(self, res):
        print("有道", "\033[0;33;47m", res, "\033[0m", flush=True)
