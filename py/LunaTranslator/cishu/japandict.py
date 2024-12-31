import requests
from urllib.parse import quote
from cishu.cishubase import cishubase
from myutils.utils import get_element_by
import re


class japandict(cishubase):

    def init(self):
        self.style = None
        self.klass = None

    def search(self, word):
        url = "https://www.japandict.com/?s={}&lang=eng&list=1".format(quote(word))
        html = requests.get(
            url,
            proxies=self.proxy,
        ).text

        check = get_element_by("class", "alert-heading", html)
        if check:
            return
        res = get_element_by("class", "list-group list-group-flush", html)
        if not res:
            return
        res = re.sub('href="(.*?)"', 'href="https://www.japandict.com\\1"', res)
        if not self.style:
            self.style, self.klass = self.parse_stylesheet(
                requests.get(
                    "https://www.japandict.com/static/css/japandict.ac087f3ecbc8.css",
                    proxies=self.proxy,
                ).text.replace("padding-top:60px !important", "")
            )
        return '<style>{}</style><div class="{}">{}</div>'.format(
            self.style, self.klass, res
        )
