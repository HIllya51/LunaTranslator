from qtsymbols import *
import functools, json
import gobject
from myutils.config import globalconfig, ui_settings
from gui.usefulwidget import (
    D_getsimplecombobox,
    IconButton,
    getIconButton,
    D_getdoclink,
    D_getsimpleswitch,
    getsmalllabel,
    D_getspinbox,
    D_getcolorbutton,
    D_getIconButton,
    makegrid,
    GroupCardWidget,
    MySwitch,
    PopupWidget,
)
from gui.dynalang import LDialog, LLabel
from gui.setting.display_ui import toolcolorchange
from gui.fluent.settingtree import FluentSettingTree, wrap_setting_tree


class dialog_selecticon(LDialog):
    def __init__(
        self, parent, cb1, dict: dict, name, key, btn: IconButton, color
    ) -> None:

        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.cb1 = cb1
        self.dict = dict
        self.btn = btn
        self.name = name
        self.key = key
        self.setWindowTitle("选择图标")
        with open(
            "files/static/fonts/fontawesome4.7-webfont-charmap.json",
            "r",
            encoding="utf8",
        ) as ff:
            js = json.load(ff)

        self.curr = self.dict.get(self.key)
        lineEdit = QLineEdit(self)
        lineEdit.setText(self.curr)
        lineEdit.textChanged.connect(self.cb)
        hb = QHBoxLayout()
        hb.addWidget(LLabel("图标_|_字符_|_图片路径_|_luna"))
        hb.addWidget(lineEdit)
        vbox = QVBoxLayout(self)
        vbox.addLayout(hb)
        layout = QGridLayout()
        vbox.addLayout(layout)
        for i, name in enumerate(js):
            layout.addWidget(
                getIconButton(
                    functools.partial(self.selectcallback, "fa." + name),
                    icon="fa." + name,
                    color=color,
                ),
                i // 30,
                i % 30,
            )
        self.show()

    def cb(self, _):
        print(_)
        self.curr = _
        self.dict[self.key] = _
        try:
            self.btn.setIconStr(_)
            self.cb1()
        except:
            pass

    def selectcallback(self, _):
        print(_)
        self.curr = _
        self.dict[self.key] = _
        self.close()
        self.btn.setIconStr(_)
        self.cb1()


def doadjust(*_):
    gobject.base.translation_ui.adjustbuttons()
    gobject.base.translation_ui.enterfunction()


class _ToolButtonList(FluentSettingTree):
    """工具按钮列表：使用/设置（无标题列）/对齐/图标/说明/移动（末列），
    拖拽或上下移按钮排序改写 rank2。上下移循环：首行再上移到末尾、
    末行再下移到开头；右键置顶/置底。"""

    def __init__(self, host, parent=None):
        super().__init__(
            parent,
            titles=["使用", "", "对齐", "图标", "说明", ""],
            draggable=True,
        )
        self._host = host
        hdr = self.header()
        for c in (0, 1, 2, 3, 5):
            hdr.setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.rebuild()

    def rebuild(self):
        self.clear()
        for k in globalconfig["toolbutton"]["rank2"]:
            conf = globalconfig["toolbutton"]["buttons"][k]
            item = QTreeWidgetItem()
            item.setData(0, Qt.ItemDataRole.UserRole, k)
            self.addTopLevelItem(item)

            def _refreshtoolicon():
                gobject.base.translation_ui.titlebar.refreshtoolicon()

            iconbtn = createbtn(self._host, k, "icon", _refreshtoolicon)
            icon2btn = (createbtn(self._host, k, "icon2", _refreshtoolicon)
                        if "icon2" in conf else None)
            # 特设按钮：点击时才构造 setter 弹窗（PopupWidget 构造即显示）
            specialbtn = (D_getIconButton(
                callback=functools.partial(specialbuttonsettings[k],
                                           self._host))()
                if k in specialbuttonsettings else None)
            t = conf.get("tip", "")
            if "belong" in conf:
                t += "_(仅{}模式下可用)".format(
                    ",".join({"texthook": "HOOK", "ocr": "OCR"}.get(_, "?")
                             for _ in conf["belong"]))
            self.setItemWidget(item, 0, self._cell(
                D_getsimpleswitch(conf, "use", callback=doadjust)(),
                center=True))
            # 特设按钮独占一列（无标题；缺席则空）
            if specialbtn is not None:
                self.setItemWidget(item, 1, self._cell(specialbtn,
                                                       center=True))
            self.setItemWidget(item, 2, self._cell(
                D_getsimplecombobox(
                    ["居左", "居右", "居中"], conf, "align",
                    callback=doadjust, fixedsize=True)(),
                center=True))
            # 图标列：icon + 可选 icon2（缺席保留等宽槽位，行间对齐）
            self.setItemWidget(item, 3, self._cell(
                iconbtn,
                icon2btn if icon2btn is not None else self._slot(iconbtn),
                center=True))
            self.setItemWidget(item, 4, self._cell(
                D_getdoclink("alltoolbuttons.html#anchor-" + k)(),
                LLabel(t),
            ))
            # 上下移按钮列（末列，右键置顶/置底）
            self.setItemWidget(
                item, 5, self._movecell(functools.partial(self._move, k)))

    def _applymove(self, idx1, idx2):
        rank = globalconfig["toolbutton"]["rank2"]
        k = rank.pop(idx1)
        rank.insert(idx2, k)
        self.rebuild()
        doadjust()

    def _ondrop(self, idx1, idx2):
        self._applymove(idx1, idx2)

    def _move(self, k, up, tomax):
        """上下移按钮：循环移一位（首行再上移到末尾、末行再下移到
        开头），右键（tomax）置顶/置底。"""
        rank = globalconfig["toolbutton"]["rank2"]
        idx1 = rank.index(k)
        if tomax:
            idx2 = 0 if up else len(rank) - 1
        else:
            idx2 = (idx1 + (-1 if up else 1)) % len(rank)
        if idx2 == idx1:
            return
        self._applymove(idx1, idx2)


