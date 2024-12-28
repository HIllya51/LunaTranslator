import requests
from urllib.parse import quote
from cishu.cishubase import cishubase
from myutils.utils import get_element_by
import threading, base64, re


class japandict(cishubase):

    def init(self):
        self.style = {}

    def makelinkbase64(self, link):
        if not self.style.get(link):
            html = requests.get(
                link,
                proxies=self.proxy,
            ).content.replace(b"padding-top:60px !important", b"")
            base64_content = base64.b64encode(html).decode("utf-8")
            self.style[link] = "data:application/octet-stream;base64," + base64_content

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
        ts = []
        styles = '<link rel="stylesheet" href="https://www.japandict.com/static/css/japandict.ac087f3ecbc8.css" type="text/css"><link rel="preload" href="https://www.japandict.com/static/JapaneseRadicals-Regular.woff2" as="font"><link rel="preload" href="https://www.japandict.com/static/radicals_font.woff" as="font">'
        for link in re.findall('href="(.*?)"', styles):
            ts.append(threading.Thread(target=self.makelinkbase64, args=(link,)))
            ts[-1].start()
        for t in ts:
            t.join()
        for link in self.style:
            styles = styles.replace(link, self.style[link])
        return res + styles
