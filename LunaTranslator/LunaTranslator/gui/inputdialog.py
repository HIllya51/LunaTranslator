from qtsymbols import *
import functools, importlib
import qtawesome
from myutils.config import globalconfig, _TR, _TRL
from myutils.utils import makehtml
from myutils.wrapper import Singleton
from gui.usefulwidget import (
    MySwitch,
    selectcolor,
    getsimpleswitch,
    threebuttons,
    listediterline,
    getsimplepatheditor,
)


@Singleton
class noundictconfigdialog1(QDialog):
    def newline(self, row, item):
        self.model.insertRow(
            row,
            [QStandardItem(), QStandardItem(item["key"]), QStandardItem(item["value"])],
        )
        self.table.setIndexWidget(
            self.model.index(row, 0), getsimpleswitch(item, "regex")
        )

    def __init__(self, parent, configdict, configkey, title, label) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_TR(title))
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(_TRL(label))
        table = QTableView(self)
        table.setModel(self.model)

        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )

        self.table = table
        for row, item in enumerate(configdict[configkey]):
            self.newline(row, item)

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = QPushButton()
        button4.setText(_TR("搜索"))

        def clicked4():
            text = searchcontent.text()

            rows = self.model.rowCount()
            cols = self.model.columnCount()
            for row in range(rows):
                ishide = True
                for c in range(cols):
                    if text in self.model.item(row, c).text():
                        ishide = False
                        break
                table.setRowHidden(row, ishide)

        button4.clicked.connect(clicked4)
        search.addWidget(button4)

        button = threebuttons()

        def clicked1():
            self.configdict[configkey].insert(
                0, {"key": "", "value": "", "regex": False}
            )
            self.newline(0, self.configdict[configkey][0])

        button.btn1clicked.connect(clicked1)

        def clicked2():
            self.model.removeRow(table.currentIndex().row())
            self.configdict[configkey].pop(table.currentIndex().row())

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(self.apply)
        self.button = button
        self.configdict = configdict
        self.configkey = configkey
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)
        self.resize(QSize(600, 400))
        self.show()

    def apply(self):
        rows = self.model.rowCount()
        rowoffset = 0
        dedump = set()
        for row in range(rows):
            k, v = self.model.item(row, 1).text(), self.model.item(row, 2).text()
            if k == "" or k in dedump:
                self.configdict[self.configkey].pop(row - rowoffset)
                rowoffset += 1
                continue
            self.configdict[self.configkey][row - rowoffset].update(
                {"key": k, "value": v}
            )
            dedump.add(k)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()


@Singleton
class regexedit(QDialog):
    def __init__(self, parent, regexlist) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.regexlist = regexlist
        self.setWindowTitle(_TR("正则匹配"))

        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(_TRL(["正则"]))
        table = QTableView(self)
        table.setModel(self.model)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table = table
        for row, regex in enumerate(regexlist):
            self.model.insertRow(row, [QStandardItem(regex)])

        button = threebuttons()

        def clicked1():
            regexlist.insert(0, "")
            self.model.insertRow(0, [QStandardItem()])

        button.btn1clicked.connect(clicked1)

        def clicked2():
            self.model.removeRow(table.currentIndex().row())
            regexlist.pop(table.currentIndex().row())

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(self.apply)
        self.button = button
        formLayout.addWidget(table)
        formLayout.addWidget(button)
        self.resize(QSize(600, 400))
        self.show()

    def apply(self):
        rows = self.model.rowCount()
        rowoffset = 0
        dedump = set()
        for row in range(rows):
            regex = self.model.item(row, 0).text()
            if regex == "" or regex in dedump:
                self.regexlist.pop(row - rowoffset)
                rowoffset += 1
                continue
            self.regexlist[row - rowoffset] = regex
            dedump.add(regex)

    def closeEvent(self, _) -> None:
        self.button.setFocus()
        self.apply()


def autoinitdialog_items(dic):
    items = []
    for arg in dic["args"]:
        default = dict(name=arg, d=dic["args"], k=arg, type="lineedit")

        if "argstype" in dic and arg in dic["argstype"]:
            default.update(dic["argstype"][arg])
        items.append(default)
    items.append({"type": "okcancel"})
    return items


