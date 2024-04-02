import time, hashlib
from translator.basetranslator import basetrans


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CHS", "cht": "zh-CHT"}

    def signx(self):
        tm = str(int(time.time() * 1000))
        key = "cybibtzhdwayqjmrncst"
        client = "deskdict"
        product = "deskdict"
        string = "client={}&mysticTime={}&product={}&key={}".format(
            client, tm, product, key
        )
        return tm, hashlib.md5(bytes(string, encoding="utf-8")).hexdigest()

    def translate10_9_8(self, content, v=10):
        if v == 10:
            cookies = {
                "DESKDICT_VENDOR": "fanyiweb_navigation",
                "OUTFOX_SEARCH_USER_ID": "-2107314897@110.242.68.66",  # 没用
            }
        elif v == 9:
            cookies = {
                "DESKDICT_VENDOR": "dict_web_product",
            }
        elif v == 8:
            cookies = {
                "OUTFOX_SEARCH_USER_ID": "-22405009@10.112.57.88",
                "DESKDICT_VENDOR": "unknown",
            }
        headers = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "Youdao Desktop Dict (Windows NT 10.0)",
        }

        data = {
            "i": content,
        }

        mysticTime, sign = self.signx()
        if v == 10:
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
                "appVer": "10.1.3.0",
                "appZengqiang": "0",
                "abTest": "0",
                "model": "LENOVO",
                "screen": "1920*1080",
                "OsVersion": "10.0.19045",
                "network": "none",
                "mid": "windows10.0.19045",
                "appVersion": "10.1.3.0",
                "product": "deskdict",
            }
        elif v == 9:
            param = {
                "keyfrom": "deskdict.main",
                "client": "deskdict",
                "from": self.srclang,
                "to": self.tgtlang,
                "keyid": "deskdict",
                "mysticTime": mysticTime,
                "pointParam": "client,product,mysticTime",
                "sign": sign,
                "domain": "0",
                "useTerm": "false",
                "noCheckPrivate": "false",
                "id": "0a464aedddbc6e4b9",
                "vendor": "unknown",
                "in": "YoudaoDictSetup",
                "appVer": "9.3.0.0",
                "appZengqiang": "0",
                "abTest": "0",
                "model": "LENOVO",
                "screen": "1920*1080",
                "OsVersion": "10.0.19045",
                "appVersion": "9.3.0.0",
                "product": "deskdict",
            }
        elif v == 8:
            param = {
                "keyfrom": "deskdict.main",
                "client": "deskdict",
                "from": self.srclang,
                "to": self.tgtlang,
                "keyid": "deskdict",
                "mysticTime": mysticTime,
                "pointParam": "client,product,mysticTime",
                "sign": sign,
                "id": "0a464aedddbc6e4b9",
                "vendor": "unknown",
                "in": "YoudaoDictSetup",
                "appVer": "8.10.8.0",
                "appZengqiang": "0",
                "abTest": "0",
                "model": "LENOVO",
                "screen": "1920*1080",
                "OsVersion": "10.0.19045",
                "appVersion": "8.10.8.0",
                "product": "deskdict",
            }
        response = self.session.post(
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
                    for _ in response.json()["translateResult"]
                ]
            )
        except:
            raise Exception(response.json())

    def translate(self, content):
        return self.translate10_9_8(content)
        if self.config["Version"] == 0:  # 10
            return self.translate10_9_8(content)
        if self.config["Version"] == 1:  # 9
            return self.translate10_9_8(content, 9)
        if self.config["Version"] == 2:  # 8
            return self.translate10_9_8(content, 8)
