import gobject
import winrtutils, windows, re
import subprocess
from myutils.config import _TR
from myutils.utils import dynamiclink
from ocrengines.baseocrclass import baseocr
from qtsymbols import *
from gui.dynalang import LPushButton, LLabel
from myutils.utils import getlanguagespace
from gui.dynalang import LPushButton, LFormLayout, LLabel
from gui.usefulwidget import SuperCombo, getboxlayout
import threading, qtawesome
from myutils.subproc import subproc_w


def getallsupports():
    _ = (
        subproc_w(
            "powershell Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*' }",
            needstdio=True,
            run=True,
        )
        .stdout.decode()
        .splitlines()
    )
    langs = []
    langsinter = []
    for i in range(len(_)):
        if _[i].startswith("Name"):
            if "Installed" in _[i + 1]:
                continue
            langs.append(re.search("Language.OCR~~~(.*?)~", _[i]).groups()[0])
            langsinter.append(re.search("Language.OCR~~~(.*)", _[i]).group())
    return langs, langsinter


class _SuperCombo(SuperCombo):
    setlist = pyqtSignal(list, list)

    def addItems(self, items, internals):
        self.clear()
        super().addItems(items, internals)


def loadlist(combo: _SuperCombo):
    lang, inter = getallsupports()
    combo.setlist.emit(lang, inter)


def installx(combo: _SuperCombo, btninstall):
    if combo.currentIndex() == -1:
        return
    btninstall.setEnabled(False)
    combo.setEnabled(False)
    lang = combo.getIndexData(combo.currentIndex())
    subprocess.run(
        "powershell $Capability = Get-WindowsCapability -Online | Where-Object {{ $_.Name -Like '{}' }} | Add-WindowsCapability -Online".format(
            lang
        ),
    )
    lang, inter = getallsupports()
    combo.setlist.emit(lang, inter)
    btninstall.setEnabled(True)
    combo.setEnabled(True)


def question():
    dialog = QWidget()
    formLayout = LFormLayout()
    formLayout.setContentsMargins(0, 0, 0, 0)
    dialog.setLayout(formLayout)
    supportlang = QLabel()
    supportlang.setText(", ".join([_[1] for _ in winrtutils.getlanguagelist()]))
    supportlang.setWordWrap(True)
    formLayout.addRow("当前支持的语言", supportlang)

    lst = []
    if not windows.IsUserAnAdmin():
        nopri = LLabel("权限不足，请以管理员权限运行！")
        lst.append(nopri)
        btndownload = LPushButton("添加语言包")
        btndownload.clicked.connect(
            lambda: gobject.baseobject.openlink(
                dynamiclink("{docs_server}/#/zh/useapis/ocrapi?id=windowsocr")
            )
        )
        lst.append(btndownload)
    else:
        combo = _SuperCombo()
        combo.setlist.connect(combo.addItems)
        btninstall = LPushButton("添加")
        btninstall.clicked.connect(
            lambda: threading.Thread(target=installx, args=(combo, btninstall)).start()
        )
        lst.append(combo)
        lst.append(btninstall)
        threading.Thread(target=loadlist, args=(combo,)).start()
        btndownload = QPushButton(icon=qtawesome.icon("fa.question"))
        btndownload.clicked.connect(
            lambda: gobject.baseobject.openlink(
                dynamiclink("{docs_server}/#/zh/useapis/ocrapi?id=windowsocr")
            )
        )
        lst.append(btndownload)
    formLayout.addRow(
        "添加语言包",
        getboxlayout(lst, makewidget=True, margin0=True),
    )
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
