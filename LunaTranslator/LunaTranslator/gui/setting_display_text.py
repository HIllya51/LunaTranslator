from qtsymbols import *
import functools
import gobject, os
from myutils.config import globalconfig, _TRL, _TR, static_data
from gui.inputdialog import multicolorset
from myutils.wrapper import tryprint
from gui.usefulwidget import (
    D_getsimplecombobox,
    Singleton_close,
    saveposwindow,
    getsimpleswitch,
    D_getspinbox,
    getspinbox,
    D_getIconButton,
    D_getcolorbutton,
    getcolorbutton,
    D_getsimpleswitch,
    selectcolor,
    FocusFontCombo,
    FocusCombo,
    FocusDoubleSpin,
    FocusSpin,
)


def maybehavefontsizespin(self, t):
    if "fontSize_spinBox" in dir(self):
        self.fontSize_spinBox.setValue(self.fontSize_spinBox.value() + 0.5 * t)
    else:
        globalconfig["fontsize"] += 0.5 * t


def createfontsizespin(self):
    self.fontSize_spinBox = getspinbox(
        1, 100, globalconfig, "fontsize", double=True, step=0.1
    )
    return self.fontSize_spinBox


def __changeuibuttonstate(self, x):
    gobject.baseobject.translation_ui.refreshtoolicon()
    try:
        self.show_hira_switch.setEnabled(x)
        self.show_fenciswitch.setEnabled(x)
    except:
        pass


def createtextfontcom(key):
    font_comboBox = FocusFontCombo()
    font_comboBox.currentTextChanged.connect(lambda x: globalconfig.__setitem__(key, x))
    font_comboBox.setCurrentFont(QFont(globalconfig[key]))
    return font_comboBox


def createshoworiginswitch(self):
    self.show_original_switch = getsimpleswitch(
        globalconfig, "isshowrawtext", callback=lambda x: __changeuibuttonstate(self, x)
    )
    return self.show_original_switch


def createhiraswitch(self):

    self.show_hira_switch = getsimpleswitch(
        globalconfig, "isshowhira", enable=globalconfig["isshowrawtext"]
    )
    return self.show_hira_switch


def createfenciwitch(self):
    self.show_fenciswitch = getsimpleswitch(
        globalconfig, "show_fenci", enable=globalconfig["isshowrawtext"]
    )
    return self.show_fenciswitch


@Singleton_close
class extrahtml(saveposwindow):
    def tryload(self):

        use = "userconfig/extrahtml.html"
        if os.path.exists(use) == False:
            use = r"LunaTranslator\rendertext\exampleextrahtml.html"
        with open(use, "r", encoding="utf8") as ff:
            self.vistext.setPlainText(ff.read())

    @tryprint
    def applyhtml(self, _):
        gobject.baseobject.translation_ui.translate_text.textbrowser.set_extra_html(
            self.vistext.toPlainText()
        )

    def savehtml(self):
        os.makedirs("userconfig", exist_ok=True)
        with open("userconfig/extrahtml.html", "w", encoding="utf8") as ff:
            ff.write(self.vistext.toPlainText())

    def __init__(self, parent) -> None:
        super().__init__(parent, poslist=globalconfig["geo_extrahtml"])
        self.setWindowTitle(_TR("额外的html"))

        self.btn_save = QPushButton(_TR("保存"))
        self.btn_save.clicked.connect(self.savehtml)
        self.btn_apply = QPushButton(_TR("测试"))
        self.btn_apply.clicked.connect(self.applyhtml)
        self.vistext = QPlainTextEdit()
        lay = QVBoxLayout()
        hl = QHBoxLayout()
        hl.addWidget(self.btn_save)
        hl.addWidget(self.btn_apply)
        lay.addWidget(self.vistext)
        lay.addLayout(hl)
        w = QWidget()
        w.setLayout(lay)
        self.setCentralWidget(w)
        self.tryload()
        self.show()


