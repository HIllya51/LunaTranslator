from qtsymbols import *
import functools, uuid, os, qtawesome, time
from datetime import datetime, timedelta, date
from datetime import time as dttime
from traceback import print_exc
import gobject, NativeUtils
import copy
from myutils.post import processfunctions
from myutils.config import (
    savehook_new_data,
    uid2gamepath,
    get_launchpath,
    _TR,
    postprocessconfig,
    defaultpost,
    globalconfig,
    static_data,
)
from myutils.magpie_builtin import MagpieConfig
from gui.setting.display_scale import makescalew
from myutils.wrapper import tryprint
import sqlite3
from gui.dialog_memory import dialog_memory
from myutils.localetools import getgamecamptools, maycreatesettings
from gui.fluent.expander import ExExpander
from gui.fluent.settingtree import FluentSettingTree, wrap_setting_tree
from myutils.hwnd import getExeIcon
from myutils.wrapper import Singleton
from myutils.utils import (
    all_langs,
    gamdidchangedtask,
    checkpostlangmatch,
    loadpostsettingwindowmethod_private,
    titlechangedtask,
    selectdebugfile,
    targetmod,
)
from gui.inputdialog import (
    noundictconfigdialog1,
    yuyinzhidingsetting,
    stringreplacedialog,
    autoinitdialog,
    autoinitdialog_items,
    postconfigdialog,
)
from gui.setting.textinput import gethookgrid_em, gethookgrid
from gui.specialwidget import chartwidget
from gui.usefulwidget import (
    makecardrow,
    makescroll,
    DarkLightAutoResetIconHelper,
    clearlayout,
    makescrollgrid,
    automakegrid,
    getsimpleswitch,
    maketabholder,
    getsimplepatheditor,
    getboxlayout,
    IconButton,
    getsimplecombobox,
    D_getIconButton,
    D_getsimpleswitch,
    getspinbox,
    ClickableLabel,
    getIconButton,
    makesubtab_lazy,
    manybuttonlayout,
    GroupCardWidget,
    getsmalllabel,
    listediterline,
    VisGridLayout,
)
from gui.dynalang import (
    LFormLayout,
    LPushButton,
    LStandardItemModel,
    LAction,
    LLabel,
    LDialog,
    LTableView,
)


def maybehavebutton(self, gameuid, post):
    save_text_process_info = savehook_new_data[gameuid]["save_text_process_info"]
    if post == "_11":
        if "mypost" not in save_text_process_info:
            save_text_process_info["mypost"] = str(uuid.uuid4()).replace("-", "_")
        return getIconButton(
            icon="fa.edit",
            callback=functools.partial(
                selectdebugfile,
                save_text_process_info["mypost"],
                ismypost=True,
            ),
            fix=False,
        )
    else:
        if post not in postprocessconfig:
            return
        if "args" in postprocessconfig[post]:
            if post == "stringreplace":
                callback = functools.partial(
                    stringreplacedialog,
                    self,
                    save_text_process_info["postprocessconfig"][post],
                    True,
                )
            elif isinstance(list(postprocessconfig[post]["args"].values())[0], dict):
                callback = functools.partial(
                    postconfigdialog,
                    self,
                    save_text_process_info["postprocessconfig"][post]["args"][
                        "替换内容"
                    ],
                    postprocessconfig[post]["name"],
                    ["原文内容", "替换为"],
                )
            else:
                items = autoinitdialog_items(
                    save_text_process_info["postprocessconfig"][post]
                )
                callback = functools.partial(
                    autoinitdialog,
                    self,
                    save_text_process_info["postprocessconfig"][post]["args"],
                    postprocessconfig[post]["name"],
                    600,
                    items,
                )
            return getIconButton(callback=callback)
        else:
            return None


class _GameTextProcTree(FluentSettingTree):
    """游戏设置-文本处理 列表（原 TableViewW 改树）：使用 / 设置（无标题列）
    /预处理方法 / 移动（末列），拖拽或上下移按钮排序（循环）。无文档链接。
    行内容写 save_text_process_info（rank 序 + 每方法私有配置）。"""

    def __init__(self, host, gameuid, parent=None):
        super().__init__(
            parent,
            titles=["使用", "", "预处理方法", ""],
            draggable=True,
        )
        self._host = host
        self._gameuid = gameuid
        hdr = self.header()
        for c in (0, 1, 3):
            hdr.setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showmenu)
        self.rebuild()

    # ---- 数据 ----
    def _rank(self):
        return savehook_new_data[self._gameuid][
            "save_text_process_info"]["rank"]

    def _pconf(self):
        return savehook_new_data[self._gameuid][
            "save_text_process_info"]["postprocessconfig"]

    def _ensureconf(self, k):
        """该游戏的私有配置副本（原 __checkaddnewmethod 的初始化）。"""
        pconf = self._pconf()
        if k not in pconf:
            if k == "stringreplace":
                pconf[k] = copy.deepcopy(defaultpost[k])
            else:
                pconf[k] = copy.deepcopy(postprocessconfig[k])
            pconf[k]["use"] = True
        return pconf[k]

    # ---- 行构建 ----
    def rebuild(self):
        self.clear()
        for k in self._rank():
            if k not in postprocessconfig:
                continue
            conf = self._ensureconf(k)
            item = QTreeWidgetItem()
            item.setData(0, Qt.ItemDataRole.UserRole, k)
            self.addTopLevelItem(item)
            self.setItemWidget(item, 0, self._cell(
                getsimpleswitch(conf, "use"), center=True))
            btn = maybehavebutton(self._host, self._gameuid, k)
            if btn is not None:
                self.setItemWidget(item, 1, self._cell(btn, center=True))
            self.setItemWidget(item, 2, self._cell(
                LLabel(_TR(postprocessconfig[k]["name"]))))
            self.setItemWidget(
                item, 3, self._movecell(functools.partial(self._move, k)))

    # ---- 排序（拖拽 / 上下移按钮共用）----
    def _applymove(self, idx1, idx2):
        rank = self._rank()
        k = rank.pop(idx1)
        rank.insert(idx2, k)
        self.rebuild()

    def _ondrop(self, idx1, idx2):
        self._applymove(idx1, idx2)

    def _move(self, k, up, tomax):
        """循环移一位（首行再上移到末尾、末行再下移到开头），
        右键（tomax）置顶/置底。"""
        rank = self._rank()
        idx1 = rank.index(k)
        if tomax:
            idx2 = 0 if up else len(rank) - 1
        else:
            idx2 = (idx1 + (-1 if up else 1)) % len(rank)
        if idx2 == idx1:
            return
        self._applymove(idx1, idx2)

    # ---- 增删 ----
    def addmethod(self, k):
        """添加行回调：新方法插到最前（同旧版）。"""
        rank = self._rank()
        if k not in rank:
            rank.insert(0, k)
        self._ensureconf(k)
        self.rebuild()

    def removecurrent(self):
        item = self.currentItem()
        if item is None:
            return
        k = item.data(0, Qt.ItemDataRole.UserRole)
        rank = self._rank()
        if k in rank:
            rank.remove(k)
        pconf = self._pconf()
        if k in pconf:
            pconf.pop(k)
        self.rebuild()

    def _showmenu(self, p):
        item = self.itemAt(p)
        if item is None:
            return
        self.setCurrentItem(item)
        menu = QMenu(self)
        remove = LAction("删除", menu)
        menu.addAction(remove)
        action = menu.exec(QCursor.pos())
        if action == remove:
            self.removecurrent()


