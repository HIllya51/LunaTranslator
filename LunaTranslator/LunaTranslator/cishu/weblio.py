import requests
from urllib.parse import quote

from myutils.proxy import getproxy
import re


class weblio:

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

        return join
