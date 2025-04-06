from qtsymbols import *
import functools, codecs
from myutils.config import globalconfig
from myutils.wrapper import Singleton
from gui.usefulwidget import (
    getspinbox,
    threebuttons,
    getlineedit,
    TableViewW,
    SuperCombo,
)
from gui.dynalang import LStandardItemModel, LDialog, LCheckBox, LLabel

nowsuppertcodes = [
    "日语_(SHIFT-JIS)",
    "简体中文_(GBK)",
    "繁体中文_(BIG5)",
    "韩语_(EUC-KR)",
    "英语_(ASCII)",
    "其他",
]
nowsuppertcodespy = ["SHIFT-JIS", "GBK", "BIG5", "EUC-KR", "ASCII"]


def checkencoding(code):

    try:
        codecs.lookup(code)
        return True
    except LookupError:
        return False


@Singleton
class codeacceptdialog(LDialog):
    def _setcode_i(self, combox: QComboBox, itemsaver_, code="", idx=0):
        itemsaver_.saveidx = idx
        if idx < len(nowsuppertcodespy):
            itemsaver_.setText(nowsuppertcodespy[idx])
            combox.setEditable(False)
        else:
            itemsaver_.setText(code)
            combox.setCurrentText(code)
            combox.setEditable(True)
            combox.setEditText(code)

    def _setcode_c(self, combox: QComboBox, itemsaver_, code=""):
        if combox.currentIndex() == len(nowsuppertcodespy):
            itemsaver_.setText(code)

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        title = "接受的编码"
        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel(len(globalconfig["accept_encoding"]), 1, self)

        self.model.setHorizontalHeaderLabels(["接受的编码"])
        self.table = TableViewW(self)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        row = 0
        for code in globalconfig["accept_encoding"]:  # 2

            if code in nowsuppertcodespy:
                idx = nowsuppertcodespy.index(code)
            else:
                idx = len(nowsuppertcodespy)
            itemsaver = QStandardItem()
            self.model.setItem(row, 0, itemsaver)
            index = self.model.index(row, 0)
            codecombox = SuperCombo()
            codecombox.addItems((nowsuppertcodes))
            codecombox.setCurrentIndex(idx)
            self.table.setIndexWidget(index, codecombox)
            self._setcode_i(codecombox, itemsaver, code, idx)

            codecombox.currentIndexChanged.connect(
                functools.partial(self._setcode_i, codecombox, itemsaver, "")
            )
            codecombox.currentTextChanged.connect(
                functools.partial(self._setcode_c, codecombox, itemsaver)
            )

            row += 1
        button = threebuttons(texts=["添加行", "删除行", "立即应用"])
        button.btn1clicked.connect(self.clicked1)
        button.btn2clicked.connect(self.table.removeselectedrows)
        button.btn3clicked.connect(self.apply)
        self.button = button
        formLayout.addWidget(self.table)
        formLayout.addWidget(button)
        formLayout.addWidget(QLabel())

        _checkunicode = LCheckBox(("使用Unicode范围过滤"))
        _checkunicode.setChecked(globalconfig["accept_use_unicode"])
        _checkunicode.stateChanged.connect(
            lambda x: globalconfig.__setitem__("accept_use_unicode", x)
        )
        formLayout.addWidget(_checkunicode)
        _hb = QHBoxLayout()
        _hb.addWidget(LLabel(("Unicode范围")))
        _hb.addWidget(getspinbox(0, 65535, globalconfig, "accept_use_unicode_start"))
        _hb.addWidget(getspinbox(0, 65535, globalconfig, "accept_use_unicode_end"))
        formLayout.addLayout(_hb)

        formLayout.addWidget(QLabel())
        _hb = QHBoxLayout()
        _hb.addWidget(LLabel(("例外允许的字符")))
        _hb.addWidget(getlineedit(globalconfig, "accept_character"))

        formLayout.addLayout(_hb)
        self.resize(QSize(600, 500))
        self.show()

    def clicked1(self):
        itemsaver = QStandardItem()
        self.model.insertRow(0, [itemsaver])
        codecombox = SuperCombo()
        codecombox.addItems((nowsuppertcodes))
        self._setcode_i(codecombox, itemsaver)
        codecombox.currentIndexChanged.connect(
            functools.partial(self._setcode_i, codecombox, itemsaver, "")
        )
        codecombox.currentTextChanged.connect(
            functools.partial(self._setcode_c, codecombox, itemsaver)
        )
        index = self.model.index(0, 0)
        self.table.setIndexWidget(index, codecombox)

    def apply(self):

        rows = self.model.rowCount()
        ll = []
        for row in range(rows):
            print(row)
            code = self.model.item(row, 0).text()
            idx = self.model.item(row, 0).saveidx
            print(idx, code)

            if idx == len(nowsuppertcodespy):
                if code.upper() in nowsuppertcodespy:
                    code = code.upper()
                elif checkencoding(code) == False:
                    continue
            else:
                code = nowsuppertcodespy[idx]
            if code in ll:
                continue
            ll.append(code)
        globalconfig["accept_encoding"] = ll

    def closeEvent(self, _):
        self.button.setFocus()
        self.apply()