@Singleton
class autoinitdialog(QDialog):
    def __init__(self, parent, title, width, lines, _=None) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_TR(title))
        self.resize(QSize(width, 10))
        formLayout = QFormLayout()
        self.setLayout(formLayout)
        regist = []

        def save(callback=None):
            for l in regist:
                l[0][l[1]] = l[2]()
            self.close()
            if callback:
                callback()

        def __getv(l):
            return l

        for line in lines:
            if "d" in line:
                dd = line["d"]
            if "k" in line:
                key = line["k"]
            if line["type"] == "label":

                if "islink" in line and line["islink"]:
                    lineW = QLabel(makehtml(dd[key]))
                    lineW.setOpenExternalLinks(True)
                else:
                    lineW = QLabel(_TR(dd[key]))
            elif line["type"] == "textlist":
                __list = dd[key]
                e = listediterline(_TR(line["name"]), _TR(line["header"]), __list)

                regist.append([dd, key, functools.partial(__getv, __list)])
                lineW = QHBoxLayout()
                lineW.addWidget(e)
            elif line["type"] == "combo":
                lineW = QComboBox()
                if "list_function" in line:
                    try:
                        func = getattr(
                            importlib.import_module(line["list_function"][0]),
                            line["list_function"][1],
                        )
                        items = func()
                    except:
                        items = []
                else:
                    items = line["list"]
                lineW.addItems(_TRL(items))
                lineW.setCurrentIndex(dd.get(key, 0))
                lineW.currentIndexChanged.connect(
                    functools.partial(dd.__setitem__, key)
                )
            elif line["type"] == "okcancel":
                lineW = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                lineW.rejected.connect(self.close)
                lineW.accepted.connect(
                    functools.partial(
                        save, None if "callback" not in line else line["callback"]
                    )
                )

                lineW.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
                lineW.button(QDialogButtonBox.StandardButton.Cancel).setText(
                    _TR("取消")
                )
            elif line["type"] == "lineedit":
                lineW = QLineEdit(dd[key])
                regist.append([dd, key, lineW.text])
            elif line["type"] == "file":
                __temp = {"k": dd[key]}
                lineW = getsimplepatheditor(
                    dd[key],
                    line.get("multi", False),
                    line["dir"],
                    line.get("filter", None),
                    callback=functools.partial(__temp.__setitem__, "k"),
                )

                regist.append([dd, key, functools.partial(__temp.__getitem__, "k")])

            elif line["type"] == "switch":
                lineW = MySwitch(sign=dd[key])
                regist.append([dd, key, lineW.isChecked])
            elif line["type"] == "spin":
                lineW = QDoubleSpinBox()
                lineW.setMinimum(0 if "min" not in line else line["min"])
                lineW.setMaximum(100 if "max" not in line else line["max"])
                lineW.setSingleStep(0.1 if "step" not in line else line["step"])
                lineW.setValue(dd[key])
                lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))

            elif line["type"] == "intspin":
                lineW = QSpinBox()
                lineW.setMinimum(0 if "min" not in line else line["min"])
                lineW.setMaximum(100 if "max" not in line else line["max"])
                lineW.setSingleStep(1 if "step" not in line else line["step"])
                lineW.setValue(dd[key])
                lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))
            if "name" in line:
                formLayout.addRow(_TR(line["name"]), lineW)
            else:
                formLayout.addRow(lineW)
        self.show()


def getsomepath1(
    parent, title, d, k, label, callback=None, isdir=False, filter1="*.db"
):
    autoinitdialog(
        parent,
        title,
        800,
        [
            {
                "type": "file",
                "name": label,
                "d": d,
                "k": k,
                "dir": isdir,
                "filter": filter1,
            },
            {"type": "okcancel", "callback": callback},
        ],
    )


@Singleton
class multicolorset(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(_TR("颜色设置"))
        self.resize(QSize(300, 10))
        formLayout = QFormLayout(self)  # 配置layout
        _hori = QHBoxLayout()
        l = QLabel(_TR("透明度"))
        _hori.addWidget(l)
        _s = QSpinBox()
        _s.setValue(globalconfig["showcixing_touming"])
        _s.setMinimum(1)
        _s.setMaximum(100)
        _hori.addWidget(_s)
        formLayout.addRow(_hori)
        _s.valueChanged.connect(
            lambda x: globalconfig.__setitem__("showcixing_touming", x)
        )
        hori = QHBoxLayout()
        hori.addWidget(QLabel(_TR("词性")))
        hori.addWidget(QLabel(_TR("是否显示")))
        hori.addWidget(QLabel(_TR("颜色")))
        for k in globalconfig["cixingcolor"]:
            hori = QHBoxLayout()

            l = QLabel(_TR(k))

            hori.addWidget(l)

            b = MySwitch(sign=globalconfig["cixingcolorshow"][k])
            b.clicked.connect(
                functools.partial(globalconfig["cixingcolorshow"].__setitem__, k)
            )

            p = QPushButton(
                qtawesome.icon("fa.paint-brush", color=globalconfig["cixingcolor"][k]),
                "",
            )

            p.setIconSize(QSize(20, 20))

            p.setStyleSheet("background: transparent;")
            p.clicked.connect(
                functools.partial(selectcolor, self, globalconfig["cixingcolor"], k, p)
            )
            hori.addWidget(b)
            hori.addWidget(p)

            formLayout.addRow(hori)
        self.show()


@Singleton
class postconfigdialog_(QDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.closeevent:
            self.button.setFocus()
            self.apply()

    def apply(self):
        rows = self.model.rowCount()
        newdict = {}
        for row in range(rows):
            if self.model.item(row, 0).text() == "":
                continue
            newdict[(self.model.item(row, 0).text())] = self.model.item(row, 1).text()
        self.configdict[self.key] = newdict

    def __init__(self, parent, configdict, title) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        print(title)
        self.setWindowTitle(_TR(title))
        # self.setWindowModality(Qt.ApplicationModal)
        self.closeevent = False
        formLayout = QVBoxLayout(self)  # 配置layout

        key = list(configdict.keys())[0]
        lb = QLabel(self)
        lb.setText(_TR(key))
        formLayout.addWidget(lb)

        model = QStandardItemModel(len(configdict[key]), 1, self)
        row = 0

        for key1 in configdict[key]:  # 2

            item = QStandardItem(key1)
            model.setItem(row, 0, item)

            item = QStandardItem(configdict[key][key1])
            model.setItem(row, 1, item)
            row += 1
        model.setHorizontalHeaderLabels(_TRL(["原文内容", "替换为"]))
        table = QTableView(self)
        table.setModel(model)
        table.setWordWrap(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # table.clicked.connect(self.show_info)
        button = threebuttons()

        def clicked1():
            model.insertRow(0, [QStandardItem(), QStandardItem()])

        button.btn1clicked.connect(clicked1)

        def clicked2():

            model.removeRow(table.currentIndex().row())

        button.btn2clicked.connect(clicked2)
        button.btn3clicked.connect(self.apply)
        self.button = button
        self.model = model
        self.key = key
        self.configdict = configdict
        self.closeevent = True
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
        self.resize(QSize(600, 400))
        self.show()


def postconfigdialog(parent, configdict, title):
    postconfigdialog_(parent, configdict, title)
