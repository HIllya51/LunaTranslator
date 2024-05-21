from myutils.config import getlangsrc
import requests
from urllib.parse import quote
import re, os
from myutils.proxy import getproxy
from cishu.cishubase import cishubase


class youdao(cishubase):
    @property
    def srclang(self):

        try:
            l = getlangsrc()
            return l

        except:
            return ""

    def search(self, word):
        text = requests.get(
            "https://dict.youdao.com/result?word={}&lang={}".format(
                quote(word), self.srclang
            ),
            proxies=getproxy(),
        ).text
        fnd = re.search('<section class="modules"(.*?)>([\\s\\S]*?)</section>', text)
        fnd = fnd.group()
        style = re.search("<style(.*?)>([\\s\\S]*?)</style>", text)
        style = style.group()
        return '<div  style="text-align: center;"><a href="{}">link</a></div><br>{}{}'.format(
            "https://dict.youdao.com/result?word={}&lang={}".format(
                quote(word), self.srclang
            ),
            style,
            fnd,
        )
