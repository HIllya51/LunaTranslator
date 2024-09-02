from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from qtsymbols import *
import os, functools, uuid
from datetime import datetime, timedelta
from traceback import print_exc
import gobject
from myutils.config import (
    savehook_new_data,
    uid2gamepath,
    get_launchpath,
    _TR,
    postprocessconfig,
    globalconfig,
    static_data,
)
from myutils.localetools import getgamecamptools, maycreatesettings
from myutils.hwnd import getExeIcon
from myutils.wrapper import Singleton, Singleton_close
from myutils.utils import (
    gamdidchangedtask,
    checkpostlangmatch,
    loadpostsettingwindowmethod_private,
    titlechangedtask,
    selectdebugfile,
    targetmod,
)
from gui.codeacceptdialog import codeacceptdialog
from gui.inputdialog import (
    noundictconfigdialog1,
    yuyinzhidingsetting,
    postconfigdialog2x,
    autoinitdialog,
    autoinitdialog_items,
    postconfigdialog,
)
from gui.specialwidget import ScrollFlow, chartwidget
from gui.usefulwidget import (
    TableViewW,
    saveposwindow,
    getsimplepatheditor,
    getboxlayout,
    auto_select_webview,
    Prompt_dialog,
    clearlayout,
    getsimplecombobox,
    getspinbox,
    getIconButton,
    makesubtab_lazy,
    getsimpleswitch,
    threebuttons,
    getspinbox,
    listediterline,
)
from gui.dynalang import (
    LFormLayout,
    LPushButton,
    LStandardItemModel,
    LAction,
    LLabel,
    LDialog,
)
from gui.dialog_savedgame_common import tagitem, TagWidget