def clearlayout(ll: QLayout):
    while ll.count():
        item = ll.takeAt(0)
        if not item:
            continue
        ll.removeItem(item)
        w = item.widget()
        if w:
            w.deleteLater()
            continue
        l = item.layout()
        if l:
            clearlayout(l)
            l.deleteLater()
            continue


def createinternalfontsettings(self, forml, group, _type):

    globalconfig["rendertext_using_internal"][group] = _type
    __internal = globalconfig["rendertext"][group][_type]
    dd = __internal.get("args", {})

    clearlayout(forml)

    for key in dd:
        line = __internal["argstype"][key]
        name = line["name"]
        _type = line["type"]
        if _type == "colorselect":
            lineW = getcolorbutton(
                dd,
                key,
                transparent=False,
                callback=functools.partial(
                    lambda dd, key, _: selectcolor(
                        self, dd, key, self.miaobian_color_button
                    ),
                    dd,
                    key,
                ),
                name="miaobian_color_button",
                parent=self,
            )
        elif _type == "spin":
            lineW = FocusDoubleSpin()
            lineW.setMinimum(line.get("min", 0))
            lineW.setMaximum(line.get("max", 100))
            lineW.setSingleStep(line.get("step", 0.1))
            lineW.setValue(dd[key])
            lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))

        elif _type == "intspin":
            lineW = FocusSpin()
            lineW.setMinimum(line.get("min", 0))
            lineW.setMaximum(line.get("max", 100))
            lineW.setSingleStep(line.get("step", 1))
            lineW.setValue(dd[key])
            lineW.valueChanged.connect(functools.partial(dd.__setitem__, key))
        forml.addRow(
            _TR(name),
            lineW,
        )


