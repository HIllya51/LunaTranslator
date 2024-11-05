from qtsymbols import *
import functools, importlib
from traceback import print_exc
import qtawesome, os, gobject, json
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
    SuperCombo,
    getsimplecombobox,
    getspinbox,
    SplitLine,
    getIconButton,
)
from gui.dynalang import (
    LFormLayout,
    LLabel,
    LPushButton,
    LStandardItemModel,
    LDialog,
    LDialog,
)


@Singleton_close
class noundictconfigdialog1(LDialog):
    def newline(self, row, item: dict):
        self.model.insertRow(
            row,
            [
                QStandardItem(),
                QStandardItem(),
                QStandardItem(item["key"]),
                QStandardItem(item["value"]),
            ],
        )
        self.table.setindexdata(self.model.index(row, 0), item.get("regex", False))
        self.table.setindexdata(
            self.model.index(row, 1), item.get("escape", item.get("regex", False))
        )

    def __init__(self, parent, reflist, title, label) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)
        self.reflist = reflist
        formLayout = QVBoxLayout(self)  # 配置layout

        self.model = LStandardItemModel()
        self.model.setHorizontalHeaderLabels(label)
        table = TableViewW(self, copypaste=True, updown=True)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )

        self.table = table

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
        table.getindexdata = self.__getindexwidgetdata
        table.setindexdata = self.__setindexwidget
        self.table = table
        for row, item in enumerate(reflist):
            self.newline(row, item)
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
            data = {"regex": self.table.compatiblebool(data)}
            self.table.setIndexWidget(index, getsimpleswitch(data, "regex"))
        elif index.column() == 1:
            data = {"escape": self.table.compatiblebool(data)}
            self.table.setIndexWidget(index, getsimpleswitch(data, "escape"))
        else:
            self.table.model().setItem(index.row(), index.column(), QStandardItem(data))

    def __getindexwidgetdata(self, index: QModelIndex):
        if index.column() == 0:
            return self.table.indexWidgetX(index).isChecked()
        if index.column() == 1:
            return self.table.indexWidgetX(index).isChecked()
        return self.model.itemFromIndex(index).text()

    def apply(self):
        def __check(row):
            k = self.table.getdata(row, 2)
            if k == "":
                return ""
            switch = self.table.getdata(row, 0)
            es = self.table.getdata(row, 1)
            return (switch, es, k)

        self.table.dedumpmodel(__check)
        self.reflist.clear()
        for row in range(self.model.rowCount()):
            k = self.table.getdata(row, 2)
            v = self.table.getdata(row, 3)
            switch = self.table.getdata(row, 0)
            es = self.table.getdata(row, 1)
            self.reflist.append(
                {
                    "key": k,
                    "value": v,
                    "escape": es,
                    "regex": switch,
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
            & ~Qt.WindowType.WindowContextHelpButtonHint
            & ~Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
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
        self.table.setindexdata(self.model.index(row, 0), item['regex'])
         
        self.table.setindexdata(self.model.index(row, 1), item['condition'])
        self.table.setindexdata(self.model.index(row, 3), item['target'])

    def createacombox(self, config):
        com = SuperCombo()
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

    def __comchange(self, com: SuperCombo, config, idx):
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
        table = TableViewW(self, updown=True, copypaste=True)
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
        table.getindexdata = self.__getindexwidgetdata
        table.setindexdata = self.__setindexwidget
        table.insertplainrow = lambda row: self.newline(
            row, {"key": "", "condition": 0, "regex": False, "target": "skip"}
        )
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

        button.btn1clicked.connect(functools.partial(self.table.insertplainrow, 0))
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

    def __setindexwidget(self, index: QModelIndex, data):
        if index.column() == 0:
            data = {"regex": self.table.compatiblebool(data)}
            self.table.setIndexWidget(index, getsimpleswitch(data, "regex"))
        elif index.column() == 1:
            try:
                data = int(data)
            except:
                data = 0
            data = {"condition": data}
            self.table.setIndexWidget(
                index, getsimplecombobox(["首尾", "包含"], data, "condition")
            )
        elif index.column() == 3:
            if data in ["default", "skip"]:
                pass
            else:
                try:
                    data = self.table.compatiblejson(data)
                except:
                    data = "default"
            self.table.setIndexWidget(index, self.createacombox({"target": data}))
        else:
            self.table.model().setItem(index.row(), index.column(), QStandardItem(data))

    def __getindexwidgetdata(self, index: QModelIndex):
        if index.column() == 0:
            return self.table.indexWidgetX(index).isChecked()
        if index.column() == 1:
            return self.table.indexWidgetX(index).currentIndex()
        if index.column() == 3:
            return self.table.indexWidgetX(index).target
        return self.model.itemFromIndex(index).text()

    def apply(self):
        self.table.dedumpmodel(2)
        rows = self.model.rowCount()
        self.reflist.clear()
        for row in range(rows):
            k = self.table.getdata(row, 2)
            switch = self.table.getdata(row, 0)
            con = self.table.getdata(row, 1)
            con2 = self.table.getdata(row, 3)
            self.reflist.append(
                {
                    "key": k,
                    "condition": con,
                    "regex": switch,
                    "target": con2,
                }
            )

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()


def autoinitdialog_items(dic):
    items = []
    for arg in dic["args"]:
        default = dict(name=arg, k=arg, type="lineedit")

        if "argstype" in dic and arg in dic["argstype"]:
            default.update(dic["argstype"][arg])
        items.append(default)
    items.append({"type": "okcancel"})
    return items


@Singleton_close
class autoinitdialog__(LDialog):
    def __init__(
        self, parent, dd, title, width, lines, modelfile=None, maybehasextrainfo=None
    ) -> None:
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
        regist = {}

        def save(callback=None):
            for k in regist:
                dd[k] = regist[k]()
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

            list_cache = line.get("list_cache", None)
            if list_cache:
                refname2line[list_cache] = None
        oklines = []

        for line in lines:
            k = line.get("k", None)
            if k in refname2line:
                refname2line[k] = line
                continue
            oklines.append(line)
        lines = oklines
        cachecombo = {}
        cachehasref = {}
        for line in lines:
            if "k" in line:
                key = line["k"]
            if line["type"] == "label":

                if "islink" in line and line["islink"]:
                    lineW = QLabel(makehtml(dd[key]))
                    lineW.setOpenExternalLinks(True)
                else:
                    lineW = LLabel(dd[key])
            elif line["type"] == "textlist":
                __list = dd[key].copy()
                lineW = listediterline(line["name"], line["header"], __list)
                regist[key] = functools.partial(__getv, __list)
            elif line["type"] == "combo":
                lineW = SuperCombo()
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
                regist[key] = lineW.currentIndex
                cachecombo[key] = lineW
            elif line["type"] == "lineedit_or_combo":
                line1 = QLineEdit()
                lineW = QHBoxLayout()
                combo = SuperCombo()
                combo.setLineEdit(line1)

                def __refresh(regist, line, combo: SuperCombo):
                    try:
                        func = getattr(
                            importlib.import_module(modelfile), line["list_function"]
                        )
                        items = func(maybehasextrainfo, regist)
                        curr = combo.currentText()
                        combo.clear()
                        combo.addItems(items)
                        if curr in items:
                            combo.setCurrentIndex(items.index(curr))

                        dd[refname2line[line["list_cache"]]["k"]] = items
                    except Exception as e:
                        print_exc()
                        QMessageBox.information(self, str(type(e))[8:-2], str(e))

                if "list_function" in line:
                    items = dd[refname2line[line["list_cache"]]["k"]]
                else:
                    items = line["list"]
                combo.addItems(items)
                if dd[key] in items:
                    combo.setCurrentIndex(items.index(dd[key]))
                else:
                    combo.setCurrentText(dd[key])
                regist[key] = combo.currentText
                if "list_function" in line:
                    lineW.addWidget(
                        getIconButton(
                            callback=functools.partial(__refresh, regist, line, combo),
                            icon="fa.refresh",
                        )
                    )
                lineW.addWidget(combo)
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
                regist[key] = lineW.text
            elif line["type"] == "multiline":
                lineW = QPlainTextEdit(dd[key])
                regist[key] = lineW.toPlainText
            elif line["type"] == "file":
                __temp = {"k": dd[key]}
                lineW = getsimplepatheditor(
                    dd[key],
                    line.get("multi", False),
                    line.get("dir", False),
                    line.get("filter", None),
                    callback=functools.partial(__temp.__setitem__, "k"),
                    reflist=__temp["k"],
                    name=line.get("name", ""),
                    header=line.get("name", ""),
                    dirorfile=line.get("dirorfile", False),
                )

                regist[key] = functools.partial(__temp.__getitem__, "k")

            elif line["type"] == "switch":
                lineW = MySwitch(sign=dd[key])
                regist[key] = lineW.isChecked
                _ = QHBoxLayout()
                _.addStretch()
                _.addWidget(lineW)
                _.addStretch()
                lineW = _
            elif line["type"] in ["spin", "intspin"]:

                __temp = {"k": dd[key]}
                lineW = getspinbox(
                    line.get("min", 0),
                    line.get("max", 100),
                    __temp,
                    "k",
                    line["type"] == "spin",
                    line.get("step", 0.1),
                )
                regist[key] = lineW.value
            elif line["type"] == "split":
                lineW = SplitLine()
                formLayout.addRow(lineW)
                continue
            refcombo = line.get("refcombo")
            if refcombo:
                if refcombo not in cachehasref:
                    cachehasref[refcombo] = []
                cachehasref[refcombo].append((lineW, line))

            refswitch = line.get("refswitch", None)
            if refswitch:
                hbox = QHBoxLayout()
                line_ref = refname2line.get(refswitch, None)
                if line_ref:
                    if "k" in line_ref:
                        key = line_ref["k"]
                    switch = MySwitch(sign=dd[key])
                    regist[key] = switch.isChecked
                    switch.clicked.connect(lineW.setEnabled)
                    lineW.setEnabled(dd[key])
                    hbox.addWidget(switch)
                    hbox.addWidget(lineW)
                    lineW = hbox
            if "name" in line:
                formLayout.addRow(line["name"], lineW)
            else:
                formLayout.addRow(lineW)

        for comboname, refitems in cachehasref.items():

            def refcombofunction(refitems, _i):
                for w, linwinfo in refitems:
                    vis = True
                    if linwinfo.get("refcombo_i") is not None:
                        vis = linwinfo.get("refcombo_i") == _i
                    elif linwinfo.get("refcombo_i_r") is not None:
                        vis = linwinfo.get("refcombo_i_r") != _i
                    elif linwinfo.get("refcombo_l") is not None:
                        vis = _i in linwinfo.get("refcombo_l")
                    w.setVisible(vis)
                    formLayout.itemAt(formLayout.indexOf(w) - 1).widget().setVisible(
                        vis
                    )

            cachecombo[comboname].currentIndexChanged.connect(
                functools.partial(refcombofunction, refitems)
            )
            cachecombo[comboname].currentIndexChanged.emit(
                cachecombo[comboname].currentIndex()
            )
        self.show()


def autoinitdialogx(
    parent, dd, title, width, lines, modelfile, maybehasextrainfo, _=None
):
    autoinitdialog__(parent, dd, title, width, lines, modelfile, maybehasextrainfo)


def autoinitdialog(parent, dd, title, width, lines, _=None):
    autoinitdialog__(parent, dd, title, width, lines)


def getsomepath1(
    parent, title, d, k, label, callback=None, isdir=False, filter1="*.db"
):
    autoinitdialog(
        parent,
        d,
        title,
        800,
        [
            {
                "type": "file",
                "name": label,
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
                text = self.table.getdata(row, 0)
                self.configdict[text] = self.table.getdata(row, 1)
        elif isinstance(self.configdict, list):
            for row in range(rows):
                text = self.table.getdata(row, 0)
                item = {}
                for _i, key in enumerate(self.dictkeys):
                    item[key] = self.table.getdata(row, _i)
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
        table = TableViewW(self, copypaste=True, updown=True)
        table.setModel(model)
        table.setWordWrap(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
