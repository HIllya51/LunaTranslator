import requests
from urllib.parse import quote
import re
from cishu.cishubase import cishubase
from myutils.utils import get_element_by


class jisho(cishubase):

    def search(self, word):
        url = "https://jisho.org/search/{}".format(quote(word))
        html = requests.get(
            url,
            proxies=self.proxy,
        ).text

        if get_element_by("id", "no-matches", html):
            return
        res = get_element_by("id", "page_container", html)
        if res is None:
            return
        res = (
            res.replace('href="//', 'href="https://')
            .replace("<h3>Discussions</h3>", "")
            .replace(
                '<a href="#" class="signin">Log in</a> to talk about this word.', ""
            )
            .replace(get_element_by("id", "other_dictionaries", html), "")
        )

        ss = re.search('href="https://assets.jisho.org/assets/application(.*)"', html)
        stl = requests.get(ss.group()[6:-1], proxies=self.proxy).text

        return f"<style>{stl}</style>{res}"