savebtns: "dict[tuple[str, str], IconButton]" = {}


def refreshtoolicon():
    for (name, key), btn in savebtns.items():

        color = (
            ui_settings.get("buttoncolor_1", "#ff03f2")
            if "icon" == key
            and globalconfig["toolbutton"]["buttons"][name].get("icon2")
            else ui_settings.get("buttoncolor", "#2e2eff")
        )
        btn.setColor(color)


def createbtn(self, name, key, cb):
    color = (
        ui_settings.get("buttoncolor_1", "#ff03f2")
        if "icon" == key and globalconfig["toolbutton"]["buttons"][name].get("icon2")
        else ui_settings.get("buttoncolor", "#2e2eff")
    )
    btn = getIconButton(
        icon=globalconfig["toolbutton"]["buttons"][name][key],
        color=color,
    )
    savebtns[(name, key)] = btn
    btn.clicked.connect(
        functools.partial(
            dialog_selecticon,
            self,
            cb,
            globalconfig["toolbutton"]["buttons"][name],
            name,
            key,
            btn,
            color,
        )
    )
    return btn


class LeftRightFunctionSetter(PopupWidget):
    def __init__(self, key, default, text1, text2, p):
        super().__init__(p)
        self.key = key
        layout = QGridLayout()
        self.setLayout(layout)

        self.btns: "list[list[QPushButton]]" = []
        for i in range(2):
            row = []
            for j in range(2):
                btn = MySwitch(sign=globalconfig.get(key, default) == (i == j))
                btn.clicked.connect(functools.partial(self.click, btn, i, j))
                row.append(btn)
                layout.addWidget(btn, i + 1, j + 1)
            self.btns.append(row)

        layout.addWidget(LLabel(text1), 1, 0)
        layout.addWidget(LLabel(text2), 2, 0)
        layout.addWidget(LLabel("左键点击"), 0, 1)
        layout.addWidget(LLabel("右键点击"), 0, 2)

        self.display()

    def click(self, btn: QPushButton, i, j):
        globalconfig[self.key] = (i == j) == btn.isChecked()
        for row in range(2):
            for col in range(2):
                if (i, j) != (row, col):
                    self.btns[row][col].setChecked(
                        btn.isChecked()
                        if (i != row and j != col)
                        else not btn.isChecked()
                    )


specialbuttonsettings = {
    "fullscreen": functools.partial(
        LeftRightFunctionSetter,
        "fullscreen_left_full",
        True,
        "全屏模式缩放",
        "窗口模式缩放",
    ),
    "grabwindow": functools.partial(
        LeftRightFunctionSetter,
        "grabwindow_left_savefile",
        True,
        "保存到文件",
        "保存到剪贴板",
    ),
}


def createbuttonwidget(self, lay: QLayout):
    # 页面内容：两张独立包裹（间距 8，同核心设置页多卡布局）
    content = QWidget()
    vlay = QVBoxLayout(content)
    vlay.setContentsMargins(16, 16, 16, 12)
    vlay.setSpacing(8)
    lay.addWidget(content)

    # 卡 1：大小 / 颜色
    card = GroupCardWidget()
    host = card.contentWidget()
    hostlay = QVBoxLayout(host)
    hostlay.setContentsMargins(0, 0, 0, 0)
    grids = [
        [
            getsmalllabel("大小"),
            D_getspinbox(
                5,
                100,
                ui_settings,
                "buttonsize",
                callback=lambda _: toolcolorchange(),
                default=25,
            ),
            getsmalllabel(""),
            getsmalllabel("颜色"),
            D_getcolorbutton(
                self,
                ui_settings,
                "buttoncolor",
                callback=lambda _: (toolcolorchange(), refreshtoolicon()),
                default="#2e2eff",
            ),
            D_getcolorbutton(
                self,
                ui_settings,
                "buttoncolor_1",
                callback=lambda _: (toolcolorchange(), refreshtoolicon()),
                default="#ff03f2",
            ),
            D_getcolorbutton(
                self,
                ui_settings,
                "button_color_normal",
                callback=lambda _: (toolcolorchange(), refreshtoolicon()),
                default="#FFFFFF",
            ),
            "",
        ]
    ]
    wid, do = makegrid(grids, delay=True)
    wid.layout().setContentsMargins(0, 0, 0, 0)
    hostlay.addWidget(wid)
    do()
    vlay.addWidget(card)

    # 包 2：工具按钮列表（StyledPanel 包裹，Gallery 包表格/树的方式）
    vlay.addWidget(wrap_setting_tree(_ToolButtonList(self)), 1)
