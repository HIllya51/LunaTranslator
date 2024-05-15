from myutils.config import globalconfig, static_data
from traceback import print_exc


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

    def parseparse(self, text):
        hira = []
        try:
            if self.needinit:
                self.init()
                self.needinit = False
            try:
                hira = self.parse(text)
            except Exception as e:
                self.needinit = True
                raise e
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
        except:
            print_exc()
        return hira
