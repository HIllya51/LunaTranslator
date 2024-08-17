from myutils.utils import getlangsrc
import requests
from urllib.parse import quote
import re, os
from cishu.cishubase import cishubase
from myutils.utils import simplehtmlparser


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
        text = requests.get(url, proxies=self.proxy).text

        text = re.sub("<header([\\s\\S]*?)></header>", "", text)
        text = re.sub("<aside([\\s\\S]*?)></aside>", "", text)

        text = re.sub("<link([\\s\\S]*?)>", "", text)
        text = re.sub('<script([\\s\\S]*?)src="(.*?)"([\\s\\S]*?)</script>', "", text)
        text = re.sub('<div class="lang-tip-con"([\\s\\S]*?)</div>', "", text)

        text = text.replace(
            simplehtmlparser(text, "div", '<div class="footer_container"'), ""
        )
        text = text.replace(
            simplehtmlparser(text, "div", '<div class="user-feed_back"'), ""
        )
        text = text.replace("min-width: 960px", "")
        text = text.replace("min-width:960px", "")
        return text
