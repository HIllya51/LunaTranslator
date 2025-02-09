from qtsymbols import *
import functools, winsharedutils
import gobject, os
from myutils.config import globalconfig, static_data, _TR
from myutils.wrapper import tryprint
from myutils.utils import translate_exits, getannotatedapiname
from gui.usefulwidget import (
    getsimplecombobox,
    Singleton_close,
    saveposwindow,
    D_getspinbox,
    D_getIconButton,
    clearlayout,
    getboxlayout,
    D_getcolorbutton,
    getcolorbutton,
    saveposwindow,
    getIconButton,
    getsimpleswitch,
    D_getsimpleswitch,
    TableViewW,
    selectcolor,
    listediter,
    FocusFontCombo,
    SuperCombo,
    getspinbox,
    getsmalllabel,
    SplitLine,
    WebviewWidget,
    ExtensionSetting,
)
from gui.dynalang import LPushButton, LFormLayout, LDialog, LStandardItemModel, LAction


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    gobject.baseobject.translation_ui.translate_text.showhideorigin(x)
    try:
        self.fenyinsettings.setEnabled(x)
    except:
        pass


def changeshowerrorstate(self, x):
    gobject.baseobject.translation_ui.translate_text.showhideerror(x)


def mayberealtimesetfont(_=None):
    gobject.baseobject.translation_ui.translate_text.setfontstyle()


def createtextfontcom(key):
    def _f(key, x):
        globalconfig[key] = x
        mayberealtimesetfont()

    font_comboBox = FocusFontCombo()
    font_comboBox.currentTextChanged.connect(functools.partial(_f, key))
    font_comboBox.setCurrentFont(QFont(globalconfig[key]))
    return font_comboBox


@Singleton_close
class extrahtml(saveposwindow):
    def tryload(self):

        use = gobject.getuserconfigdir(self.fn)
        if os.path.exists(use) == False:
            use = self.fneg
        with open(use, "r", encoding="utf8") as ff:
            self.vistext.setPlainText(ff.read())

    @tryprint
    def applyhtml(self, _):
        self.tester.loadex(self.vistext.toPlainText())

    def savehtml(self):
        with open(gobject.getuserconfigdir(self.fn), "w", encoding="utf8") as ff:
            ff.write(self.vistext.toPlainText())

    def __init__(self, parent, fn, fneg, tester) -> None:
        super().__init__(parent, poslist=globalconfig["geo_extrahtml"])
        self.setWindowTitle("附加HTML")
        self.tester = tester
        self.fneg = fneg
        self.fn = fn
        self.btn_save = LPushButton("保存")
        self.btn_save.clicked.connect(self.savehtml)
        self.btn_apply = LPushButton("测试")
        self.btn_apply.clicked.connect(self.applyhtml)
        self.vistext = QPlainTextEdit()
        w = QWidget()
        lay = QVBoxLayout(w)
        hl = QHBoxLayout()
        hl.addWidget(self.btn_save)
        hl.addWidget(self.btn_apply)
        lay.addWidget(self.vistext)
        lay.addLayout(hl)
        self.setCentralWidget(w)
        self.tryload()
        self.show()


def createinternalfontsettings(self, forml: LFormLayout, group, _type):
    need = globalconfig["rendertext_using_internal"][group] != _type
    globalconfig["rendertext_using_internal"][group] = _type
    if need:
        gobject.baseobject.translation_ui.translate_text.resetstyle()
    __internal = globalconfig["rendertext"][group][_type]
    dd = __internal.get("args", {})

    clearlayout(forml)

    for key in dd:
        line = __internal["argstype"][key]
        name = line["name"]
        _type = line["type"]
        if key in ["width", "shadowR_ex"]:
            if key == "width":
                keyx = "width_rate"
            elif key == "shadowR_ex":
                keyx = "shadowR"
            widthline = __internal["argstype"].get(keyx, None)
            if widthline is not None:
                __ = getsmalllabel("x_字体大小_+")()
                forml.addRow(
                    name,
                    getboxlayout(
                        [
                            getspinbox(
                                widthline.get("min", 0),
                                widthline.get("max", 100),
                                dd,
                                keyx,
                                True,
                                widthline.get("step", 0.1),
                                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                            ),
                            __,
                            getspinbox(
                                line.get("min", 0),
                                line.get("max", 100),
                                dd,
                                key,
                                True,
                                line.get("step", 0.1),
                                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                            ),
                        ]
                    ),
                )
                continue
        elif key in ["width_rate", "shadowR"]:
            continue
        if _type == "colorselect":
            lineW = getcolorbutton(
                dd,
                key,
                callback=functools.partial(
                    lambda dd, key: selectcolor(
                        self,
                        dd,
                        key,
                        self.miaobian_color_button,
                        callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                    ),
                    dd,
                    key,
                ),
                name="miaobian_color_button",
                parent=self,
            )
        elif _type in ["spin", "intspin"]:
            lineW = getspinbox(
                line.get("min", 0),
                line.get("max", 100),
                dd,
                key,
                _type == "spin",
                line.get("step", 0.1),
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
            )
        elif _type == "switch":
            lineW = getsimpleswitch(
                d=dd,
                key=key,
                callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
            )

        forml.addRow(
            name,
            lineW,
        )


