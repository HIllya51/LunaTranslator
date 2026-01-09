from qtsymbols import *
import functools, binascii
from collections import OrderedDict
from traceback import print_exc
import qtawesome, NativeUtils, gobject, os
from myutils.config import (
    savehook_new_data,
    globalconfig,
    _TR,
    static_data,
    dynamiclink,
)
from myutils.utils import get_time_stamp, is_ascii_control
from gui.gamemanager.dialog import dialog_setting_game
from textio.textsource.texthook import texthook
from gui.usefulwidget import (
    closeashidewindow,
    getsimplecombobox,
    MySwitch,
    D_getdoclink,
    getsimpleswitch,
    getsimplepatheditor,
    FocusSpin,
    FocusCombo,
    TableViewW,
)
from gui.RichMessageBox import RichMessageBox
from gui.dynalang import (
    LFormLayout,
    LRadioButton,
    LLabel,
    LPushButton,
    LStandardItemModel,
    LDialog,
    LAction,
    LTabWidget,
    LCheckBox,
)


class HOSTINFO:
    Console = 0
    EmuWarning = 1
    EmuGameName = 2
    EmuConnected = 3


def getformlayoutw(w=None, cls=LFormLayout, hide=False):
    if w is None:
        _w = QWidget()
    else:
        _w = w
    _l = cls(_w)
    if hide:
        _w.hide()
    _l.setContentsMargins(0, 0, 0, 0)
    return _w, _l


class QButtonGroup_switch_widegt(QWidget):
    selectidx = pyqtSignal(int)

    def __init__(self, p: QWidget) -> None:
        super().__init__()
        self._parent = p
        self.mainlayout: QVBoxLayout = getformlayoutw(self, QVBoxLayout)[1]
        self.selectlayout = QHBoxLayout()
        self.selectlayout.setContentsMargins(0, 0, 0, 0)
        self.mainlayout.addLayout(self.selectlayout)
        self.selectGroup = QButtonGroup()
        self.wlist: "list[QWidget]" = []
        self.selectGroup.buttonClicked.connect(self.selectmodelf)

    def idx(self):
        return self.selectGroup.checkedId()

    def selectmodelf(self, idx):
        idx = self.idx()
        self.selectidx.emit(idx)
        for _ in range(len(self.wlist)):
            if _ != idx:
                self.wlist[_].hide()
                self._parent.resize(self._parent.width(), 1)
        self.wlist[idx].show()
        self._parent.resize(self._parent.width(), 1)

    def addW(self, text, widget: QWidget):
        if isinstance(widget, QLayout):
            w = QWidget()
            w.setLayout(widget)
            widget = w
        self.mainlayout.addWidget(widget)
        btn = LRadioButton(text)
        self.selectGroup.addButton(btn, len(self.wlist))
        self.selectlayout.addWidget(btn)
        if len(self.wlist) == 0:
            btn.setChecked(True)
        else:
            widget.hide()
        self.wlist.append(widget)


class HexValidator(QValidator):
    def validate(self, input_str, pos):
        # 检查输入是否是有效的16进制数
        if all(c in "0123456789abcdefABCDEF" for c in input_str):
            return QValidator.State.Acceptable, input_str, pos
        elif input_str == "" or (
            len(input_str) == 1 and input_str in "0123456789abcdefABCDEF"
        ):
            return QValidator.State.Intermediate, input_str, pos
        else:
            return QValidator.State.Invalid, input_str, pos


class PatternValidator(QValidator):
    def validate(self, input_str, pos):
        # 检查输入是否是有效的16进制数
        if all(c in "0123456789abcdefABCDEF ?" for c in input_str):
            return QValidator.State.Acceptable, input_str, pos
        elif input_str == "" or (
            len(input_str) == 1 and input_str in "0123456789abcdefABCDEF ?"
        ):
            return QValidator.State.Intermediate, input_str, pos
        else:
            return QValidator.State.Invalid, input_str, pos


