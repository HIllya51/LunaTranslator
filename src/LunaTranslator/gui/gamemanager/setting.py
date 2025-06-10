from qtsymbols import *
import functools, uuid, os
from datetime import datetime, timedelta
from traceback import print_exc
from language import TransLanguages
import gobject, NativeUtils
import copy
from myutils.post import processfunctions
from myutils.config import (
    savehook_new_data,
    uid2gamepath,
    get_launchpath,
    _TR,
    postprocessconfig,
    globalconfig,
    static_data,
)
from myutils.wrapper import tryprint
from myutils.utils import autosql
from gui.dialog_memory import dialog_memory
from myutils.localetools import getgamecamptools, maycreatesettings
from myutils.hwnd import getExeIcon
from myutils.wrapper import Singleton
from myutils.utils import (
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
    postconfigdialog2x,
    autoinitdialog,
    autoinitdialog_items,
    postconfigdialog,
)
from gui.specialwidget import chartwidget
from gui.usefulwidget import (
    TableViewW,
    automakegrid,
    D_getspinbox,
    FocusFontCombo,
    getsimpleswitch,
    getsimplepatheditor,
    getboxlayout,
    NQGroupBox,
    clearlayout,
    getcenterX,
    getsimplecombobox,
    D_getIconButton,
    D_getsimpleswitch,
    getspinbox,
    ClickableLabel,
    getIconButton,
    makesubtab_lazy,
    getsimpleswitch,
    manybuttonlayout,
    getspinbox,
    CollapsibleBox,
    getsmalllabel,
    listediterline,
    FocusCombo,
    VisGridLayout,
)
from gui.dynalang import (
    LFormLayout,
    LPushButton,
    LStandardItemModel,
    LAction,
    LLabel,
    LDialog,
    LGroupBox,
)
from gui.gamemanager.common import tagitem
from gui.inputdialog import postconfigdialog_


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
        )
    else:
        if post not in postprocessconfig:
            return
        if "args" in postprocessconfig[post]:
            if post == "stringreplace":
                callback = functools.partial(
                    postconfigdialog2x,
                    self,
                    save_text_process_info["postprocessconfig"][post]["args"][
                        "internal"
                    ],
                    save_text_process_info["postprocessconfig"][post]["name"],
                    ["正则", "转义", "原文内容", "替换为"],
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


class FlowWidget(QWidget):
    def __init__(self, parent=None, groups=3):
        super().__init__(parent)
        self.margin = QMargins(5, 5, 5, 5)
        self.spacing = 5
        self._item_list: "list[list[QWidget]]" = [[] for _ in range(groups)]

    def insertWidget(self, group: int, index, w: QWidget):
        w.setParent(self)
        w.show()
        self._item_list[group].insert(index, w)
        self.doresize()

    def addWidget(self, group, w: QWidget):
        self.insertWidget(group, len(self._item_list[group]), w)

    def removeWidget(self, w: QWidget):
        for _ in self._item_list:
            if w in _:
                _.remove(w)
                w.deleteLater()
                self.doresize()
                break

    def doresize(self):
        line_height = 0
        spacing = self.spacing
        y = self.margin.left()
        for listi in self._item_list:
            x = self.margin.top()
            for i, item in enumerate(listi):

                next_x = x + item.sizeHint().width() + spacing
                if (
                    next_x - spacing + self.margin.right() > self.width()
                    and line_height > 0
                ):
                    x = self.margin.top()
                    y = y + line_height + spacing
                    next_x = x + item.sizeHint().width() + spacing

                size = item.sizeHint()
                item.setGeometry(QRect(QPoint(x, y), size))
                line_height = max(line_height, size.height())
                x = next_x
            y = y + line_height + spacing
        self.setFixedHeight(y + self.margin.bottom() - spacing)

    def resizeEvent(self, a0):
        self.doresize()


def userlabelset(key="usertags"):
    s = set()
    for gameuid in savehook_new_data:
        s = s.union(savehook_new_data[gameuid][key])
    return sorted(list(s))


class dialog_setting_game_internal(QWidget):
    def selectexe(self, res):
        uid2gamepath[self.gameuid] = res
        _icon = getExeIcon(get_launchpath(self.gameuid), cache=True)

        self.setWindowIcon(_icon)
        if self.lauchpath:
            self.lauchpath.clear.clicked.emit()

    def __init__(self, parent, gameuid, keepindexobject=None) -> None:
        super().__init__(parent)
        self.keepindexobject = keepindexobject
        vbox = QVBoxLayout(self)
        self.lauchpath = None
        formLayout = LFormLayout()
        self.gameuid = gameuid
        formLayout.addRow(
            "路径",
            getboxlayout(
                [
                    getsimplepatheditor(
                        uid2gamepath[gameuid],
                        callback=self.selectexe,
                        clearable=False,
                        icons=("fa.gear",),
                    ),
                    getIconButton(
                        lambda: dialog_memory(self, gameuid=gameuid),
                        icon="fa.list-ul",
                    ),
                ]
            ),
        )
        titleedit = QLineEdit(savehook_new_data[gameuid]["title"])

        def _titlechange():
            x = titleedit.text()
            titlechangedtask(gameuid, x)
            self.setWindowTitle(x)

        titleedit.textEdited.connect(
            functools.partial(savehook_new_data[gameuid].__setitem__, "title")
        )
        titleedit.returnPressed.connect(_titlechange)

        formLayout.addRow(
            "标题",
            getboxlayout(
                [
                    titleedit,
                    getIconButton(_titlechange, icon="fa.search"),
                ]
            ),
        )

        functs = [
            ("游戏设置", functools.partial(self.___tabf3, self.makegamesettings)),
            ("游戏数据", functools.partial(self.___tabf3, self.makegamedata)),
        ]
        methodtab, do = makesubtab_lazy(
            [_[0] for _ in functs],
            [functools.partial(self.doaddtab, _[1], gameuid) for _ in functs],
            delay=True,
            initial=(
                (self.keepindexobject, "p1")
                if (self.keepindexobject is not None)
                else None
            ),
            fast=True,
        )
        vbox.addLayout(formLayout)
        vbox.addWidget(methodtab)
        do()

    def ___tabf(self, function, gameuid):
        _w = QWidget()
        formLayout = LFormLayout(_w)
        do = functools.partial(function, formLayout, gameuid)
        return _w, do

    def ___tabf2(self, function, gameuid):
        _w = QWidget()
        formLayout = QVBoxLayout(_w)
        do = functools.partial(function, formLayout, gameuid)
        return _w, do

    def ___tabf3(self, function, gameuid):
        _w = QWidget()
        formLayout = QVBoxLayout(_w)
        formLayout.setContentsMargins(0, 0, 0, 0)
        do = functools.partial(function, formLayout, gameuid)
        return _w, do

    def makegamedata(self, vbox: QVBoxLayout, gameuid):

        functs = [
            ("元数据", functools.partial(self.___tabf, self.metadataorigin)),
            ("统计", functools.partial(self.___tabf2, self.getstatistic)),
            ("标签", functools.partial(self.___tabf2, self.getlabelsetting)),
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
            ("语言", functools.partial(self.___tabf, self.getlangtab)),
            ("文本处理", functools.partial(self.___tabf, self.gettextproc)),
            ("翻译优化", functools.partial(self.___tabf, self.gettransoptimi)),
            ("语音", functools.partial(self.___tabf, self.getttssetting)),
            ("预翻译", functools.partial(self.___tabf, self.getpretranstab)),
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
        vbox.addWidget(methodtab)
        do()

    def openrefmainpage(self, key, idname, gameuid):
        try:
            os.startfile(targetmod[key].refmainpage(savehook_new_data[gameuid][idname]))
        except:
            print_exc()

    def metadataorigin(self, formLayout: LFormLayout, gameuid):
        vislf = VisGridLayout()
        formLayout.addRow(vislf)
        vislf.setColumnStretch(0, 0)
        vislf.setColumnStretch(1, 1)

        linei = 0
        notvislineis = []
        for i, key in enumerate(targetmod):
            try:
                idname = targetmod[key].idname
                name = targetmod[key].name

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
                _vbox_internal = [
                    getsimpleswitch(
                        globalconfig["metadata"][key],
                        "auto",
                    ),
                    vndbid,
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
                coll = CollapsibleBox(
                    functools.partial(__settting, gameuid), self, margin0=False
                )

                def _revert(c: CollapsibleBox, li):
                    vis = c.isVisible()
                    vislf.setRowVisible(li, not vis)
                    c.toggle(not vis)

                _vbox_internal.insert(
                    2,
                    getIconButton(functools.partial(_revert, coll, linei + 1)),
                )
                vislf.addWidget(self.getrenameablellabel(key, name), linei, 0)
                vislf.addLayout(getboxlayout(_vbox_internal), linei, 1)
                vislf.addWidget(coll, linei + 1, 0, 1, 2)
                notvislineis.append(linei + 1)
                linei += 2
            except:
                vislf.addWidget(self.getrenameablellabel(key, name), linei, 0)
                vislf.addLayout(getboxlayout(_vbox_internal), linei, 1)
                linei += 1
        for _ in notvislineis:
            vislf.setRowVisible(_, False)

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
            name.setClickable(globalconfig["useproxy"])

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
        box = NQGroupBox()
        settinglayout = LFormLayout(box)

        def __(box, layout, config, uid):
            clearlayout(layout)
            maycreatesettings(layout, config, uid)
            if layout.count() == 0:
                box.hide()
            else:
                box.show()

        __launch_method = getsimplecombobox(
            [_.name for _ in getgamecamptools(get_launchpath(gameuid))],
            savehook_new_data[gameuid],
            "launch_method",
            internal=[_.id for _ in getgamecamptools(get_launchpath(gameuid))],
            callback=functools.partial(
                __, box, settinglayout, savehook_new_data[gameuid]
            ),
        )
        self.lauchpath = getsimplepatheditor(
            get_launchpath(gameuid),
            callback=self.selectexe_lauch,
            icons=("fa.gear", "fa.refresh"),
            clearset=lambda: uid2gamepath[gameuid],
        )
        formLayout.addRow("启动程序", self.lauchpath)
        formLayout.addRow("启动方式", __launch_method)
        formLayout.addRow(box)

        formLayout.addRow(
            "自动切换到模式",
            getsimplecombobox(
                ["不切换", "HOOK", "剪贴板", "OCR"],
                savehook_new_data[gameuid],
                "onloadautochangemode2",
                default=0,
            ),
        )

        __launch_method.currentIndexChanged.emit(__launch_method.currentIndex())

    @tryprint
    def __refresh(self):
        _filename, _ = os.path.splitext(os.path.basename(uid2gamepath[self.gameuid]))
        sqlitef = gobject.gettranslationrecorddir(
            "{}_{}.sqlite".format(_filename, self.gameuid)
        )
        if not os.path.exists(sqlitef):
            return
        sql = autosql(sqlitef, check_same_thread=False, isolation_level=None)
        cnt = 0
        for (_,) in sql.execute("SELECT source FROM artificialtrans").fetchall():
            cnt += len(_)
        savehook_new_data[self.gameuid]["statistic_wordcount"] = max(
            cnt, savehook_new_data[self.gameuid]["statistic_wordcount"]
        )

    def getstatistic(self, formLayout: QVBoxLayout, gameuid):
        chart = chartwidget()
        chart.xtext = lambda x: (
            "0" if x == 0 else str(datetime.fromtimestamp(x)).split(" ")[0]
        )
        chart.ytext = lambda y: self.formattime(y, False)

        self.chart = chart
        self._timelabel = QLabel()
        self._wordlabel = QLabel()
        self._wordlabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self._timelabel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        formLayout.addLayout(
            getboxlayout(
                [
                    "文字计数",
                    getboxlayout(
                        [self._wordlabel, getIconButton(self.__refresh, "fa.refresh")]
                    ),
                ]
            )
        )

        t = QTimer(self)
        formLayout.addLayout(
            getboxlayout(
                [
                    "游戏时间",
                    self._timelabel,
                    getsmalllabel("严格的"),
                    getsimpleswitch(
                        globalconfig,
                        "is_tracetime_strict",
                        callback=lambda _: t.timeout.emit(),
                    ),
                ]
            )
        )

        formLayout.addWidget(chart)
        t = QTimer(self)
        t.setInterval(1000)
        t.timeout.connect(self.refresh)
        t.timeout.emit()
        t.start()

    def split_range_into_days(self, times):
        everyday = {}
        for start, end in times:
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
                if today not in everyday:
                    everyday[today] = 0
                everyday[today] += duration
                current_date += timedelta(days=1)
                current_date = current_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
        lists = []
        for k in sorted(everyday.keys()):
            lists.append((k, everyday[k]))
        return lists

    def refresh(self):
        __ = gobject.baseobject.playtimemanager.querytraceplaytime(self.gameuid)
        _cnt = sum([_[1] - _[0] for _ in __])
        self._timelabel.setText(self.formattime(_cnt))
        self._wordlabel.setText(
            str(savehook_new_data[self.gameuid].get("statistic_wordcount", 0))
        )
        self.chart.setdata(self.split_range_into_days(__))

    def formattime(self, t, usingnotstart=True):
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
        if string == "":
            if usingnotstart:
                string = _TR("未开始")
            else:
                string = "0"
        return string

    def tagenewitem(
        self,
        gameuid,
        text,
        refkey,
        first=False,
        _type=tagitem.TYPE_SEARCH,
    ):
        qw = tagitem(
            (
                globalconfig["tagNameRemap"].get(text, text)
                if _type == tagitem.TYPE_TAG
                else text
            ),
            True,
            _type,
        )

        def __(text, gameuid, _qw, refkey, _):
            try:
                savehook_new_data[gameuid][refkey].remove(text)
                self.flowwidget.removeWidget(_qw)
            except:
                print_exc()

        qw.removesignal.connect(functools.partial(__, text, gameuid, qw, refkey))

        def safeaddtags(_):
            try:
                gobject.global_dialog_savedgame_new.tagswidget.addTag(*_)
            except:
                NativeUtils.ClipBoard.text = _[0]
                QToolTip.showText(QCursor.pos(), _TR("已复制到剪贴板"), self)

        qw.labelclicked.connect(safeaddtags)
        if first:
            self.flowwidget.insertWidget(self.labelflowmap[refkey], 1, qw)
        else:
            self.flowwidget.addWidget(self.labelflowmap[refkey], qw)

    def getlabelsetting(self, formLayout: QVBoxLayout, gameuid):
        self.labelflowmap = {}
        flowwidget = FlowWidget(groups=4)
        tagitem.setstyles(flowwidget)
        self.flowwidget = flowwidget
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(flowwidget)
        formLayout.addWidget(scroll)
        self.tagtypes = ["developers", "webtags", "usertags"]
        self.tagtypes_zh = ["开发商", "标签", "自定义"]
        self.tagtypes_1 = [
            tagitem.TYPE_DEVELOPER,
            tagitem.TYPE_TAG,
            tagitem.TYPE_USERTAG,
        ]

        def createflows(label, key, _t, index):
            self.labelflowmap[key] = index
            flowwidget.addWidget(index, LLabel(label))
            for tag in savehook_new_data[gameuid][key]:
                self.tagenewitem(gameuid, tag, key, _type=_t)

        for i in range(len(self.tagtypes)):
            createflows(self.tagtypes_zh[i], self.tagtypes[i], self.tagtypes_1[i], i)

        button = LPushButton("添加")
        typecombo = getsimplecombobox(self.tagtypes_zh, default=2)
        combo = FocusCombo()
        combo.setEditable(True)
        self.fuckcombo = combo

        def closeEventFucker(origin, e):
            try:
                combo.setEditable(False)
            except:
                pass
            return origin(e)

        origin = self.window().closeEvent
        if not isqt5:
            self.window().closeEvent = functools.partial(closeEventFucker, origin)

        def __(idx):
            t = combo.currentText()
            combo.clear()
            combo.addItems(userlabelset(self.tagtypes[idx]))
            combo.setCurrentText(t)

        typecombo.currentIndexChanged.connect(__)
        __(2)

        def _add(_):
            tag = combo.currentText()
            tp = self.tagtypes[typecombo.currentIndex()]
            if (not tag) or (tag in savehook_new_data[gameuid][tp]):
                return
            savehook_new_data[gameuid][tp].insert(0, tag)
            self.tagenewitem(
                gameuid,
                tag,
                tp,
                first=True,
                _type=self.tagtypes_1[typecombo.currentIndex()],
            )
            combo.clearEditText()

        button.clicked.connect(_add)

        formLayout.addLayout(
            getboxlayout(
                [
                    combo,
                    typecombo,
                    button,
                    getIconButton(callback=self.edittagremap),
                ]
            )
        )

    def edittagremap(self):
        postconfigdialog_(
            self, globalconfig["tagNameRemap"], "标签映射", ["From", "To"]
        )

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
            yuyinzhidingsetting(self, savehook_new_data[gameuid]["tts_skip_regex"])

        def __delay2():
            if "tts_repair_regex" not in savehook_new_data[gameuid]:
                savehook_new_data[gameuid]["tts_repair_regex"] = [
                    {"regex": True, "key": "(.*?)「", "value": ""}
                ]
            noundictconfigdialog1(
                self,
                savehook_new_data[gameuid]["tts_repair_regex"],
                "语音修正",
                ["正则", "转义", "原文", "替换"],
                extraX=savehook_new_data[gameuid],
            )

        automakegrid(
            formLayout2,
            [
                ["", "", "", "", getcenterX("继承默认"), ""],
                [
                    getsmalllabel("语音指定"),
                    D_getsimpleswitch(
                        savehook_new_data[gameuid],
                        "tts_skip",
                        default=globalconfig["ttscommon"]["tts_skip"],
                    ),
                    D_getIconButton(callback=__delay1),
                    "",
                    getcenterX(
                        D_getsimpleswitch(
                            savehook_new_data[gameuid], "tts_skip_merge", default=False
                        ),
                    ),
                ],
                [
                    getsmalllabel("语音修正"),
                    D_getsimpleswitch(
                        savehook_new_data[gameuid],
                        "tts_repair",
                        default=globalconfig["ttscommon"]["tts_repair"],
                    ),
                    D_getIconButton(callback=__delay2),
                    "",
                    getcenterX(
                        D_getsimpleswitch(
                            savehook_new_data[gameuid],
                            "tts_repair_merge",
                            default=False,
                        )
                    ),
                ],
            ],
        )

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
                icons=("fa.folder-open", "fa.refresh"),
            ),
        )

    def gettransoptimi(self, formLayout: LFormLayout, gameuid):

        vbox: QGridLayout = self.createfollowdefault(
            savehook_new_data[gameuid],
            "transoptimi_followdefault",
            formLayout,
            klass=QGridLayout,
        )
        vbox.addLayout(getcenterX("继承默认")(), 0, 4)
        vbox.addWidget(QLabel(), 0, 5)

        for i, item in enumerate(static_data["transoptimi"]):
            name = item["name"]
            visname = item["visname"]
            if checkpostlangmatch(name):
                setting = loadpostsettingwindowmethod_private(name)
                if not setting:
                    continue

                def __(_f, _1, gameuid):
                    return _f(_1, gameuid)

                vbox.addWidget(LLabel(visname), i + 1, 0)
                vbox.addWidget(
                    getsimpleswitch(
                        savehook_new_data[gameuid],
                        name + "_use",
                        default=False,
                    ),
                    i + 1,
                    1,
                )
                vbox.addWidget(
                    getIconButton(
                        callback=functools.partial(__, setting, self, gameuid)
                    ),
                    i + 1,
                    2,
                )
                vbox.addWidget(QLabel(), i + 1, 3)
                vbox.addLayout(
                    getcenterX(
                        getsimpleswitch(
                            savehook_new_data[gameuid],
                            name + "_merge",
                            default=False,
                        )
                    )(),
                    i + 1,
                    4,
                )

    def gettextproc(self, formLayout: LFormLayout, gameuid):

        vbox = self.createfollowdefault(
            savehook_new_data[gameuid], "textproc_follow_default", formLayout
        )

        model = LStandardItemModel()
        model.setHorizontalHeaderLabels(["预处理方法", "使用", "设置"])

        table = TableViewW()

        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setWordWrap(False)

        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.__privatetextproc_showmenu)
        self.__textprocinternaltable = table
        self.__textprocinternalmodel = model
        self.__privatetextproc_gameuid = gameuid
        for row, k in enumerate(
            savehook_new_data[gameuid]["save_text_process_info"]["rank"]
        ):
            self.__checkaddnewmethod(row, k)
        vbox.addWidget(table)
        button = manybuttonlayout(
            [
                ("添加行", self.__privatetextproc_btn1),
                ("删除行", self.removerows),
                ("上移", functools.partial(self.__privatetextproc_moverank, -1)),
                ("下移", functools.partial(self.__privatetextproc_moverank, 1)),
            ]
        )
        vbox.addRow(button)

    def __privatetextproc_showmenu(self, p):
        r = self.__textprocinternaltable.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(self.__textprocinternaltable)
        remove = LAction("删除", menu)
        up = LAction("上移", menu)
        down = LAction("下移", menu)
        menu.addAction(remove)
        menu.addAction(up)
        menu.addAction(down)
        action = menu.exec(self.__textprocinternaltable.cursor().pos())

        if action == remove:
            self.__privatetextproc_btn2()
        elif action == up:
            self.__privatetextproc_moverank(-1)
        elif action == down:
            self.__privatetextproc_moverank(1)

    def __privatetextproc_moverank(self, dy):
        __row = self.__textprocinternaltable.currentIndex().row()

        __list = savehook_new_data[self.__privatetextproc_gameuid][
            "save_text_process_info"
        ]["rank"]
        game = __list[__row]
        idx1 = __list.index(game)
        idx2 = (idx1 + dy) % len(__list)
        __list.insert(idx2, __list.pop(idx1))
        self.__textprocinternalmodel.removeRow(idx1)
        self.__checkaddnewmethod(idx2, game)
        self.__textprocinternaltable.setCurrentIndex(
            self.__textprocinternalmodel.index(__row, 0)
        )

    def __checkaddnewmethod(self, row, _internal):
        if _internal not in postprocessconfig:
            return
        self.__textprocinternalmodel.insertRow(
            row,
            [
                QStandardItem(_TR(postprocessconfig[_internal]["name"])),
                QStandardItem(),
                QStandardItem(),
            ],
        )
        __dict = savehook_new_data[self.__privatetextproc_gameuid][
            "save_text_process_info"
        ]["postprocessconfig"]
        if _internal not in __dict:
            __dict[_internal] = copy.deepcopy(postprocessconfig[_internal])
            __dict[_internal]["use"] = True
        btn = maybehavebutton(self, self.__privatetextproc_gameuid, _internal)

        self.__textprocinternaltable.setIndexWidget(
            self.__textprocinternalmodel.index(row, 1),
            getsimpleswitch(__dict[_internal], "use"),
        )
        if btn:
            self.__textprocinternaltable.setIndexWidget(
                self.__textprocinternalmodel.index(row, 2),
                btn,
            )

    def removerows(self):

        skip = []
        for index in self.__textprocinternaltable.selectedIndexes():
            if index.row() in skip:
                continue
            skip.append(index.row())
        skip = reversed(sorted(skip))

        for row in skip:
            self.__textprocinternalmodel.removeRow(row)
            _dict = savehook_new_data[self.__privatetextproc_gameuid][
                "save_text_process_info"
            ]
            post = _dict["rank"][row]
            _dict["rank"].pop(row)
            if post in _dict["postprocessconfig"]:
                _dict["postprocessconfig"].pop(post)

    def __privatetextproc_btn2(self):
        row = self.__textprocinternaltable.currentIndex().row()
        if row < 0:
            return
        self.__textprocinternalmodel.removeRow(row)
        _dict = savehook_new_data[self.__privatetextproc_gameuid][
            "save_text_process_info"
        ]
        post = _dict["rank"][row]
        _dict["rank"].pop(row)
        if post in _dict["postprocessconfig"]:
            _dict["postprocessconfig"].pop(post)

    def __privatetextproc_btn1(self):

        __viss = []
        _internal = []
        for xx in postprocessconfig:
            if xx not in processfunctions:
                continue
            __list = savehook_new_data[self.__privatetextproc_gameuid][
                "save_text_process_info"
            ]["rank"]
            if xx in __list:
                continue
            __viss.append(postprocessconfig[xx]["name"])
            _internal.append(xx)

        def __callback(_internal, d):
            __ = _internal[d["k"]]
            __list.insert(0, __)
            self.__checkaddnewmethod(0, __)

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
                {
                    "type": "okcancel",
                    "callback": functools.partial(__callback, _internal, __d),
                },
            ],
            exec_=True,
        )

    def getlangtab(self, formLayout: LFormLayout, gameuid):

        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid], "lang_follow_default", formLayout
        )
        formLayout2.addRow(
            "源语言",
            getsimplecombobox(
                ["自动"] + [_.zhsname for _ in TransLanguages],
                savehook_new_data[gameuid],
                "private_srclang_2",
                internal=["auto"] + [_.code for _ in TransLanguages],
                default=globalconfig["srclang4"],
            ),
        )
        formLayout2.addRow(
            "目标语言",
            getsimplecombobox(
                [_.zhsname for _ in TransLanguages],
                savehook_new_data[gameuid],
                "private_tgtlang_2",
                internal=[_.code for _ in TransLanguages],
                default=globalconfig["tgtlang4"],
            ),
        )

    def getembedtab(self, formLayout: LFormLayout, gameuid):

        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid],
            "embed_follow_default",
            formLayout,
            callback=lambda: gobject.baseobject.textsource.flashembedsettings(),
        )
        formLayout2.addRow(
            "清除游戏内显示的文字",
            getsimpleswitch(
                savehook_new_data[gameuid]["embed_setting_private"],
                "clearText",
                default=globalconfig["embedded"]["clearText"],
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
            ),
        )

        formLayout2.addRow(
            "显示模式",
            getsimplecombobox(
                ["翻译", "原文_翻译", "翻译_原文"],
                savehook_new_data[gameuid]["embed_setting_private"],
                "displaymode",
                default=globalconfig["embedded"]["displaymode"],
                callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
            ),
        )
        formLayout2.addRow(
            "将汉字转换成繁体/日式汉字",
            getsimpleswitch(
                savehook_new_data[gameuid]["embed_setting_private"],
                "trans_kanji",
                default=globalconfig["embedded"]["trans_kanji"],
            ),
        )
        formLayout2.addRow(
            "限制每行字数",
            getboxlayout(
                [
                    D_getsimpleswitch(
                        savehook_new_data[gameuid]["embed_setting_private"],
                        "limittextlength_use",
                        default=globalconfig["embedded"]["limittextlength_use"],
                    ),
                    D_getspinbox(
                        0,
                        1000,
                        savehook_new_data[gameuid]["embed_setting_private"],
                        "limittextlength_length",
                        default=globalconfig["embedded"]["limittextlength_length"],
                    ),
                ]
            ),
        )
        formLayout2.addRow(
            "修改游戏字体",
            getboxlayout(
                [
                    D_getsimpleswitch(
                        savehook_new_data[gameuid]["embed_setting_private"],
                        "changefont",
                        default=globalconfig["embedded"]["changefont"],
                        callback=lambda _: gobject.baseobject.textsource.flashembedsettings(),
                    ),
                    functools.partial(self.creategamefont_comboBox, gameuid),
                ]
            ),
        )
        formLayout2.addRow(
            "内嵌安全性检查",
            getsimpleswitch(
                savehook_new_data[gameuid]["embed_setting_private"],
                "safecheck_use",
                default=globalconfig["embedded"]["safecheck_use"],
            ),
        )
        if savehook_new_data[gameuid].get("embedablehook"):
            box = NQGroupBox()
            settinglayout = LFormLayout(box)

            settinglayout.addRow(
                "已激活的",
                listediterline(
                    "已激活的",
                    savehook_new_data[gameuid]["embedablehook"],
                    specialklass=embeddisabler,
                ),
            )
            formLayout.addRow(box)

    def creategamefont_comboBox(self, gameuid):

        gamefont_comboBox = FocusFontCombo()

        def callback(x):
            savehook_new_data[gameuid]["embed_setting_private"].__setitem__(
                "changefont_font", x
            )
            try:
                gobject.baseobject.textsource.flashembedsettings()
            except:
                pass

        gamefont_comboBox.setCurrentFont(
            QFont(
                savehook_new_data[gameuid]["embed_setting_private"].get(
                    "changefont_font", globalconfig["embedded"]["changefont_font"]
                )
            )
        )
        gamefont_comboBox.currentTextChanged.connect(callback)
        return gamefont_comboBox

    def gethooktab_internal(self, formLayout: LFormLayout, gameuid):

        box = LGroupBox()
        box.setTitle("额外的钩子")
        settinglayout = LFormLayout(box)
        formLayout.addRow(box)
        settinglayout.addRow(
            "Win32通用钩子",
            getsimpleswitch(
                savehook_new_data[gameuid],
                "insertpchooks_string",
                callback=lambda _: (
                    (
                        gobject.baseobject.textsource.InsertPCHooks(0),
                        gobject.baseobject.textsource.InsertPCHooks(1),
                    )
                    if _
                    else None
                ),
                default=False,
            ),
        )
        if "needinserthookcode" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["needinserthookcode"] = []
        settinglayout.addRow(
            "特殊码",
            listediterline(
                "特殊码",
                savehook_new_data[gameuid]["needinserthookcode"],
            ),
        )
        box = NQGroupBox()
        settinglayout = LFormLayout(box)
        formLayout.addRow(box)

        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid],
            "hooksetting_follow_default",
            settinglayout,
            lambda: gobject.baseobject.textsource.setsettings(),
        )
        formLayout2.addRow(
            "代码页",
            getsimplecombobox(
                static_data["codepage_display"],
                savehook_new_data[gameuid]["hooksetting_private"],
                "codepage_value",
                lambda _: gobject.baseobject.textsource.setsettings(),
                default=globalconfig["codepage_value"],
                internal=static_data["codepage_real"],
            ),
        )

        formLayout2.addRow(
            "刷新延迟_(ms)",
            getspinbox(
                0,
                10000,
                savehook_new_data[gameuid]["hooksetting_private"],
                "textthreaddelay",
                callback=lambda _: gobject.baseobject.textsource.setsettings(),
                default=globalconfig["textthreaddelay"],
            ),
        )
        formLayout2.addRow(
            "最大缓冲区长度",
            getspinbox(
                0,
                1000000,
                savehook_new_data[gameuid]["hooksetting_private"],
                "maxBufferSize",
                callback=lambda _: gobject.baseobject.textsource.setsettings(),
                default=globalconfig["maxBufferSize"],
            ),
        )
        formLayout2.addRow(
            "最大缓存文本长度",
            getspinbox(
                0,
                1000000000,
                savehook_new_data[gameuid]["hooksetting_private"],
                "maxHistorySize",
                callback=lambda _: gobject.baseobject.textsource.setsettings(),
                default=globalconfig["maxHistorySize"],
            ),
        )
        formLayout2.addRow(
            "延迟注入_(ms)",
            getspinbox(
                0, 1000000, savehook_new_data[gameuid], "inserthooktimeout", default=500
            ),
        )
        if savehook_new_data[gameuid].get("removeforeverhook"):
            box = NQGroupBox()
            settinglayout = LFormLayout(box)

            settinglayout.addRow(
                "移除且总是移除",
                listediterline(
                    "移除且总是移除",
                    savehook_new_data[gameuid]["removeforeverhook"],
                    specialklass=embeddisabler,
                ),
            )
            formLayout.addRow(box)

    def gethooktab(self, gameuid):
        _w = QWidget()
        formLayout = QVBoxLayout(_w)
        formLayout.setContentsMargins(0, 0, 0, 0)
        functs = [
            ("HOOK设置", functools.partial(self.___tabf, self.gethooktab_internal)),
            ("内嵌翻译", functools.partial(self.___tabf, self.getembedtab)),
        ]
        methodtab, do = makesubtab_lazy(
            [_[0] for _ in functs],
            [functools.partial(self.doaddtab, _[1], gameuid) for _ in functs],
            delay=True,
            initial=(
                (self.keepindexobject, "gamesettinghook")
                if (self.keepindexobject is not None)
                else None
            ),
        )
        formLayout.addWidget(methodtab)
        return _w, do


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
        table = QTableView()
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


@Singleton
class dialog_setting_game(QDialog):

    def __init__(self, parent, gameuid, setindexhook=0) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        gobject.global_dialog_setting_game = self

        self.setWindowTitle(savehook_new_data[gameuid]["title"])

        self.setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))
        _ = dialog_setting_game_internal(
            self, gameuid, keepindexobject={"gamesetting": setindexhook}
        )
        _.setMinimumWidth(600)
        l = QHBoxLayout(self)
        l.addWidget(_)
        l.setContentsMargins(0, 0, 0, 0)
        self.show()
