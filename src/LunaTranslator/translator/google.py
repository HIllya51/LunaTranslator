from language import Languages
import json
from translator.cdp_helper import cdp_helper
from html import unescape
from translator.basetranslator import basetrans


class cdp_gg(cdp_helper):
    target_url = "https://translate.google.com/"

    @property
    def using(self):
        return self.ref.using and self.config["usewhich"] == 2

    def __init__(self, ref):
        super().__init__(ref)
        self.langs = None

    def checklang(self):
        if (self.ref.srclang, self.ref.tgtlang) == self.langs:
            return
        self.langs = (self.ref.srclang, self.ref.tgtlang)
        self.Page_navigate(
            "https://translate.google.com/?sl={}&tl={}&op=translate".format(
                self.ref.srclang, self.ref.tgtlang
            )
        )

    def translate(self, content):

        self.checklang()

        self.Runtime_evaluate(
            "document.querySelector('.DVHrxd').querySelector('button').click()"
        )
        self.Runtime_evaluate("document.querySelector('textarea').focus()")
        self.send_keys(content)
        return self.wait_for_result(
            """document.querySelector('div[class="lRu31"]').innerText""",
        )


# https://github.com/bookfere/Ebook-Translator-Calibre-Plugin/blob/master/engines/google.py


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CN", Languages.TradChinese: "zh-TW"}

    def translate(self, content):
        response = self.proxysession.post(
            "https://translate-pa.googleapis.com/v1/translateHtml",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json+protobuf",
                "X-Goog-Api-Key": "AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 "
                "Safari/537.36",
            },
            data=json.dumps([[[content], self.srclang, self.tgtlang], "wt_lib"]),
        )
        try:
            return unescape(response.json()[0][0])
        except:
            raise Exception(response)
