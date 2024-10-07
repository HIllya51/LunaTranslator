from hiraparse.basehira import basehira


def splitstr(input_str: str, delimiters):
    lst = []
    cl = ""
    while len(input_str):
        su = False
        for deli in delimiters:
            if input_str.startswith(deli):
                if len(cl):
                    lst.append(cl)
                    cl = ""
                lst.append(deli)
                input_str = input_str[len(deli) :]
                su = True
                break
        if su:
            continue
        else:
            cl += input_str[0]
            input_str = input_str[1:]
    if len(cl):
        lst.append(cl)
    return lst


class latin(basehira):

    def parse(self, text: str):
        punctuations = self.config["punctuations"]
        sps = splitstr(text, punctuations)

        _x = []
        for c in sps:
            if c in punctuations:
                _x.append({"orig": c, "hira": "", "isdeli": True})
            else:
                _x.append({"orig": c, "hira": c})

        return _x
