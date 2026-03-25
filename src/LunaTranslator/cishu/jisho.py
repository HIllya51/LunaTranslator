import re
from cishu.cishubase import cishubase
from myutils.utils import get_element_by, simplehtmlparser_all, localcachehelper


class jisho(cishubase):
    backgroundparser = "document.querySelectorAll('.lunajisho').forEach((ele) => { ele.style.backgroundColor = {color} });"

    def init(self):
        self.style = localcachehelper("cishucss/jisho_1")
        self.klass = "lunajisho"

    def paradown(self, word, key, saver):

        link = "https://jisho.org/{}/{}".format(key, word)
        url = link
        html = self.proxysession.get(url).text

        if get_element_by("id", "no-matches", html):
            return
        res = get_element_by("id", "page_container", html)
        if not res:
            return
        res = (
            res.replace('href="//', 'href="https://')
            .replace("<h3>Discussions</h3>", "")
            .replace(
                '<a href="#" class="signin">Log in</a> to talk about this word.', ""
            )
            .replace(get_element_by("id", "other_dictionaries", html), "")
        )
        for link in simplehtmlparser_all(
            res, "a", '<a class="concept_audio concept_light-status_link"'
        ):
            res = res.replace(link, "")
        for link in simplehtmlparser_all(
            res, "a", '<a class="concept_light-status_link"'
        ):
            res = res.replace(link, "")
        for link in simplehtmlparser_all(res, "a", '<a href="#"'):
            res = res.replace(link, "")

        ss = re.search('href="https://assets.jisho.org/assets/application(.*)"', html)
        link = ss.group()[6:-1]
        if not self.style.get(link):
            self.style[link] = self.parse_stylesheet(
                self.proxysession.get(link).text, self.klass
            )
        saver["style"] = self.style[link]
        return (
            get_element_by("id", "main_results", res)
            + "<script>document.documentElement.setAttribute('data-color-theme', 'auto');</script>"
        )

    def search(self, word):
        saver = {}
        res = self.paradown(word, "search", saver)
        return '<style>{}</style><div class="{}">{}</div>'.format(
            saver.get("style", ""), self.klass, res
        )

    def getUrl(self, word):
        return "https://jisho.org/{}/{}".format("search", word)
