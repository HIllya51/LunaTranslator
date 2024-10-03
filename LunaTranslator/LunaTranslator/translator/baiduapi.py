from translator.basetranslator import basetrans
import hashlib
import urllib
import random


class TS(basetrans):
    def inittranslator(self):
        self.keys = {}
        if self.config["interface"] == 1:
            self.getaccess()

    def langmap(self):
        return {
            "es": "spa",
            "ko": "kor",
            "fr": "fra",
            "ja": "jp",
            "cht": "cht",
            "vi": "vie",
            "uk": "ukr",
            "ar": "ara",
            "sv": "swe",
            "la": "lat",
        }

    def translate(self, query):
        if self.config["interface"] == 0:
            return self.translate_fy(query)
        elif self.config["interface"] == 1:
            return self.translate_bce(query)
        raise Exception("unknown")

    def getaccess(self):
        self.checkempty(["API Key", "Secret Key"])
        pair = (
            self.multiapikeycurrent["API Key"],
            self.multiapikeycurrent["Secret Key"],
        )
        if pair not in self.keys:
            accstoken = self.proxysession.get(
                "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id="
                + self.appid
                + "&client_secret="
                + self.secretKey
            ).json()["access_token"]
            self.keys[pair] = accstoken
        return self.keys[pair]

    def translate_bce(self, q):
        accstoken = self.getaccess()
        url = "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1"
        para = {
            "access_token": accstoken,
            "q": q,
            "from": self.srclang,
            "to": self.tgtlang,
        }
        r = self.proxysession.post(url, params=para)
        try:
            return "\n".join([_["dst"] for _ in r.json()["result"]["trans_result"]])
        except:
            raise Exception(r.text)

    def translate_fy(self, q):
        self.checkempty(["APP ID", "密钥"])
        appid = self.multiapikeycurrent["APP ID"]
        secretKey = self.multiapikeycurrent["密钥"]
        salt = random.randint(32768, 65536)
        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        para = {
            "appid": appid,
            "q": q,
            "from": self.srclang,
            "to": self.tgtlang,
            "salt": salt,
            "sign": sign,
        }

        res = self.proxysession.get(
            "https://api.fanyi.baidu.com/api/trans/vip/translate", params=para
        )
        try:
            return "\n".join([_["dst"] for _ in res.json()["trans_result"]])

        except:
            raise Exception(res.text)
