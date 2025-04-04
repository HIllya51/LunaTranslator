import hashlib
from translator.basetranslator import basetrans
import time
from language import Languages


class TS(basetrans):

    def init(self):
        _ = self.proxysession.get(
            "https://www.modernmt.com/translate",
            headers={
                "Referer": "https://www.modernmt.com/translate",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            },
        )

    def translate(self, content):
        time_stamp = int(time.time() * 1e3)
        form_data = {
            "q": content,
            "source": self.srclang,
            "target": self.tgtlang,
            "ts": time_stamp,
            "verify": hashlib.md5(
                "webkey_E3sTuMjpP8Jez49GcYpDVH7r#{}#{}".format(
                    time_stamp, content
                ).encode()
            ).hexdigest(),
            "hints": "",
            "multiline": "true",
        }
        r = self.proxysession.post(
            "https://webapi.modernmt.com/translate",
            json=form_data,
            headers={
                "Origin": "https://www.modernmt.com",
                "Referer": "https://www.modernmt.com/translate",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
                "X-HTTP-Method-Override": "GET",
            },
        )
        try:
            data = r.json()
            return data["data"]["translation"]
        except:
            raise Exception(r)

    def langmap(self):
        return {
            Languages.Chinese: "zh-CN",
            Languages.TradChinese: "zh-TW",
            Languages.Auto: "",
        }
