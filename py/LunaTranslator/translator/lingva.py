import requests
import urllib
from urllib.parse import quote_plus
from translator.basetranslator import basetrans
from language import Languages


class TS(basetrans):
    def langmap(self):
        return {Languages.TradChinese: "zh_HANT"}

    # def inittranslator(self):
    # res=requests.get(self.config['host'],headers=
    #     {
    #     'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
    #     'Referer': self.config['host'],
    #     'sec-ch-ua-mobile': '?0',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
    #     'sec-ch-ua-platform': '"Windows"',
    # },proxies=self.proxy).text
    # _id=re.findall('buildId":"(.*?)"',res)[0]
    # self.url=self.config['host']+'_next/data/{}/%s/%s/%s.json'.format(_id)
    def translate(self, content):
        # print(self.url%(self.srclang,self.tgtlang,urllib.parse.quote(content)))
        
        x = self.proxysession.get(
            "https://"
            + self.config["host"]
            + "/api/v1/%s/%s/%s" % (self.srclang, self.tgtlang, quote_plus(content)),
            headers={
                # 'authority': self.config['host'],
                # 'accept': '*/*',
                # 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                # 'cache-control': 'no-cache',
                # 'pragma': 'no-cache',
                # 'referer': self.config['host'],
                # 'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
                # 'sec-ch-ua-mobile': '?0',
                # 'sec-ch-ua-platform': '"Windows"',
                # 'sec-fetch-dest': 'empty',
                # 'sec-fetch-mode': 'cors',
                # 'sec-fetch-site': 'same-origin',
                # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
            },
        ).json()
        return x["translation"]
        x = requests.get(
            self.url % (self.srclang, self.tgtlang, urllib.parse.quote(content)),
            headers={
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "referer": self.config["host"],
                "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46",
            },
            proxies=self.proxy,
        ).json()
        return x["pageProps"]["translation"]
