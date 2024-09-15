from qtsymbols import *
import functools, json, subprocess, os, time, binascii
from collections import OrderedDict
from traceback import print_exc
import qtawesome, windows, winsharedutils, gobject
from myutils.config import savehook_new_data, static_data, globalconfig, _TR
from myutils.utils import checkchaos, get_time_stamp, dynamiclink
from myutils.wrapper import Singleton_close
from gui.dialog_savedgame import dialog_setting_game
from gui.usefulwidget import (
    closeashidewindow,
    getQMessageBox,
    getsimplecombobox,
    MySwitch,
    getsimpleswitch,
    FocusSpin,
    FocusCombo,
    TableViewW,
)
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


def getformlayoutw(w=None, cls=LFormLayout, hide=False):
    if w is None:
        _w = QWidget()
    else:
        _w = w
    _l = cls()
    if hide:
        _w.hide()
    _l.setContentsMargins(0, 0, 0, 0)
    _w.setLayout(_l)
    return _w, _l


class QButtonGroup_switch_widegt(QWidget):
    selectidx = pyqtSignal(int)

    def __init__(self, p) -> None:
        super().__init__()
        self._parent = p
        _, self.mainlayout = getformlayoutw(self, QVBoxLayout)
        self.selectlayout = QHBoxLayout()
        self.selectlayout.setContentsMargins(0, 0, 0, 0)
        self.mainlayout.addLayout(self.selectlayout)
        self.selectGroup = QButtonGroup()
        self.wlist = []
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

    def addW(self, text, widget):
        self.mainlayout.addWidget(widget)
        btn = LRadioButton(text)
        self.selectGroup.addButton(btn, len(self.wlist))
        self.selectlayout.addWidget(btn)
        if len(self.wlist) == 0:
            btn.setChecked(True)
        else:
            widget.hide()
        self.wlist.append(widget)


hookcodehelp = r"""
1、内存读取
R{S|Q|V|U}[codepage#]@addr
R是内存读取码标志
S是默认ascii字符串，Q是UTF16，U是UTF32，V是UTF8
2、HOOK
{H|B}{A|B|W|I|S|Q|U|V}[F][N][codepage#][padding+]data_offset[*deref_offset][:split_offset[*deref_offset]]@addr[:module[:func]]
H是inlineHook，B是vehhook
单字符：A/B是小端/大端的mbcs，W是UTF16，I是UTF32
字符串：S是默认ascii字符串，Q是UTF16，U是UTF32，V是UTF8。
F：每次读取字符串后添加换行符
N：无视上下文
-4 for EAX, -8 for ECX, -C for EDX, -10 for EBX, -14 for ESP, -18 for EBP, -1C for ESI, -20 for EDI
-C for RAX, -14 for RBX, -1C for RCX, -24 for RDX, and so on for RSP, RBP, RSI, RDI, R8-R15
3、JIT
{H|B}{A|B|W|I|S|Q|M|U|V}[F][N][codepage#][padding+]arg_index[*deref_offset][:split_offset[*deref_offset]]@{info}:JIT:{UNITY|YUZU|PPSSPP|VITA3K|RPCS3}
arg_index是JIT函数的参数index。M为C#字符串，仅UNITY可用。
UNITY的info为：[程序集]:[命名空间]:类名:函数名:参数量
YUZU/PPSSPP/VITA3K/RPCS3的info为模拟地址
4、内嵌
E[D][S][N|O]HOOKCODE
E是使用内嵌的标注，HOOKCODE是JIT特殊码或HOOK特殊码。
D：写入时转换中文字符为日语字符集
S：提取时使用HOOKCODE指定的文本提取方式
N：写入时创建新的字符串并交换字符串指针
O：写入时在原字符串上覆写
"""


