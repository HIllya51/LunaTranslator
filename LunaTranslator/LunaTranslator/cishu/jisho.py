import requests
from urllib.parse import quote
import re
from myutils.proxy import getproxy
from cishu.cishubase import cishubase

from html.parser import HTMLParser


class IDParser(HTMLParser):
    """Modified HTMLParser that isolates a tag with the specified id"""

    def __init__(self, id):
        self.id = id
        self.result = None
        self.started = False
        self.depth = {}
        self.html = None
        self.watch_startpos = False
        HTMLParser.__init__(self)

    def loads(self, html):
        self.html = html
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.started:
            self.find_startpos(None)
        if "id" in attrs and attrs["id"] == self.id:
            self.result = [tag]
            self.started = True
            self.watch_startpos = True
        if self.started:
            if not tag in self.depth:
                self.depth[tag] = 0
            self.depth[tag] += 1

    def handle_endtag(self, tag):
        if self.started:
            if tag in self.depth:
                self.depth[tag] -= 1
            if self.depth[self.result[0]] == 0:
                self.started = False
                self.result.append(self.getpos())

    def find_startpos(self, x):
        """Needed to put the start position of the result (self.result[1])
        after the opening tag with the requested id"""
        if self.watch_startpos:
            self.watch_startpos = False
            self.result.append(self.getpos())

    handle_entityref = handle_charref = handle_data = handle_comment = handle_decl = (
        handle_pi
    ) = unknown_decl = find_startpos

    def get_result(self):
        if self.result == None:
            return None
        if len(self.result) != 3:
            return None
        lines = self.html.split("\n")
        lines = lines[self.result[1][0] - 1 : self.result[2][0]]
        lines[0] = lines[0][self.result[1][1] :]
        if len(lines) == 1:
            lines[-1] = lines[-1][: self.result[2][1] - self.result[1][1]]
        lines[-1] = lines[-1][: self.result[2][1]]
        return "\n".join(lines).strip()


def get_element_by_id(id, html):
    """Return the content of the tag with the specified id in the passed HTML document"""
    parser = IDParser(id)
    parser.loads(html)
    return parser.get_result()


class jisho(cishubase):

    def search(self, word):
        url = "https://jisho.org/word/{}".format(quote(word))
        html = requests.get(
            url,
            proxies=getproxy(),
        ).text

        res = get_element_by_id("page_container", html)
        if res is None:
            return
        res = (
            res.replace('href="//', 'href="https://')
            .replace("<h3>Discussions</h3>", "")
            .replace(
                '<a href="#" class="signin">Log in</a> to talk about this word.', ""
            )
        )

        ss = re.search('href="https://assets.jisho.org/assets/application(.*)"', html)
        stl = requests.get(ss.group()[6:-1], proxies=getproxy()).text

        return (
            '<div  style="text-align: center;"><a href="{}">link</a></div><br>'.format(
                url
            )
            + f"<style>{stl}</style>{res}"
        )
