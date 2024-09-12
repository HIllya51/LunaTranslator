from translator.basetranslator import basetrans
import hashlib
import urllib
import random


class TS(basetrans):
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

        self.checkempty(["APP ID", "密钥"])

        appid = self.multiapikeycurrent["APP ID"]
        secretKey = self.multiapikeycurrent["密钥"]
        myurl = "/api/trans/vip/translate"

        fromLang = self.srclang  # 原文语种
        toLang = self.tgtlang  # 译文语种
        salt = random.randint(32768, 65536)
        q = query
        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = (
            myurl
            + "?appid="
            + appid
            + "&q="
            + urllib.parse.quote(q)
            + "&from="
            + fromLang
            + "&to="
            + toLang
            + "&salt="
            + str(salt)
            + "&sign="
            + sign
        )

        res = self.proxysession.get("https://api.fanyi.baidu.com" + myurl)
        try:
            _ = "\n".join([_["dst"] for _ in res.json()["trans_result"]])

            self.countnum(query)
            return _
        except:
            raise Exception(res.text)
