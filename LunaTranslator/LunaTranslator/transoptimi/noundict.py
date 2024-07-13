from myutils.config import noundictconfig, savehook_new_data, _TR, _TRL
import gobject, re, functools
from qtsymbols import *
from traceback import print_exc
import gobject
from gui.usefulwidget import getQMessageBox, threebuttons
from myutils.wrapper import Singleton_close
from myutils.utils import checkpostusing


@Singleton_close
class noundictconfigdialog(QDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()

    def showmenu(self, table: QTableView, pos):
        r = table.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(table)
        up = QAction(_TR("上移"))
        down = QAction(_TR("下移"))
        menu.addAction(up)
        menu.addAction(down)
        action = menu.exec(table.cursor().pos())

        if action == up:

            self.moverank(table, -1)

        elif action == down:
            self.moverank(table, 1)

    def moverank(self, table: QTableView, dy):
        curr = table.currentIndex()
        target = (curr.row() + dy) % table.model().rowCount()
        texts = [
            table.model().item(curr.row(), i).text()
            for i in range(table.model().columnCount())
        ]

        table.model().removeRow(curr.row())
        table.model().insertRow(target, [QStandardItem(text) for text in texts])
        table.setCurrentIndex(table.model().index(target, curr.column()))

    def apply(self):
        rows = self.model.rowCount()
        self.configdict.clear()
        for row in range(rows):
            if self.model.item(row, 1).text() == "":
                continue
            if self.model.item(row, 1).text() not in self.configdict:
                self.configdict[self.model.item(row, 1).text()] = [
                    self.model.item(row, 0).text(),
                    self.model.item(row, 2).text(),
                ]
            else:
                self.configdict[self.model.item(row, 1).text()] += [
                    self.model.item(row, 0).text(),
                    self.model.item(row, 2).text(),
                ]

    def __init__(
        self, parent, configdict, title, label=["游戏ID MD5", "原文", "翻译"], _=None
    ) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_TR(title))
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        model = QStandardItemModel(len(configdict), 1, self)
        row = 0
        for key in configdict:  # 2
            if type(configdict[key]) == str:
                configdict[key] = ["0", configdict[key]]

            for i in range(len(configdict[key]) // 2):
                item = QStandardItem(configdict[key][i * 2])
                model.setItem(row, 0, item)
                item = QStandardItem(key)
                model.setItem(row, 1, item)
                item = QStandardItem(configdict[key][1 + i * 2])
                model.setItem(row, 2, item)
                row += 1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(self)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            functools.partial(self.showmenu, table)
        )
        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])
        self.table = table

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

            skip = []
            for index in self.table.selectedIndexes():
                if index.row() in skip:
                    continue
                skip.append(index.row())
            skip = reversed(sorted(skip))

            for row in skip:
                model.removeRow(row)

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(functools.partial(self.moverank, table, -1))
        button.btn4clicked.connect(functools.partial(self.moverank, table, 1))

        button.btn5clicked.connect(self.apply)
        button2 = threebuttons(texts=["设置所有词条为全局词条", "以当前md5复制选中行"])

        def clicked5():
            rows = model.rowCount()
            for row in range(rows):
                model.item(row, 0).setText("0")

        button2.btn1clicked.connect(
            lambda: getQMessageBox(
                self,
                "警告",
                "!!!",
                True,
                True,
                lambda: clicked5(),
            )
        )

        button2.btn2clicked.connect(self.copysetmd5)

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
        formLayout.addWidget(button2)
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

    def copysetmd5(self):
        if len(self.table.selectedIndexes()) == 0:
            return
        md5 = gobject.baseobject.currentmd5
        row = self.table.selectedIndexes()[0].row()
        skip = []
        for index in self.table.selectedIndexes():
            if index.row() in skip:
                continue
            skip.append(index.row())
            self.model.insertRow(
                row,
                [
                    QStandardItem(md5),
                    QStandardItem(self.model.item(index.row(), 1).text()),
                    QStandardItem(self.model.item(index.row(), 2).text()),
                ],
            )