@Singleton_close
class dialog_showinfo(QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("HOOKCODE")
        l = QLabel(hookcodehelp)
        l.setWordWrap(True)
        layout = QHBoxLayout()
        layout.addWidget(l)
        self.setLayout(layout)
        self.show()


class searchhookparam(LDialog):
    def safehex(self, string, default):
        try:
            return int(string.replace(" ", "").replace("0x", ""), 16)
        except:
            return default

    def searchstart(self):
        idx = self.searchmethod.idx()
        usestruct = gobject.baseobject.textsource.defaultsp()
        if idx == 0:
            usestruct.length = 0
            usestruct.codepage = static_data["codepage_real"][self.codepagesave["spcp"]]
            # sp = spUser.length == 0 ? spDefault : spUser;
        elif idx == 1:  # 0默认
            # usestruct.codepage=self.codepage.value()
            usestruct.codepage = static_data["codepage_real"][self.codepagesave["spcp"]]
            usestruct.text = self.searchtext.text()[:30]
            if len(usestruct.text) < 4:
                getQMessageBox(self, "警告", "搜索文本过短！", True)
                return
        elif idx == 2:
            dumpvalues = {}
            for k, widget in self.regists.items():
                if type(widget) == QLineEdit:
                    dumpvalues[k] = widget.text()
                if type(widget) == FocusSpin:
                    dumpvalues[k] = widget.value()
                if callable(widget):
                    dumpvalues[k] = widget()
            pattern = dumpvalues["pattern"]
            if "." in pattern:
                usestruct.length = 1
                usestruct.exportModule = pattern[:120]
            else:
                try:
                    bs = bytes.fromhex(
                        pattern.replace(" ", "").replace("0x", "").replace("??", "11")
                    )
                    usestruct.pattern = bs[:30]
                    usestruct.length = len(bs)
                except:
                    pass
            usestruct.boundaryModule = dumpvalues["module"][:120]
            usestruct.address_method = self.search_addr_range.idx()
            usestruct.search_method = self.search_method.idx()
            usestruct.jittype = dumpvalues["jittype"]
            if self.search_addr_range.idx() == 0:
                usestruct.minAddress = self.safehex(
                    dumpvalues["startaddr"], usestruct.minAddress
                )
                usestruct.maxAddress = self.safehex(
                    dumpvalues["stopaddr"], usestruct.maxAddress
                )
            else:
                usestruct.minAddress = self.safehex(
                    dumpvalues["offstartaddr"], usestruct.minAddress
                )
                usestruct.maxAddress = self.safehex(
                    dumpvalues["offstopaddr"], usestruct.maxAddress
                )
            usestruct.padding = 0  # self.safehex(dumpvalues[4], usestruct.padding)
            usestruct.offset = dumpvalues["offset"]
            usestruct.codepage = static_data["codepage_real"][
                self.codepagesave["spcp"]
            ]  # dumpvalues[6]
            usestruct.searchTime = dumpvalues["time"] * 1000  # dumpvalues[7]
            usestruct.maxRecords = dumpvalues["maxrecords"]  # dumpvalues[8]
        gobject.baseobject.textsource.findhook(usestruct)
        if idx != 1:
            self.parent().findhookchecked()
        self.close()

    def hex2str(self, h):
        byte_data = h
        hex_str = binascii.hexlify(byte_data).decode()
        space_hex_str = " ".join(
            [hex_str[i : i + 2] for i in range(0, len(hex_str), 2)]
        )
        return space_hex_str

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        windows.SetWindowPos(
            int(int(self.winId())),
            windows.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            windows.SWP_NOACTIVATE | windows.SWP_NOSIZE | windows.SWP_NOMOVE,
        )
        self.setWindowTitle("搜索设置")
        mainlayout = QVBoxLayout()
        checks = QButtonGroup_switch_widegt(self)
        self.searchmethod = checks
        self.setLayout(mainlayout)

        layout1 = QHBoxLayout()
        layout1.addWidget(LLabel("代码页"))
        if savehook_new_data[gobject.baseobject.gameuid]["hooksetting_follow_default"]:
            cp = globalconfig["codepage_index"]
        else:
            cp = savehook_new_data[gobject.baseobject.gameuid][
                "hooksetting_private"
            ].get("codepage_index", globalconfig["codepage_index"])
        self.codepagesave = {"spcp": cp}
        layout1.addWidget(
            getsimplecombobox(
                static_data["codepage_display"], self.codepagesave, "spcp"
            )
        )

        mainlayout.addLayout(layout1)

        usestruct = gobject.baseobject.textsource.defaultsp()
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
                regwid = addwid = line
            elif _type == 1:
                sp = FocusSpin()
                sp.setMaximum(10000000)
                sp.setValue(_val)
                regwid = addwid = sp
            elif _type == 2:
                line = QLineEdit(str(_val))
                try:
                    _list = getlistcall()
                except:
                    _list = []
                if len(_list) == 0:
                    regwid = addwid = line
                else:
                    combo = FocusCombo()
                    combo.addItems(_list)

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
            "起始地址(hex)",
            hex(usestruct.minAddress)[2:],
            0,
            uselayout=absaddrl,
        )
        autoaddline(
            "stopaddr",
            "结束地址(hex)",
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
            getlistcall=gobject.baseobject.textsource.listprocessm,
        )
        autoaddline(
            "offstartaddr",
            "起始地址(hex)",
            hex(usestruct.minAddress)[2:],
            0,
            uselayout=offaddrl,
        )
        autoaddline(
            "offstopaddr",
            "结束地址(hex)",
            hex(usestruct.maxAddress)[2:],
            0,
            uselayout=offaddrl,
        )

        _typelayout = LFormLayout()

        self.layoutsettings.addRow("搜索方式", _typelayout)
        _jitcombo = FocusCombo()
        _jitcombo.addItems(["PC", "YUZU", "PPSSPP", "VITA3K", "RPCS3"])
        self.search_method = QButtonGroup_switch_widegt(self)
        _jitcombo.currentIndexChanged.connect(
            lambda idx: [
                self.search_method.setVisible(idx == 0),
                self.resize(self.width(), 1),
            ]
        )
        self.regists["jittype"] = lambda: _jitcombo.currentIndex()

        _typelayout.addRow("类型", _jitcombo)

        self.layoutsettings.addWidget(self.search_method)

        patternW, patternWl = getformlayoutw()
        # presetW,presetWl=getformlayoutw()
        self.search_method.addW("特征匹配", patternW)
        self.search_method.addW("函数对齐", QLabel())
        self.search_method.addW("函数调用", QLabel())

        autoaddline(
            "pattern",
            "搜索匹配的特征(hex)",
            self.hex2str(usestruct.pattern),
            0,
            uselayout=patternWl,
        )
        autoaddline(
            "offset", "相对特征地址的偏移", usestruct.offset, 1, uselayout=patternWl
        )

        autoaddline("time", "搜索持续时间(s)", usestruct.searchTime // 1000, 1)
        autoaddline("maxrecords", "搜索结果数上限", usestruct.maxRecords, 1)

        checks.addW("默认搜索", _)
        checks.addW("文本搜索", w1)
        checks.addW("自定义搜索", w2)
        mainlayout.addWidget(checks)
        btn = LPushButton("开始搜索")
        btn.clicked.connect(self.searchstart)
        mainlayout.addWidget(btn)
        self.show()


class hookselect(closeashidewindow):
    addnewhooksignal = pyqtSignal(tuple, bool)
    getnewsentencesignal = pyqtSignal(str)
    sysmessagesignal = pyqtSignal(str)
    removehooksignal = pyqtSignal(tuple)
    getfoundhooksignal = pyqtSignal(dict)
    update_item_new_line = pyqtSignal(tuple, str)

    def __init__(self, parent):
        super(hookselect, self).__init__(parent, globalconfig["selecthookgeo"])
        self.setupUi()
        self.save = []
        self.hidesearchhookbuttons()
        self.removehooksignal.connect(self.removehook)
        self.addnewhooksignal.connect(self.addnewhook)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.sysmessagesignal.connect(self.sysmessage)
        self.update_item_new_line.connect(self.update_item_new_line_function)
        self.getfoundhooksignal.connect(self.getfoundhook)
        self.setWindowTitle("选择文本")
        self.changeprocessclear()

    def update_item_new_line_function(self, hook, output):
        if hook not in self.save:
            return
        row = self.save.index(hook)
        output = output[:200].replace("\n", " ")
        colidx = 2 + int(bool(self.embedablenum))
        self.ttCombomodelmodel.item(row, colidx).setText(output)

    def removehook(self, key):
        if key not in self.save:
            return
        self.ttCombomodelmodel.removeRow(self.save.index(key))
        self.selectionbutton.pop(self.save.index(key))
        self.save.remove(key)
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
        self.save = []
        self.at1 = 1
        self.textOutput.clear()
        self.selectionbutton = []
        self.typecombo = []
        self.allres = OrderedDict()
        self.hidesearchhookbuttons()
        self.currentheader = ["显示", "HOOK", "文本"]
        self.saveifembedable = {}
        self.embedablenum = 0

    def addnewhook(self, key, select):
        hc, hn, tp = key
        isembedable = hc[0] == "E"

        if len(self.save) == 0:
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
        if isembedable:
            self.selectionbutton.insert(
                0,
                getsimpleswitch(
                    {1: False}, 1, callback=functools.partial(self.accept, key)
                ),
            )
            self.save.insert(0, key)
            rown = 0
        else:
            self.save.append(key)
            rown = self.ttCombomodelmodel.rowCount()
            self.selectionbutton.append(
                getsimpleswitch(
                    {1: False}, 1, callback=functools.partial(self.accept, key)
                )
            )
        items = [
            QStandardItem(),
            QStandardItem("%s %s %x:%x" % (hn, hc, tp.ctx, tp.ctx2)),
            QStandardItem(),
        ]
        if self.embedablenum:
            items.insert(1, QStandardItem())
        self.ttCombomodelmodel.insertRow(rown, items)

        if select:
            self.selectionbutton[rown].click()
        self.tttable.setIndexWidget(
            self.ttCombomodelmodel.index(rown, 0), self.selectionbutton[rown]
        )
        if isembedable:
            checkbtn = MySwitch(sign=self._check_tp_using(key))

            checkbtn.clicked.connect(functools.partial(self._embedbtnfn, key))

            self.tttable.setIndexWidget(
                self.ttCombomodelmodel.index(rown, 1),
                checkbtn,
            )

    def _check_tp_using(self, key):
        hc, hn, tp = key
        _isusing = gobject.baseobject.textsource.checkisusingembed(
            tp.addr, tp.ctx, tp.ctx2
        )
        if _isusing:

            if hn[:8] == "UserHook":
                needinserthookcode = savehook_new_data[gobject.baseobject.gameuid][
                    "needinserthookcode"
                ]
                needinserthookcode = list(set(needinserthookcode + [hc]))
                savehook_new_data[gobject.baseobject.gameuid].update(
                    {"needinserthookcode": needinserthookcode}
                )
            else:
                pass
        return _isusing

    def _embedbtnfn(self, key, _):
        hc, hn, tp = key
        gobject.baseobject.textsource.useembed(tp.addr, tp.ctx, tp.ctx2, _)
        _use = self._check_tp_using(key)
        if _use:
            savehook_new_data[gobject.baseobject.gameuid]["embedablehook"].append(
                [hc, tp.addr, tp.ctx, tp.ctx2]
            )
        else:
            save = []
            for _ in savehook_new_data[gobject.baseobject.gameuid]["embedablehook"]:
                hc, ad, c1, c2 = _
                if (hc, 0, c1, c2) == (hc, 0, tp.ctx, tp.ctx2):
                    save.append(_)
            for _ in save:
                savehook_new_data[gobject.baseobject.gameuid]["embedablehook"].remove(_)

    def setupUi(self):
        self.widget = QWidget()

        self.setCentralWidget(self.widget)
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        self.hboxlayout = QHBoxLayout()
        self.widget.setLayout(self.hboxlayout)
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
        # self.tttable.setFont(font)
        self.vboxlayout.addWidget(self.tttable)
        # table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # table.clicked.connect(self.show_info)

        self.tttable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tttable.customContextMenuRequested.connect(self.showmenu)

        # self.ttCombo.setMaxVisibleItems(50)

        self.userhooklayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.userhooklayout)
        self.userhook = QLineEdit()
        self.userhooklayout.addWidget(self.userhook)
        self.userhookinsert = LPushButton("插入特殊码")
        self.userhookinsert.clicked.connect(self.inserthook)
        self.userhooklayout.addWidget(self.userhookinsert)

        self.userhookinsert = QPushButton(icon=qtawesome.icon("fa.question"))
        self.userhookinsert.clicked.connect(lambda: dialog_showinfo(self))
        self.userhooklayout.addWidget(self.userhookinsert)

        self.userhookfind = LPushButton("搜索特殊码")
        self.userhookfind.clicked.connect(self.findhook)
        self.userhooklayout.addWidget(self.userhookfind)

        self.opensolvetextb = LPushButton("文本处理")
        self.opensolvetextb.clicked.connect(self.opensolvetext)
        self.userhooklayout.addWidget(QLabel("      "))
        self.userhooklayout.addWidget(self.opensolvetextb)

        self.settingbtn = LPushButton("游戏设置")
        self.settingbtn.clicked.connect(self.opengamesetting)
        self.userhooklayout.addWidget(self.settingbtn)

        #################
        self.searchtextlayout = QHBoxLayout()
        self.vboxlayout.addLayout(self.searchtextlayout)
        self.searchtext = QLineEdit()
        __ = LPushButton("游戏适配")
        __.clicked.connect(
            lambda: gobject.baseobject.openlink(
                dynamiclink("{main_server}/Resource/game_support")
            )
        )
        self.searchtextlayout.addWidget(__)
        self.searchtextlayout.addWidget(self.searchtext)
        self.searchtextbutton = LPushButton("搜索")
        self.searchtextbutton.clicked.connect(self.searchtextfunc)
        self.searchtextlayout.addWidget(self.searchtextbutton)
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
        self.tabwidget.addTab(self.sysOutput, ("系统"))

    def showmenu(self, p: QPoint):
        r = self.tttable.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(self.tttable)
        remove = LAction(("移除"))
        copy = LAction(("复制特殊码"))
        menu.addAction(remove)
        menu.addAction(copy)
        action = menu.exec(self.tttable.cursor().pos())

        hc, hn, tp = self.save[r]
        if action == remove:
            pid = tp.processId
            addr = tp.addr
            gobject.baseobject.textsource.removehook(pid, addr)

        elif action == copy:
            winsharedutils.clipboard_set(hc)

    def opensolvetext(self):
        try:
            dialog_setting_game(self, gobject.baseobject.gameuid, 3)
        except:
            print_exc()

    def opengamesetting(self):
        try:
            dialog_setting_game(self, gobject.baseobject.gameuid, 1)
        except:
            print_exc()

    def gethide(self, res):
        hide = False

        if self.checkfilt_notascii.isChecked():
            try:
                res.encode("ascii")
                hide = True
            except:
                pass
        if self.checkfilt_notshiftjis.isChecked():
            if checkchaos(res):
                hide = True

        if self.checkfilt_notcontrol.isChecked():
            lres = list(res)

            for r in lres:
                _ord = ord(r)
                if _ord < 0x20 or (_ord > 0x80 and _ord < 0xA0):

                    hide = True
                    break

        return hide

    def searchtextfunc2(self):
        searchtext = self.searchtext2.text()

        for index in range(len(self.allres)):
            _index = len(self.allres) - 1 - index

            resbatch = self.allres[list(self.allres.keys())[_index]]

            hide = all(
                [(searchtext not in res) or self.gethide(res) for res in resbatch]
            )
            self.tttable2.setRowHidden(_index, hide)

    def searchtextfunc(self):
        searchtext = self.searchtext.text()

        # self.ttCombomodelmodel.blockSignals(True)
        try:
            for index, key in enumerate(
                gobject.baseobject.textsource.hookdatacollecter
            ):
                ishide = True
                for i in range(
                    len(gobject.baseobject.textsource.hookdatacollecter[key])
                ):

                    if any(
                        [
                            searchtext in _.replace("\n", "")
                            for _ in gobject.baseobject.textsource.hookdatacollecter[
                                key
                            ][-i:]
                        ]
                    ):
                        ishide = False
                        break
                self.tttable.setRowHidden(index, ishide)
        except:
            pass
        # self.ttCombomodelmodel.blockSignals(False)
        # self.ttCombo.setItemData(index,'',Qt.UserRole-(1 if ishide else 0))
        # self.ttCombo.setRowHidden(index,ishide)

    def inserthook(self):
        hookcode = self.userhook.text()
        if len(hookcode) == 0:
            return

        if gobject.baseobject.textsource.pids:
            gobject.baseobject.textsource.inserthook(hookcode)
            self.tabwidget.setCurrentIndex(1)

    def hidesearchhookbuttons(self, hide=True):

        self.tttable2.setHidden(hide)
        self.searchtextbutton2.setHidden(hide)
        self.searchtext2.setHidden(hide)
        self.checkfilt_notcontrol.setHidden(hide)
        self.checkfilt_notascii.setHidden(hide)
        self.checkfilt_notshiftjis.setHidden(hide)

    def findhook(self):
        if not gobject.baseobject.textsource.pids:
            return
        if globalconfig["sourcestatus2"]["texthook"]["use"] == False:
            return
        getQMessageBox(
            self,
            "警告",
            "该功能可能会导致游戏崩溃！",
            True,
            True,
            lambda: searchhookparam(self),
        )

    def findhookchecked(self):
        if gobject.baseobject.textsource.pids:
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
            if key in gobject.baseobject.textsource.selectedhook:
                gobject.baseobject.textsource.selectedhook.remove(key)

            if select:
                gobject.baseobject.textsource.selectedhook.append(key)

                if hn[:8] == "UserHook":
                    needinserthookcode = savehook_new_data[gobject.baseobject.gameuid][
                        "needinserthookcode"
                    ]
                    needinserthookcode = list(set(needinserthookcode + [hc]))
                    savehook_new_data[gobject.baseobject.gameuid].update(
                        {"needinserthookcode": needinserthookcode}
                    )
            else:
                pass

            savehook_new_data[gobject.baseobject.gameuid].update(
                {"hook": gobject.baseobject.textsource.serialselectedhook()}
            )
        except:
            print_exc()

    def showEvent(self, e):
        gobject.baseobject.safecloseattachprocess()
        try:
            for i in range(len(self.save)):
                if self.save[i] in gobject.baseobject.textsource.selectedhook:
                    self.tttable.setCurrentIndex(self.ttCombomodelmodel.index(i, 0))
                    break
        except:
            print_exc()

    def textbrowappendandmovetoend(self, textOutput, sentence, addspace=True):
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

    def sysmessage(self, sentence):

        self.textbrowappendandmovetoend(
            self.sysOutput, get_time_stamp() + " " + sentence
        )

    def getnewsentence(self, sentence):
        if self.at1 == 2:
            return

        self.textbrowappendandmovetoend(self.textOutput, sentence)

    def ViewThread2(self, index: QModelIndex):
        self.tabwidget.setCurrentIndex(0)
        self.at1 = 2
        key = list(self.allres.keys())[index.row()]
        self.userhook.setText(key)
        self.textOutput.setPlainText("\n".join(self.allres[key]))

    def ViewThread(self, index: QModelIndex):
        self.tabwidget.setCurrentIndex(0)
        self.at1 = 1
        try:
            # print(gobject.baseobject.textsource)
            gobject.baseobject.textsource.selectinghook = self.save[index.row()]
            hc, hn, tp = self.save[index.row()]

            self.textOutput.setPlainText(
                gobject.baseobject.textsource.QueryThreadHistory(tp)
            )
            self.textOutput.moveCursor(QTextCursor.MoveOperation.End)

        except:
            print_exc()

    def table1doubleclicked(self, index: QModelIndex):
        self.selectionbutton[index.row()].click()