def alertwhenrestart(self, x):
    QMessageBox.information(
        self,
        _TR("注意"),
        _TR("将在重新启动后生效！"),
    )
    try:
        self.fuckshit__1.setChecked(x)
    except:
        pass
    try:
        self.fuckshit__2.setChecked(x)
    except:
        pass


@Singleton_close
class Exteditor(LDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("浏览器插件")
        self.resize(QSize(600, 400))

        model = LStandardItemModel()
        model.setHorizontalHeaderLabels(["移除", "", "名称", "禁用", "设置"])

        table = TableViewW()

        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.__menu)
        vbox = QVBoxLayout(self)
        vbox.addWidget(table)
        btn = LPushButton("添加")
        btn.clicked.connect(functools.partial(self.tryMessage, self.Addext))
        vbox.addWidget(btn)
        self.show()
        self.model = model
        self.table = table
        self.tryMessage(self.listexts)

    def Addext(self, *_):
        chromes = os.path.join(
            os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Default\Extensions"
        )
        edges = os.path.join(
            os.environ["LOCALAPPDATA"], r"Microsoft\Edge\User Data\Default\Extensions"
        )
        if os.path.exists(edges):
            edgeslen = len(os.listdir(edges))
        else:
            edgeslen = 0
        if os.path.exists(chromes):
            chromelen = len(os.listdir(chromes))
        else:
            chromelen = 0
        if chromelen > edgeslen:
            path = chromes
        elif edgeslen > 0:
            path = edges
        else:
            path = ""
        res = QFileDialog.getExistingDirectory(
            self, None, path, options=QFileDialog.Option.DontResolveSymlinks
        )
        if not res:
            return

        WebviewWidget.Extensions_Add(res)
        self.listexts()

    def __menu(self, _):
        curr = self.table.currentIndex()
        if not curr.isValid():
            return
        if curr.column() != 2:
            return
        menu = QMenu(self.table)
        copyid = LAction("复制_ID", menu)

        menu.addAction(copyid)
        action = menu.exec(self.table.cursor().pos())

        if action == copyid:
            winsharedutils.clipboard_set(
                self.table.model().data(curr, Qt.ItemDataRole.UserRole + 10)
            )

    def listexts(self):
        self.model.removeRows(0, self.model.rowCount())
        for _i, (_id, name, able) in enumerate(WebviewWidget.Extensions_List()):

            _i = self.model.rowCount()
            item = QStandardItem(name)
            item.setData(_id, Qt.ItemDataRole.UserRole + 10)
            self.model.appendRow(
                [
                    QStandardItem(""),
                    QStandardItem(""),
                    item,
                    QStandardItem(""),
                    QStandardItem(""),
                ]
            )
            d = {"1": able}
            self.table.setIndexWidget(
                self.model.index(_i, 3),
                getsimpleswitch(
                    d,
                    "1",
                    callback=functools.partial(
                        self.tryMessage, self.enablex, _id, not able
                    ),
                ),
            )
            self.table.setIndexWidget(
                self.model.index(_i, 0),
                getIconButton(
                    callback=functools.partial(self.tryMessage, self.removex, _id),
                    icon="fa.times",
                ),
            )
            t = QTimer(self)
            t.setInterval(1000)
            t.timeout.connect(
                functools.partial(
                    self.checkinfo,
                    _id,
                    self.model.index(_i, 1),
                    self.model.index(_i, 3),
                    self.model.index(_i, 4),
                    name,
                    t,
                )
            )
            t.start(0)

    def checkinfo(
        self, _id, i1: QModelIndex, i3: QModelIndex, i4: QModelIndex, name, t: QTimer
    ):
        if not (i1.isValid() and i4.isValid()):
            return t.stop()
        info = WebviewWidget.Extensions_Manifest_Info(_id)
        if info is None:
            return
        setting = info.get("url")
        if setting:
            self.table.setIndexWidget(
                i4,
                getIconButton(
                    callback=functools.partial(
                        ExtensionSetting, name, setting, info.get("icon")
                    ),
                    enable=self.table.indexWidgetX(i3).isChecked(),
                ),
            )
        icon = info.get("icon")
        if icon:
            self.table.setIndexWidget(
                i1,
                getIconButton(
                    qicon=QIcon(icon),
                    callback=functools.partial(os.startfile, info["path"]),
                    enable=self.table.indexWidgetX(i3).isChecked(),
                ),
            )
        t.stop()

    def enablex(self, _id, able, _):
        WebviewWidget.Extensions_Enable(_id, able)
        self.listexts()

    def removex(self, _id):
        WebviewWidget.Extensions_Remove(_id)
        self.listexts()

    def tryMessage(self, func, *args):
        try:
            func(*args)
        except Exception as e:
            QMessageBox.critical(self, _TR("错误"), str(e))


