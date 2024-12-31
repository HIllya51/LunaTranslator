import requests
from urllib.parse import quote
import re
from cishu.cishubase import cishubase


class goo(cishubase):

    def init(self):
        self.style = None
        self.klass = None

    def search(self, word):
        url = "https://dictionary.goo.ne.jp/srch/all/{}/m1u/".format(quote(word))
        x = requests.get(url, proxies=self.proxy).text
        xx = re.findall("<section>([\\s\\S]*?)</section>", x)

        xx = "".join(xx).replace('href="/', 'href="https://dictionary.goo.ne.jp/')
        if not self.style:
            self.style, self.klass = self.parse_stylesheet(
                (
                    requests.get(
                        "https://dictionary.goo.ne.jp/mix/css/app.css",
                        proxies=self.proxy,
                    )
                    .text.replace("width:1004px", "")
                    .replace("width:1024px", "")
                    .replace("width:644px", "")
                )
            )

        if len(xx):
            return '<style>{}</style><div class="{}"><div id="NR-wrapper"><div id="NR-wrapper-in" class="cx">{}</div></div></div>'.format(
                self.style, self.klass, xx
            )
