from myutils.config import noundictconfig
import gobject, re


class Process:
    @property
    def using(self):
        return noundictconfig["use"]

    def process_before(self, content):

        mp1 = {}
        for key in noundictconfig["dict"]:
            usedict = False
            if type(noundictconfig["dict"][key]) == str:
                usedict = True
            else:
                for i in range(len(noundictconfig["dict"][key]) // 2):
                    if noundictconfig["dict"][key][i * 2] in [
                        "0",
                        gobject.baseobject.currentmd5,
                    ]:
                        usedict = True
                        break

            if usedict and key in content:
                xx = "{{{}}}".format(gobject.baseobject.zhanweifu)
                content = content.replace(key, xx)
                mp1[xx] = key
                gobject.baseobject.zhanweifu += 1
        return content, mp1

    def process_after(self, res, mp1):
        for key in mp1:
            reg = re.compile(re.escape(key), re.IGNORECASE)
            if type(noundictconfig["dict"][mp1[key]]) == str:
                v = noundictconfig["dict"][mp1[key]]
            elif type(noundictconfig["dict"][mp1[key]]) == list:
                v = ""
                for i in range(len(noundictconfig["dict"][mp1[key]]) // 2):
                    if noundictconfig["dict"][mp1[key]][i * 2] in [
                        "0",
                        gobject.baseobject.currentmd5,
                    ]:
                        v = noundictconfig["dict"][mp1[key]][i * 2 + 1]
                        break
            res = reg.sub(v, res)
        return res