class searchhookparam(LDialog):
    @property
    def textsource(self) -> texthook:
        return gobject.base.textsource

    def safehex(self, string: str, default):
        try:
            return int(string.replace(" ", "").replace("0x", ""), 16)
        except:
            return default

    def searchstart(self):
        dumpvalues = {}
        idx = self.searchmethod.idx()
        usestruct = self.textsource.defaultsp()
        usestruct.codepage = self.codepagesave["spcp"]
        if idx == 0:
            usestruct.length = 0
            # sp = spUser.length == 0 ? spDefault : spUser;
        elif idx == 1:  # 0默认
            # usestruct.codepage=self.codepage.value()
            usestruct.text = self.searchtext.text()[:30]
            if len(usestruct.text) < 3:
                QMessageBox.information(self, _TR("警告"), _TR("搜索文本过短！"))
                return
        elif idx == 2:
            for k, widget in self.regists.items():
                if isinstance(widget, QLineEdit):
                    dumpvalues[k] = widget.text()
                elif isinstance(widget, QSpinBox):
                    dumpvalues[k] = widget.value()
                elif callable(widget):
                    dumpvalues[k] = widget()
            pattern = dumpvalues["pattern"]
            if "." in pattern:
                usestruct.length = 1
                usestruct.exportModule = pattern[:120]
            else:
                try:
                    p = pattern.replace(" ", "").replace("??", "11")
                    if ("?" in p) or (len(p) % 2 != 0):
                        QMessageBox.information(self, _TR("警告"), _TR("无效"))
                        raise Exception()
                    bs = bytes.fromhex(p)
                    usestruct.pattern = bs[:30]
                    usestruct.length = len(bs)
                except:
                    pass
            usestruct.address_method = self.search_addr_range.idx()
            usestruct.search_method = self.search_method.idx()
            usestruct.isjithook = bool(dumpvalues["isjithook"])
            if self.search_addr_range.idx() == 0:
                usestruct.minAddress = self.safehex(
                    dumpvalues["startaddr"], usestruct.minAddress
                )
                usestruct.maxAddress = self.safehex(
                    dumpvalues["stopaddr"], usestruct.maxAddress
                )
            else:
                usestruct.boundaryModule = dumpvalues["module"][:120]
                usestruct.minAddress = self.safehex(
                    dumpvalues["offstartaddr"], usestruct.minAddress
                )
                usestruct.maxAddress = self.safehex(
                    dumpvalues["offstopaddr"], usestruct.maxAddress
                )
            usestruct.padding = dumpvalues["stroffset"]
            usestruct.offset = dumpvalues["offset"]
            usestruct.searchTime = dumpvalues["time"] * 1000  # dumpvalues[7]
            usestruct.maxRecords = dumpvalues["maxrecords"]  # dumpvalues[8]
        self.textsource.findhook(usestruct, dumpvalues.get("addresses", None))
        if idx != 1:
            self.parent().findhookchecked()
        self.close()

    def closeEvent(self, a0: QCloseEvent):
        self.hide()
        a0.ignore()
        # return super().closeEvent(a0)

    def hex2str(self, h):
        byte_data = h
        hex_str = binascii.hexlify(byte_data).decode()
        space_hex_str = " ".join(
            [hex_str[i : i + 2] for i in range(0, len(hex_str), 2)]
        )
        return space_hex_str

    def showEvent(self, a0):

        try:
            _list = self.getlistcall()
        except:
            _list = []
        text: QLineEdit = self.saveline
        t = text.text()
        self.savecombo.clear()
        self.savecombo.addItems(_list)
        if t:
            text.setText(t)
            if t in _list:
                self.savecombo.setCurrentIndex(_list.index(t))
        return super().showEvent(a0)

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("搜索设置")
        mainlayout = QVBoxLayout(self)
        checks = QButtonGroup_switch_widegt(self)
        self.searchmethod = checks

        layout1 = QHBoxLayout()
        layout1.addWidget(LLabel("代码页"))
        if savehook_new_data[gobject.base.gameuid].get(
            "hooksetting_follow_default", True
        ):
            cp = globalconfig["codepage_value"]
        else:
            cp = savehook_new_data[gobject.base.gameuid]["hooksetting_private"].get(
                "codepage_value", globalconfig["codepage_value"]
            )
        self.codepagesave = {"spcp": cp}
        layout1.addWidget(
            getsimplecombobox(
                static_data["codepage_display"],
                self.codepagesave,
                "spcp",
                internal=static_data["codepage_real"],
            )
        )

        mainlayout.addLayout(layout1)

        usestruct = self.textsource.defaultsp()
        w1, self.layoutseatchtext = getformlayoutw(hide=True)

        self.searchtext = QLineEdit()
        # self.codepage=QSpinBox()
        # self.codepage.setMaximum(100000)
        # self.codepage.setValue(usestruct.codepage)
        self.layoutseatchtext.addRow("文本", self.searchtext)

        w2, self.layoutsettings = getformlayoutw(hide=True)
        _ = QWidget()
        self.wlist = [_, w1, w2]

        self.regists = {}

        def autoaddline(
            reg,
            _vis,
            _val,
            _type,
            uselayout=self.layoutsettings,
            getlistcall=None,
            listeditable=True,
        ):
            if _type == 0:
                line = QLineEdit(_val)
                line.setValidator(HexValidator())
                regwid = addwid = line
            elif _type == -2:
                line = QLineEdit(_val)
                line.setValidator(PatternValidator())
                regwid = addwid = line
            elif _type == -1:
                sp = FocusSpin()
                sp.setDisplayIntegerBase(16)
                sp.setMaximum(0x7FFFFFFF)
                sp.setMinimum(-0x7FFFFFFF)
                sp.setValue(_val)
                regwid = addwid = sp
            elif _type == 1:
                sp = FocusSpin()
                sp.setMaximum(10000000)
                sp.setValue(_val)
                regwid = addwid = sp
            elif _type == 2:
                line = QLineEdit(str(_val))

                combo = FocusCombo()
                self.getlistcall = getlistcall
                self.savecombo = combo
                self.saveline = line
                combo.setLineEdit(line)
                line.setReadOnly(not listeditable)

                addwid = combo
                regwid = line
            uselayout.addRow(_vis, addwid)
            self.regists[reg] = regwid

        self.search_addr_range = QButtonGroup_switch_widegt(self)
        self.layoutsettings.addRow("搜索范围", self.search_addr_range)
        absaddrw, absaddrl = getformlayoutw()
        offaddrw, offaddrl = getformlayoutw()
        self.search_addr_range.addW("绝对地址", absaddrw)
        self.search_addr_range.addW("相对地址", offaddrw)
        autoaddline(
            "startaddr",
            "起始地址_(hex)",
            hex(usestruct.minAddress)[2:],
            0,
            uselayout=absaddrl,
        )
        autoaddline(
            "stopaddr",
            "结束地址_(hex)",
            hex(usestruct.maxAddress)[2:],
            0,
            uselayout=absaddrl,
        )

        autoaddline(
            "module",
            "指定模块",
            usestruct.boundaryModule,
            2,
            uselayout=offaddrl,
            getlistcall=self.textsource.listprocessm,
        )
        autoaddline(
            "offstartaddr",
            "起始地址_(hex)",
            hex(usestruct.minAddress)[2:],
            0,
            uselayout=offaddrl,
        )
        autoaddline(
            "offstopaddr",
            "结束地址_(hex)",
            hex(usestruct.maxAddress)[2:],
            0,
            uselayout=offaddrl,
        )

        _typelayout = LFormLayout()

        self.layoutsettings.addRow("搜索方式", _typelayout)
        _jitcombo = FocusCombo()
        _jitcombo.addItems(["PC", "JIT"])
        self.search_method = QButtonGroup_switch_widegt(self)
        _jitcombo.currentIndexChanged.connect(
            lambda idx: [
                self.search_method.setVisible(idx == 0),
                self.resize(self.width(), 1),
            ]
        )
        self.regists["isjithook"] = lambda: bool(_jitcombo.currentIndex())

        _typelayout.addRow("类型", _jitcombo)

        self.layoutsettings.addWidget(self.search_method)

        patternW, patternWl = getformlayoutw()
        # presetW,presetWl=getformlayoutw()
        self.search_method.addW("特征匹配", patternW)
        self.search_method.addW("函数对齐", QLabel())
        self.search_method.addW("函数调用", QLabel())

        addresses = []

        def callback():
            try:
                with open(addresses[-1], "r", encoding="utf8", errors="ignore") as ff:
                    return ff.read()
            except:
                return ""

        self.regists["addresses"] = callback
        self.search_method.addW(
            "地址表",
            getsimplepatheditor(
                text="",
                callback=addresses.append,
                icons=("fa.folder-open",),
                clearable=False,
            ),
        )

        autoaddline(
            "pattern",
            "搜索匹配的特征_(hex)",
            self.hex2str(usestruct.pattern),
            -2,
            uselayout=patternWl,
        )
        autoaddline(
            "offset", "相对特征地址的偏移", usestruct.offset, 1, uselayout=patternWl
        )

        autoaddline("stroffset", "字符串地址偏移", usestruct.padding, -1)
        autoaddline("time", "搜索持续时间_(s)", usestruct.searchTime // 1000, 1)
        autoaddline("maxrecords", "搜索结果数上限", usestruct.maxRecords, 1)

        checks.addW("默认搜索", _)
        checks.addW("文本搜索", w1)
        checks.addW("自定义搜索", w2)
        mainlayout.addWidget(checks)
        btn = LPushButton("开始搜索")
        btn.clicked.connect(self.searchstart)
        mainlayout.addWidget(btn)


class hookselect(closeashidewindow):
    addnewhooksignal = pyqtSignal(tuple, bool, bool)
    sysmessagesignal = pyqtSignal(int, str)
    removehooksignal = pyqtSignal(tuple)
    getfoundhooksignal = pyqtSignal(dict)
    update_item_new_line = pyqtSignal(tuple, str)
    SaveTextThreadRole = Qt.ItemDataRole.UserRole + 1

    @property
    def textsource(self) -> texthook:
        return gobject.base.textsource

    def __init__(self, parent):
        super(hookselect, self).__init__(parent, globalconfig["selecthookgeo"])
        self.setupUi()
        self.hidesearchhookbuttons()
        self.is_focus_normal = True
        self.firsttimex = True
        self.searchhookparam = None
        self.removehooksignal.connect(self.removehook)
        self.addnewhooksignal.connect(self.addnewhook)
        self.sysmessagesignal.connect(self.sysmessage)
        self.update_item_new_line.connect(self.update_item_new_line_function)
        self.getfoundhooksignal.connect(self.getfoundhook)
        self.setWindowTitleWithVersion("选择文本")
        self.changeprocessclear()

    def querykeyofrow(self, row):
        if isinstance(row, QModelIndex):
            row = row.row()
        return self.ttCombomodelmodel.data(
            self.ttCombomodelmodel.index(row, 0), self.SaveTextThreadRole
        )

    def querykeyindex(self, k):
        for row in range(self.ttCombomodelmodel.rowCount()):
            if self.querykeyofrow(row) == k:
                return row
        return -1

    def update_item_new_line_function(self, key, output: str):
        row = self.querykeyindex(key)
        if row == -1:
            return
        if self.is_focus_normal and row == self.tttable.currentIndex().row():
            self.getnewsentence(output)
        output = output[:200].replace("\n", " ")
        colidx = 2 + int(bool(self.embedablenum))
        self.ttCombomodelmodel.item(row, colidx).setText(output)

    def removehook(self, key):
        row = self.querykeyindex(key)
        if row == -1:
            return
        self.ttCombomodelmodel.removeRow(row)
        self.solveifembedablenumdecreaseto0(key)

    def solveifembedablenumdecreaseto0(self, key):
        embedable = self.saveifembedable.pop(key)
        if not embedable:
            return
        self.embedablenum -= 1
        if self.embedablenum > 0:
            return
        self.currentheader.pop(1)
        self.ttCombomodelmodel.removeColumn(1)
        self.ttCombomodelmodel.setHorizontalHeaderLabels(self.currentheader)

    def solveifembedablenumincreaseto1(self, key, isembedable):
        self.saveifembedable[key] = isembedable
        if not isembedable:
            return
        self.embedablenum += 1
        if self.embedablenum != 1:
            return

        self.currentheader.insert(1, "内嵌")
        self.ttCombomodelmodel.insertColumn(1, [])
        self.ttCombomodelmodel.setHorizontalHeaderLabels(self.currentheader)
        self.tttable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )

    def changeprocessclear(self):
        # self.ttCombo.clear()
        self.ttCombomodelmodel.clear()
        self.textOutput.clear()
        self.allres = OrderedDict()
        self.hidesearchhookbuttons()
        self.currentheader = ["显示", "HOOK", "文本"]
        self.saveifembedable = {}
        self.embedablenum = 0
        self.embedselectall = {}
        self.hookselectall = {}

    def addnewhook(self, key, select, isembedable):
        hc, hn, tp = key

        if self.ttCombomodelmodel.rowCount() == 0:
            self.ttCombomodelmodel.setHorizontalHeaderLabels(self.currentheader)
            self.tttable.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )
            self.tttable.horizontalHeader().setSectionResizeMode(
                len(self.currentheader) - 1, QHeaderView.ResizeMode.Interactive
            )
            self.tttable.horizontalHeader().setSectionResizeMode(
                len(self.currentheader) - 2, QHeaderView.ResizeMode.Interactive
            )
        self.solveifembedablenumincreaseto1(key, isembedable)
        selectbutton = getsimpleswitch(
            {1: select}, 1, callback=functools.partial(self.accept, key)
        )
        if self.hookselectall.get(hc, False):
            selectbutton.click()
        rown = 0 if isembedable else self.ttCombomodelmodel.rowCount()

        items = [
            QStandardItem(),
            QStandardItem("%s %s %x:%x" % (hn, hc, tp.ctx, tp.ctx2)),
            QStandardItem(),
        ]
        if self.embedablenum:
            items.insert(1, QStandardItem())
        self.ttCombomodelmodel.insertRow(rown, items)
        items[0].setData(key, self.SaveTextThreadRole)

        self.tttable.setIndexWidget(self.ttCombomodelmodel.index(rown, 0), selectbutton)
        if isembedable:
            checkbtn = MySwitch(sign=self._check_tp_using(key))

            checkbtn.clicked.connect(functools.partial(self._embedbtnfn, key))

            self.tttable.setIndexWidget(
                self.ttCombomodelmodel.index(rown, 1),
                checkbtn,
            )
            if self.embedselectall.get(hc, False):
                checkbtn.click()

        if select and self.tttable.currentIndex() == -1:
            self.tttable.setCurrentIndex(rown)

    def _check_tp_using(self, key):
        hc, hn, tp = key
        _isusing = self.textsource.Luna_CheckIsUsingEmbed(tp)
        if _isusing:

            if hn[:8] == "UserHook":
                needinserthookcode = savehook_new_data[gobject.base.gameuid].get(
                    "needinserthookcode", []
                )
                needinserthookcode = list(set(needinserthookcode + [hc]))
                savehook_new_data[gobject.base.gameuid].update(
                    {"needinserthookcode": needinserthookcode}
                )
            else:
                pass
        return _isusing

    def _embedbtnfn(self, key, use):
        hc, hn, tp = key
        self.textsource.Luna_UseEmbed(tp, use)
        _use = self._check_tp_using(key)
        if "embedablehook" not in savehook_new_data[gobject.base.gameuid]:
            savehook_new_data[gobject.base.gameuid]["embedablehook"] = []
        if _use:
            savehook_new_data[gobject.base.gameuid]["embedablehook"].append(
                [hc, tp.addr, tp.ctx, tp.ctx2]
            )
        else:
            save = []
            for _ in savehook_new_data[gobject.base.gameuid]["embedablehook"]:
                hc, ad, c1, c2 = _
                if (hc, 0, c1, c2) == (hc, 0, tp.ctx, tp.ctx2):
                    save.append(_)
            for _ in save:
                savehook_new_data[gobject.base.gameuid]["embedablehook"].remove(_)

    def keyPressEvent__(self, e: QKeyEvent):
        if e.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            curr = self.tttable.currentIndex()
            self.tttable.setCurrentIndex(curr)
            self.ViewThread(curr)
        elif e.key() == Qt.Key.Key_Return:
            self.table1doubleclicked(self.tttable.currentIndex())

    def setupUi(self):
        self.widget = QWidget()

        self.setCentralWidget(self.widget)
        self.setWindowIcon(
            qtawesome.icon(globalconfig["toolbutton"]["buttons"]["selecttext"]["icon"])
        )
        self.hboxlayout = QHBoxLayout(self.widget)
        self.vboxlayout = QVBoxLayout()
        self.hboxlayout.addLayout(self.vboxlayout)
        self.ttCombomodelmodel = LStandardItemModel()

        self.tttable = TableViewW()
        self.tttable.setModel(self.ttCombomodelmodel)
        # self.tttable .horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tttable.horizontalHeader().setStretchLastSection(True)
        self.tttable.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tttable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tttable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tttable.doubleClicked.connect(self.table1doubleclicked)
        self.tttable.clicked.connect(self.ViewThread)
        self.tttable.keyPressed.connect(self.keyPressEvent__)
        # self.tttable.setFont(font)
        self.vboxlayout.addWidget(self.tttable)
        # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # table.clicked.connect(self.show_info)

        self.tttable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tttable.customContextMenuRequested.connect(self.showmenu)

        # self.ttCombo.setMaxVisibleItems(50)

        self.userhooklayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.userhooklayout)

        self.searchtext = QLineEdit()
        self.searchtext.textChanged.connect(self.searchtextfunc)
        self.userhooklayout.addWidget(self.searchtext)
        self.opensolvetextb = LPushButton("文本处理")
        self.opensolvetextb.clicked.connect(self.opensolvetext)
        self.userhooklayout.addWidget(self.opensolvetextb)

        self.settingbtn = LPushButton("游戏设置")
        self.settingbtn.clicked.connect(self.opengamesetting)
        self.userhooklayout.addWidget(self.settingbtn)

        #################
        self.searchtextlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchtextlayout)
        __ = LPushButton("游戏适配")
        __.clicked.connect(lambda: os.startfile(dynamiclink("Resource/game_support")))

        self.userhook = QLineEdit()
        self.searchtextlayout.addWidget(self.userhook)
        userhookinsert = LPushButton("插入特殊码")
        userhookinsert.clicked.connect(self.inserthook)
        self.searchtextlayout.addWidget(userhookinsert)

        self.searchtextlayout.addWidget(D_getdoclink("hooksettings.html#特殊码格式")())

        self.userhookfind = LPushButton("搜索特殊码")
        self.userhookfind.clicked.connect(self.findhook)
        self.searchtextlayout.addWidget(self.userhookfind)
        self.searchtextlayout.addWidget(__)

        ###################
        self.ttCombomodelmodel2 = LStandardItemModel()
        self.tttable2 = TableViewW()
        self.vboxlayout.addWidget(self.tttable2)
        self.tttable2.setModel(self.ttCombomodelmodel2)
        # self.tttable2 .horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tttable2.horizontalHeader().setStretchLastSection(True)
        self.tttable2.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tttable2.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tttable2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tttable2.clicked.connect(self.ViewThread2)

        self.searchtextlayout2 = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchtextlayout2)
        self.searchtext2 = QLineEdit()
        self.searchtextlayout2.addWidget(self.searchtext2)
        self.searchtextbutton2 = LPushButton("搜索")
        self.checkfilt_notcontrol = LCheckBox(("过滤控制字符"))
        self.checkfilt_notascii = LCheckBox(("过滤纯英文"))
        self.checkfilt_notshiftjis = LCheckBox(("过滤乱码文本"))
        self.checkfilt_notcontrol.setChecked(True)
        self.checkfilt_notascii.setChecked(True)
        self.checkfilt_notshiftjis.setChecked(True)
        self.searchtextlayout2.addWidget(self.checkfilt_notcontrol)
        self.searchtextlayout2.addWidget(self.checkfilt_notascii)
        self.searchtextlayout2.addWidget(self.checkfilt_notshiftjis)
        self.searchtextbutton2.clicked.connect(self.searchtextfunc2)
        self.searchtextlayout2.addWidget(self.searchtextbutton2)

        self.textOutput = QPlainTextEdit()
        self.textOutput.setUndoRedoEnabled(False)
        self.textOutput.setReadOnly(True)

        self.sysOutput = QPlainTextEdit()
        self.sysOutput.setUndoRedoEnabled(False)
        self.sysOutput.setReadOnly(True)

        self.tabwidget = LTabWidget()
        self.vboxlayout.addWidget(self.tabwidget)
        self.tabwidget.setTabPosition(QTabWidget.TabPosition.East)
        self.tabwidget.addTab(self.textOutput, ("文本"))
        self.tabwidget.addTab(self.sysOutput, ("日志"))
        self.tabwidget.setCurrentIndex(1)

    def parse_hook_menu(self, index: QModelIndex):
        _ = self.querykeyofrow(index)
        if not _:
            return
        mp = (self.embedselectall, self.hookselectall)[index.column() == 0]
        hc, hn, tp = _
        menu = QMenu(self.tttable)
        selectall = LAction("选取同名全部", menu)
        selectall.setCheckable(True)
        selectall.setChecked(mp.get(hc, False))
        menu.addAction(selectall)
        action = menu.exec(self.tttable.cursor().pos())
        if action == selectall:
            mp[hc] = selectall.isChecked()
            if not mp[hc]:
                return
            for _ in range(self.tttable.model().rowCount()):
                w: MySwitch = self.tttable.indexWidgetX(_, index.column())
                if not w:
                    continue
                _ = self.querykeyofrow(_)
                if not _:
                    continue
                hc, hn, tp = _
                if not mp.get(hc, False):
                    continue
                w.click()

    def showmenu(self, _):
        index = self.tttable.currentIndex()
        if not index.isValid():
            return
        elif (self.embedablenum and index.column() == 1) or (index.column() == 0):
            return self.parse_hook_menu(index)
        elif self.tttable.indexWidget(index):
            return
        menu = QMenu(self.tttable)
        remove = LAction("移除", menu)
        removeforever = LAction("移除且总是移除", menu)
        copy = LAction("复制特殊码", menu)
        menu.addAction(remove)
        menu.addAction(removeforever)
        menu.addAction(copy)
        action = menu.exec(self.tttable.cursor().pos())
        _ = self.querykeyofrow(index)
        if not _:
            return
        hc, hn, tp = _
        if action in (remove, removeforever):
            self.textsource.Luna_RemoveHook(tp.processId, tp.addr)
            if hn[:8] == "UserHook":
                try:
                    savehook_new_data[gobject.base.gameuid][
                        "needinserthookcode"
                    ].remove(hc)
                except:
                    pass
            if action == removeforever:
                removeforeverhook = savehook_new_data[gobject.base.gameuid].get(
                    "removeforeverhook", []
                )
                removeforeverhook = list(set(removeforeverhook + [hc]))
                savehook_new_data[gobject.base.gameuid].update(
                    {"removeforeverhook": removeforeverhook}
                )
        elif action == copy:
            NativeUtils.ClipBoard.text = hc

    def opensolvetext(self):
        try:
            dialog_setting_game(self, gobject.base.gameuid, 3)
        except:
            print_exc()

    def opengamesetting(self):
        try:
            dialog_setting_game(self, gobject.base.gameuid, 1)
        except:
            print_exc()

    def checkchaos(self, text):
        try:
            text.encode("shift-jis")
            return False
        except:
            pass
        return True

    def gethide(self, res: str):
        if self.checkfilt_notascii.isChecked():
            if res.isascii():
                return True
        if self.checkfilt_notshiftjis.isChecked():
            if self.checkchaos(res):
                return True
        if self.checkfilt_notcontrol.isChecked():
            for r in res:
                if is_ascii_control(r):
                    return True
        return False

    def searchtextfunc2(self):
        searchtext = self.searchtext2.text()

        for index in range(len(self.allres)):
            _index = len(self.allres) - 1 - index

            res = "\n".join(self.allres[list(self.allres.keys())[_index]])

            hide = (searchtext not in res) or self.gethide(res)
            self.tttable2.setRowHidden(_index, hide)

    def searchtextfunc(self, searchtext):
        # self.ttCombomodelmodel.blockSignals(True)
        try:
            for row in range(self.ttCombomodelmodel.rowCount()):
                key = self.querykeyofrow(row)
                _, _, tp = key
                hist = self.textsource.QueryThreadHistory(tp)
                self.tttable.setRowHidden(row, searchtext not in hist)
        except:
            pass
        # self.ttCombomodelmodel.blockSignals(False)
        # self.ttCombo.setItemData(index,'',Qt.UserRole-(1 if ishide else 0))
        # self.ttCombo.setRowHidden(index,ishide)

    def inserthook(self):
        hookcode = self.userhook.text()
        if len(hookcode) == 0:
            return

        if self.textsource.pids:
            self.textsource.inserthook(hookcode)
            self.tabwidget.setCurrentIndex(1)

    def hidesearchhookbuttons(self, hide=True):

        self.tttable2.setHidden(hide)
        self.searchtextbutton2.setHidden(hide)
        self.searchtext2.setHidden(hide)
        self.checkfilt_notcontrol.setHidden(hide)
        self.checkfilt_notascii.setHidden(hide)
        self.checkfilt_notshiftjis.setHidden(hide)

    def findhook(self):
        if not self.textsource.pids:
            return
        if globalconfig["sourcestatus2"]["texthook"]["use"] == False:
            return
        if self.firsttimex:
            self.firsttimex = False
            QMessageBox.warning(self, _TR("警告"), _TR("该功能可能会导致游戏崩溃！"))
        if not self.searchhookparam:
            self.searchhookparam = searchhookparam(self)
        self.searchhookparam.show()

    def findhookchecked(self):
        if self.textsource.pids:
            self.allres.clear()
            self.ttCombomodelmodel2.clear()
            self.ttCombomodelmodel2.setHorizontalHeaderLabels(["HOOK", "文本"])
            self.hidesearchhookbuttons()
        else:
            self.getnewsentence(_TR("！未选定进程！"))

    def getfoundhook(self, hooks):

        searchtext = self.searchtext2.text()

        for hookcode in hooks:
            string = hooks[hookcode][-1]
            if hookcode not in self.allres:
                self.allres[hookcode] = hooks[hookcode].copy()
                self.ttCombomodelmodel2.insertRow(
                    self.ttCombomodelmodel2.rowCount(),
                    [QStandardItem(hookcode), QStandardItem(string[:100])],
                )
            else:
                self.allres[hookcode] += hooks[hookcode].copy()
                self.ttCombomodelmodel2.setItem(
                    list(self.allres.keys()).index(hookcode),
                    1,
                    QStandardItem(string[:100]),
                )

            resbatch = self.allres[hookcode]
            hide = all(
                [(searchtext not in res) or self.gethide(res) for res in resbatch]
            )
            self.tttable2.setRowHidden(list(self.allres.keys()).index(hookcode), hide)
        if len(hooks) == 0:
            return
        self.hidesearchhookbuttons(False)

    def accept(self, key, select):
        try:
            hc, hn, tp = key
            self.textsource.usermanualaccepthooks.append(key)
            self.textsource.edit_selectedhook_remove(key)

            if select:
                self.textsource.edit_selectedhook_insert(key)

                if hn[:8] == "UserHook":
                    needinserthookcode = savehook_new_data[gobject.base.gameuid].get(
                        "needinserthookcode", []
                    )
                    needinserthookcode = list(set(needinserthookcode + [hc]))
                    savehook_new_data[gobject.base.gameuid].update(
                        {"needinserthookcode": needinserthookcode}
                    )
            else:
                pass

            savehook_new_data[gobject.base.gameuid].update(
                {"hook": self.textsource.serialselectedhook()}
            )

            directshowcollect = []
            for key in self.textsource.selectedhook:
                hc, hn, tp = key
                directshowcollect.append(
                    (key, self.textsource.QueryThreadHistory(tp, True))
                )
            self.textsource.dispatchtextlines(directshowcollect)
        except:
            print_exc()

    def showEvent(self, e):
        gobject.base.safecloseattachprocess()
        if len(self.textsource.selectedhook) == 0:
            return
        row = self.querykeyindex(self.textsource.selectedhook[0])
        if row == -1:
            return
        self.tttable.setCurrentIndex(self.ttCombomodelmodel.index(row, 0))

    def textbrowappendandmovetoend(
        self, textOutput: QPlainTextEdit, sentence, addspace=True
    ):
        scrollbar = textOutput.verticalScrollBar()
        atBottom = (
            scrollbar.value() + 3 > scrollbar.maximum()
            or scrollbar.value() / scrollbar.maximum() > 0.975
        )
        cursor = QTextCursor(textOutput.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(
            (("" if textOutput.document().isEmpty() else "\n") if addspace else "")
            + sentence
        )
        if atBottom:
            scrollbar.setValue(scrollbar.maximum())

    def sysmessage(self, info, sentence):
        if info == HOSTINFO.Console:
            self.textbrowappendandmovetoend(
                self.sysOutput, get_time_stamp() + " " + sentence
            )
        elif info == HOSTINFO.EmuWarning:
            RichMessageBox(
                self,
                _TR("警告"),
                sentence
                + '\n<a href="{}">{}</a>'.format(
                    dynamiclink("emugames.html", docs=True), _TR("使用说明")
                ),
                iserror=False,
                iswarning=True,
            )
        elif info == HOSTINFO.EmuGameName:
            gobject.base.displayinfomessage(sentence, "<msg_info_refresh>")
        elif info == HOSTINFO.EmuConnected:
            gobject.base.translation_ui.showMarkDownSig.emit(
                "{}\n[{}]({})".format(
                    sentence,
                    _TR("模拟器游戏支持表"),
                    dynamiclink("emugames.html", docs=True),
                )
            )

    def getnewsentence(self, sentence):
        self.textbrowappendandmovetoend(self.textOutput, sentence)

    def ViewThread2(self, index: QModelIndex):
        self.is_focus_normal = False
        self.tabwidget.setCurrentIndex(0)
        key = list(self.allres.keys())[index.row()]
        self.userhook.setText(key)
        self.textOutput.setPlainText("\n".join(self.allres[key]))

    def ViewThread(self, index: QModelIndex):
        self.tabwidget.setCurrentIndex(0)
        try:
            _, _, tp = self.querykeyofrow(index)
            self.textOutput.setPlainText(self.textsource.QueryThreadHistory(tp))
            self.textOutput.moveCursor(QTextCursor.MoveOperation.End)
        except:
            print_exc()
        self.is_focus_normal = True

    def table1doubleclicked(self, index: QModelIndex):
        if index.isValid():
            self.tttable.indexWidgetX(index.row(), 0).click()
