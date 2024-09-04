from textsource.textsourcebase import basetext
from myutils.wrapper import threader
import json, time, os, gobject, re
from myutils.config import globalconfig


class parsejson:
    def __del__(self):

        with open(
            os.path.join(
                os.path.dirname(self.file), "ts_" + os.path.basename(self.file)
            ),
            "w",
            encoding="utf8",
        ) as ff:
            json.dump(self.data, ff, ensure_ascii=False, indent=4)

    def __init__(self, file):
        self.file = file
        with open(file, "r", encoding="utf8") as ff:
            self.data = json.load(ff)

    def __len__(self):
        return len(self.data)

    def save(self, index, k, ts):
        self.data[k] = ts

    def load(self):
        for i, k in enumerate(self.data):
            if self.data[k]:
                yield i, None
                continue
            yield i, k


class parsetxt:
    def __del__(self):

        with open(
            os.path.join(
                os.path.dirname(self.file), "luna_" + os.path.basename(self.file)
            ),
            "w",
            encoding="utf8",
        ) as ff:
            ff.write("\n".join(self.data))

    def __init__(self, file):
        self.file = file
        with open(file, "r", encoding="utf8") as ff:
            self.data = ff.read().split("\n")

    def __len__(self):
        return len(self.data)

    def save(self, index, k, ts):
        self.data[index] = ts

    def load(self):
        for i, k in enumerate(self.data):
            yield i, k


class parsesrt:
    def __del__(self):
        with open(
            os.path.join(
                os.path.dirname(self.file), "luna_" + os.path.basename(self.file)
            ),
            "w",
            encoding="utf8",
        ) as ff:
            ff.write("\n\n".join(self.blocks))

    def __init__(self, file):
        self.file = file
        with open(file, "r", encoding="utf8") as ff:
            self.blocks = ff.read().split("\n\n")

    def __len__(self):
        return len(self.blocks)

    def save(self, index, k, ts):
        self.blocks[index] = "\n".join(self.blocks[index].split("\n")[:2]) + "\n" + ts

    def load(self):
        for i, k in enumerate(self.blocks):
            yield i, "\n".join(k.split("\n")[2:])


class parselrc:
    def __del__(self):

        with open(
            os.path.join(
                os.path.dirname(self.file), "luna_" + os.path.basename(self.file)
            ),
            "w",
            encoding="utf8",
        ) as ff:
            ff.write("\n".join(self.data))

    def __init__(self, file):
        self.file = file
        with open(file, "r", encoding="utf8") as ff:
            self.data = ff.read().split("\n")

    def __len__(self):
        return len(self.data)

    def save(self, index, k, ts):
        self.data[index] = self.data[index][: self.data[index].find("]") + 1] + ts

    def load(self):
        for i, a in enumerate(self.data):
            yield i, a[a.find("]") + 1 :]


class filetrans(basetext):

    def end(self):

        gobject.baseobject.settin_ui.progresssignal2.emit("", 0)

    def __init__(self) -> None:
        super(filetrans, self).__init__()

    def __query(self, origin):
        try:
            get = self.sqlwrite2.execute(
                "select machineTrans from artificialtrans where origin=?", (origin,)
            ).fetchone()
            if not get:
                return {}
            return json.loads(get[0])
        except:
            return {}

    def query(self, origin):
        ts = self.__query(origin)
        t = ts.get(globalconfig["embedded"]["translator_2"], None)
        if t:
            return t
        if globalconfig["embedded"]["as_fast_as_posible"]:
            return (list(ts.values()) + [None])[0]

    @threader
    def starttranslatefile(self, file):
        self.startsql(file + ".sqlite")
        if file.lower().endswith(".txt"):
            file = parsetxt(file)
        elif file.lower().endswith(".json"):
            file = parsejson(file)
        elif file.lower().endswith(".lrc"):
            file = parselrc(file)
        elif file.lower().endswith(".srt"):
            file = parsesrt(file)
        gobject.baseobject.settin_ui.progresssignal3.emit(len(file))
        gobject.baseobject.settin_ui.progresssignal2.emit("", 0)

        for index, line in file.load():
            if self.ending:
                return
            while not self.isautorunning:
                if self.ending:
                    return
                time.sleep(0.1)

            lenfile = len(file)

            class __p:
                def __del__(self):
                    gobject.baseobject.settin_ui.progresssignal2.emit(
                        "{}/{} {:0.2f}% ".format(
                            index + 1, lenfile, 100 * (index + 1) / lenfile
                        ),
                        (index + 1),
                    )

            _ref = __p()
            if not line:
                continue
            ts = self.query(line)
            if not ts:
                ts = self.waitfortranslation(line)
            if self.ending:
                return

            if not ts:
                continue
            if len(ts.split("\n")) == len(line.split("\n")):
                file.save(index, line, ts)
