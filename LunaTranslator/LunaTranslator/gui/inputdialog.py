from qtsymbols import *
import functools, importlib
from traceback import print_exc
import qtawesome, os, gobject
from myutils.config import globalconfig, _TR
from myutils.utils import makehtml
from myutils.wrapper import Singleton_close
from gui.usefulwidget import (
    MySwitch,
    selectcolor,
    getsimpleswitch,
    threebuttons,
    listediterline,
    TableViewW,
    getsimplepatheditor,
    FocusSpin,
    FocusDoubleSpin,
    LFocusCombo,
    getsimplecombobox,
    getspinbox,
    SplitLine,
)
from gui.dynalang import (
    LFormLayout,
    LLabel,
    LPushButton,
    LStandardItemModel,
    LDialog,
    LDialog,
    LAction,
)


@Singleton_close
class noundictconfigdialog1(LDialog):
    def newline(self, row, item):
        self.model.insertRow(
            row,
            [
                QStandardItem(),
                QStandardItem(),
                QStandardItem(item["key"]),
                QStandardItem(item["value"]),
            ],
        )
        if "regex" not in item:
            item["regex"] = False
        if "escape" not in item:
            item["escape"] = item["regex"]
        self.table.setIndexWidget(
            self.model.index(row, 0), getsimpleswitch(item, "regex")
        )
        self.table.setIndexWidget(
            self.model.index(row, 1), getsimpleswitch(item, "escape")
        )

    def __init__(self, parent, reflist, title, label) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)
        self.reflist = reflist
        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(label)
        table = TableViewW(self)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.setsimplemenu()

        self.table = table
        for row, item in enumerate(reflist):
            self.newline(row, item)

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

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
        table.getindexwidgetdata = self.__getindexwidgetdata
        table.setindexwidget = self.__setindexwidget
        self.table = table
        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])
        table.insertplainrow = lambda row: self.newline(
            row, {"key": "", "value": "", "regex": False}
        )

        button.btn1clicked.connect(functools.partial(table.insertplainrow, 0))

        button.btn2clicked.connect(self.table.removeselectedrows)
        button.btn5clicked.connect(self.apply)
        button.btn3clicked.connect(functools.partial(table.moverank, -1))
        button.btn4clicked.connect(functools.partial(table.moverank, 1))
        self.button = button
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)

        self.resize(QSize(600, 400))
        self.show()

    def __setindexwidget(self, index: QModelIndex, data):
        if index.column() == 0:
            self.table.setIndexWidget(index, getsimpleswitch(data, "regex"))
        if index.column() == 1:
            self.table.setIndexWidget(index, getsimpleswitch(data, "escape"))

    def __getindexwidgetdata(self, index: QModelIndex):
        if index.column() == 0:
            return {"regex": self.table.indexWidgetX(index).isChecked()}
        if index.column() == 1:
            return {"escape": self.table.indexWidgetX(index).isChecked()}

    def apply(self):
        def __check(row):
            k = self.model.item(row, 2).text()
            if k == "":
                return ""
            switch = self.table.indexWidgetX(row, 0).isChecked()
            es = self.table.indexWidgetX(row, 1).isChecked()
            return (switch, es, k)

        self.table.dedumpmodel(__check)
        self.reflist.clear()
        for row in range(self.model.rowCount()):
            k = self.model.item(row, 2).text()
            v = self.model.item(row, 3).text()
            switch = self.table.indexWidgetX(row, 0)
            es = self.table.indexWidgetX(row, 1)
            self.reflist.append(
                {
                    "key": k,
                    "value": v,
                    "escape": es.isChecked(),
                    "regex": switch.isChecked(),
                }
            )

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()


