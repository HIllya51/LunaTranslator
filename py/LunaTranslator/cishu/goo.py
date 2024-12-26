import requests
from urllib.parse import quote
import re, os, gobject
from cishu.cishubase import cishubase


class goo(cishubase):

    def init(self):
        self.style = None

    def search(self, word):
        url = "https://dictionary.goo.ne.jp/srch/all/{}/m1u/".format(quote(word))
        x = requests.get(url, proxies=self.proxy).text
        xx = re.findall("<section>([\\s\\S]*?)</section>", x)

        xx = "".join(xx).replace('href="/', 'href="https://dictionary.goo.ne.jp/')
        if not self.style:
            self.style = requests.get(
                "https://dictionary.goo.ne.jp/mix/css/app.css", proxies=self.proxy
            ).text

        if len(xx):
            return '<div style="text-align: center;"><a href="{}">link</a><style>{}</style></div><div id="NR-main-in">{}</div>'.format(
                url, self.style, xx
            )
