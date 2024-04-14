from myutils.config import transerrorfixdictconfig
from myutils.utils import parsemayberegexreplace


class Process:
    @property
    def using(self):
        return transerrorfixdictconfig["use"]

    def process_before(self, content):

        return content, {}

    def process_after(self, res, mp1):
        res = parsemayberegexreplace(transerrorfixdictconfig["dict_v2"], res)
        return res
