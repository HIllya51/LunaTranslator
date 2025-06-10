import json, gobject
from translator.basetranslator import basetrans


class TS(basetrans):

    def translate(self, content):
        try:
            sql = gobject.base.textsource.sqlwrite2

        except:
            return None
        ret = sql.execute(
            "SELECT machineTrans FROM artificialtrans WHERE source = ?", (content,)
        ).fetchone()
        if ret is None:
            return None
        (ret,) = ret
        ret = json.loads(ret)
        return ret.get("realtime_edit", None)