class _GameTransOptimiTree(FluentSettingTree):
    """游戏设置-翻译优化 列表：使用 / 设置（无标题列）/ 名称（静态，
    无排序、无文档链接）。开关写 savehook_new_data[gameuid][name_use]，
    设置按钮为该游戏的私有设置窗口（仅有私有设置项的行）。"""

    def __init__(self, host, gameuid, parent=None):
        super().__init__(parent, titles=["使用", "", "名称"])
        self._host = host
        self._gameuid = gameuid
        hdr = self.header()
        for c in (0, 1):
            hdr.setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.rebuild()

    def rebuild(self):
        self.clear()
        for item_ in static_data["transoptimi"]:
            name = item_["name"]
            visname = item_["visname"]
            if not checkpostlangmatch(name):
                continue
            setting = loadpostsettingwindowmethod_private(name)
            if not setting:
                continue
            item = QTreeWidgetItem()
            item.setData(0, Qt.ItemDataRole.UserRole, name)
            self.addTopLevelItem(item)

            def __(f, host, gameuid):
                return f(host, gameuid)

            self.setItemWidget(item, 0, self._cell(
                getsimpleswitch(
                    savehook_new_data[self._gameuid],
                    name + "_use",
                    default=False,
                ),
                center=True,
            ))
            self.setItemWidget(item, 1, self._cell(
                getIconButton(
                    callback=functools.partial(
                        __, setting, self._host, self._gameuid)),
                center=True,
            ))
            self.setItemWidget(item, 2, self._cell(LLabel(visname)))


class timelistediter(LDialog, DarkLightAutoResetIconHelper):

    def __init__(
        self,
        parent: "dialog_setting_game_internal",
    ) -> None:
        super().__init__(parent)
        gobject.base.somedatabase.lockdata()
        self.gameuid = parent.gameuid
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self.setWindowIcon(qtawesome.icon("fa.edit"))
        self.setWindowTitle("编辑")

        model = LStandardItemModel()
        model.setHorizontalHeaderLabels(["开始", "结束", "删除"])
        self.hcmodel = model
        table = LTableView()
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setWordWrap(False)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        self.hctable = table
        self.internalrealname = []
        self.rm = []
        formLayout = QVBoxLayout(self)
        formLayout.addWidget(self.hctable)
        button = manybuttonlayout(
            [
                ("添加行", self.newline),
                ("保存", self.closeEvent11),
            ]
        )
        formLayout.addLayout(button)
        self.lst = gobject.base.somedatabase.querytraceplaytime(self.gameuid)
        self.lst = [list(_) for _ in self.lst]
        for row, (s, e) in enumerate(self.lst):
            self.createline(s, e, row)
        self.resize(600, 400)
        self.exec()

    def newline(self):
        t = time.time()
        self.createline(t, t, self.hcmodel.rowCount())
        self.lst.append([t, t])

    def createline(self, s, e, row):
        item = QStandardItem()
        item2 = QStandardItem()
        item3 = QStandardItem()
        self.hcmodel.insertRow(row, [item, item2, item3])
        detail_time_edit = QDateTimeEdit()
        detail_time_edit2 = QDateTimeEdit()
        for _, (i, t, edit) in enumerate(
            ((item, s, detail_time_edit), (item2, e, detail_time_edit2))
        ):
            edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
            edit.setDateTime(QDateTime.fromMSecsSinceEpoch(int(t * 1000)))
            if _ == 0:
                another = detail_time_edit2
                another.setMinimumDateTime(edit.dateTime())
            else:
                another = detail_time_edit
                another.setMaximumDateTime(edit.dateTime())
            edit.dateTimeChanged.connect(
                functools.partial(self._changed, _, row, another)
            )
            self.hctable.setIndexWidget(self.hcmodel.indexFromItem(i), edit)
        self.hctable.setIndexWidget(
            self.hcmodel.indexFromItem(item3),
            getIconButton(
                callback=functools.partial(self.remote, row), icon="fa.times"
            ),
        )

    def remote(self, row):
        self.hctable.setRowHidden(row, True)
        self.rm.append(row)

    def _changed(self, i, row, another: QDateTimeEdit, curr: QDateTime):
        self.lst[row][i] = curr.toMSecsSinceEpoch() / 1000
        if i == 0:
            another.setMinimumDateTime(curr)
        else:
            another.setMaximumDateTime(curr)

    def closeEvent11(self):
        lst = []
        for i, _ in enumerate(self.lst):
            if i in self.rm:
                continue
            if _[0] < _[1]:
                lst.append(_)
        lst = self.merge_intervals(lst)
        gobject.base.somedatabase.settraceplaytime(self.gameuid, lst)
        self.close()

    def closeEvent(self, a0):
        gobject.base.somedatabase.unlockdata()
        return super().closeEvent(a0)

    def merge_intervals(self, intervals):
        if len(intervals) <= 1:
            return intervals
        sorted_intervals = sorted(intervals, key=lambda x: x[0])

        merged = []
        current = sorted_intervals[0]

        for interval in sorted_intervals[1:]:
            if interval[0] <= current[1]:
                current = (current[0], max(current[1], interval[1]))
            else:
                merged.append(current)
                current = interval

        merged.append(current)
        return merged


