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
            self.style = (
                requests.get(
                    "https://dictionary.goo.ne.jp/mix/css/app.css", proxies=self.proxy
                )
                .text.replace("width:1004px", "")
                .replace("width:1024px", "")
                .replace("width:644px", "")
            )

        if len(xx):
            return '<div style="text-align: center;"><a href="{}">link</a><style>{}</style></div><div id="NR-wrapper"><div id="NR-wrapper-in" class="cx">{}</div></div>'.format(
                url, self.style, xx
            )