class voiceselect(LDialog):
    voicelistsignal = pyqtSignal(object)

    def __init__(self, *argc, **kwarg):
        super().__init__(*argc, **kwarg)
        self.setWindowTitle("选择声音")
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowContextHelpButtonHint
            & ~Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowStaysOnTopHint
        )
        _layout = LFormLayout(self)

        button = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button.accepted.connect(self.accept)
        button.rejected.connect(self.reject)

        self.engine_vis = []
        self.engine_internal = []
        for name in globalconfig["reader"]:

            _f = "./LunaTranslator/tts/{}.py".format(name)
            if os.path.exists(_f) == False:
                continue
            self.engine_vis.append(globalconfig["reader"][name]["name"])
            self.engine_internal.append(name)
        self.datas = {
            "engine": self.engine_internal[0],
            "voice": None,
            "vis": "",
            "visx": "",
        }
        combo = getsimplecombobox(
            self.engine_vis,
            self.datas,
            "engine",
            internal=self.engine_internal,
            callback=self.__engine_cb,
        )
        _layout.addRow("引擎", combo)
        self._layout = _layout
        combo.currentIndexChanged.emit(combo.currentIndex())
        _layout.addRow(button)
        self.voicelistsignal.connect(self.loadedvoice)
        self.object = None
        self.lastwidget = None

    def loadedvoice(self, obj):
        vl = obj.voiceshowlist
        if self._layout.rowCount() == 3:
            self._layout.removeRow(1)
        self.datas["voice"] = obj.voice
        voices = getsimplecombobox(
            vl,
            self.datas,
            "voice",
            internal=obj.voicelist,
            callback=functools.partial(self._selectvoice, obj),
        )
        self._layout.insertRow(1, "语音", voices)
        voices.currentIndexChanged.emit(voices.currentIndex())

    def _selectvoice(self, obj, internal):
        vis = obj.voiceshowlist[obj.voicelist.index(internal)]
        self.datas["vis"] = self.datas["visx"] + " " + vis

    def __engine_cb(self, internal):
        self.datas["visx"] = self.engine_vis[self.engine_internal.index(internal)]
        self.datas["vis"] = self.datas["visx"]
        self.datas["voice"] = None
        try:
            self.object = gobject.baseobject.loadreader(internal, init=False)
            self.voicelistsignal.emit(self.object)
        except:

            if self._layout.rowCount() == 3:
                self._layout.removeRow(1)


@Singleton_close
class yuyinzhidingsetting(LDialog):
    def newline(self, row, item):

        self.model.insertRow(
            row,
            [
                QStandardItem(),
                QStandardItem(),
                QStandardItem(item["key"]),
                QStandardItem(),
            ],
        )
        self.table.setIndexWidget(
            self.model.index(row, 0), getsimpleswitch(item, "regex")
        )
        com = getsimplecombobox(["首尾", "包含"], item, "condition")
        self.table.setIndexWidget(self.model.index(row, 1), com)
        self.table.setIndexWidget(self.model.index(row, 3), self.createacombox(item))

    def createacombox(self, config):
        com = LFocusCombo()
        com.addItems(["跳过", "默认", "选择声音"])
        target = config.get("target", "skip")
        com.target = target
        if target == "skip":
            com.setCurrentIndex(0)
        elif target == "default":
            com.setCurrentIndex(1)
        else:
            ttsklass, ttsvoice, voicename = target
            com.addItem(voicename)
            com.setCurrentIndex(3)
        com.currentIndexChanged.connect(
            functools.partial(self.__comchange, com, config)
        )
        return com

    def __comchange(self, com: LFocusCombo, config, idx):
        if idx == 0:
            com.target = "skip"
            if com.count() > 3:
                com.removeItem(com.count() - 1)
        elif idx == 1:
            com.target = "default"
            if com.count() > 3:
                com.removeItem(com.count() - 1)
        elif idx == 2:
            voice = voiceselect(self)
            if voice.exec():
                if voice.datas["voice"] is None:
                    com.setCurrentIndex(1)
                    return
                com.target = (
                    voice.datas["engine"],
                    voice.datas["voice"],
                    voice.datas["vis"],
                )
                com.blockSignals(True)
                com.clear()
                com.addItems(["跳过", "默认", "选择声音", voice.datas["vis"]])
                com.setCurrentIndex(3)
                com.blockSignals(False)
            else:
                com.setCurrentIndex(1)

    def __init__(self, parent, reflist) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("语音指定")

        # self.setWindowModality(Qt.ApplicationModal)
        self.reflist = reflist
        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(["正则", "条件", "目标", "指定为"])
        table = TableViewW(self)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.setsimplemenu({"copypaste": False})

        self.table = table
        for row, item in enumerate(reflist):
            self.newline(row, item)

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

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

        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])

        def clicked1():
            self.newline(
                0, {"key": "", "condition": 0, "regex": False, "target": "skip"}
            )

        button.btn1clicked.connect(clicked1)

        button.btn2clicked.connect(table.removeselectedrows)
        button.btn5clicked.connect(self.apply)
        button.btn3clicked.connect(functools.partial(table.moverank, -1))
        button.btn4clicked.connect(functools.partial(table.moverank, 1))
        self.button = button
        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)

        self.resize(QSize(600, 400))
        self.show()

    def apply(self):
        self.table.dedumpmodel(2)
        rows = self.model.rowCount()
        self.reflist.clear()
        for row in range(rows):
            k = self.model.item(row, 2).text()
            switch = self.table.indexWidgetX(row, 0)
            con = self.table.indexWidgetX(row, 1)
            con2 = self.table.indexWidgetX(row, 3)
            self.reflist.append(
                {
                    "key": k,
                    "condition": con.currentIndex(),
                    "regex": switch.isChecked(),
                    "target": con2.target,
                }
            )

    def closeEvent(self, a0: QCloseEvent) -> None:
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


