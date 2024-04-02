from myutils.config import globalconfig
import sqlite3, os
import winsharedutils, re
from myutils.utils import argsort, autosql


class edict:
    def __init__(self):
        self.sql = None
        try:
            path = globalconfig["cishu"]["edict"]["path"]
            if os.path.exists(path):
                self.sql = autosql(sqlite3.connect(path, check_same_thread=False))
        except:
            pass

    def search(self, word):

        x = self.sql.execute(
            "select text, entry_id from surface where  text like ?",
            ("%{}%".format(word),),
        )
        exp = x.fetchall()
        dis = 9999
        dis = []
        for w, xx in exp:
            d = winsharedutils.distance(w, word)
            dis.append(d)
        save = []
        srt = argsort(dis)
        for ii in srt:
            if exp[ii][1] not in save:
                save.append(exp[ii][1])
            if len(save) >= 10:
                break
        saveres = []
        for _id in save:
            x = self.sql.execute(
                "select word, content from entry where  id =?", (_id,)
            ).fetchone()
            saveres.append(x[0] + "<br>" + re.sub("/EntL.*/", "", x[1][1:]))

        return "<hr>".join(saveres)
