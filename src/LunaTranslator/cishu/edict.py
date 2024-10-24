import sqlite3, os
import winsharedutils, re
from myutils.utils import argsort, autosql
from cishu.cishubase import cishubase, DictTree


class edict(cishubase):
    def init(self):
        self.sql = None
        try:
            path = self.config["path"]
            if os.path.exists(path):
                self.sql = autosql(sqlite3.connect(path, check_same_thread=False))
        except:
            pass

    def search(self, word):
        if not self.sql:
            return
        x = self.sql.execute(
            "select text, entry_id from surface where  text like ?",
            ("%{}%".format(word),),
        )
        exp = x.fetchall()
        dis = 9999
        dis = []
        for w, xx in exp:
            d = winsharedutils.distance(w, word)
            if d <= self.config["distance"]:
                dis.append(d)
        save = []
        srt = argsort(dis)
        for ii in srt[: self.config["max_num"]]:
            if exp[ii][1] not in save:
                save.append(exp[ii][1])
        saveres = []
        for _id in save:
            x = self.sql.execute(
                "select word, content from entry where  id =?", (_id,)
            ).fetchone()
            saveres.append(x[0] + "<hr>" + re.sub("/EntL.*/", "", x[1][1:]))

        return "<hr>".join(saveres)

    def tree(self):
        if not self.sql:
            return

        class DictTreeRoot(DictTree):
            def __init__(self, ref) -> None:
                self.ref = ref

            def childrens(self):
                c = []
                for _ in self.ref.sql.execute("select text from surface").fetchall():
                    c.append(_[0])
                return c

        return DictTreeRoot(self)
