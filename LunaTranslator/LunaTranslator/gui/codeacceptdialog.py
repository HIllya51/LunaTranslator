import functools
from PyQt5.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QHeaderView,
)
from PyQt5.QtWidgets import QHBoxLayout, QTableView
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt, QSize
from gui.usefulwidget import getspinbox, threebuttons
from myutils.utils import checkencoding
from myutils.config import globalconfig, _TR, _TRL

from myutils.wrapper import Singleton

nowsuppertcodes = _TRL(
    [
        "日语(SHIFT-JIS)",
        "简体中文(GBK)",
        "繁体中文(BIG5)",
        "韩语(EUC-KR)",
        "英语(ASCII)",
        "其他",
    ]
)
nowsuppertcodespy = ["SHIFT-JIS", "GBK", "BIG5", "EUC-KR", "ASCII"]


@Singleton
class codeacceptdialog(QDialog):
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
        super().__init__(parent, Qt.WindowCloseButtonHint)
        title = "接受的编码"
        self.setWindowTitle(_TR(title))
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = QStandardItemModel(len(globalconfig["accept_encoding"]), 1, self)

        self.model.setHorizontalHeaderLabels(_TRL(["接受的编码"]))
        self.table = QTableView(self)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        row = 0
        for code in globalconfig["accept_encoding"]:  # 2

            if code in nowsuppertcodespy:
                idx = nowsuppertcodespy.index(code)
            else:
                idx = len(nowsuppertcodespy)
            itemsaver = QStandardItem()
            self.model.setItem(row, 0, itemsaver)
            index = self.model.index(row, 0)
            codecombox = QComboBox()
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
        button = threebuttons()
        button.btn1clicked.connect(self.clicked1)
        button.btn2clicked.connect(self.clicked2)
        button.btn3clicked.connect(self.apply)
        self.button = button
        formLayout.addWidget(self.table)
        formLayout.addWidget(button)
        formLayout.addWidget(QLabel())

        _checkunicode = QCheckBox(_TR("使用Unicode范围过滤"))
        _checkunicode.setChecked(globalconfig["accept_use_unicode"])
        _checkunicode.stateChanged.connect(
            lambda x: globalconfig.__setitem__("accept_use_unicode", x)
        )
        formLayout.addWidget(_checkunicode)
        liwai = QLineEdit(globalconfig["accept_character"])
        liwai.textChanged.connect(
            lambda x: globalconfig.__setitem__("accept_character", x)
        )
        _hb = QHBoxLayout()
        _hb.addWidget(QLabel(_TR("Unicode范围")))
        _hb.addWidget(getspinbox(0, 65535, globalconfig, "accept_use_unicode_start"))
        _hb.addWidget(getspinbox(0, 65535, globalconfig, "accept_use_unicode_end"))
        formLayout.addLayout(_hb)

        formLayout.addWidget(QLabel())
        _hb = QHBoxLayout()
        _hb.addWidget(QLabel(_TR("例外允许的字符")))
        _hb.addWidget(liwai)

        formLayout.addLayout(_hb)
        self.resize(QSize(600, 500))
        self.show()

    def clicked1(self):
        itemsaver = QStandardItem()
        self.model.insertRow(0, [itemsaver])
        codecombox = QComboBox()
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

    def clicked2(self):

        self.model.removeRow(self.table.currentIndex().row())

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
