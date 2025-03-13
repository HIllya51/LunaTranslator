import time, hashlib
from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CHS", Languages.TradChinese: "zh-CHT"}

    def signx(self):
        tm = str(int(time.time() * 1000))
        key = "cybibtzhdwayqjmrncst"
        client = "deskdict"
        product = "deskdict"
        string = "client={}&mysticTime={}&product={}&key={}".format(
            client, tm, product, key
        )
        return tm, hashlib.md5(bytes(string, encoding="utf-8")).hexdigest()

    def translate(self, content):
        cookies = {"DESKDICT_VENDOR": "unknown"}
        headers = {
            "Connection": "Keep-Alive",
            "Accept": "*/*",
            "User-Agent": "Youdao Desktop Dict (Windows NT 10.0)",
        }

        data = {
            "i": content,
        }

        mysticTime, sign = self.signx()

        param = {
            "keyfrom": "deskdict.main",
            "client": "deskdict",
            "from": self.srclang,
            "to": self.tgtlang,
            "keyid": "deskdict",
            "mysticTime": mysticTime,
            "pointParam": "client,product,mysticTime",  # 只要不改pointParam,client,product,mysticTime，就不需要重新签名
            "sign": sign,
            "domain": "0",
            "useTerm": "false",
            "noCheckPrivate": "false",
            "recTerms": "[]",
            "id": "0a464aedddbc6e4b9",  # 无所谓
            "vendor": "fanyiweb_navigation",
            "in": "YoudaoDict_fanyiweb_navigation",
            "appVer": "11.2.0.0",
            "appZengqiang": "0",
            "abTest": "0",
            "model": "LENOVO",
            "screen": "1920*1080",
            "OsVersion": "10.0.19045",
            "network": "none",
            "mid": "windows10.0.19045",
            "appVersion": "11.2.0.0",
            "product": "deskdict",
            "source": "mine_transtab_realtime",
        }
        response = self.proxysession.post(
            "https://dict.youdao.com/dicttranslate",
            params=param,
            cookies=cookies,
            headers=headers,
            data=data,
        )
        try:
            return "".join(
                [
                    "".join([__["tgt"] for __ in _])
                    for _ in response.json().get("translateResult", [])
                ]
            )
        except:
            raise Exception(response)
