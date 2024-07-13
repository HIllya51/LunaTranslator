import os
import winrtutils
from myutils.config import _TR, static_data, getlang_inner2show
from myutils.utils import dynamiclink
from ocrengines.baseocrclass import baseocr
from qtsymbols import *
from gui.usefulwidget import getboxlayout


def initsupports():
    _allsupport = winrtutils.getlanguagelist()
    supportmap = {}
    for lang in static_data["language_list_translator_inner"] + [
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
    formLayout = QFormLayout()
    dialog.setLayout(formLayout)
    _allsupport = initsupports()
    supportlang = QLabel()
    supportlang.setText(", ".join([getlang_inner2show(f) for f in _allsupport]))
    btndownload = QPushButton(_TR("添加语言包"))
    btndownload.clicked.connect(
        lambda: os.startfile(dynamiclink("{docs_server}/#/zh/windowsocr"))
    )
    formLayout.addRow(
        _TR("当前支持的语言"), getboxlayout([supportlang, btndownload], makewidget=True)
    )


class OCR(baseocr):
    def initocr(self):
        self.supportmap = initsupports()

    def ocr(self, imagebinary):
        if self.srclang not in self.supportmap:

            _allsupport = initsupports()
            idx = static_data["language_list_translator_inner"].index(self.srclang)
            raise Exception(
                _TR("系统未安装")
                + ' "'
                + _TR(static_data["language_list_translator"][idx])
                + '" '
                + _TR("的OCR模型")
                + "\n"
                + _TR("当前支持的语言")
                + ": "
                + ", ".join([getlang_inner2show(f) for f in _allsupport])
            )

        if self.srclang in ["zh", "ja", "cht"]:
            space = ""
        else:
            space = " "

        ret = winrtutils.OCR_f(imagebinary, self.supportmap[self.srclang], space)
        boxs = [_[1:] for _ in ret]
        texts = [_[0] for _ in ret]

        return self.common_solve_text_orientation(boxs, texts)
