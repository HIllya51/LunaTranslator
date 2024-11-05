from ocrengines.baseocrclass import baseocr
from ctypes import CDLL, c_char_p, c_size_t, c_void_p, CFUNCTYPE, sizeof, c_wchar_p
import json, os

youdaosig = CDLL(
    os.path.join(os.path.dirname(__file__), f"ydocr{sizeof(c_void_p)*8}.dll")
)
ydocr = youdaosig.ydocr
ydocr.argtypes = c_void_p, c_size_t, c_wchar_p, c_wchar_p, c_void_p


def doocr(image, src, tgt):
    ret = []
    fp = CFUNCTYPE(None, c_char_p)(ret.append)
    ydocr(image, len(image), src, tgt, fp)
    boxs = []
    texts = []
    transs = []
    for line in ret:
        line = json.loads(line.decode("utf8"))
        boxs.append(line[:4])
        texts.append(line[4])
        transs.append(line[5])
    return boxs, transs, texts


class OCR(baseocr):

    def langmap(self):
        return {"zh": "zh-CHS", "cht": "zh-CHT"}

    def ocr(self, imagebinary):

        boxs, transs, texts = doocr(imagebinary, self.srclang, self.tgtlang)

        if self.config["Translate"]:
            return {"box": boxs, "text": transs, "isocrtranslate": True}
        else:
            return {"box": boxs, "text": texts}