def resetgroudswitchcallback(self, group):
    clearlayout(self.goodfontsettingsformlayout)

    goodfontgroupswitch = FocusCombo()

    # if group == "textbrowser" or group == "QWebEngine":

    if group == "webview" or group == "QWebEngine":
        _btn = QPushButton(_TR("额外的html"))
        self.goodfontsettingsformlayout.addRow(_btn)
        _btn.clicked.connect(lambda: extrahtml(self))
    if group == "QWebEngine":
        group = "webview"
    __form = QFormLayout()
    __form.addRow(_TR("字体样式"), goodfontgroupswitch)
    self.goodfontsettingsformlayout.addRow(__form)
    forml = QFormLayout()
    __form.addRow(forml)

    goodfontgroupswitch.addItems(
        _TRL(
            [
                globalconfig["rendertext"][group][x]["name"]
                for x in static_data["textrender"][group]
            ]
        )
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


def creategoodfontwid(self):

    self.goodfontsettingsWidget = QGroupBox()
    self.goodfontsettingsformlayout = QFormLayout()
    self.goodfontsettingsWidget.setLayout(self.goodfontsettingsformlayout)
    return self.goodfontsettingsWidget, lambda: resetgroudswitchcallback(
        self, globalconfig["rendertext_using"]
    )


def xianshigrid(self):
    visengine = ["Webview2", "Qt"]
    visengine_internal = ["webview", "textbrowser"]
    if gobject.testuseqwebengine():
        visengine.append("QWebEngine")
        visengine_internal.append("QWebEngine")
    textgrid = [
        [
            (
                dict(
                    title="样式",
                    type="grid",
                    grid=(
                        [
                            ("原文字体", 3),
                            (functools.partial(createtextfontcom, "fonttype"), 6),
                        ],
                        [
                            ("译文字体", 3),
                            (functools.partial(createtextfontcom, "fonttype2"), 6),
                        ],
                        [
                            ("原文颜色", 3),
                            D_getcolorbutton(
                                globalconfig,
                                "rawtextcolor",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "rawtextcolor",
                                    self.original_color_button,
                                ),
                                name="original_color_button",
                                parent=self,
                            ),
                        ],
                        [
                            ("字体大小", 3),
                            (functools.partial(createfontsizespin, self), 3),
                            "",
                            ("额外的行间距", 3),
                            (D_getspinbox(-100, 100, globalconfig, "extra_space"), 3),
                        ],
                        [
                            ("居中显示", 3),
                            D_getsimpleswitch(globalconfig, "showatcenter"),
                            ("", 3),
                            ("加粗字体", 3),
                            D_getsimpleswitch(globalconfig, "showbold"),
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
                    type="grid",
                    grid=(
                        [
                            ("显示引擎_重启生效", 3),
                            (
                                D_getsimplecombobox(
                                    visengine,
                                    globalconfig,
                                    "rendertext_using",
                                    internallist=visengine_internal,
                                    callback=functools.partial(
                                        resetgroudswitchcallback, self
                                    ),
                                ),
                                6,
                            ),
                        ],
                        [(functools.partial(creategoodfontwid, self), 0)],
                    ),
                ),
                0,
                "group",
            )
        ],
        [
            (
                dict(
                    title="注音",
                    type="grid",
                    grid=(
                        [
                            ("显示", 5),
                            functools.partial(createhiraswitch, self),
                            "",
                            ("颜色", 5),
                            D_getcolorbutton(
                                globalconfig,
                                "jiamingcolor",
                                callback=lambda: selectcolor(
                                    self,
                                    globalconfig,
                                    "jiamingcolor",
                                    self.jiamingcolor_b,
                                ),
                                name="jiamingcolor_b",
                                parent=self,
                            ),
                        ],
                        [
                            ("字体缩放", 5),
                            D_getspinbox(
                                0.05,
                                1,
                                globalconfig,
                                "kanarate",
                                double=True,
                                step=0.05,
                                dec=2,
                            ),
                            "",
                            ("日语注音方案", 5),
                            D_getsimplecombobox(
                                _TRL(["平假名", "片假名", "罗马音"]),
                                globalconfig,
                                "hira_vis_type",
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
                    title="分词",
                    type="grid",
                    grid=(
                        [
                            ("语法加亮", 5),
                            functools.partial(createfenciwitch, self),
                            "",
                            ("词性颜色(需要Mecab)", 5),
                            D_getIconButton(
                                callback=lambda: multicolorset(self), icon="fa.gear"
                            ),
                        ],
                        [
                            ("点击单词查词", 5),
                            (D_getsimpleswitch(globalconfig, "usesearchword"), 1),
                            "",
                            ("点击单词复制", 5),
                            (D_getsimpleswitch(globalconfig, "usecopyword"), 1),
                        ],
                        [
                            ("使用原型查询", 5),
                            (D_getsimpleswitch(globalconfig, "usewordorigin"), 1),
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
                    title="显示行为",
                    type="grid",
                    grid=(
                        [
                            ("显示原文", 5),
                            functools.partial(createshoworiginswitch, self),
                            "",
                            ("显示翻译", 5),
                            (D_getsimpleswitch(globalconfig, "showfanyi"), 1),
                        ],
                        [
                            ("显示翻译器名称", 5),
                            (D_getsimpleswitch(globalconfig, "showfanyisource"), 1),
                            "",
                            ("最长显示字数", 5),
                            (
                                D_getspinbox(
                                    0, 1000000, globalconfig, "maxoriginlength"
                                ),
                                3,
                            ),
                        ],
                        [
                            ("收到翻译结果时才刷新", 5),
                            D_getsimpleswitch(globalconfig, "refresh_on_get_trans"),
                        ],
                        [
                            ("可选取的", 5),
                            D_getsimpleswitch(
                                globalconfig,
                                "selectable",
                                callback=lambda x: gobject.baseobject.translation_ui.refreshtoolicon(),
                                parent=self,
                                name="selectable_btn",
                            ),
                        ],
                    ),
                ),
                0,
                "group",
            )
        ],
    ]
    return textgrid
