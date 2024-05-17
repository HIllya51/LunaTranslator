from myutils.config import globalconfig
from myutils.wrapper import threader


class cishubase:
    def init(self):
        pass

    def search(self, word):
        return word

    def __init__(self, typename) -> None:
        self.typename = typename
        self.callback = print
        self.needinit = True
        try:
            self.init()
            self.needinit = False
        except:
            pass

    @threader
    def safesearch(self, sentence):
        try:
            if self.needinit:
                self.init()
                self.needinit = False
            try:
                res = self.search(sentence)
            except:
                self.needinit = True

            if res and len(res):
                self.callback(res)
        except:
            pass

    @property
    def config(self):
        return globalconfig["cishu"][self.typename]["args"]
