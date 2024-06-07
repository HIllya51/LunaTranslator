import requests
from urllib.parse import quote
import re, os
from cishu.cishubase import cishubase


class goo(cishubase):

    def search(self, word):
        url = "https://dictionary.goo.ne.jp/srch/all/{}/m1u/".format(quote(word))
        x = requests.get(url, proxies=self.proxy).text
        xx = re.findall("<section>([\\s\\S]*?)</section>", x)

        xx = "".join(xx).replace('href="/', 'href="https://dictionary.goo.ne.jp/')
        if os.path.exists("cache/temp/goo.css") == False:
            stl = requests.get(
                "https://dictionary.goo.ne.jp/mix/css/app.css", proxies=self.proxy
            ).text
            os.makedirs("cache/temp", exist_ok=True)
            with open("cache/temp/goo.css", "w", encoding="utf8") as ff:
                ff.write(stl)
        else:
            with open("cache/temp/goo.css", "r", encoding="utf8") as ff:
                stl = ff.read()

        if len(xx):
            return '<div style="text-align: center;"><a href="{}">link</a><style>{}</style></div><div id="NR-main-in">{}</div>'.format(
                url, stl, xx
            )
