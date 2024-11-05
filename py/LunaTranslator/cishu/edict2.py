import winsharedutils, os
import re
from myutils.utils import argsort
from traceback import print_exc
from cishu.cishubase import cishubase, DictTree


class edict2(cishubase):
    def init(self):
        self.save = None
        try:
            path = self.config["path"]
            if os.path.exists(path):
                with open(path, "r", encoding="euc-jp") as ff:
                    _ = ff.read()
                _ = _.split("\n")[1:]
                self.save = {}
                for _l in _:
                    try:
                        _s = _l.index(" ")
                    except:
                        continue
                    self.save[_l[:_s]] = _l[_s:]
        except:
            print_exc()

    def search(self, word):
        if not self.save:
            return
        dis = 9999
        dis = []
        savew = []
        for w in self.save:
            if word in w or w in word:
                d = winsharedutils.distance(w, word)
                if d <= self.config["distance"]:
                    dis.append(d)
                    savew.append(w)
        saveres = []
        srt = argsort(dis)
        for ii in srt[: self.config["max_num"]]:
            saveres.append(
                savew[ii] + "<hr>" + re.sub("/EntL.*/", "", self.save[savew[ii]][1:])
            )
        return "<hr>".join(saveres)

    def tree(self):
        if not self.save:
            return

        class DictTreeRoot(DictTree):
            def __init__(self, ref) -> None:
                self.ref = ref

            def childrens(self):
                return list(self.ref.save.keys())

        return DictTreeRoot(self)
