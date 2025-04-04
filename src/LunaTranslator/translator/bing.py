import re
from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def init(self):
        host_html = self.proxysession.get("https://www.bing.com/Translator").text
        self.tk = self.get_tk(host_html)
        self.ig_iid = self.get_ig_iid(host_html)

    def get_ig_iid(self, host_html):

        iid = re.search(
            '<div[ ]+id="tta_outGDCont"[ ]+data-iid="(.*?)">', host_html
        ).groups()[0]
        ig = re.compile('IG:"(.*?)"').findall(host_html)[0]
        return {"IG": iid, "IID": ig, "isVertical": 1}

    def get_tk(self, host_html):
        result_str = re.compile("var params_AbusePreventionHelper = (.*?);").findall(
            host_html
        )[0]
        result = eval(result_str)
        return {"key": result[0], "token": result[1]}

    def translate(self, content):

        form_data = {
            "text": content,
            "fromLang": self.srclang,
            "to": self.tgtlang,
            "tryFetchingGenderDebiasedTranslations": "true",
        }
        form_data.update(self.tk)
        r = self.proxysession.post(
            "https://www.bing.com/ttranslatev3",
            params=self.ig_iid,
            data=form_data,
        )

        try:
            data = r.json()
            return data[0]["translations"][0]["text"]
        except:
            raise Exception(r)

    def langmap(self):
        return {
            Languages.Chinese: "zh-Hans",
            Languages.TradChinese: "zh-Hant",
            Languages.Auto: "auto-detect",
        }
