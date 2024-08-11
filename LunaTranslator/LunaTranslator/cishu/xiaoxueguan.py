import sqlite3, os, re
import winsharedutils
from myutils.utils import argsort, autosql

from cishu.cishubase import cishubase


class xiaoxueguan(cishubase):
    def init(self):
        self.sql = None
        try:
            path = self.config["path"]
            if os.path.exists(path):
                self.sql = autosql(sqlite3.connect(path, check_same_thread=False))
        except:
            pass

    def search(self, word: str):
        if not self.sql:
            return
        if word in "【】":
            return
        if not word.strip():
            return
        x = self.sql.execute(
            "select word,explanation from xiaoxueguanrizhong where word like ?",
            ("%{}%".format(word),),
        )
        exp = x.fetchall()
        dis = 9999
        save = []
        dis = []
        for w, xx in exp:
            w: str = w.strip()
            if w.startswith("-"):
                w = w[1:]
            match1 = re.match("(.*?)【(.*?)】", w)
            if match1:
                pr, w = match1.groups()
                d = min(
                    winsharedutils.distance(pr, word), winsharedutils.distance(w, word)
                )
            else:
                d = winsharedutils.distance(w, word)
            if d <= self.config["distance"]:
                dis.append(d)

        srt = argsort(dis)[:10]
        save = ["<span h>" + exp[i][1].replace("\\n", "") for i in srt]
        return "<hr>".join(save)
