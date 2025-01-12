from urllib.parse import quote
from cishu.cishubase import cishubase
from myutils.utils import get_element_by, localcachehelper
import re


class japandict(cishubase):

    def init(self):
        self.style = localcachehelper("cishucss/japandict")
        self.klass = "lunajapandictcsswrapper"

    def search(self, word):
        url = "https://www.japandict.com/?s={}&lang=eng&list=1".format(quote(word))
        html = self.proxysession.get(url).text

        check = get_element_by("class", "alert-heading", html)
        if check:
            return
        res = get_element_by("class", "list-group list-group-flush", html)
        if not res:
            return
        res = re.sub('href="(.*?)"', 'href="https://www.japandict.com\\1"', res)
        csslink = "https://www.japandict.com/static/css/japandict.ac087f3ecbc8.css"
        if not self.style[csslink]:
            css = self.proxysession.get(csslink).text
            css = css.replace("padding-top:60px !important", "")
            css = self.parse_stylesheet(css, self.klass)
            self.style[csslink] = css
        return '<style>{}</style><div class="{}">{}</div>'.format(
            self.style[csslink], self.klass, res
        )