@Singleton_close
class autoinitdialog(LDialog):
    def __init__(self, parent, title, width, lines, _=None) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.resize(QSize(width, 10))
        for line in lines:
            if line["type"] != "program":
                continue
            try:
                func = getattr(
                    importlib.import_module(line["route"][0]),
                    line["route"][1],
                )
                func(self)
            except:
                print_exc()
            self.show()
            return
        formLayout = LFormLayout()
        self.setLayout(formLayout)
        regist = []

        def save(callback=None):
            for l in regist:
                l[0][l[1]] = l[2]()
            self.close()
            if callback:
                try:
                    callback()
                except:
                    print_exc()

        def __getv(l):
            return l

        hasrank = []
        hasnorank = []
        for line in lines:
            rank = line.get("rank", None)
            if rank is None:
                hasnorank.append(line)
                continue
            hasrank.append(line)
        hasrank.sort(key=lambda line: line.get("rank", None))
        lines = hasrank + hasnorank

        refname2line = {}
        for line in lines:
            refswitch = line.get("refswitch", None)
            if refswitch:
                refname2line[refswitch] = None
        oklines = []

        for line in lines:
            k = line.get("k", None)
            if k in refname2line:
                refname2line[k] = line
                continue
            oklines.append(line)
        lines = oklines
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
                    lineW = LLabel(dd[key])
            elif line["type"] == "textlist":
                __list = dd[key]
                e = listediterline(line["name"], line["header"], __list)

                regist.append([dd, key, functools.partial(__getv, __list)])
                lineW = QHBoxLayout()
                lineW.addWidget(e)
            elif line["type"] == "combo":
                lineW = LFocusCombo()
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
                lineW.addItems(items)
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
                    functools.partial(save, line.get("callback", None))
                )

                lineW.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
                lineW.button(QDialogButtonBox.StandardButton.Cancel).setText(
                    _TR("取消")
                )
            elif line["type"] == "lineedit":
                lineW = QLineEdit(dd[key])
                regist.append([dd, key, lineW.text])
            elif line["type"] == "multiline":
                lineW = QPlainTextEdit(dd[key])
                regist.append([dd, key, lineW.toPlainText])
            elif line["type"] == "file":
                __temp = {"k": dd[key]}
                lineW = getsimplepatheditor(
                    dd[key],
                    line.get("multi", False),
                    line["dir"],
                    line.get("filter", None),
                    callback=functools.partial(__temp.__setitem__, "k"),
                    reflist=__temp["k"],
                    name=line.get("name", ""),
                    header=line.get("name", ""),
                )

                regist.append([dd, key, functools.partial(__temp.__getitem__, "k")])

            elif line["type"] == "switch":
                lineW = MySwitch(sign=dd[key])
                regist.append([dd, key, lineW.isChecked])
                _ = QHBoxLayout()
                _.addStretch()
                _.addWidget(lineW)
                _.addStretch()
                lineW = _
            elif line["type"] in ["spin", "intspin"]:
                lineW = getspinbox(
                    line.get("min", 0),
                    line.get("max", 100),
                    dd,
                    key,
                    line["type"] == "spin",
                    line.get("step", 0.1),
                )
            elif line["type"] == "split":
                lineW = SplitLine()
                formLayout.addRow(lineW)
                continue
            refswitch = line.get("refswitch", None)
            if refswitch:
                hbox = QHBoxLayout()
                line_ref = refname2line.get(refswitch, None)
                if line_ref:
                    if "d" in line_ref:
                        dd = line_ref["d"]
                    if "k" in line_ref:
                        key = line_ref["k"]
                    switch = MySwitch(sign=dd[key])
                    regist.append([dd, key, switch.isChecked])
                    switch.clicked.connect(lineW.setEnabled)
                    lineW.setEnabled(dd[key])
                    hbox.addWidget(switch)
                    hbox.addWidget(lineW)
                    lineW = hbox
            if "name" in line:
                formLayout.addRow(line["name"], lineW)
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


