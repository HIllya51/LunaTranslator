from myutils.utils import getlangsrc
import requests
from urllib.parse import quote
import re, os
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
        url = "https://dict.youdao.com/result?word={}&lang={}".format(
            quote(word), self.srclang
        )
        text = requests.get(
            url,
            proxies=self.proxy,
        ).text
        fnd = re.search('<section class="modules"(.*?)>([\\s\\S]*?)</section>', text)
        fnd = fnd.group()

        tip = re.search('<div class="lang-tip-con"(.*?)</div>', fnd)
        if tip:
            tip = tip.group()
            fnd = fnd.replace(tip, "")
        style = re.search("<style(.*?)>([\\s\\S]*?)</style>", text)
        style = style.group()
        return f'<div style="text-align: center;"><a href="{url}">link</a></div><br>{style}{fnd}'
