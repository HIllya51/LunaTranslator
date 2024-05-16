from myutils.config import getlangsrc
import requests
from urllib.parse import quote
import re
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
        fnd = re.findall('<section class="modules"(.*?)>([\\s\\S]*?)</section>', text)
        return fnd[0][1]
