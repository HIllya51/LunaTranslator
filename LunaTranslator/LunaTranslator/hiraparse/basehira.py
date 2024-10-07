from myutils.config import globalconfig, static_data
from traceback import print_exc
from myutils.proxy import getproxy


class basehira:
    def init(self):
        pass

    def parse(self, text):
        return []

    def __init__(self, typename) -> None:
        self.typename = typename
        self.castkata2hira = str.maketrans(
            static_data["allkata"], static_data["allhira"]
        )
        self.casthira2kata = str.maketrans(
            static_data["allhira"], static_data["allkata"]
        )
        self.needinit = True
        self.init()
        self.needinit = False

    @property
    def config(self):
        return globalconfig["hirasetting"][self.typename]["args"]

    @property
    def proxy(self):
        return getproxy(("hirasetting", self.typename))

    def splitspace(self, word: str):
        start = ""
        end = ""
        while word.startswith(" "):
            start += " "
            word = word[1:]
        while word.endswith(" "):
            end += " "
            word = word[:-1]
        return start, word, end

    def safeparse(self, text):
        try:

            if self.needinit:
                self.init()
                self.needinit = False
            return self.parse_multilines(text)
        except:
            print_exc()
            self.needinit = True
            return []

    def parse_multilines(self, text):

        hira = []
        for i, _ in enumerate(text.split("\n")):
            h = self.parse_singleline(_)
            if "".join(__["orig"] for __ in h) != _:
                raise Exception("not match")
            if i:
                hira += [{"orig": "\n", "hira": "\n"}]
            hira += h
        return hira

    def parse_singleline(self, text):
        hira = self.parse(text)

        __parsekonge = []
        for word in hira:
            ori = word["orig"]
            start, w, end = self.splitspace(ori)
            if len(start) == 0 and len(end) == 0:
                __parsekonge.append(word)
                continue
            word["orig"] = w
            word["hira"] = self.splitspace(word["hira"])[1]

            if len(start):
                __parsekonge.append({"orig": start, "hira": start})
            __parsekonge.append(word)
            if len(end):
                __parsekonge.append({"orig": end, "hira": end})
        hira = __parsekonge
        for _1 in range(len(hira)):
            _ = len(hira) - 1 - _1
            if globalconfig["hira_vis_type"] == 0:
                hira[_]["hira"] = hira[_]["hira"].translate(self.castkata2hira)
            elif globalconfig["hira_vis_type"] == 1:
                hira[_]["hira"] = hira[_]["hira"].translate(self.casthira2kata)
            elif globalconfig["hira_vis_type"] == 2:
                __kanas = [
                    static_data["hira"] + ["っ"],
                    static_data["kata"] + ["ッ"],
                ]
                target = static_data["roma"] + ["-"]
                for _ka in __kanas:
                    for __idx in range(len(_ka)):
                        _reverse_idx = len(_ka) - 1 - __idx
                        hira[_]["hira"] = hira[_]["hira"].replace(
                            _ka[_reverse_idx], target[_reverse_idx]
                        )

        return hira
