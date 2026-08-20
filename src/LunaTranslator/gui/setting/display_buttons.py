from qtsymbols import *
import functools, json
import gobject
from myutils.config import globalconfig, ui_settings
from gui.usefulwidget import (
    D_getsimplecombobox,
    IconButton,
    getIconButton,
    D_getdoclink,
    D_getIconButton_mousefollow,
    makescrollgrid,
    D_getsimpleswitch,
    getsmalllabel,
    getcenterX,
    D_getspinbox,
    D_getcolorbutton,
    D_getIconButton,
    makegrid,
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
        self.btn.setIconStr(_)
        self.cb1()

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


def changerank(item, up, tomax, sortlist: list, savelist, savelay, savescroll):
    idx = sortlist.index(item)
    if tomax:
        idx2 = 0 if up else (len(sortlist) - 1)
    else:
        idx2 = idx + (-1 if up else 1)
    if idx2 < 0 or idx2 >= len(sortlist):
        return
    headoffset = 1
    sortlist[idx], sortlist[idx2] = sortlist[idx2], sortlist[idx]
    for i, ww in enumerate(savelist[idx + headoffset]):
        ll: QGridLayout = savelay[0]
        w1 = ll.indexOf(ww)
        w2 = ll.indexOf(savelist[idx2 + headoffset][i])
        p1 = ll.getItemPosition(w1)
        p2 = ll.getItemPosition(w2)
        ll.removeWidget(ww)
        ll.removeWidget(savelist[idx2 + headoffset][i])
        ll.addWidget(savelist[idx2 + headoffset][i], *p1)
        ll.addWidget(ww, *p2)
    savelist[idx + headoffset], savelist[idx2 + headoffset] = (
        savelist[idx2 + headoffset],
        savelist[idx + headoffset],
    )
    if tomax:
        scroll: QScrollArea = savescroll[0]
        if up:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().minimum())
        else:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    doadjust()


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
    lay.addWidget(wid)
    do()

    sortlist = globalconfig["toolbutton"]["rank2"]
    savelist = []
    savelay = []
    savescroll = []
    grids = [
        [
            getcenterX("使用"),
            "",
            "",
            "",
            getcenterX("对齐"),
            "",
            (getcenterX("图标"), 2),
            "",
            ("说明", 2),
        ]
    ]
    for i, k in enumerate(sortlist):

        button_up = D_getIconButton_mousefollow(
            callback=functools.partial(
                changerank, k, True, False, sortlist, savelist, savelay, savescroll
            ),
            icon="fa.arrow-up",
            callback2=functools.partial(
                changerank, k, True, True, sortlist, savelist, savelay, savescroll
            ),
        )
        button_down = D_getIconButton_mousefollow(
            callback=functools.partial(
                changerank, k, False, False, sortlist, savelist, savelay, savescroll
            ),
            icon="fa.arrow-down",
            callback2=functools.partial(
                changerank, k, False, True, sortlist, savelist, savelay, savescroll
            ),
        )

        l = [
            D_getsimpleswitch(
                globalconfig["toolbutton"]["buttons"][k],
                "use",
                callback=doadjust,
            ),
            (
                D_getIconButton(
                    callback=functools.partial(specialbuttonsettings[k], self)
                )
                if k in specialbuttonsettings
                else getsmalllabel()
            ),
            button_up,
            button_down,
            D_getsimplecombobox(
                ["居左", "居右", "居中"],
                globalconfig["toolbutton"]["buttons"][k],
                "align",
                callback=doadjust,
                fixedsize=True,
            ),
            getsmalllabel(),
            functools.partial(
                createbtn,
                self,
                k,
                "icon",
                lambda: gobject.base.translation_ui.titlebar.refreshtoolicon(),
            ),
        ]
        if "icon2" in globalconfig["toolbutton"]["buttons"][k]:
            l.append(
                functools.partial(
                    createbtn,
                    self,
                    k,
                    "icon2",
                    lambda: gobject.base.translation_ui.titlebar.refreshtoolicon(),
                )
            )
        else:
            l.append("")
        l.append(getsmalllabel())
        t = globalconfig["toolbutton"]["buttons"][k].get("tip", "")
        if "belong" in globalconfig["toolbutton"]["buttons"][k]:
            t += "_(仅{}模式下可用)".format(
                ",".join(
                    {"texthook": "HOOK", "ocr": "OCR"}.get(_, "?")
                    for _ in globalconfig["toolbutton"]["buttons"][k]["belong"]
                )
            )
        l.append(D_getdoclink("alltoolbuttons.html#anchor-" + k))
        l.append(t)
        grids.append(l)
    makescrollgrid(grids, lay, savelist, savelay)
    savescroll.append(lay.itemAt(lay.count() - 1).widget())