@Singleton_close
class noundictconfigdialog_private(QDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()

    def showmenu(self, table: QTableView, pos):
        r = table.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(table)
        up = QAction(_TR("上移"))
        down = QAction(_TR("下移"))
        menu.addAction(up)
        menu.addAction(down)
        action = menu.exec(table.cursor().pos())

        if action == up:

            self.moverank(table, -1)

        elif action == down:
            self.moverank(table, 1)

    def moverank(self, table: QTableView, dy):
        curr = table.currentIndex()
        target = (curr.row() + dy) % table.model().rowCount()
        texts = [
            table.model().item(curr.row(), i).text()
            for i in range(table.model().columnCount())
        ]

        table.model().removeRow(curr.row())
        table.model().insertRow(target, [QStandardItem(text) for text in texts])
        table.setCurrentIndex(table.model().index(target, curr.column()))

    def apply(self):
        rows = self.model.rowCount()
        self.configdict.clear()
        _dedump = set()
        for row in range(rows):
            k, v = self.model.item(row, 0).text(), self.model.item(row, 1).text()
            if k == "":
                continue
            if k in _dedump:
                continue
            self.configdict.append([k, v])
            _dedump.add(k)

    def __init__(
        self, parent, configdict, title, label=["原文", "翻译"], _=None
    ) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_TR(title))
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        model = QStandardItemModel(len(configdict), 1, self)
        row = 0
        for key in configdict:  # 2
            item = QStandardItem(key[0])
            model.setItem(row, 0, item)
            item = QStandardItem(key[1])
            model.setItem(row, 1, item)
            row += 1
        model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(self)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            functools.partial(self.showmenu, table)
        )
        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])
        self.table = table

        def clicked1():

            model.insertRow(0, [QStandardItem(), QStandardItem()])

        button.btn1clicked.connect(clicked1)

        def clicked2():

            skip = []
            for index in self.table.selectedIndexes():
                if index.row() in skip:
                    continue
                skip.append(index.row())
            skip = reversed(sorted(skip))

            for row in skip:
                model.removeRow(row)

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(functools.partial(self.moverank, table, -1))
        button.btn4clicked.connect(functools.partial(self.moverank, table, 1))

        button.btn5clicked.connect(self.apply)

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
        self.button = button
        self.model = model
        self.configdict = configdict
        self.resize(QSize(600, 400))
        self.show()

    def copysetmd5(self):
        if len(self.table.selectedIndexes()) == 0:
            return
        row = self.table.selectedIndexes()[0].row()
        skip = []
        for index in self.table.selectedIndexes():
            if index.row() in skip:
                continue
            skip.append(index.row())
            self.model.insertRow(
                row,
                [
                    QStandardItem(self.model.item(index.row(), 1).text()),
                    QStandardItem(self.model.item(index.row(), 2).text()),
                ],
            )


class Process:

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):
        return (
            noundictconfigdialog_private(
                parent_window,
                savehook_new_data[gameuid]["noundictconfig"],
                "专有名词翻译设置",
            ),
        )

    @staticmethod
    def get_setting_window(parent_window):
        return (
            noundictconfigdialog(
                parent_window,
                noundictconfig["dict"],
                "专有名词翻译设置_游戏ID 0表示全局",
            ),
        )

    @property
    def using_X(self):
        for _ in (0,):
            try:
                if not gobject.baseobject.textsource:
                    break
                gameuid = gobject.baseobject.textsource.gameuid
                if not gameuid:
                    break
                if savehook_new_data[gameuid]["transoptimi_followdefault"]:
                    break
                return savehook_new_data[gameuid]["noundict_use"]

            except:
                print_exc()
                break
        return checkpostusing("noundict")

    def usewhich(self) -> dict:
        for _ in (0,):
            try:
                if not gobject.baseobject.textsource:
                    break
                gameuid = gobject.baseobject.textsource.gameuid
                if not gameuid:
                    break
                if savehook_new_data[gameuid]["transoptimi_followdefault"]:
                    break
                return 0, savehook_new_data[gameuid]["noundictconfig"]

            except:
                print_exc()
                break
        return 1, noundictconfig["dict"]

    def process_before(self, content):
        def __createfake():

            ___idx = 1
            if ___idx == 1:
                xx = "ZX{}Z".format(chr(ord("B") + gobject.baseobject.zhanweifu))
            elif ___idx == 2:
                xx = "{{{}}}".format(gobject.baseobject.zhanweifu)
            elif ___idx == 3:
                xx = v
            gobject.baseobject.zhanweifu += 1
            return xx

        mp1 = {}
        _type, dic = self.usewhich()
        if _type == 1:
            for key in dic:
                v = None
                if type(dic[key]) == str:
                    v = dic[mp1[key]]
                else:
                    for i in range(len(dic[key]) // 2):
                        if dic[key][i * 2] in [
                            "0",
                            gobject.baseobject.currentmd5,
                        ]:
                            v = dic[key][i * 2 + 1]
                            break

                if v is not None and key in content:
                    xx = __createfake()
                    content = content.replace(key, xx)
                    mp1[xx] = v
            return content, mp1
        elif _type == 0:
            for k, v in dic:

                xx = __createfake()
                content = content.replace(k, xx)
                mp1[xx] = v
            return content, mp1

    def process_after(self, res, mp1):
        for key in mp1:
            reg = re.compile(re.escape(key), re.IGNORECASE)
            res = reg.sub(mp1[key], res)
        return res
