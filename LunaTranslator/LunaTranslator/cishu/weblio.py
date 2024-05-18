import requests
from urllib.parse import quote
from cishu.cishubase import cishubase

from myutils.proxy import getproxy
import re


class weblio(cishubase):

    def search(self, word):
        url = "https://www.weblio.jp/content/" + quote(word)
        x = requests.get(url, proxies=getproxy()).text
        x = re.sub("<img(.*?)>", "", x)
        _all = []
        _xx = re.findall('<div class="kijiWrp">([\\s\\S]*?)<br class=clr>', x)

        for xx in _xx:

            xx = re.sub("<a(.*?)>", "", xx)

            xx = re.sub("</a>", "", xx)

            xx = re.sub('class="(.*?)"', "", xx)
            _all.append(xx)

        join = "<br>".join(_all)
        if len(join):
            return (
                '<div  style="text-align: center;"><a href="{}">link</a></div>'.format(
                    url
                )
                + join
            )
