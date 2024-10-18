from translator.basetranslator import basetrans
import hashlib
import urllib
import random


class TS(basetrans):
    def inittranslator(self):
        self.access = {}
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

    def get_access_token(self, API_KEY, SECRET_KEY):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": SECRET_KEY,
        }
        js = self.proxysession.post(url, params=params).json()

        try:
            return js["access_token"]
        except:
            raise Exception(js)

    def getaccess(self):
        self.checkempty(["API Key", "Secret Key"])
        SECRET_KEY, API_KEY = (
            self.multiapikeycurrent["Secret Key"],
            self.multiapikeycurrent["API Key"],
        )
        if not self.access.get((API_KEY, SECRET_KEY)):
            acss = self.get_access_token(API_KEY, SECRET_KEY)
            self.access[(API_KEY, SECRET_KEY)] = acss
        return self.access[(API_KEY, SECRET_KEY)]

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
            raise Exception(r.maybejson)

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
            raise Exception(res.maybejson)
