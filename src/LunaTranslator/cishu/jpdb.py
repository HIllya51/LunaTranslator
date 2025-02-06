from urllib.parse import quote
from cishu.cishubase import cishubase
from myutils.utils import simplehtmlparser, localcachehelper
import re


class jpdb(cishubase):

    def init(self):
        self.style = localcachehelper("cishucss/jpdb")
        self.klass = "lunajpdbcsswrapper"

    def search(self, word: str):
        url = "https://jpdb.io/search?q={}&lang=english".format(quote(word))
        text = self.proxysession.get(url).text

        res = simplehtmlparser(text, "div", '<div class="results search">')
        if not res:
            return
        res = res.replace('<i class="ti ti-volume"></i>', "")  # 播音图标无法跨域访问
        res = re.sub('href="/(.*?)"', 'href="https://jpdb.io/\\1"', res)
        res = '<div class="container bugfix" style="padding-top:16px;padding-bottom:16px;">{}</div>'.format(
            res
        )

        csss = re.findall('<link rel="stylesheet" media="screen" href="(.*?)" />', text)
        cssall = ""
        for link in csss:
            link = "https://jpdb.io" + link
            if not self.style[link]:
                css = self.proxysession.get(link).text
                # css = self.parse_stylesheet(css, self.klass) parse了样式会不正确。先不parse了，影响不大。
                self.style[link] = css
            if self.style[link].startswith("@font-face"):
                # 这个又大又没卵用
                continue
            cssall += self.style[link]
        cssall = "<style>{}</style>".format(cssall)
        return res + cssall