@Singleton
class browserdialog(saveposwindow):
    seturlsignal = pyqtSignal(str)

    def startupsettitle(self, gameuid):

        if gameuid:
            title = savehook_new_data[gameuid]["title"]
        else:
            title = "LunaTranslator"
        self.setWindowTitle(title)

    def loadalllinks(self, gameuid):
        items = []
        if gameuid:
            self.setWindowTitle(savehook_new_data[gameuid]["title"])

        for link in globalconfig["relationlinks"]:
            items.append((link[0], tagitem.TYPE_GLOABL_LIKE, link[1]))
        if gameuid:
            for link in savehook_new_data[self.gameuid]["relationlinks"]:
                items.append((link[0], tagitem.TYPE_GAME_LIKE, link[1]))
        if len(items) == 0:
            items.append(
                (
                    "Luna",
                    tagitem.TYPE_GLOABL_LIKE,
                    static_data["main_server"][gobject.serverindex],
                )
            )
        self.tagswidget.clearTag(False)
        self.tagswidget.addTags(items)

    def startupnavi(self, gameuid):
        for idx in range(2, 100):
            if idx == 2:
                if gameuid:
                    if len(savehook_new_data[gameuid]["relationlinks"]):
                        navitarget = savehook_new_data[gameuid]["relationlinks"][-1][1]
                        break
            elif idx == 3:
                if len(globalconfig["relationlinks"]):
                    navitarget = globalconfig["relationlinks"][-1][1]
                    break
            else:
                navitarget = None
                break
        if navitarget:
            self.browser.navigate(navitarget)
            self.urlchanged(navitarget)

    def urlchanged(self, url):
        self.tagswidget.lineEdit.setCurrentText(url)
        self.current = url

    def likelink(self):
        _dia = Prompt_dialog(
            self,
            "收藏",
            "",
            [
                ["名称", ""],
                ["网址", self.current],
            ],
        )

        if _dia.exec():

            text = []
            for _t in _dia.text:
                text.append(_t.text())
            if self.gameuid:
                savehook_new_data[self.gameuid]["relationlinks"].append(text)
                self.tagswidget.addTag(text[0], tagitem.TYPE_GAME_LIKE, text[1])
            else:
                globalconfig["relationlinks"].append(text)
                self.tagswidget.addTag(text[0], tagitem.TYPE_GLOABL_LIKE, text[1])

    def tagschanged(self, tags):
        __ = []
        __2 = []
        for _name, _type, _url in tags:
            if _type == tagitem.TYPE_GLOABL_LIKE:
                __.append([_name, _url])
            elif _type == tagitem.TYPE_GAME_LIKE:
                __2.append([_name, _url])
        globalconfig["relationlinks"] = __
        if self.gameuid:
            savehook_new_data[self.gameuid]["relationlinks"] = __2

    def reinit(self, gameuid=None):

        self.gameuid = gameuid
        self.loadalllinks(gameuid)
        self.startupnavi(gameuid)
        self.startupsettitle(gameuid)

    def __init__(self, parent, gameuid=None) -> None:
        super().__init__(parent, poslist=globalconfig["browserwidget"])
        if gameuid:
            self.setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))
        self.browser = auto_select_webview(self)

        self.tagswidget = TagWidget(self)
        self.tagswidget.tagschanged.connect(self.tagschanged)

        self.tagswidget.tagclicked.connect(self.urlclicked)
        self.tagswidget.linepressedenter.connect(self.browser.navigate)
        self.browser.on_load.connect(self.urlchanged)

        hlay = QHBoxLayout()
        hlay.addWidget(self.tagswidget)

        hlay.addWidget(getIconButton(self.likelink, icon="fa.heart"))
        hlay.addWidget(
            getIconButton(
                lambda: self.urlclicked((None, None, self.current)), icon="fa.repeat"
            )
        )
        _topw = QWidget()
        _topw.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        _topw.setLayout(hlay)
        layout = QVBoxLayout()
        layout.setContentsMargins(*(0 for i in range(4)))
        hlay.setContentsMargins(*(0 for i in range(4)))
        layout.addWidget(_topw)
        layout.addWidget(self.browser)
        layout.setSpacing(0)
        __w = QWidget()
        __w.setLayout(layout)
        self.setCentralWidget(__w)

        self.reinit(gameuid)
        self.show()

    def urlclicked(self, _):
        tag, _, url = _
        if url[:4].lower() != "http":
            url = os.path.abspath(url)
        self.browser.navigate(url)

    def showmenu(self, p):
        tab_index = self.nettab.tabBar().tabAt(p)
        if (self.hasvndb and tab_index == 0) or tab_index == self.nettab.count() - 1:
            return
        menu = QMenu(self)
        shanchu = LAction(("删除"))
        menu.addAction(shanchu)
        action = menu.exec(self.mapToGlobal(p))
        if action == shanchu:
            self.nettab.setCurrentIndex(0)
            self.nettab.removeTab(tab_index)
            savehook_new_data[self.gameuid]["relationlinks"].pop(
                tab_index - self.hasvndb
            )


def maybehavebutton(self, gameuid, post):
    save_text_process_info = savehook_new_data[gameuid]["save_text_process_info"]
    if post == "_11":
        if "mypost" not in save_text_process_info:
            save_text_process_info["mypost"] = str(uuid.uuid4()).replace("-", "_")
        return getIconButton(
            callback=functools.partial(
                selectdebugfile,
                save_text_process_info["mypost"],
                ismypost=True,
            ),
            icon="fa.gear",
        )
    else:
        if post not in postprocessconfig:
            return
        if post == "_remove_chaos":
            return getIconButton(
                icon="fa.gear", callback=lambda: codeacceptdialog(self)
            )
        elif "args" in postprocessconfig[post]:
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
                    postprocessconfig[post]["name"],
                    600,
                    items,
                )
            return getIconButton(callback=callback, icon="fa.gear")
        else:
            return None


