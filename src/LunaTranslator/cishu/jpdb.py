from cishu.cishubase import cishubase
from myutils.utils import simplehtmlparser, localcachehelper
import re


class jpdb(cishubase):
    backgroundparser = "document.querySelectorAll('.lunajpdbcsswrapper').forEach((ele) => { ele.style.backgroundColor = {color} });"

    def init(self):
        self.style = localcachehelper("cishucss/jpdb")
        self.klass = "lunajpdbcsswrapper"

    def search(self, word: str):
        url = "https://jpdb.io/search"
        text = self.proxysession.get(url, params={"q": word, "lang": "english"}).text

        res = simplehtmlparser(text, "div", '<div class="results search">')
        if not res:
            res = simplehtmlparser(text, "div", '<div class="results details">')
        if not res:
            return
        if "<div" not in res[1:]:
            return
        res = res.replace('<i class="ti ti-volume"></i>', "")  # 播音图标无法跨域访问
        res = re.sub('href="/(.*?)"', 'href="https://jpdb.io/\\1"', res)
        res = '<div class="{}"><div class="container bugfix" style="padding-top:16px;padding-bottom:16px;">{}</div></div>'.format(
            self.klass, res
        )

        csss = re.findall('<link rel="stylesheet" media="screen" href="(.*?)" />', text)
        cssall = ""
        for link in csss:
            link = "https://jpdb.io" + link
            if not self.style[link]:
                css = self.proxysession.get(link).text
                if css.startswith("@font-face"):
                    # 这个又大又没卵用
                    continue
                css = css.replace("width:100%;", "")
                css = self.parse_stylesheet(css, self.klass)
                self.style[link] = css

            cssall += self.style[link]

        cssall = "<style>{}</style>".format(cssall)
        return res + cssall
