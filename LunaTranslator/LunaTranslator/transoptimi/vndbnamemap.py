from myutils.config import savehook_new_data
import gobject


class Process:

    def process_before(self, s):

        exepath = gobject.baseobject.textsource.pname
        namemap = savehook_new_data[exepath]["namemap"]
        bettermap = {}
        for k, v in namemap.items():
            for sp in ["・", " "]:
                spja = k.split(sp)
                spen = v.split(" ")
                if len(spja) == len(spen) and len(spen) > 1:
                    for i in range(len(spja)):
                        if len(spja[i]) >= 2:
                            bettermap[spja[i]] = spen[i]

        for k, v in namemap.items():
            s = s.replace(k, v)
        for k, v in bettermap.items():
            s = s.replace(k, v)
        return s, {}
