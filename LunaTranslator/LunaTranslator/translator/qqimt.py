from translator.basetranslator import basetrans


class TS(basetrans):

    def translate(self, query):
        headers = {
            "authority": "transmart.qq.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            #'content-type': 'text/plain;charset=UTF-8',
            "origin": "chrome-extension://bcgpmkngbhpgdgbjgbaoddljkbabdkmm",
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53",
        }

        data = {
            "header": {
                "fn": "auto_translation_block",
                "client_key": "ddsdasdsadasuMzYg",
            },
            "source": {
                "lang": self.srclang,
                "text_block": query,
                "orig_text_block": "",
                "orig_url": "https://www.baidu.com/",
            },
            "target": {"lang": self.tgtlang},
        }

        response = self.session.post(
            "https://transmart.qq.com/api/imt", headers=headers, json=data
        )
        return response.json()["auto_translation"]

    def show(self, res):
        print("百度", "\033[0;32;47m", res, "\033[0m", flush=True)