def resetgroudswitchcallback(self, group):
    clearlayout(self.goodfontsettingsformlayout)

    goodfontgroupswitch = SuperCombo()
    if group == "webview":
        _btn = getIconButton(
            callback=functools.partial(
                extrahtml,
                self,
                "extrahtml.html",
                r"LunaTranslator\rendertext\exampleextrahtml.html",
                gobject.baseobject.translation_ui.translate_text.textbrowser,
            ),
            icon="fa.edit",
        )
        switch = getsimpleswitch(
            globalconfig,
            "useextrahtml",
            callback=lambda x: gobject.baseobject.translation_ui.translate_text.textbrowser.loadex(),
        )
        _btn2 = getIconButton(callback=functools.partial(Exteditor, self))
        switch2 = getsimpleswitch(
            globalconfig, "webviewLoadExt", callback=lambda x: alertwhenrestart(self, x)
        )
        self.fuckshit__2 = switch2
        self.goodfontsettingsformlayout.addRow(
            getboxlayout(
                ["附加HTML", switch, _btn, "", "附加浏览器插件", switch2, _btn2, ""]
            ),
        )
        self.goodfontsettingsformlayout.addRow(SplitLine())

    __form = LFormLayout()
    __form.addRow("字体样式", goodfontgroupswitch)
    self.goodfontsettingsformlayout.addRow(__form)
    forml = LFormLayout()
    __form.addRow(forml)

    goodfontgroupswitch.addItems(
        [
            globalconfig["rendertext"][group][x]["name"]
            for x in static_data["textrender"][group]
        ]
    )
    goodfontgroupswitch.currentIndexChanged.connect(
        lambda idx: createinternalfontsettings(
            self, forml, group, static_data["textrender"][group][idx]
        )
    )
    goodfontgroupswitch.setCurrentIndex(
        static_data["textrender"][group].index(
            globalconfig["rendertext_using_internal"][group]
        )
    )
    gobject.baseobject.translation_ui.translate_text.loadinternal(shoudong=True)
    visengine_internal = ["textbrowser", "webview"]
    self.seletengeinecombo.setCurrentIndex(
        visengine_internal.index(globalconfig["rendertext_using"])
    )


def creategoodfontwid(self):

    self.goodfontsettingsWidget = QGroupBox()
    self.goodfontsettingsWidget.setStyleSheet(
        "QGroupBox{ margin-top:0px;} QGroupBox:title {margin-top: 0px;}"
    )
    self.goodfontsettingsformlayout = LFormLayout(self.goodfontsettingsWidget)
    resetgroudswitchcallback(self, globalconfig["rendertext_using"])
    return self.goodfontsettingsWidget


def _createseletengeinecombo(self):

    self.seletengeinecombo = getsimplecombobox(
        ["Qt", "Webview2"],
        globalconfig,
        "rendertext_using",
        internal=["textbrowser", "webview"],
        callback=functools.partial(resetgroudswitchcallback, self),
        static=True,
    )
    return self.seletengeinecombo


