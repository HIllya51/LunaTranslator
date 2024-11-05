from myutils.config import globalconfig
from myutils.wrapper import threader
from traceback import print_exc
from myutils.proxy import getproxy


class DictTree:
    def text(self) -> str: ...
    def childrens(self) -> list: ...


class cishubase:
    typename = None

    def init(self):
        pass

    def search(self, word):
        return word

    @property
    def proxy(self):
        return getproxy(("cishu", self.typename))

    def __init__(self, typename) -> None:
        self.typename = typename
        self.callback = print
        self.needinit = True
        try:
            self.init()
            self.needinit = False
        except:
            print_exc()

    @threader
    def safesearch(self, sentence, callback):
        try:
            if self.needinit:
                self.init()
                self.needinit = False
            try:
                res = self.search(sentence)
            except:
                print_exc()
                self.needinit = True
                res = None
            if res and len(res):
                callback(res)
            else:
                callback(None)
        except:
            pass

    @property
    def config(self):
        return globalconfig["cishu"][self.typename]["args"]
