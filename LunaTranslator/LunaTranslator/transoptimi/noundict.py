from myutils.config import noundictconfig
import gobject, re
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    noundictconfig,
    _TR,
    _TRL,
)
import gobject
from gui.usefulwidget import getQMessageBox, threebuttons
from myutils.wrapper import Singleton


@Singleton
class noundictconfigdialog(QDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()

    def apply(self):
        rows = self.model.rowCount()
        newdict = {}
        for row in range(rows):
            if self.model.item(row, 1).text() == "":
                continue
            if self.model.item(row, 1).text() not in newdict:
                newdict[self.model.item(row, 1).text()] = [
                    self.model.item(row, 0).text(),
                    self.model.item(row, 2).text(),
                ]
            else:
                newdict[self.model.item(row, 1).text()] += [
                    self.model.item(row, 0).text(),
                    self.model.item(row, 2).text(),
                ]
        self.configdict["dict"] = newdict

    def __init__(
        self, parent, configdict, title, label=["游戏ID MD5", "原文", "翻译"], _=None
    ) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_TR(title))
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        model = QStandardItemModel(len(list(configdict["dict"].keys())), 1, self)
        row = 0
        for key in configdict["dict"]:  # 2
            if type(configdict["dict"][key]) == str:
                configdict["dict"][key] = ["0", configdict["dict"][key]]

            for i in range(len(configdict["dict"][key]) // 2):
                item = QStandardItem(configdict["dict"][key][i * 2])
                model.setItem(row, 0, item)
                item = QStandardItem(key)
                model.setItem(row, 1, item)
                item = QStandardItem(configdict["dict"][key][1 + i * 2])
                model.setItem(row, 2, item)
                row += 1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(self)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # table.clicked.connect(self.show_info)
        button = threebuttons()

        def clicked1():
            try:
                md5 = gobject.baseobject.currentmd5
                model.insertRow(
                    0, [QStandardItem(md5), QStandardItem(), QStandardItem()]
                )
            except:
                print_exc()
                model.insertRow(
                    0, [QStandardItem("0"), QStandardItem(), QStandardItem()]
                )

        button.btn1clicked.connect(clicked1)

        def clicked2():

            model.removeRow(table.currentIndex().row())

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(self.apply)
        button5 = QPushButton(self)
        button5.setText(_TR("设置所有词条为全局词条"))

        def clicked5():
            rows = model.rowCount()
            for row in range(rows):
                model.item(row, 0).setText("0")

        button5.clicked.connect(
            lambda: getQMessageBox(
                self,
                "警告",
                "!!!",
                True,
                True,
                lambda: clicked5(),
            )
        )

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = QPushButton()
        button4.setText(_TR("搜索"))

        def clicked4():
            text = searchcontent.text()

            rows = model.rowCount()
            cols = model.columnCount()
            for row in range(rows):
                ishide = True
                for c in range(cols):
                    if text in model.item(row, c).text():
                        ishide = False
                        break
                table.setRowHidden(row, ishide)

        button4.clicked.connect(clicked4)
        search.addWidget(button4)

        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)
        formLayout.addWidget(button5)
        setmd5layout = QHBoxLayout()
        setmd5layout.addWidget(QLabel(_TR("当前MD5")))
        md5content = QLineEdit(gobject.baseobject.currentmd5)
        setmd5layout.addWidget(md5content)
        button5 = QPushButton()
        button5.clicked.connect(
            lambda x: gobject.baseobject.__setattr__("currentmd5", md5content.text())
        )
        button5.setText(_TR("修改"))
        setmd5layout.addWidget(button5)
        self.button = button
        self.model = model
        self.configdict = configdict
        formLayout.addLayout(setmd5layout)
        self.resize(QSize(600, 400))
        self.show()


class Process:
    @staticmethod
    def get_setting_window(parent_window):
        return (
            noundictconfigdialog(
                parent_window, noundictconfig, "专有名词翻译设置(游戏ID 0表示全局)"
            ),
        )

    def process_before(self, content):
        ___idx = 1
        mp1 = {}
        for key in noundictconfig["dict"]:
            v = None
            if type(noundictconfig["dict"][key]) == str:
                v = noundictconfig["dict"][mp1[key]]
            else:
                for i in range(len(noundictconfig["dict"][key]) // 2):
                    if noundictconfig["dict"][key][i * 2] in [
                        "0",
                        gobject.baseobject.currentmd5,
                    ]:
                        v = noundictconfig["dict"][key][i * 2 + 1]
                        break

            if v is not None and key in content:
                if ___idx == 1:
                    xx = "ZX{}Z".format(chr(ord("B") + gobject.baseobject.zhanweifu))
                elif ___idx == 2:
                    xx = "{{{}}}".format(gobject.baseobject.zhanweifu)
                elif ___idx == 3:
                    xx = v
                content = content.replace(key, xx)
                mp1[xx] = v
                gobject.baseobject.zhanweifu += 1
        return content, mp1

    def process_after(self, res, mp1):
        for key in mp1:
            reg = re.compile(re.escape(key), re.IGNORECASE)
            res = reg.sub(mp1[key], res)
        return res
