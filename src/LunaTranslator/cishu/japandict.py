from cishu.cishubase import cishubase
from myutils.utils import get_element_by, localcachehelper
import re


class japandict(cishubase):
    backgroundparser = """document.querySelectorAll('.lunajapandictcsswrapper').forEach((ele) => {
                ele.style.backgroundColor = {color}
                ele.querySelectorAll('.list-group-item').forEach((ele) => {
                    ele.style.backgroundColor = {color}
                })
            });"""

    def init(self):
        self.style = localcachehelper("cishucss/japandict")
        self.klass = "lunajapandictcsswrapper"

    def search(self, word):
        url = "https://www.japandict.com/"
        params = {"s": word, "lang": "eng", "list": 1}
        html = self.proxysession.get(url, params=params).text

        check = get_element_by("class", "alert-heading", html)
        if check:
            return
        res = get_element_by("class", "list-group list-group-flush", html)
        if not res:
            return
        res = re.sub('href="(.*?)"', 'href="https://www.japandict.com\\1"', res)
        res = re.sub('src="(.*?)"', 'src="https://www.japandict.com\\1"', res)
        csslink = "https://www.japandict.com/static/css/japandict.ac087f3ecbc8.css"
        if not self.style[csslink]:
            css = self.proxysession.get(csslink).text
            css = css.replace("padding-top:60px !important", "")
            css = self.parse_stylesheet(css, self.klass)
            self.style[csslink] = css
        return '<style>{}</style><div class="{}">{}</div>'.format(
            self.style[csslink], self.klass, res
        )

    def getUrl(self, word):
        return "https://www.japandict.com/?s={}&lang=eng&list=1".format(word)
