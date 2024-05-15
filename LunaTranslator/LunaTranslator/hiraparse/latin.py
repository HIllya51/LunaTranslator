from hiraparse.basehira import basehira


class latin(basehira):

    def parse(self, text):
        _x = []
        i = 0
        for _ in text.split(" "):
            if i:
                _x.append({"orig": " ", "hira": ""})

            _x.append({"orig": _, "hira": ""})
            i += 1
        return _x