@Singleton_close
class multicolorset(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("颜色设置")
        self.resize(QSize(300, 10))
        formLayout = LFormLayout(self)  # 配置layout
        _hori = QHBoxLayout()
        l = LLabel("不透明度")
        _hori.addWidget(l)
        _s = FocusSpin()
        _s.setValue(globalconfig["showcixing_touming"])
        _s.setMinimum(1)
        _s.setMaximum(100)
        _hori.addWidget(_s)
        formLayout.addRow(_hori)
        _s.valueChanged.connect(
            lambda x: globalconfig.__setitem__("showcixing_touming", x)
        )
        hori = QHBoxLayout()
        hori.addWidget(LLabel("词性"))
        hori.addWidget(LLabel("是否显示"))
        hori.addWidget(LLabel("颜色"))
        for k in globalconfig["cixingcolor"]:
            hori = QHBoxLayout()

            l = LLabel(k)

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


@Singleton_close
class postconfigdialog_(LDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()

    def apply(self):
        self.table.dedumpmodel(0)
        rows = self.model.rowCount()
        self.configdict.clear()

        if isinstance(self.configdict, dict):
            for row in range(rows):
                text = self.model.item(row, 0).text()
                self.configdict[text] = self.model.item(row, 1).text()
        elif isinstance(self.configdict, list):
            for row in range(rows):
                text = self.model.item(row, 0).text()
                item = {}
                for _i, key in enumerate(self.dictkeys):
                    item[key] = self.model.item(row, _i).text()
                self.configdict.append(item)
        else:
            raise

    def __init__(self, parent, configdict, title, headers, dictkeys=None) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(title)
        formLayout = QVBoxLayout(self)  # 配置layout
        self.dictkeys = dictkeys
        model = LStandardItemModel(len(configdict), 1, self)
        row = 0
        if isinstance(configdict, dict):
            for key1 in configdict:  # 2

                item = QStandardItem(key1)
                model.setItem(row, 0, item)

                item = QStandardItem(configdict[key1])
                model.setItem(row, 1, item)
                row += 1
        elif isinstance(configdict, list):
            for line in configdict:  # 2
                for _i, k in enumerate(dictkeys):
                    item = QStandardItem(line.get(k, ""))
                    model.setItem(row, _i, item)
                row += 1
        else:
            raise
        model.setHorizontalHeaderLabels(headers)
        table = TableViewW(self)
        table.setModel(model)
        table.setWordWrap(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setsimplemenu()
        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])
        self.table = table
        button.btn1clicked.connect(table.insertplainrow)
        button.btn2clicked.connect(table.removeselectedrows)

        button.btn3clicked.connect(functools.partial(table.moverank, -1))
        button.btn4clicked.connect(functools.partial(table.moverank, 1))
        button.btn5clicked.connect(self.apply)
        self.button = button
        self.model = model
        self.configdict = configdict
        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

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


def postconfigdialog(parent, configdict, title, header):
    postconfigdialog_(parent, configdict, title, header)


def postconfigdialog2x(parent, reflist, title, header):
    noundictconfigdialog1(parent, reflist, title, header)
