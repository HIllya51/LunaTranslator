import gobject
import winrtutils
from myutils.config import _TR, static_data, getlang_inner2show
from myutils.utils import dynamiclink
from ocrengines.baseocrclass import baseocr
from qtsymbols import *
from gui.dynalang import LPushButton, LLabel
from myutils.utils import getlanguagespace


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


def question():
    dialog = QWidget()
    formLayout = QHBoxLayout()
    formLayout.setContentsMargins(0, 0, 0, 0)
    dialog.setLayout(formLayout)
    _allsupport = initsupports()
    supportlang = LLabel()
    supportlang.setText("_,_".join([getlang_inner2show(f) for f in _allsupport]))
    btndownload = LPushButton("添加语言包")
    btndownload.clicked.connect(
        lambda: gobject.baseobject.openlink(
            dynamiclink("{docs_server}/#/zh/useapis/ocrapi?id=windowsocr")
        )
    )
    formLayout.addWidget(LLabel("当前支持的语言"))
    formLayout.addWidget(supportlang)
    formLayout.addWidget(btndownload)
    return dialog


class OCR(baseocr):

    def langmap(self):
        return {"cht": "cht"}

    def initocr(self):
        self.supportmap = initsupports()

    def ocr(self, imagebinary):
        if len(self.supportmap) == 0:

            raise Exception(_TR("无可用语言"))
        if self.srclang == "auto":
            if len(self.supportmap) == 1:
                uselang = list(self.supportmap.values())[0]
            else:
                self.raise_cant_be_auto_lang()
        else:
            if self.srclang not in self.supportmap:

                _allsupport = initsupports()
                idx = [_["code"] for _ in static_data["lang_list_all"]].index(
                    self.srclang
                )
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
            else:
                uselang = self.srclang
        ret = winrtutils.OCR_f(
            imagebinary, self.supportmap[uselang], getlanguagespace(uselang)
        )
        boxs = [_[1:] for _ in ret]
        texts = [_[0] for _ in ret]
        return {"box": boxs, "text": texts}
