from qtsymbols import *
import functools, json
import gobject
from myutils.config import globalconfig, ui_settings, _TR
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


class _ToolButtonList(QTreeWidget):
    """工具按钮列表：使用/对齐/图标/说明 四列（列为标题，_TR 翻译 +
    居中），行内控件经 setItemWidget 挂载。可选控件（使用列的特设
    按钮、图标列的 icon2）缺席时保留等宽槽位，各行控件对齐。排序为
    自管拖拽——Qt 的 InternalMove 对带 item widget 的行是 remove+insert
    重建，widget 全部丢失（同侧栏导航树，见 _gamelistnav 注释），故
    自管 DnD：拖拽落点改写 rank2 后整体重建行（几十行小控件，重建
    成本可忽略）。"""

    _HEADER_TITLES = ["使用", "对齐", "图标", "说明"]

    def __init__(self, host, parent=None):
        super().__init__(parent)
        self._host = host
        self._dragitem = None
        self._dragpos = None
        self.setColumnCount(4)
        self.setHeaderLabels([_TR(t) for t in self._HEADER_TITLES])
        hdr = self.header()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        for c in range(3):
            hdr.setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 自管拖拽（不启用 Qt 的 dragDropMode）
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # 透明：让内容卡底色透出（QSS 只作用于本控件类，见 makescroll 注释）
        self.setStyleSheet(
            "QTreeWidget{background-color:transparent;border:0;}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.rebuild()

    def updatelangtext(self):
        # 语言切换：表头标题重翻译（app 级事件过滤器驱动，同 LLabel）
        for i, t in enumerate(self._HEADER_TITLES):
            self.headerItem().setText(i, _TR(t))

    # ---- 行构建 ----
    def _cell(self, *ws, center=False):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(8)
        if center:
            lay.addStretch(1)
        for x in ws:
            if x is not None:
                lay.addWidget(x)
        if center:
            lay.addStretch(1)
        return w

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

            def _slot():
                # 等宽占位：可选按钮缺席时仍保留槽位（同尺寸按钮），行间对齐
                sp = QWidget()
                sp.setFixedSize(iconbtn.size())
                return sp

            # 特设按钮：点击时才构造 setter 弹窗（PopupWidget 构造即显示）
            specialbtn = (D_getIconButton(
                callback=functools.partial(specialbuttonsettings[k],
                                           self._host))()
                if k in specialbuttonsettings else None)
            usecell = self._cell(
                D_getsimpleswitch(conf, "use", callback=doadjust)(),
                specialbtn if specialbtn is not None else _slot(),
                center=True,
            )
            aligncell = self._cell(
                D_getsimplecombobox(
                    ["居左", "居右", "居中"], conf, "align",
                    callback=doadjust, fixedsize=True)(),
                center=True,
            )
            iconcell = self._cell(
                iconbtn,
                icon2btn if icon2btn is not None else _slot(),
                center=True,
            )
            t = conf.get("tip", "")
            if "belong" in conf:
                t += "_(仅{}模式下可用)".format(
                    ",".join({"texthook": "HOOK", "ocr": "OCR"}.get(_, "?")
                             for _ in conf["belong"]))
            tipcell = self._cell(
                D_getdoclink("alltoolbuttons.html#anchor-" + k)(),
                LLabel(t),
            )
            self.setItemWidget(item, 0, usecell)
            self.setItemWidget(item, 1, aligncell)
            self.setItemWidget(item, 2, iconcell)
            self.setItemWidget(item, 3, tipcell)

    # ---- 自管拖拽排序（DnD 事件坐标均为 viewport 坐标）----
    def mousePressEvent(self, ev):
        self._dragitem = self.itemAt(ev.pos())
        self._dragpos = ev.pos()
        return super().mousePressEvent(ev)

    def mouseMoveEvent(self, e):
        if (
            self._dragitem is not None
            and (e.buttons() & Qt.MouseButton.LeftButton)
            and (e.pos() - self._dragpos).manhattanLength()
            >= QApplication.startDragDistance()
        ):
            mime = QMimeData()
            mime.setText("lunatoolbtnrankmove")
            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mouseMoveEvent(e)

    def _isrankmove(self, e):
        return e.mimeData().text().startswith("lunatoolbtnrankmove")

    def dragEnterEvent(self, e):
        if self._isrankmove(e):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._isrankmove(e):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        if not self._isrankmove(e):
            e.ignore()
            return
        src = self._dragitem
        self._dragitem = None
        if src is None:
            e.ignore()
            return
        idx1 = self.indexOfTopLevelItem(src)
        if idx1 < 0:
            e.ignore()
            return
        pos = e.pos()
        dst = self.itemAt(pos)
        if dst is None:
            # 落在内容之下：移到末尾
            idx2 = self.topLevelItemCount()
        else:
            r = self.visualItemRect(dst)
            idx2 = self.indexOfTopLevelItem(dst) + (
                1 if pos.y() > r.center().y() else 0)
        if idx1 < idx2:
            idx2 -= 1
        rank = globalconfig["toolbutton"]["rank2"]
        if 0 <= idx2 < len(rank) and idx2 != idx1:
            k = rank.pop(idx1)
            rank.insert(idx2, k)
            self.rebuild()
            doadjust()
        e.acceptProposedAction()


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

    # 包 2：工具按钮列表——tree 包 QFrame::StyledPanel（Gallery 包表格/树
    # 的方式：插件 PE_Frame = Base 底色 + 6px 圆角 + lineEdit 式描边）
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    flay = QVBoxLayout(frame)
    flay.setContentsMargins(0, 0, 0, 0)
    flay.addWidget(_ToolButtonList(self))
    vlay.addWidget(frame, 1)
