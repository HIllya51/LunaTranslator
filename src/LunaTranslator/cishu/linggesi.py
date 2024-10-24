from myutils.utils import autosql
import sqlite3
import winsharedutils
import os
from cishu.cishubase import cishubase, DictTree


class linggesi(cishubase):
    def init(self):
        self.sql = None
        try:
            if (
                os.path.exists(os.path.join(self.config["path"], "ja-zh.db")) == False
                or os.path.exists(os.path.join(self.config["path"], "ja-zh-gbk.db"))
                == False
            ):
                return
            self.sql = autosql(
                sqlite3.connect(
                    os.path.join(self.config["path"], "ja-zh.db"),
                    check_same_thread=False,
                )
            )
            self.sql2 = sqlite3.connect(
                os.path.join(self.config["path"], "ja-zh-gbk.db"),
                check_same_thread=False,
            )
        except:
            pass

    def search(self, word):
        if not self.sql:
            return
        mp = {}
        for sql in [self.sql, self.sql2]:
            x = sql.execute(
                "select word,content from entry where word like ?",
                ("%{}%".format(word),),
            )
            exp = x.fetchall()

            for w, xx in exp:

                d = winsharedutils.distance(w, word)
                if d <= self.config["distance"]:
                    mp[w] = [xx, d]

        x = sorted(list(mp.keys()), key=lambda x: mp[x][1])[: self.config["max_num"]]
        save = [w + "<hr>" + mp[w][0] for w in x]
        return "<hr>".join(save)

    def tree(self):
        if not self.sql:
            return

        class DictTreeRoot(DictTree):
            def __init__(self, ref) -> None:
                self.ref = ref

            def childrens(self):
                c = []
                for _ in self.ref.sql.execute(
                    "select word from entry"
                ).fetchall():
                    c.append(_[0])
                return c

        return DictTreeRoot(self)
