import requests
from urllib.parse import quote
import re, os, gobject
from cishu.cishubase import cishubase


class goo(cishubase):

    def search(self, word):
        url = "https://dictionary.goo.ne.jp/srch/all/{}/m1u/".format(quote(word))
        x = requests.get(url, proxies=self.proxy).text
        xx = re.findall("<section>([\\s\\S]*?)</section>", x)

        xx = "".join(xx).replace('href="/', 'href="https://dictionary.goo.ne.jp/')
        temp = gobject.gettempdir("goo.css")
        if os.path.exists(temp) == False:
            stl = requests.get(
                "https://dictionary.goo.ne.jp/mix/css/app.css", proxies=self.proxy
            ).text
            with open(temp, "w", encoding="utf8") as ff:
                ff.write(stl)
        else:
            with open(temp, "r", encoding="utf8") as ff:
                stl = ff.read()

        if len(xx):
            return '<div style="text-align: center;"><a href="{}">link</a><style>{}</style></div><div id="NR-main-in">{}</div>'.format(
                url, stl, xx
            )