class dialog_setting_game_internal(QWidget):
    def selectexe(self, res):
        uid2gamepath[self.gameuid] = res
        _icon = getExeIcon(get_launchpath(self.gameuid), cache=True)

        self.setWindowIcon(_icon)
        if self.lauchpath:
            self.lauchpath.clear.clicked.emit()

    def __init__(self, parent, gameuid, keepindexobject=None) -> None:
        super().__init__(parent)
        self.__quanju_wc = False
        self.keepindexobject = keepindexobject
        self.lauchpath = None
        self.gameuid = gameuid

    def toplevelpages(self):
        """游戏设置/游戏数据 两页的构建器——原 L2 methodtab 已上提，
        页直接挂到宿主 tab（游戏管理 righttop / 独立设置窗口）。
        本控件只作状态宿主（对话框 parent / keepindexobject / lauchpath
        等），自身无 UI。构建器经 doaddtab 调用：wfunct(gameuid) ->
        (页 QWidget, do)。"""
        return [
            ("游戏设置", functools.partial(self.___tabf3, self.makegamesettings)),
            ("游戏数据", functools.partial(self.___tabf3, self.makegamedata)),
        ]

    def _addtitlerow(self, vbox: QVBoxLayout, gameuid):
        """标题卡：标题编辑 + 搜索 + 记忆列表按钮（游戏数据页顶部，
        统计/元数据 之上）。"""
        titleedit = QLineEdit(savehook_new_data[gameuid]["title"])

        def _titlechange():
            x = titleedit.text()
            titlechangedtask(gameuid, x)
            self.setWindowTitle(x)

        titleedit.textEdited.connect(
            functools.partial(savehook_new_data[gameuid].__setitem__, "title")
        )
        titleedit.returnPressed.connect(_titlechange)
        __list = [
            titleedit,
            getIconButton(_titlechange, icon="fa.search"),
            getIconButton(
                lambda: dialog_memory(self, gameuid=gameuid),
                icon="fa.list-ul",
            ),
        ]
        if savehook_new_data[gameuid].get("emugameid"):
            __list.insert(1, getsmalllabel(savehook_new_data[gameuid].get("emugameid")))
        # 卡片 16 内缩（与 L3 页内表单同缩进），下接 统计/元数据 bar
        vbox.addWidget(makecardrow("标题", getboxlayout(__list), fill=True))

    def ___tabf(self, function, gameuid):
        # 滚动内容控件同 makegrid 的 gridwidget 用 QSS 类做透明（否则被
        # autofill 以 Window(243) 盖掉页面卡底色，见 gethooktab 注释）；
        # 表单 0 边距——页内缩由 dgi 顶层 vbox 的 16px 统一提供
        class formscrollcontent(QWidget):
            pass

        _w = formscrollcontent()
        _w.setStyleSheet("formscrollcontent{background-color:transparent;}")
        formLayout = LFormLayout(_w)
        formLayout.setContentsMargins(16, 16, 16, 12 )
        do = functools.partial(function, formLayout, gameuid)
        scroll = makescroll()
        scroll.setWidget(_w)
        return scroll, do

    def ___tabf2(self, function, gameuid):
        class formscrollcontent2(QWidget):
            pass

        _w = formscrollcontent2()
        _w.setStyleSheet("formscrollcontent2{background-color:transparent;}")
        formLayout = QVBoxLayout(_w)
        formLayout.setContentsMargins(16, 16, 16, 12 )
        do = functools.partial(function, formLayout, gameuid)
        scroll = makescroll()
        scroll.setWidget(_w)
        return scroll, do

    def ___tabf3(self, function, gameuid):
        _w = QWidget()
        formLayout = QVBoxLayout(_w)
        formLayout.setContentsMargins(0, 0, 0, 0)
        do = functools.partial(function, formLayout, gameuid)
        return _w, do

    def makegamedata(self, vbox: QVBoxLayout, gameuid):
        # 标题行在 统计/元数据 之上（游戏数据 tab 内容顶部）
        self._addtitlerow(vbox, gameuid)
        vbox.setContentsMargins(16, 16, 16, 12)
        vbox.setSpacing(0)
        functs = [
            ("统计", functools.partial(self.___tabf2, self.getstatistic)),
            ("元数据", functools.partial(self.___tabf, self.metadataorigin)),
        ]
        methodtab, do = makesubtab_lazy(
            [_[0] for _ in functs],
            [functools.partial(self.doaddtab, _[1], gameuid) for _ in functs],
            delay=True,
            initial=(
                (self.keepindexobject, "gamedata")
                if (self.keepindexobject is not None)
                else None
            ),
            fast=True,
        )
        vbox.addWidget(methodtab)
        do()

    def makegamesettings(self, vbox: QVBoxLayout, gameuid):

        functs = [
            ("启动", functools.partial(self.___tabf, self.starttab)),
            ("HOOK", self.gethooktab),
            ("文本处理", functools.partial(self.___tabf, self.gettextproctab)),
            ("语音", functools.partial(self.___tabf, self.getttssetting)),
            ("预翻译", functools.partial(self.___tabf, self.getpretranstab)),
            ("窗口缩放", functools.partial(self.___tabf, self.getmagpietab)),
        ]
        methodtab, do = makesubtab_lazy(
            [_[0] for _ in functs],
            [functools.partial(self.doaddtab, _[1], gameuid) for _ in functs],
            delay=True,
            initial=(
                (self.keepindexobject, "gamesetting")
                if (self.keepindexobject is not None)
                else None
            ),
            fast=True,
        )

        self.methodtab = methodtab
        vbox.addWidget(maketabholder(methodtab))
        do()

    def openrefmainpage(self, key, idname, gameuid):
        try:
            os.startfile(targetmod[key].refmainpage(savehook_new_data[gameuid][idname]))
        except:
            print_exc()

    def _metaheader(self, key, name, labelw, edit, switch, btns, header=False):
        """元数据卡头行：标签列定宽（各卡控件几何一致：开关/输入框/
        按钮的总长度与位置对齐），其后 [自动开关][ID 输入框(伸展)]
        [跳转/搜索按钮]。
        header=True 供折叠卡头部：ExExpander 头部自带左 16/右 60
        (chevron) 让位，控件右缘与普通卡的右边距 60 一致。"""
        row = QWidget()
        lay = QHBoxLayout(row)
        if header:
            lay.setContentsMargins(0, 12, 0, 12)
        else:
            lay.setContentsMargins(16, 8, 60, 8)
        lay.setSpacing(8)
        label = self.getrenameablellabel(key, name)
        font = label.font()
        font.setPixelSize(15)
        label.setFont(font)
        label.setFixedWidth(labelw)
        lay.addWidget(label)
        lay.addWidget(switch)
        lay.addWidget(edit, 1)
        for b in btns:
            lay.addWidget(b)
        return row

    def metadataorigin(self, formLayout: LFormLayout, gameuid):
        # 每源一张卡；有设置项（querysettingwindow）的源为折叠卡，
        # 设置内容放折叠里（原 CollapsibleBox + "设置"按钮移除）。
        # 标签列按全部源名计算定宽（名字可被用户改），各卡控件对齐。
        srcs = []
        for key in targetmod:
            try:
                srcs.append((key, targetmod[key].idname, targetmod[key].name))
            except:
                print_exc()
                continue
        font = self.font()
        font.setPixelSize(15)
        fm = QFontMetrics(font)
        labelw = min(240, max([80] + [fm.horizontalAdvance(_[2]) for _ in srcs]) + 16)

        for key, idname, name in srcs:
            try:
                vndbid = QLineEdit()
                vndbid.setText(str(savehook_new_data[gameuid].get(idname, "")))
                vndbid.setSizePolicy(
                    QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
                )

                vndbid.textEdited.connect(
                    functools.partial(savehook_new_data[gameuid].__setitem__, idname)
                )
                vndbid.returnPressed.connect(
                    functools.partial(gamdidchangedtask, key, idname, gameuid)
                )
                switch = getsimpleswitch(
                    globalconfig["metadata"][key],
                    "auto",
                )
                btns = [
                    getIconButton(
                        functools.partial(self.openrefmainpage, key, idname, gameuid),
                        icon="fa.chrome",
                    ),
                    getIconButton(
                        functools.partial(gamdidchangedtask, key, idname, gameuid),
                        icon="fa.search",
                    ),
                ]
            except:
                print_exc()
                continue
            try:
                __settting = targetmod[key].querysettingwindow
                has_setting = True
            except:
                has_setting = False
            row = self._metaheader(
                key, name, labelw, vndbid, switch, btns, header=has_setting
            )
            if has_setting:
                # 折叠卡：头部 = 同款行，设置表单放折叠里
                exp = ExExpander(content_pad=True)
                exp.setHeaderWidget(row)
                content = QWidget()
                clayout = QVBoxLayout(content)
                clayout.setContentsMargins(0, 0, 0, 0)
                try:
                    __settting(gameuid, clayout)
                except:
                    print_exc()
                    continue
                exp.addContentWidget(content)
                formLayout.addRow(exp)
            else:
                row.setAttribute(Qt.WA_StyledBackground, True)
                row.setProperty("isCard", True)
                row.setMinimumHeight(48)
                formLayout.addRow(row)

    def renameapi(self, qlabel: QLabel, apiuid):
        menu = QMenu(qlabel)
        useproxy = LAction("使用代理", menu)
        useproxy.setCheckable(True)

        menu.addAction(useproxy)
        useproxy.setChecked(globalconfig["metadata"][apiuid].get("useproxy", True))
        pos = QCursor.pos()
        action = menu.exec(pos)

        if action == useproxy:
            globalconfig["metadata"][apiuid]["useproxy"] = useproxy.isChecked()

    def getrenameablellabel(self, key, name):

        def checkclickable(name: ClickableLabel):
            name.setClickable(globalconfig.get("useproxy", True))

        name = ClickableLabel(name)
        fn = functools.partial(self.renameapi, name, key)
        name.clicked.connect(fn)
        name.beforeEnter.connect(functools.partial(checkclickable, name))
        return name

    def doaddtab(self, wfunct, exe, layout: QLayout):
        w, do = wfunct(exe)
        layout.addWidget(w)
        do()

    def selectexe_lauch(self, p):
        savehook_new_data[self.gameuid]["launchpath"] = p

        _icon = getExeIcon(get_launchpath(self.gameuid), cache=True)

        self.setWindowIcon(_icon)

    def starttab(self, formLayout: LFormLayout, gameuid):
        # 每项一张卡；启动方式为折叠卡，子项随方式切换（无设置时收起）。
        # 方式的每行设置经 _MethodRows 转为折叠卡的一个子项。
        tools = getgamecamptools(get_launchpath(gameuid))

        class _MethodRows:
            """launcher.setting(layout, config) 的 layout 适配：
            每行 addRow(标签, 控件) -> 折叠卡子项（同设置窗口
            ExExpander 的行式子项），不再走平铺表单。"""

            def __init__(self, expander):
                self._expander = expander

            def addRow(self, label, widget):
                row = QWidget()
                lay = QHBoxLayout(row)
                lay.setContentsMargins(0, 0, 0, 0)
                lay.addWidget(LLabel(label) if isinstance(label, str) else label)
                lay.addStretch(1)
                # 控件伸展：更长，且各行控件同宽对齐（setting() 可能传
                # QWidget 或 QLayout）
                if isinstance(widget, QLayout):
                    lay.addLayout(widget, 1)
                else:
                    lay.addWidget(widget, 1)
                self._expander.addContentWidget(row)

        __launch_method = getsimplecombobox(
            [_.name for _ in tools],
            savehook_new_data[gameuid],
            "launch_method",
            internal=[_.id for _ in tools],
        )
        self.lauchpath = getsimplepatheditor(
            get_launchpath(gameuid),
            callback=self.selectexe_lauch,
            icons=("fa.gear", "fa.undo"),
            clearset=lambda: uid2gamepath[gameuid],
        )
        # 路径（游戏本体路径；记忆列表按钮随标题行走）——与 启动程序 相邻成组
        formLayout.addRow(makecardrow(
            "路径",
            getsimplepatheditor(
                uid2gamepath[gameuid],
                callback=self.selectexe,
                clearable=False,
                icons=("fa.gear",),
            ),
            fill=True,
        ))
        exp = ExExpander(content_pad=True)
        rows = _MethodRows(exp)
        header = QWidget()
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(0, 12, 0, 12)
        hlay.setSpacing(8)
        titlelabel = LLabel("启动方式")
        titlefont = titlelabel.font()
        titlefont.setPixelSize(15)
        titlelabel.setFont(titlefont)
        hlay.addWidget(titlelabel)
        hlay.addStretch(1)
        hlay.addWidget(__launch_method)
        exp.setHeaderWidget(header)

        def __(idx):
            exp.clearContentWidgets()
            try:
                maycreatesettings(
                    rows,
                    savehook_new_data[gameuid],
                    tools[idx].id,
                )
            except:
                print_exc()
            # 当前方式无设置项（如 直接启动）时退化为普通卡；
            # 有设置为折叠卡。不触碰展开态：默认折叠（ExExpander 初始
            # 态），切换方式保留用户当前的展开/折叠
            exp.setFoldable(exp.hasContentWidgets())

        __launch_method.currentIndexChanged.connect(__)
        formLayout.addRow(makecardrow("启动程序", self.lauchpath, fill=True))
        formLayout.addRow(exp)
        # 语言（原独立 tab）：启动方式之下的跟随默认折叠卡
        self.getlangcard(formLayout, gameuid)
        formLayout.addRow(
            makecardrow(
                "自动切换到模式",
                getsimplecombobox(
                    ["不切换", "HOOK", "剪贴板", "OCR"],
                    savehook_new_data[gameuid],
                    "onloadautochangemode2",
                    default=0,
                ),
            )
        )
        __( __launch_method.currentIndex() )

    @tryprint
    def __refresh(self):
        _filename, _ = os.path.splitext(os.path.basename(uid2gamepath[self.gameuid]))
        sqlitef = gobject.getcachedir(
            "translation_record/{}_{}.sqlite".format(_filename, self.gameuid)
        )
        if not os.path.exists(sqlitef):
            return
        with sqlite3.connect(
            sqlitef, check_same_thread=False, isolation_level=None
        ) as sql:
            cnt = 0
            for (_,) in sql.execute("SELECT source FROM artificialtrans").fetchall():
                cnt += len(_)
            savehook_new_data[self.gameuid]["statistic_wordcount"] = max(
                cnt, savehook_new_data[self.gameuid].get("statistic_wordcount", 0)
            )

    def chartwidget_ctxmenu(self, refreshcallback, p):
        menu = QMenu(self)
        quanju = LAction("this" if self.__quanju_wc else "all", menu)
        menu.addAction(quanju)
        action = menu.exec(self.cursor().pos())
        if action == quanju:
            self.__quanju_wc = not self.__quanju_wc
            refreshcallback()

    def getstatistic(self, formLayout: QVBoxLayout, gameuid):

        chart = chartwidget(timechart=True)
        chart.xtext = lambda x: (
            "0" if x == 0 else str(datetime.fromtimestamp(x)).split(" ")[0]
        )
        chart.ytext = lambda y: self.formattime(y)

        chart2 = chartwidget(timechart=False)
        chart2.xtext = chart.xtext
        chart2.ytext = str
        self._timelabel = QLabel()
        self._timelabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self._wordlabel = QLabel()
        self._wordlabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self._wordlabel = QLabel()
        self._wordlabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        refreshcallback = functools.partial(self.refresh, chart, chart2, gameuid)
        stack = QStackedWidget()
        stack.addWidget(chart)
        stack.addWidget(chart2)
        stack.setCurrentIndex(1)
        stack.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        stack.customContextMenuRequested.connect(
            functools.partial(self.chartwidget_ctxmenu, refreshcallback)
        )
        wc = LPushButton("文字计数")
        tm = LPushButton("游戏时间")
        wc.setCheckable(True)
        tm.setCheckable(True)

        def clicktm(b):
            stack.setCurrentIndex(1 - b)
            globalconfig["statisticvistm"] = b
            wc.setChecked(not b)
            refreshcallback()

        def clickwc(b):
            stack.setCurrentIndex(b)
            globalconfig["statisticvistm"] = not b
            tm.setChecked(not b)
            refreshcallback()

        tm.toggled.connect(clicktm)
        wc.toggled.connect(clickwc)
        if globalconfig.get("statisticvistm", True):
            tm.setChecked(True)
        else:
            wc.setChecked(True)

        btn = IconButton(
            icon="fa.line-chart",
            parent=self,
            checkable=True,
            checkablechangecolor=False,
        )
        btn.setChecked(globalconfig.get("timecharttype", 0) == 0)
        btn.clicked.connect(
            lambda x: (
                globalconfig.__setitem__("timecharttype", 0 if x else 1),
                self.update(),
            )
        )
        formLayout.addLayout(
            getboxlayout(
                [
                    wc,
                    self._wordlabel,
                    "",
                    tm,
                    self._timelabel,
                    getIconButton(
                        icon="fa.edit", callback=functools.partial(timelistediter, self)
                    ),
                    getIconButton(self.__refresh, "fa.refresh"),
                    btn,
                ]
            )
        )
        formLayout.addWidget(stack)
        t = QTimer(self)
        t.setInterval(1000)
        t.timeout.connect(refreshcallback)
        t.timeout.emit()
        t.start()

    def split_range_into_days(
        self, times: "list[tuple[float, float]|tuple[float, float, str]]"
    ):
        everyday: "dict[date, int|dict[str, int]]" = {}
        for _ in times:
            if len(_) == 2:
                start, end = _
            elif len(_) == 3:
                start, end, gameuid = _
            if start == 0:
                everyday[0] = end
                continue

            start_date = datetime.fromtimestamp(start)
            end_date = datetime.fromtimestamp(end)

            current_date = start_date
            while current_date <= end_date:
                end_of_day = current_date.replace(
                    hour=23, minute=59, second=59, microsecond=0
                )
                end_of_day = end_of_day.timestamp() + 1

                if end_of_day >= end_date.timestamp():
                    useend = end_date.timestamp()
                else:
                    useend = end_of_day
                duration = useend - current_date.timestamp()
                today = end_of_day - 1
                if len(_) == 2:
                    everyday[today] = everyday.get(today, 0) + duration
                elif len(_) == 3:
                    if today not in everyday:
                        everyday[today] = {}
                    everyday[today][gameuid] = (
                        everyday[today].get(gameuid, 0) + duration
                    )
                current_date += timedelta(days=1)
                current_date = current_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
        lists: "list[tuple[float, int|dict[str, int]]]" = []
        for k in sorted(everyday.keys()):
            lists.append((k, everyday[k]))
        return lists

    def refresh(self, chart: chartwidget, chart2: chartwidget, gameuid):
        _gameuid = None if self.__quanju_wc else gameuid

        __ = gobject.base.somedatabase.querytraceplaytime(_gameuid)
        _cnt = sum([_[1] - _[0] for _ in __])
        self._timelabel.setText(self.formattime(_cnt))
        count = savehook_new_data[gameuid].get("statistic_wordcount", 0)
        self._wordlabel.setText(str(count) if _gameuid else "")
        chart.setdata(self.split_range_into_days(__))

        __ = gobject.base.somedatabase.querywordcount(_gameuid)
        chart2.setdata(self.wordcountbydate(__, count))

    def wordcountbydate(
        self, l: "list[tuple[float, int]|tuple[float, int, str]]", count: int
    ):
        daily_sum: "dict[date, int|dict[str, int]]" = {}
        cnt = 0
        for _ in l:
            if len(_) == 2:
                timestamp, value = _
                date = datetime.fromtimestamp(timestamp).date()
                daily_sum[date] = daily_sum.get(date, 0) + value
                cnt += value
            elif len(_) == 3:
                timestamp, value, gameuid = _
                date = datetime.fromtimestamp(timestamp).date()
                if date not in daily_sum:
                    daily_sum[date] = {}
                daily_sum[date][gameuid] = daily_sum[date].get(gameuid, 0) + value
                cnt += value
        lists: "list[tuple[float, int|dict[str, int]]]" = []
        if cnt < count:
            lists.append((0, count - cnt))
        for k in sorted(daily_sum.keys()):
            lists.append((datetime.combine(k, dttime.min).timestamp(), daily_sum[k]))
        return lists

    def formattime(self, t):
        t = int(t)
        s = t % 60
        t = t // 60
        m = t % 60
        t = t // 60
        h = t
        string = ""
        if h:
            string += str(h) + _TR("时")
        if m:
            string += str(m) + _TR("分")
        if s:
            string += str(s) + _TR("秒")
        if not string:
            string = "0"
        return string

        def safeaddtags(_):
            try:
                from gui.gamemanager.v3 import dialog_savedgame_v3

                dialog_savedgame_v3.reference.gridpage.tagswidget.addTag(*_)
            except:
                NativeUtils.ClipBoard.text = _[0]
                QToolTip.showText(QCursor.pos(), _TR("已复制到剪贴板"), self)

        qw.labelclicked.connect(safeaddtags)
        if first:
            self.flowwidget.insertWidget(self.labelflowmap[refkey], 1, qw)
        else:
            self.flowwidget.addWidget(self.labelflowmap[refkey], qw)

    def createfollowdefault(
        self,
        dic: dict,
        key: str,
        formLayout: LFormLayout,
        callback=None,
        klass=LFormLayout,
    ) -> LFormLayout:

        __extraw = QWidget()

        def __function(__extraw: QWidget, callback, _):
            __extraw.setEnabled(not _)
            if callback:
                try:
                    callback()
                except:
                    print_exc()

        formLayout.addRow(
            "跟随默认",
            getsimpleswitch(
                dic,
                key,
                callback=functools.partial(__function, __extraw, callback),
                default=True,
            ),
        )
        __extraw.setEnabled(not dic.get(key, True))
        formLayout.addRow(__extraw)
        formLayout2 = klass(__extraw)
        formLayout2.setContentsMargins(0, 0, 0, 0)
        return formLayout2

    def createfollowdefaultfold(self, dic: dict, key: str, callback=None,
                                title="跟随默认"):
        """跟随默认折叠卡：头部标题 + [跟随默认]开关（文字在开关旁），
        内容为各设置行子项（开关开启=跟随默认时内容禁用）。
        返回 (折叠卡, 内容网格)——调用方填充网格后 addRow 并 setExpanded。"""
        exp = ExExpander()
        header = QWidget()
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(0, 12, 0, 12)
        hlay.setSpacing(8)
        titlelabel = LLabel(title)
        titlefont = titlelabel.font()
        titlefont.setPixelSize(15)
        titlelabel.setFont(titlefont)
        hlay.addWidget(titlelabel)
        hlay.addStretch(1)
        content = QWidget()
        grid = VisGridLayout(content)
        grid.setContentsMargins(0, 0, 0, 0)

        def __function(content, callback, _):
            content.setEnabled(not _)
            if callback:
                try:
                    callback()
                except:
                    print_exc()

        hlay.addWidget(getsmalllabel("跟随默认")())
        hlay.addWidget(
            getsimpleswitch(
                dic,
                key,
                callback=functools.partial(__function, content, callback),
                default=True,
            )
        )
        exp.setHeaderWidget(header)
        exp.addContentWidget(content)
        content.setEnabled(not dic.get(key, True))
        return exp, grid

    def getttssetting(self, formLayout: LFormLayout, gameuid):
        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid],
            "tts_follow_default",
            formLayout,
            klass=QGridLayout,
        )

        def __delay1():
            if "tts_skip_regex" not in savehook_new_data[gameuid]:
                savehook_new_data[gameuid]["tts_skip_regex"] = []
            yuyinzhidingsetting(
                self,
                savehook_new_data[gameuid]["tts_skip_regex"],
                savehook_new_data[gameuid],
                "tts_skip_merge",
                False,
            )

        def __delay2():
            if "tts_repair_regex" not in savehook_new_data[gameuid]:
                savehook_new_data[gameuid]["tts_repair_regex"] = [
                    {"regex": True, "key": "(.*?)「", "value": ""}
                ]
            noundictconfigdialog1(
                self,
                savehook_new_data[gameuid]["tts_repair_regex"],
                "语音修正",
                ["原文", "替换"],
                extraX=savehook_new_data[gameuid],
                merged=savehook_new_data[gameuid],
                mergek="tts_repair_merge",
                mergedf=False,
            )

        automakegrid(
            formLayout2,
            [
                ["", "", "", ""],
                [
                    getsmalllabel("语音指定"),
                    D_getsimpleswitch(
                        savehook_new_data[gameuid],
                        "tts_skip",
                        default=globalconfig["ttscommon"]["tts_skip"],
                    ),
                    D_getIconButton(callback=__delay1),
                ],
                [
                    getsmalllabel("语音修正"),
                    D_getsimpleswitch(
                        savehook_new_data[gameuid],
                        "tts_repair",
                        default=globalconfig["ttscommon"]["tts_repair"],
                    ),
                    D_getIconButton(callback=__delay2),
                ],
            ],
        )

    def getmagpietab(self, formLayout: LFormLayout, gameuid):
        def __(x):
            clearlayout(internal)
            if x:
                MagpieConfig.remove(gameuid)
            else:
                # 取消跟随时创建的全部设置项包一张内容卡
                card = GroupCardWidget()
                hostlay = QVBoxLayout(card.contentWidget())
                hostlay.setContentsMargins(0, 0, 0, 0)
                makescrollgrid(
                    makescalew(MagpieConfig.find(gameuid, notexitscreate=True)),
                    hostlay,
                )
                internal.addWidget(card)

        internal = QGridLayout()
        internal.setContentsMargins(0, 0, 0, 0)
        btn = getsimpleswitch(
            {}, None, default=not MagpieConfig.find(gameuid), callback=__
        )
        _w = QWidget()
        btnline = LFormLayout(_w)
        btnline.setContentsMargins(0, 0, 0, 0)
        btnline.addRow("跟随默认", btn)
        formLayout.addRow(_w)
        formLayout.addRow(internal)
        if MagpieConfig.find(gameuid):
            __(False)

    def getpretranstab(self, formLayout: LFormLayout, gameuid):

        def selectimg(gameuid, key, res):
            savehook_new_data[gameuid][key] = res

        if "gamejsonfile" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["gamejsonfile"] = []
        if isinstance(savehook_new_data[gameuid]["gamejsonfile"], str):
            savehook_new_data[gameuid]["gamejsonfile"] = [
                savehook_new_data[gameuid]["gamejsonfile"]
            ]
        formLayout.addRow(
            "json翻译文件",
            listediterline(
                "json翻译文件",
                savehook_new_data[gameuid]["gamejsonfile"],
                ispathsedit=dict(filter1="*.json"),
                exec=True,
            ),
        )
        formLayout.addRow(
            "sqlite翻译记录",
            getsimplepatheditor(
                savehook_new_data[gameuid].get("gamesqlitefile", ""),
                False,
                False,
                "*.sqlite",
                functools.partial(selectimg, gameuid, "gamesqlitefile"),
                icons=("fa.folder-open", "fa.undo"),
            ),
        )

    def gettextproctab(self, formLayout: LFormLayout, gameuid):
        """文本处理 tab（原 文本处理/翻译优化 两 tab 合并）：各一张
        跟随默认折叠卡（头部右侧 跟随默认 + 开关，开启跟随时内容禁用），
        卡内为对应的树列表。"""
        # 文本预处理
        exp, grid = self.createfollowdefaultfold(
            savehook_new_data[gameuid],
            "textproc_follow_default",
            title="文本预处理",
        )
        tree = _GameTextProcTree(self, gameuid)
        tree.setMinimumHeight(120)
        self.__textproctree = tree
        grid.addWidget(wrap_setting_tree(tree), 0, 0)
        # 排序由树的移动按钮/拖拽承担，这里只留增删
        grid.addLayout(
            manybuttonlayout(
                [
                    ("添加行", self.__privatetextproc_btn1),
                    ("删除行", self.__privatetextproc_btn2),
                ]
            ),
            1, 0,
        )
        exp.setExpanded(True)
        formLayout.addRow(exp)
        # 翻译优化
        exp2, grid2 = self.createfollowdefaultfold(
            savehook_new_data[gameuid],
            "transoptimi_followdefault",
            title="翻译优化",
        )
        tree2 = _GameTransOptimiTree(self, gameuid)
        tree2.setMinimumHeight(120)
        grid2.addWidget(wrap_setting_tree(tree2), 0, 0)
        exp2.setExpanded(True)
        formLayout.addRow(exp2)

    def __privatetextproc_btn2(self):
        self.__textproctree.removecurrent()

    def __privatetextproc_btn1(self):

        __viss = []
        _internal = []
        for xx in postprocessconfig:
            if xx not in processfunctions:
                continue
            __list = self.__textproctree._rank()
            if xx in __list:
                continue
            __viss.append(postprocessconfig[xx]["name"])
            _internal.append(xx)

        def __callback(_internal, d):
            __ = _internal[d["k"]]
            self.__textproctree.addmethod(__)

        __d = {"k": 0}
        autoinitdialog(
            self,
            __d,
            "预处理方法",
            400,
            [
                {
                    "type": "combo",
                    "name": "预处理方法",
                    "k": "k",
                    "list": __viss,
                },
            ],
            exec_=True,
            callback=functools.partial(__callback, _internal, __d),
        )

    def getlangcard(self, formLayout: LFormLayout, gameuid):
        """语言（原独立 tab，并入 启动-启动方式 之下）：跟随默认折叠卡，
        源语言/目标语言各为一个子项（独立内容面板）。"""
        # content_pad：子项右缘与头部跟随默认开关右缘对齐
        exp = ExExpander(content_pad=True)
        header = QWidget()
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(0, 12, 0, 12)
        hlay.setSpacing(8)
        titlelabel = LLabel("语言")
        titlefont = titlelabel.font()
        titlefont.setPixelSize(15)
        titlelabel.setFont(titlefont)
        hlay.addWidget(titlelabel)
        hlay.addStretch(1)
        rows = []

        def __use(v):
            for r in rows:
                r.setEnabled(not v)

        hlay.addWidget(getsmalllabel("跟随默认")())
        hlay.addWidget(
            getsimpleswitch(
                savehook_new_data[gameuid],
                "lang_follow_default",
                callback=__use,
                default=True,
            )
        )
        exp.setHeaderWidget(header)

        def _langrow(label, key, langs, dflt):
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(LLabel(label))
            lay.addStretch(1)
            lay.addWidget(
                getsimplecombobox(
                    langs[0],
                    savehook_new_data[gameuid],
                    key,
                    internal=langs[1],
                    default=dflt,
                )
            )
            rows.append(row)
            exp.addContentWidget(row)

        _langrow("源语言", "private_srclang_2", all_langs(),
                 globalconfig.get("srclang4", "auto"))
        _langrow("目标语言", "private_tgtlang_2", all_langs(False),
                 globalconfig.get("tgtlang4", "zh"))
        __use(savehook_new_data[gameuid].get("lang_follow_default", True))
        formLayout.addRow(exp)

    def getembedtab(self, formLayout: LFormLayout, gameuid):

        # 跟随默认 → 折叠卡（各设置行为子项）
        exp, grid = self.createfollowdefaultfold(
            savehook_new_data[gameuid],
            "embed_follow_default",
            callback=lambda: gobject.base.textsource.set_settings_ex(),
            title="内嵌翻译",
        )
        automakegrid(
            grid,
            gethookgrid_em(savehook_new_data[gameuid]["embed_setting_private"]),
        )
        formLayout.addRow(exp)
        if savehook_new_data[gameuid].get("embedablehook"):
            formLayout.addRow(
                makecardrow(
                    "已激活的",
                    listediterline(
                        "已激活的",
                        savehook_new_data[gameuid]["embedablehook"],
                        specialklass=embeddisabler,
                    ),
                )
            )

    def gethooktab_internal(self, formLayout: LFormLayout, gameuid):

        __label = getsmalllabel("重新启动后生效")()
        __label.hide()
        formLayout.addRow(
            makecardrow(
                "延迟注入_(ms)",
                getspinbox(
                    0,
                    1000000,
                    savehook_new_data[gameuid],
                    "inserthooktimeout",
                    default=500,
                    callback=lambda _: __label.show(),
                ),
                __label,
            )
        )
        __label2 = getsmalllabel("重新启动后生效")()
        __label2.hide()
        formLayout.addRow(
            makecardrow(
                "Win32通用钩子",
                getsimpleswitch(
                    savehook_new_data[gameuid],
                    "insertpchooks_string",
                    callback=lambda _: (
                        (
                            gobject.base.textsource.InsertPCHooks()
                            if _
                            else __label2.show()
                        )
                    ),
                    default=False,
                ),
                __label2,
            )
        )
        if "needinserthookcode" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["needinserthookcode"] = []
        formLayout.addRow(
            makecardrow(
                "特殊码",
                listediterline(
                    "特殊码",
                    savehook_new_data[gameuid]["needinserthookcode"],
                ),
            )
        )
        if savehook_new_data[gameuid].get("removeforeverhook"):
            formLayout.addRow(
                makecardrow(
                    "移除且总是移除",
                    listediterline(
                        "移除且总是移除",
                        savehook_new_data[gameuid]["removeforeverhook"],
                        specialklass=embeddisabler,
                    ),
                )
            )

        # 跟随默认 → 折叠卡（各设置行为子项）
        exp, grid = self.createfollowdefaultfold(
            savehook_new_data[gameuid],
            "hooksetting_follow_default",
            callback=lambda: gobject.base.textsource.setsettings(),
            title="HOOK设置",
        )
        automakegrid(
            grid,
            gethookgrid(savehook_new_data[gameuid]["hooksetting_private"]),
        )
        formLayout.addRow(exp)

    def gethooktab(self, gameuid):
        # 滚动区内容控件必须同 makegrid 的 gridwidget 一样用 QSS 类做透明：
        # 否则会被设上 autofill，以 Window(243) 盖掉页面卡底色(249)
        # （见 makegrid/makescroll 的配套注释）
        class hookscrollcontent(QWidget):
            pass

        _w = hookscrollcontent()
        _w.setStyleSheet("hookscrollcontent{background-color:transparent;}")
        formLayout = LFormLayout(_w)
        formLayout.setContentsMargins(16, 16, 16, 12 )

        def __():
            self.gethooktab_internal(formLayout, gameuid)
            self.getembedtab(formLayout, gameuid)

        # 两个折叠卡全展开时内容过长——包滚动区
        scroll = makescroll()
        scroll.setWidget(_w)
        return scroll, __


@Singleton
class embeddisabler(LDialog):

    def __init__(
        self,
        parent,
        name,
        lst,
        closecallback=None,
        **_,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )
        self.lst: list = lst
        self.closecallback = closecallback

        self.setWindowTitle(name)
        model = QStandardItemModel()
        self.hcmodel = model
        table = LTableView()
        table.horizontalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setWordWrap(False)
        table.setModel(model)

        self.hctable = table
        formLayout = QVBoxLayout(self)
        formLayout.addWidget(self.hctable)
        for row, k in enumerate(lst):
            item = QStandardItem(str(k))
            self.hcmodel.insertRow(row, [item])
        btn = LPushButton("删除行")
        btn.clicked.connect(self.clicked2)
        formLayout.addWidget(btn)
        self.resize(600, self.sizeHint().height())
        self.show()
        self.changed = False

    def clicked2(self):
        idx = self.hctable.currentIndex()
        if not idx.isValid():
            return
        self.lst.pop(idx.row())
        self.hctable.model().removeRow(idx.row())
        self.changed = True

    def closeEvent(self, _):
        self.closecallback(self.changed)
