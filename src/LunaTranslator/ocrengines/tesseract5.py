import os, uuid, gobject
from myutils.utils import subprochiderun
from myutils.config import _TR, globalconfig
from ocrengines.baseocrclass import baseocr
from language import Languages
from myutils.regedit import LOCAL_MACHINE


class OCR(baseocr):

    def findts(self):
        try:
            _ = LOCAL_MACHINE.open(r"SOFTWARE\Tesseract-OCR", query=True).query("Path")
            _ = os.path.join(_, "tesseract.exe")
            return _
        except:
            return

    def list_langs(self):
        if not (self.path and os.path.exists(self.path)):
            raise Exception(_TR("未安装"))
        res = subprochiderun('"{}" --list-langs'.format(self.path)).stdout
        return res.split("\n")[1:-1]

    def langmap(self):
        # https://github.com/tesseract-ocr/tessdoc/blob/main/tess3/Data-Files.md
        return {
            Languages.Chinese: "chi_sim",
            Languages.TradChinese: "chi_tra",
            Languages.Japanese: "jpn",
            Languages.English: "eng",
            Languages.Russian: "rus",
            Languages.Korean: "kor",
            Languages.Arabic: "ara",
            Languages.Italian: "ita",
            Languages.Polish: "pol",
            Languages.Spanish: "spa",
            Languages.Swedish: "swe",
            Languages.Ukrainian: "ukr",
            Languages.Vietnamese: "vie",
            Languages.French: "fra",
            Languages.Turkish: "tur",
            Languages.German: "deu",
            Languages.Dutch: "nld",
            Languages.Portuguese: "por",
            Languages.Czech: "ces",
            Languages.Hungarian: "hun",
            Languages.Thai: "tha",
            Languages.Latin: "lat",
        }

    def init(self):
        self.path = self.findts()
        self.langs = self.list_langs()
        print(self.langs)

    def ocr(self, imagebinary):
        if not (self.path and os.path.exists(self.path)):
            raise Exception(_TR("未安装"))
        self.raise_cant_be_auto_lang()
        lang = self.srclang
        psm = 6
        imgfile = None
        verticalocr = globalconfig.get("verticalocr", 2)
        if verticalocr == 0:
            pass
        elif verticalocr == 1:
            lang += "_vert"
            psm = 5
        elif verticalocr == 2:
            fname = gobject.gettempdir(str(uuid.uuid4()) + ".png")
            with open(fname, "wb") as ff:
                ff.write(imagebinary)
            imgfile = os.path.abspath(fname)
            _ = subprochiderun(
                '"{}" "{}" stdout -l osd --psm 0'.format(self.path, imgfile)
            )
            err = _.stderr
            if len(err):
                pass
            elif "Orientation in degrees: 0" not in _.stdout:
                lang += "_vert"
                psm = 5
        if not imgfile:
            fname = gobject.gettempdir(str(uuid.uuid4()) + ".png")
            with open(fname, "wb") as ff:
                ff.write(imagebinary)
            imgfile = os.path.abspath(fname)
        _ = subprochiderun(
            '"{}" "{}" - -l {} --psm {}'.format(self.path, imgfile, lang, psm)
        )
        try:
            os.remove(imgfile)
        except:
            pass
        res = _.stdout
        err = _.stderr
        if len(err):
            raise Exception(err)

        return res.split("\n")
