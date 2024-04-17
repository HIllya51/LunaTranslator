from myutils.config import noundictconfig
import gobject, re




class Process:

    def process_before(self, content):
        ___idx = 1
        mp1 = {}
        for key in noundictconfig["dict"]:
            v = None
            if type(noundictconfig["dict"][key]) == str:
                v = noundictconfig["dict"][mp1[key]]
            else:
                for i in range(len(noundictconfig["dict"][key]) // 2):
                    if noundictconfig["dict"][key][i * 2] in [
                        "0",
                        gobject.baseobject.currentmd5,
                    ]:
                        v = noundictconfig["dict"][key][i * 2 + 1]
                        break

            if v is not None and key in content:
                if ___idx == 1:
                    xx = "ZX{}Z".format(chr(ord("B") + gobject.baseobject.zhanweifu))
                elif ___idx == 2:
                    xx = "{{{}}}".format(gobject.baseobject.zhanweifu)
                elif ___idx == 3:
                    xx = v
                content = content.replace(key, xx)
                mp1[xx] = v
                gobject.baseobject.zhanweifu += 1
        return content, mp1

    def process_after(self, res, mp1):
        for key in mp1:
            reg = re.compile(re.escape(key), re.IGNORECASE)
            res = reg.sub(mp1[key], res)
        return res
