import gobject
import winrtutils
from myutils.config import _TR, static_data, getlang_inner2show
from myutils.utils import dynamiclink
from ocrengines.baseocrclass import baseocr
from qtsymbols import *
from gui.usefulwidget import getboxlayout
from gui.dynalang import LPushButton, LFormLayout, LLabel


def initsupports():
    _allsupport = winrtutils.getlanguagelist()
    supportmap = {}
    for lang in [_["code"] for _ in static_data["lang_list_all"]] + [
        "zh-Hans",
        "zh-Hant",
    ]:
        if lang == "zh" or lang == "cht":
            continue
        for s in _allsupport:
            if s.startswith(lang) or lang.startswith(s):
                supportmap[lang] = s
                break
    if "zh-Hans" in supportmap:
        v = supportmap.pop("zh-Hans")
        supportmap["zh"] = v
    if "zh-Hant" in supportmap:
        v = supportmap.pop("zh-Hant")
        supportmap["cht"] = v
    return supportmap


def question(dialog: QDialog):
    formLayout = LFormLayout()
    dialog.setLayout(formLayout)
    _allsupport = initsupports()
    supportlang = LLabel()
    supportlang.setText("_,_".join([getlang_inner2show(f) for f in _allsupport]))
    btndownload = LPushButton("添加语言包")
    btndownload.clicked.connect(
        lambda: gobject.baseobject.openlink(
            dynamiclink("{docs_server}/#/zh/windowsocr")
        )
    )
    formLayout.addRow(
        "当前支持的语言", getboxlayout([supportlang, btndownload], makewidget=True)
    )


class OCR(baseocr):
    ocr_cant_auto = True

    def langmap(self):
        return {"cht": "cht"}

    def initocr(self):
        self.supportmap = initsupports()

    def ocr(self, imagebinary):
        if self.srclang not in self.supportmap:

            _allsupport = initsupports()
            idx = [_["code"] for _ in static_data["lang_list_all"]].index(self.srclang)
            raise Exception(
                _TR("系统未安装")
                + ' "'
                + _TR([_["zh"] for _ in static_data["lang_list_all"]][idx])
                + '" '
                + _TR("的OCR模型")
                + "\n"
                + _TR("当前支持的语言")
                + ": "
                + ", ".join([_TR(getlang_inner2show(f)) for f in _allsupport])
            )

        ret = winrtutils.OCR_f(imagebinary, self.supportmap[self.srclang], self.space_1)
        boxs = [_[1:] for _ in ret]
        texts = [_[0] for _ in ret]
        return {"box": boxs, "text": texts}
