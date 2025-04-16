from language import Languages
import json
from translator.cdp_helper import cdp_helper
import re, html, time
from urllib.parse import quote
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


class TS(basetrans):
    def langmap(self):
        return {Languages.Chinese: "zh-CN", Languages.TradChinese: "zh-TW"}

    def init(self):

        self.devtool = None
        if self.config["usewhich"] == 2:
            self.devtool = cdp_gg(self)
        _ = self.proxysession.get(
            "https://translate.google.com/",
            headers={
                "authority": "translate.google.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                "sec-ch-ua-arch": '"x86"',
                "sec-ch-ua-bitness": '"64"',
                "sec-ch-ua-full-version": '"105.0.1343.53"',
                "sec-ch-ua-full-version-list": '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-model": '""',
                "sec-ch-ua-platform": '"Windows"',
                "sec-ch-ua-platform-version": '"10.0.0"',
                "sec-ch-ua-wow64": "?0",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53",
            },
            verify=False,
        ).text

    def realfy1(self, content):
        param = json.dumps([[content, self.srclang, self.tgtlang, True], [1]])
        freq = json.dumps([[["MkEWBc", param, None, "generic"]]])
        freq = {"f.req": freq}

        headers = {
            "Origin": "https://translate.google.com",
            "Referer": "https://translate.google.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        }

        response = self.proxysession.post(
            "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute",
            verify=False,
            headers=headers,
            data=freq,
        )
        json_data = json.loads(response.text[6:])
        data = json.loads(json_data[0][2])
        return " ".join([x[0] for x in (data[1][0][0][5] or data[1][0]) if x[0]])

    def translate(self, content):
        if self.config["usewhich"] == 0:
            return self.realfy1(content)
        elif self.config["usewhich"] == 1:
            return self.translate_M(content)
        elif self.config["usewhich"] == 2:
            if not self.devtool:
                self.devtool = cdp_gg(self)
            return self.devtool.translate(content)

    def translate_M(self, content):

        headers = {
            "authority": "translate.google.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://translate.google.com/m",
            "sec-ch-ua": '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"105.0.1343.53"',
            "sec-ch-ua-full-version-list": '"Microsoft Edge";v="105.0.1343.53", "Not)A;Brand";v="8.0.0.0", "Chromium";v="105.0.5195.127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"10.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53",
        }
        params = {
            "sl": self.srclang,
            "tl": self.tgtlang,
            "hl": "zh-CN",
            "q": content,
        }

        response = self.proxysession.get(
            "https://translate.google.com/m",
            params=params,
            verify=False,
            headers=headers,
        )

        res = re.search(
            '<div class="result-container">([\\s\\S]*?)</div>', response.text
        ).groups()
        return html.unescape(res[0])
