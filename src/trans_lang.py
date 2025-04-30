import sys, os

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, "./LunaTranslator")
from translator.youdaodict import TS


class TS1(TS):

    @property
    def srclang(self):
        return "zh"

    @property
    def tgtlang(self):
        return self.xxxxx

    @tgtlang.setter
    def tgtlang(self, _):
        self.xxxxx = _


if __name__ == "__main__":

    import os, json

    f = "zh.json"
    with open("./files/lang/" + f, "r", encoding="utf8") as ff:
        js = ff.read()
        js = json.loads(js)
    xxx = {
        # "en": "en",
        # "cht": "cht",
    }
    needpop = []
    for k in js:
        kk = False
        try:
            k.encode("ascii")
            print(k)
            kk = True
        except:
            pass
        if k not in js or kk:
            needpop.append(k)
    for k in needpop:
        js.pop(k)
    with open(f"./files/lang/" + f, "w", encoding="utf8") as ff:
        ff.write(json.dumps(js, ensure_ascii=False, sort_keys=False, indent=4))
    a = TS1("baiduapi")
    for kk in os.listdir("./files/lang"):
        with open(f"./files/lang/{kk}", "r", encoding="utf8") as ff:

            jsen = json.loads(ff.read())

        needpop = []
        for k in jsen:
            if k not in js:
                needpop.append(k)
        print(kk, needpop)
        for k in needpop:
            jsen.pop(k)
        with open(f"./files/lang/{kk}", "w", encoding="utf8") as ff:
            ff.write(json.dumps(jsen, ensure_ascii=False, sort_keys=False, indent=4))

        for k in js:

            if k not in jsen or jsen[k] == "":
                a.tgtlang = xxx.get(kk.split(".")[0])
                if not a.tgtlang:
                    jsen[k] = ""
                else:
                    jsen[k] = list(a.translate(k))[0]
                    print(k, jsen[k])
                with open(f"./files/lang/{kk}", "w", encoding="utf8") as ff:
                    ff.write(
                        json.dumps(jsen, ensure_ascii=False, sort_keys=False, indent=4)
                    )
