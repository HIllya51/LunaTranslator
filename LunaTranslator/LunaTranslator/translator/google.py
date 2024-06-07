from urllib.parse import urlencode
import json

from translator.basetranslator import basetrans
import time


class TS(basetrans):
    def langmap(self):
        return {"zh": "zh-CN", "cht": "zh-TW"}

    def inittranslator(self):

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
        # print(html)
        # self.bl=re.search('"cfb2h":"(.*?)"',html).groups()[0]
        # self.fsid=re.search('"FdrFJe":"(.*?)"',html).groups()[0]

    def realfy1(self, content):
        t1 = time.time()
        param = json.dumps([[content, self.srclang, self.tgtlang, True], [1]])
        # print([content, 'ja', 'zh-CN', True])
        freq = json.dumps([[["MkEWBc", param, None, "generic"]]])
        freq = {"f.req": freq}
        freq = urlencode(freq)
        # print(freq)
        # params = {
        #     'rpcids': 'MkEWBc',
        #     'source-path': '/',
        #     'f.sid': self.fsid,
        #     'bl': self.bl,
        #     'hl': 'zh-CN',
        #     'soc-app': '1',
        #     'soc-platform': '1',
        #     'soc-device': '1',
        #     '_reqid': '86225',
        #     'rt': 'c',
        # }

        headers = {
            "Origin": "https://translate.google.com",
            "Referer": "https://translate.google.com",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        }

        response = self.proxysession.post(
            "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute",
            verify=False,
            headers=headers,
            data=freq,
        )
        # good=response.text.split('\n')[3]
        # print(response.text)
        json_data = json.loads(response.text[6:])
        data = json.loads(json_data[0][2])
        return " ".join([x[0] for x in (data[1][0][0][5] or data[1][0])])

    def translate(self, content):
        s = self.realfy1(content)
        # print(s,time.time()-t1)
        return s
