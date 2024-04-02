import os
from myutils.config import _TR, ocrsetting

from ocrengines.baseocrclass import baseocr
from myutils.subproc import subproc_w


def list_langs():
    path = ocrsetting["tesseract5"]["args"]["路径"]
    if os.path.exists(path) == False:
        return []
    res = subproc_w(
        '"{}" --list-langs'.format(path), needstdio=True, run=True, encoding="utf8"
    ).stdout
    return res.split("\n")[1:-1]


class OCR(baseocr):
    def initocr(self):
        self.langs = list_langs()

    def ocr(self, imgfile):
        self.checkempty(["路径"])
        path = self.config["路径"]
        if os.path.exists(path) == False:
            raise Exception(_TR("路径不存在"))
        _ = subproc_w(
            '"{}" "{}" - -l {} {}'.format(
                path, imgfile, self.langs[self.config["语言"]], self.config["附加参数"]
            ),
            needstdio=True,
            encoding="utf8",
            run=True,
        )
        res = _.stdout
        err = _.stderr
        if len(err):
            raise Exception(err)

        return self.space.join(res.split("\n"))
