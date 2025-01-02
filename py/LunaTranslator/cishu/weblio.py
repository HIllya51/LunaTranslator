import requests
from urllib.parse import quote, unquote
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
        if not content:
            return
        collect = []
        for i, xx in enumerate(head):
            xx = re.sub('src="//(.*?)"', 'src="https://\\1"', xx + content[i])
            collect.append(xx)
        join = '<div ID="base" style="overflow-x: hidden; min-width: 0; margin:0;">{}</div>'.format(
            "".join(collect)
        )
        for shit in simplehtmlparser_all(join, "script", "<script"):
            join = join.replace(shit, "")

        def removeklass(join, klass):
            while True:
                sig = "class=" + klass
                fnd = join.find(sig)
                if fnd == -1:
                    break
                start = join.rfind("<img", None, fnd)
                if start == -1:
                    break
                end = join.find(">", fnd)
                if end == -1:
                    break
                join = join[:start] + join[end + 1 :]
            return join

        join = removeklass(join, "lgDictLg")
        join = removeklass(join, "lgDictSp")
        join = join.replace('href="//', 'href="https://')

        def __(match):
            word = unquote(match.groups()[0])
            return '''href="javascript:safe_weblio_search_word('{}')"'''.format(word)

        join = re.sub('href="https://www.weblio.jp/content/(.*?)"', __, join)
        join+=r'''
<script>
function safe_weblio_search_word(word){
    if(window.luna_search_word)
        window.luna_search_word(word)
    else if(window.LUNAJSObject)
        window.LUNAJSObject.luna_search_word(word)
}</script>
'''
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
            req = requests.get(
                link,
                proxies=self.proxy,
            )
            html = req.text if req.status_code == 200 else ""
            self.style[link] = html
