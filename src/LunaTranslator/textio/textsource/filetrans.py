from textio.textsource.textsourcebase import basetext
from myutils.wrapper import threader
import json, time, os, gobject, NativeUtils, uuid
from myutils.config import globalconfig
from gui.usefulwidget import request_for_something


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

    def save(self, _, k, ts):
        self.data[k] = ts

    def load(self):
        for k in self.data:
            if not (isinstance(k, str) and isinstance(self.data[k], str)):
                yield None
                continue
            if self.data[k] and NativeUtils.similarity(self.data[k], k) < 0.2:
                yield None
                continue
            yield k


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
        for k in self.data:
            yield k


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

    def __init__(self, file, saveorigin):
        self.file = file
        self.saveorigin = saveorigin
        with open(file, "r", encoding="utf8") as ff:
            text = ff.read()
            if text.endswith("\n"):
                text = text[:-1]
            self.blocks = text.split("\n\n")

    def __len__(self):
        return len(self.blocks)

    def save(self, index, k, ts):
        if self.saveorigin:
            self.blocks[index] = (
                "\n".join(self.blocks[index].split("\n")[:2]) + "\n" + ts + "\n" + k
            )
        else:
            self.blocks[index] = (
                "\n".join(self.blocks[index].split("\n")[:2]) + "\n" + ts
            )

    def load(self):
        for k in self.blocks:
            yield "\n".join(k.split("\n")[2:])


class parsevtt:
    def __del__(self):
        with open(
            os.path.join(
                os.path.dirname(self.file), "luna_" + os.path.basename(self.file)
            ),
            "w",
            encoding="utf8",
        ) as ff:
            ff.write("\n".join(self.header + self.blocks))

    def __init__(self, file):
        self.file = file
        with open(file, "r", encoding="utf8") as ff:
            text = ff.read()
            lines = text.split("\n")
            if lines[0] != "WEBVTT":
                raise Exception("invalid")
            self.header = lines[:2]
            self.blocks = lines[2:]

    def __len__(self):
        return (len(self.blocks) + 1) // 3

    def save(self, index, k, ts):
        self.blocks[3 * index + 1] = ts

    def load(self):
        for i in range((len(self.blocks) + 1) // 3):
            yield self.blocks[3 * i + 1]


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
        for a in self.data:
            yield a[a.find("]") + 1 :]


class filetrans(basetext):

    def end(self):

        gobject.base.progresssignal2.emit("", 0)

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
        toppest = globalconfig["toppest_translator"]
        if toppest:
            return ts.get(toppest, None)
        return (list(ts.values()) + [None])[0]

    srtsaveoriginuuid = uuid.uuid4()

    def starttranslatefiles(self, files: "list[str]"):
        for i, file in enumerate(files):
            self.startsql(file + ".sqlite")
            if file.lower().endswith(".txt"):
                file = parsetxt(file)
            elif file.lower().endswith(".json"):
                file = parsejson(file)
            elif file.lower().endswith(".lrc"):
                file = parselrc(file)
            elif file.lower().endswith(".srt"):
                saveorigin = request_for_something(
                    gobject.base.focusWindow, self.srtsaveoriginuuid, "是否保留原文？"
                )
                file = parsesrt(file, saveorigin)
            elif file.lower().endswith(".vtt"):
                file = parsevtt(file)
            self.__starttranslatefile(file, i, len(files))

    def __starttranslatefile(self, file: parsetxt, i, n):
        gobject.base.progresssignal3.emit(len(file))
        gobject.base.progresssignal2.emit("", 0)

        for index, line in enumerate(file.load()):
            if self.ending:
                return
            while not self.isautorunning:
                if self.ending:
                    return
                time.sleep(0.1)

            lenfile = len(file)

            class __p:
                def __del__(self):
                    gobject.base.progresssignal2.emit(
                        "{}{}/{}{}{:0.2f}% ".format(
                            "{}/{}{}".format(i + 1, n, " " * 8) if (n > 1) else "",
                            index + 1,
                            lenfile,
                            " " * 8,
                            100 * (index + 1) / lenfile,
                        ),
                        (index + 1),
                    )

            _ref = __p()
            if not line:
                continue
            ts: str = self.query(line)
            if not ts:
                ts = self.waitfortranslation(line)
            if self.ending:
                return

            if not ts:
                continue
            if len(ts.split("\n")) == len(line.split("\n")):
                file.save(index, line, ts)
            elif len(ts.split("\n")) > len(line.split("\n")):
                # 删除空行
                lines = [line for line in ts.split("\n") if line]
                tsx = "\n".join(lines)
                if len(tsx.split("\n")) == len(line.split("\n")):
                    file.save(index, line, tsx)
