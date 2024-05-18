import requests
from urllib.parse import quote
import re
from myutils.proxy import getproxy
from cishu.cishubase import cishubase


class goo(cishubase):

    def search(self, word):
        url = "https://dictionary.goo.ne.jp/srch/all/{}/m1u/".format(quote(word))
        x = requests.get(url, proxies=getproxy()).text
        xx = re.findall("<section>([\\s\\S]*?)</section>", x)

        xx = "".join(xx)
        xx = re.sub("<h1>([\\s\\S]*?)</h1>", "", xx)
        xx = re.sub("<a([\\s\\S]*?)>", "", xx)

        xx = re.sub("</a>", "", xx)
        if len(xx):
            return (
                '<div  style="text-align: center;"><a href="{}">link</a></div>'.format(
                    url
                )
                + xx
            )