class dialog_setting_game_internal(QWidget):
    def selectexe(self, res):
        res = os.path.normpath(res)
        uid2gamepath[self.gameuid] = res
        _icon = getExeIcon(get_launchpath(self.gameuid), cache=True)

        self.setWindowIcon(_icon)

    def __init__(self, parent, gameuid) -> None:
        super().__init__(parent)
        vbox = QVBoxLayout(self)
        formLayout = LFormLayout()
        self.setLayout(vbox)
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
                        lambda: browserdialog(
                            gobject.baseobject.commonstylebase, gameuid
                        ),
                        icon="fa.book",
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
        )
        vbox.addLayout(formLayout)
        vbox.addWidget(methodtab)
        do()

    def ___tabf(self, function, gameuid):
        _w = QWidget()
        formLayout = LFormLayout()
        _w.setLayout(formLayout)
        do = functools.partial(function, formLayout, gameuid)
        return _w, do

    def ___tabf2(self, function, gameuid):
        _w = QWidget()
        formLayout = QVBoxLayout()
        _w.setLayout(formLayout)
        do = functools.partial(function, formLayout, gameuid)
        return _w, do

    def ___tabf3(self, function, gameuid):
        _w = QWidget()
        formLayout = QVBoxLayout()
        formLayout.setContentsMargins(0, 0, 0, 0)
        _w.setLayout(formLayout)
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
        )
        vbox.addWidget(methodtab)
        do()

    def makegamesettings(self, vbox: QVBoxLayout, gameuid):

        functs = [
            ("启动", functools.partial(self.___tabf, self.starttab)),
            ("HOOK", functools.partial(self.___tabf, self.gethooktab)),
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
        )

        self.methodtab = methodtab
        vbox.addWidget(methodtab)
        do()

    def openrefmainpage(self, key, idname, gameuid):
        try:
            gobject.baseobject.openlink(
                targetmod[key].refmainpage(savehook_new_data[gameuid][idname])
            )
        except:
            print_exc()

    def metadataorigin(self, formLayout: LFormLayout, gameuid):
        formLayout.addRow(
            "首选的",
            getsimplecombobox(
                list(targetmod.keys()),
                globalconfig,
                "primitivtemetaorigin",
                internal=list(targetmod.keys()),
                static=True,
            ),
        )
        formLayout.addRow(None, QLabel())
        for key in targetmod:
            try:
                idname = targetmod[key].idname

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
                    getsimpleswitch(globalconfig["metadata"][key], "auto"),
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
                _vbox_internal.insert(
                    2,
                    getIconButton(
                        functools.partial(__settting, self, gameuid), icon="fa.gear"
                    ),
                )
            except:
                pass
            formLayout.addRow(
                key,
                getboxlayout(_vbox_internal),
            )

    def doaddtab(self, wfunct, exe, layout):
        w, do = wfunct(exe)
        layout.addWidget(w)
        do()

    def selectexe_lauch(self, p):
        if p:
            p = os.path.normpath(p)
        savehook_new_data[self.gameuid]["launchpath"] = p

        _icon = getExeIcon(get_launchpath(self.gameuid), cache=True)

        self.setWindowIcon(_icon)

    def starttab(self, formLayout: LFormLayout, gameuid):
        box = QGroupBox()
        settinglayout = LFormLayout()
        box.setLayout(settinglayout)

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
        formLayout.addRow(
            "启动程序",
            getsimplepatheditor(
                get_launchpath(gameuid),
                callback=self.selectexe_lauch,
                icons=("fa.gear", "fa.refresh"),
                clearset=uid2gamepath[gameuid],
            ),
        )
        formLayout.addRow("启动方式", __launch_method)
        formLayout.addRow(box)

        formLayout.addRow(
            "自动切换到模式",
            getsimplecombobox(
                ["不切换", "HOOK", "剪贴板", "OCR"],
                savehook_new_data[gameuid],
                "onloadautochangemode2",
            ),
        )

        __launch_method.currentIndexChanged.emit(__launch_method.currentIndex())

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
        formLayout.addLayout(getboxlayout([LLabel(("文字计数")), self._wordlabel]))
        formLayout.addLayout(getboxlayout([LLabel(("游戏时间")), self._timelabel]))

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
        __ = gobject.baseobject.playtimemanager.querytraceplaytime_v4(self.gameuid)
        _cnt = sum([_[1] - _[0] for _ in __])
        savehook_new_data[self.gameuid]["statistic_playtime"] = _cnt
        self._timelabel.setText(self.formattime(_cnt))
        self._wordlabel.setText(
            str(savehook_new_data[self.gameuid]["statistic_wordcount"])
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

    def getlabelsetting(self, formLayout: QVBoxLayout, gameuid):
        self.labelflow = ScrollFlow()

        def newitem(text, refkey, first=False, _type=tagitem.TYPE_RAND):
            qw = tagitem(text, True, _type)

            def __(_qw, refkey, _):
                t, _type, _ = _
                try:
                    _qw.remove()
                    savehook_new_data[gameuid][refkey].remove(t)
                    self.labelflow.removewidget(_qw)
                except:
                    print_exc()

            qw.removesignal.connect(functools.partial(__, qw, refkey))

            def safeaddtags(_):
                try:
                    gobject.global_dialog_savedgame_new.tagswidget.addTag(*_)
                except:
                    pass

            qw.labelclicked.connect(safeaddtags)
            if first:
                self.labelflow.insertwidget(0, qw)
            else:
                self.labelflow.addwidget(qw)

        for tag in savehook_new_data[gameuid]["usertags"]:
            newitem(tag, "usertags", _type=tagitem.TYPE_USERTAG)
        for tag in savehook_new_data[gameuid]["developers"]:
            newitem(tag, "developers", _type=tagitem.TYPE_DEVELOPER)
        for tag in savehook_new_data[gameuid]["webtags"]:
            newitem(tag, "webtags", _type=tagitem.TYPE_TAG)
        formLayout.addWidget(self.labelflow)
        _dict = {"new": 0}

        formLayout.addWidget(self.labelflow)
        button = LPushButton("添加")

        combo = getsimplecombobox(globalconfig["labelset"], _dict, "new", static=True)
        combo.setEditable(True)
        combo.clearEditText()

        def _add(_):

            tag = combo.currentText()
            # tag = globalconfig["labelset"][_dict["new"]]
            if tag and tag not in savehook_new_data[gameuid]["usertags"]:
                savehook_new_data[gameuid]["usertags"].insert(0, tag)
                newitem(tag, True, True, _type=tagitem.TYPE_USERTAG)
            combo.clearEditText()

        button.clicked.connect(_add)

        formLayout.addLayout(
            getboxlayout(
                [
                    combo,
                    button,
                ]
            )
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
            ),
        )
        __extraw.setEnabled(not dic[key])
        formLayout.addRow(__extraw)
        formLayout2 = klass()
        formLayout2.setContentsMargins(0, 0, 0, 0)
        __extraw.setLayout(formLayout2)
        return formLayout2

    def getttssetting(self, formLayout: LFormLayout, gameuid):
        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid], "tts_follow_default", formLayout
        )
        if "tts_repair_use_at_translate" not in savehook_new_data[gameuid]:
            savehook_new_data[gameuid]["tts_repair_use_at_translate"] = globalconfig[
                "ttscommon"
            ]["tts_repair"]
        formLayout2.addRow(
            "语音指定",
            getboxlayout(
                [
                    getsimpleswitch(savehook_new_data[gameuid], "tts_skip"),
                    getIconButton(
                        callback=lambda: yuyinzhidingsetting(
                            self, savehook_new_data[gameuid]["tts_skip_regex"]
                        ),
                        icon="fa.gear",
                    ),
                    QLabel(),
                ],
                margin0=True,
                makewidget=True,
            ),
        )
        formLayout2.addRow(
            "语音修正",
            getboxlayout(
                [
                    getsimpleswitch(savehook_new_data[gameuid], "tts_repair"),
                    getIconButton(
                        callback=lambda: noundictconfigdialog1(
                            self,
                            savehook_new_data[gameuid]["tts_repair_regex"],
                            "语音修正",
                            ["正则", "转义", "原文", "替换"],
                        ),
                        icon="fa.gear",
                    ),
                    QLabel(),
                    getsimpleswitch(
                        savehook_new_data[gameuid], "tts_repair_use_at_translate"
                    ),
                    LLabel("作用于翻译"),
                ],
                margin0=True,
                makewidget=True,
            ),
        )

    def getpretranstab(self, formLayout: LFormLayout, gameuid):

        def selectimg(gameuid, key, res):
            savehook_new_data[gameuid][key] = res

        for showname, key, filt in [
            ("json翻译文件", "gamejsonfile", "*.json"),
        ]:
            if isinstance(savehook_new_data[gameuid][key], str):
                savehook_new_data[gameuid][key] = [savehook_new_data[gameuid][key]]
            formLayout.addRow(
                (showname),
                listediterline(
                    showname,
                    showname,
                    savehook_new_data[gameuid][key],
                    ispathsedit=dict(filter1=filt),
                ),
            )

        for showname, key, filt in [
            ("sqlite翻译记录", "gamesqlitefile", "*.sqlite"),
        ]:
            formLayout.addRow(
                showname,
                getsimplepatheditor(
                    savehook_new_data[gameuid][key],
                    False,
                    False,
                    filt,
                    functools.partial(selectimg, gameuid, key),
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
        vbox.addWidget(LLabel("继承默认"), 0, 4)
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
                    getsimpleswitch(savehook_new_data[gameuid], name + "_use"), i + 1, 1
                )
                vbox.addWidget(
                    getIconButton(
                        callback=functools.partial(__, setting, self, gameuid),
                        icon="fa.gear",
                    ),
                    i + 1,
                    2,
                )
                vbox.addWidget(QLabel(), i + 1, 3)
                vbox.addWidget(
                    getsimpleswitch(savehook_new_data[gameuid], name + "_merge"),
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

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        table.setModel(model)

        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.__privatetextproc_showmenu)
        self.__textprocinternaltable = table
        self.__textprocinternalmodel = model
        self.__privatetextproc_gameuid = gameuid
        for row, k in enumerate(
            savehook_new_data[gameuid]["save_text_process_info"]["rank"]
        ):  # 2
            self.__checkaddnewmethod(row, k)
        vbox.addWidget(table)
        buttons = threebuttons(texts=["添加行", "删除行", "上移", "下移"])
        buttons.btn1clicked.connect(self.__privatetextproc_btn1)
        buttons.btn2clicked.connect(self.removerows)
        buttons.btn3clicked.connect(
            functools.partial(self.__privatetextproc_moverank, -1)
        )
        buttons.btn4clicked.connect(
            functools.partial(self.__privatetextproc_moverank, 1)
        )
        vbox.addWidget(buttons)
        vbox.addWidget(buttons)

    def __privatetextproc_showmenu(self, p):
        r = self.__textprocinternaltable.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(self.__textprocinternaltable)
        remove = LAction(("删除"))
        up = LAction("上移")
        down = LAction("下移")
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
        self.__textprocinternalmodel.insertRow(
            row,
            [
                QStandardItem(postprocessconfig[_internal]["name"]),
                QStandardItem(),
                QStandardItem(),
            ],
        )
        __dict = savehook_new_data[self.__privatetextproc_gameuid][
            "save_text_process_info"
        ]["postprocessconfig"]
        if _internal not in __dict:
            __dict[_internal] = postprocessconfig[_internal]
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
            ("预处理方法"),
            400,
            [
                {
                    "type": "combo",
                    "name": ("预处理方法"),
                    "d": __d,
                    "k": "k",
                    "list": __viss,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(__callback, _internal, __d),
                },
            ],
        )

    def getlangtab(self, formLayout: LFormLayout, gameuid):

        savehook_new_data[gameuid]["private_tgtlang_2"] = savehook_new_data[
            gameuid
        ].get("private_tgtlang_2", globalconfig["tgtlang4"])
        savehook_new_data[gameuid]["private_srclang_2"] = savehook_new_data[
            gameuid
        ].get("private_srclang_2", globalconfig["srclang4"])

        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid], "lang_follow_default", formLayout
        )
        formLayout2.addRow(
            "源语言",
            getsimplecombobox(
                static_data["language_list_translator"],
                savehook_new_data[gameuid],
                "private_srclang_2",
                internal=static_data["language_list_translator_inner"],
            ),
        )
        formLayout2.addRow(
            "目标语言",
            getsimplecombobox(
                static_data["language_list_translator"],
                savehook_new_data[gameuid],
                "private_tgtlang_2",
                internal=static_data["language_list_translator_inner"],
            ),
        )

    def gethooktab(self, formLayout: LFormLayout, gameuid):

        formLayout.addRow(
            "延迟注入(ms)",
            getspinbox(0, 1000000, savehook_new_data[gameuid], "inserthooktimeout"),
        )

        formLayout.addRow(
            "特殊码",
            listediterline(
                ("特殊码"),
                ("特殊码"),
                savehook_new_data[gameuid]["needinserthookcode"],
            ),
        )

        for k in [
            "codepage_index",
            "direct_filterrepeat",
            "textthreaddelay",
            "maxBufferSize",
            "maxHistorySize",
            "filter_chaos_code",
        ]:
            if k not in savehook_new_data[gameuid]["hooksetting_private"]:
                savehook_new_data[gameuid]["hooksetting_private"][k] = globalconfig[k]

        formLayout2 = self.createfollowdefault(
            savehook_new_data[gameuid],
            "hooksetting_follow_default",
            formLayout,
            lambda: gobject.baseobject.textsource.setsettings(),
        )
        formLayout2.addRow(
            "代码页",
            getsimplecombobox(
                static_data["codepage_display"],
                savehook_new_data[gameuid]["hooksetting_private"],
                "codepage_index",
                lambda x: gobject.baseobject.textsource.setsettings(),
            ),
        )

        formLayout2.addRow(
            "刷新延迟(ms)",
            getspinbox(
                0,
                10000,
                savehook_new_data[gameuid]["hooksetting_private"],
                "textthreaddelay",
                callback=lambda x: gobject.baseobject.textsource.setsettings(),
            ),
        )
        formLayout2.addRow(
            "最大缓冲区长度",
            getspinbox(
                0,
                1000000,
                savehook_new_data[gameuid]["hooksetting_private"],
                "maxBufferSize",
                callback=lambda x: gobject.baseobject.textsource.setsettings(),
            ),
        )
        formLayout2.addRow(
            "最大缓存文本长度",
            getspinbox(
                0,
                1000000000,
                savehook_new_data[gameuid]["hooksetting_private"],
                "maxHistorySize",
                callback=lambda x: gobject.baseobject.textsource.setsettings(),
            ),
        )
        formLayout2.addRow(
            "过滤反复刷新的句子",
            getsimpleswitch(
                savehook_new_data[gameuid]["hooksetting_private"],
                "direct_filterrepeat",
                callback=lambda x: gobject.baseobject.textsource.setsettings(),
            ),
        )
        formLayout2.addRow(
            "过滤包含乱码的文本行",
            getsimpleswitch(
                savehook_new_data[gameuid]["hooksetting_private"],
                "filter_chaos_code",
            ),
        )


def calculate_centered_rect(original_rect: QRect, size: QSize) -> QRect:
    original_center = original_rect.center()
    new_left = original_center.x() - size.width() // 2
    new_top = original_center.y() - size.height() // 2
    new_rect = QRect(new_left, new_top, size.width(), size.height())
    return new_rect


@Singleton_close
class dialog_setting_game(LDialog):

    def __init__(self, parent, gameuid, setindexhook=0) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        gobject.global_dialog_setting_game = self

        self.setWindowTitle(savehook_new_data[gameuid]["title"])

        self.setWindowIcon(getExeIcon(get_launchpath(gameuid), cache=True))
        _ = dialog_setting_game_internal(self, gameuid)
        _.methodtab.setCurrentIndex(setindexhook)
        _.setMinimumSize(QSize(600, 500))
        l = QHBoxLayout(self)
        self.setLayout(l)
        l.addWidget(_)
        l.setContentsMargins(0, 0, 0, 0)
        self.show()
        try:
            self.setGeometry(
                calculate_centered_rect(
                    gobject.global_dialog_savedgame_new.parent().parent().geometry(),
                    self.size(),
                )
            )
        except:
            pass
