import gobject
import winrtutils
from myutils.config import _TR, static_data
from myutils.utils import dynamiclink
from ocrengines.baseocrclass import baseocr
from qtsymbols import *
from gui.dynalang import LPushButton, LLabel
from myutils.utils import getlanguagespace


def question():
    dialog = QWidget()
    formLayout = QHBoxLayout()
    formLayout.setContentsMargins(0, 0, 0, 0)
    dialog.setLayout(formLayout)
    supportlang = QLabel()
    supportlang.setText(", ".join([_[1] for _ in winrtutils.getlanguagelist()]))
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
        return {"zh": "zh-Hans", "cht": "zh-Hant"}

    def ocr(self, imagebinary):
        supports = [_[0] for _ in winrtutils.getlanguagelist()]
        if len(supports) == 0:

            raise Exception(_TR("无可用语言"))
        if self.srclang == "auto":
            if len(supports) == 1:
                uselang = supports[0]
            else:
                self.raise_cant_be_auto_lang()
        else:
            if not winrtutils.check_language_valid(self.srclang):
                raise Exception(
                    _TR("系统未安装当前语言的OCR模型")
                    + "\n"
                    + _TR("当前支持的语言")
                    + ": "
                    + ", ".join([_[1] for _ in winrtutils.getlanguagelist()])
                )
            uselang = self.srclang
        ret = winrtutils.OCR_f(imagebinary, uselang, getlanguagespace(uselang))
        boxs = [_[1:] for _ in ret]
        texts = [_[0] for _ in ret]
        return {"box": boxs, "text": texts}
