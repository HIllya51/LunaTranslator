import requests
from urllib.parse import quote
from cishu.cishubase import cishubase
from myutils.utils import simplehtmlparser_all, simplehtmlparser
import re, threading


class weblio(cishubase):

    def init(self):
        self.style = {}

    def search(self, word):
        url = "https://www.weblio.jp/content/" + quote(word)
        html = requests.get(url, proxies=self.proxy).text
        head = simplehtmlparser_all(html, "div", '<div class="pbarT">')
        content = simplehtmlparser_all(html, "div", '<div class="kijiWrp">')
        collect = []
        for i, xx in enumerate(head):
            xx = re.sub('src="//(.*?)"', 'src="https://\\1"', xx + content[i])
            collect.append(xx)
        join = '<div ID="base" style="overflow-x: hidden; min-width: 0; margin:0;">{}</div>'.format(
            "".join(collect)
        )
        links = []
        style = simplehtmlparser(html, "style", "<style>")[7:-8]
        for link in simplehtmlparser_all(html, "link", '<link rel="stylesheet"'):
            for _ in re.findall('href="(.*?)"', link):
                links.append("https:" + _)
        ts = []
        for _ in links:
            ts.append(threading.Thread(target=self.makelink, args=(_,)))
            ts[-1].start()
        for t in ts:
            t.join()
        style += "".join(self.style.get(link, "") for link in links)
        style, klass = self.parse_stylesheet(style)
        return '<style>{}</style><div class="{}">{}</div>'.format(style, klass, join)

    def makelink(self, link):
        if not self.style.get(link):
            html = requests.get(
                link,
                proxies=self.proxy,
            ).text
            self.style[link] = html
