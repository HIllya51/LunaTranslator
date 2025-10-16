import re
from myutils.utils import localcachehelper
from cishu.cishubase import cishubase


class goo(cishubase):

    def init(self):
        self.cache = localcachehelper("cishucss/goo")
        self.klass = "lunagoocsswrapper"

    def search(self, word):
        url = self.getUrl(word)
        x = self.proxysession.get(url).text
        xx = re.findall("<section>([\\s\\S]*?)</section>", x)
        if not xx:
            return
        xx = "".join(xx)
        xx = xx.replace('href="/', 'href="https://dictionary.goo.ne.jp/')
        xx = xx.replace('src="/', 'src="https://dictionary.goo.ne.jp/')
        cssurl = "https://dictionary.goo.ne.jp/mix/css/app.css"
        if not self.cache[cssurl]:
            origin = self.proxysession.get(cssurl).text
            origin = (
                origin.replace("width:1004px", "")
                .replace("width:1024px", "")
                .replace("width:644px", "")
            )
            origin = self.parse_stylesheet(origin, self.klass)
            self.cache[cssurl] = origin

        return '<style>{}</style><div class="{}"><div id="NR-wrapper"><div id="NR-wrapper-in" class="cx">{}</div></div></div>'.format(
            self.cache[cssurl], self.klass, xx
        )

    def getUrl(self, word):
        return "https://dictionary.goo.ne.jp/srch/all/{}/m1u/".format(word)