def vistranslate_rank(self):
    _not = []
    for i, k in enumerate(globalconfig["fix_translate_rank_rank"]):
        if not translate_exits(k):
            _not.append(i)
    for _ in reversed(_not):
        globalconfig["fix_translate_rank_rank"].pop(_)
    listediter(
        self,
        "显示顺序",
        globalconfig["fix_translate_rank_rank"],
        isrankeditor=True,
        namemapfunction=lambda k: _TR(getannotatedapiname(k)),
    )


def xianshigrid_style(self):
    textgrid = [
        [
            (
                dict(
                    title="字体",
                    type="grid",
                    grid=(
                        [
                            (
                                dict(
                                    title="原文",
                                    type="grid",
                                    grid=(
                                        [
                                            "字体",
                                            (
                                                functools.partial(
                                                    createtextfontcom, "fonttype"
                                                ),
                                                0,
                                            ),
                                            "",
                                            "字体大小",
                                            D_getspinbox(
                                                5,
                                                100,
                                                globalconfig,
                                                "fontsizeori",
                                                double=True,
                                                step=0.1,
                                                callback=mayberealtimesetfont,
                                            ),
                                        ],
                                        [
                                            "行间距",
                                            D_getspinbox(
                                                -100,
                                                100,
                                                globalconfig,
                                                "extra_space",
                                                callback=mayberealtimesetfont,
                                            ),
                                            "",
                                            "加粗",
                                            D_getsimpleswitch(
                                                globalconfig,
                                                "showbold",
                                                callback=mayberealtimesetfont,
                                            ),
                                            "",
                                            "颜色",
                                            D_getcolorbutton(
                                                globalconfig,
                                                "rawtextcolor",
                                                callback=lambda: selectcolor(
                                                    self,
                                                    globalconfig,
                                                    "rawtextcolor",
                                                    self.original_color_button,
                                                    callback=gobject.baseobject.translation_ui.translate_text.setcolorstyle,
                                                ),
                                                name="original_color_button",
                                                parent=self,
                                            ),
                                        ],
                                    ),
                                ),
                                0,
                                "group",
                            )
                        ],
                        [
                            (
                                dict(
                                    title="译文",
                                    type="grid",
                                    grid=(
                                        [
                                            "字体",
                                            (
                                                functools.partial(
                                                    createtextfontcom, "fonttype2"
                                                ),
                                                0,
                                            ),
                                            "",
                                            "字体大小",
                                            D_getspinbox(
                                                1,
                                                100,
                                                globalconfig,
                                                "fontsize",
                                                double=True,
                                                step=0.1,
                                                callback=mayberealtimesetfont,
                                            ),
                                        ],
                                        [
                                            "行间距",
                                            D_getspinbox(
                                                -100,
                                                100,
                                                globalconfig,
                                                "extra_space_trans",
                                                callback=mayberealtimesetfont,
                                            ),
                                            "",
                                            "加粗",
                                            D_getsimpleswitch(
                                                globalconfig,
                                                "showbold_trans",
                                                callback=mayberealtimesetfont,
                                            ),
                                            "",
                                            "",
                                            "",
                                        ],
                                    ),
                                ),
                                0,
                                "group",
                            )
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="内容",
                    type="grid",
                    grid=(
                        [
                            "居中显示",
                            D_getsimpleswitch(
                                globalconfig,
                                "showatcenter",
                                callback=gobject.baseobject.translation_ui.translate_text.showatcenter,
                            ),
                            "",
                            "收到翻译时才刷新",
                            D_getsimpleswitch(globalconfig, "refresh_on_get_trans"),
                            "",
                            "固定翻译显示顺序",
                            D_getsimpleswitch(globalconfig, "fix_translate_rank"),
                            D_getIconButton(functools.partial(vistranslate_rank, self)),
                        ],
                        [
                            "显示原文",
                            D_getsimpleswitch(
                                globalconfig,
                                "isshowrawtext",
                                callback=lambda x: __changeuibuttonstate(self, x),
                                name="show_original_switch",
                                parent=self,
                            ),
                            "",
                            "显示错误信息",
                            D_getsimpleswitch(
                                globalconfig,
                                "showtranexception",
                                callback=lambda x: changeshowerrorstate(self, x),
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="样式",
                    grid=(
                        [
                            "显示引擎",
                            functools.partial(_createseletengeinecombo, self),
                        ],
                        [functools.partial(creategoodfontwid, self)],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    return textgrid
