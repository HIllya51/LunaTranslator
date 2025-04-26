from qtsymbols import *
import functools, json
import gobject
from myutils.config import globalconfig
from gui.usefulwidget import (
    D_getsimplecombobox,
    IconButton,
    getIconButton,
    D_getIconButton_mousefollow,
    makescrollgrid,
    D_getsimpleswitch,
    getsmalllabel,
    qtawesome,
    D_getspinbox,
    D_getcolorbutton,
    makegrid,
)
from gui.dynalang import LDialog
from gui.setting.display_ui import toolcolorchange


class dialog_selecticon(LDialog):
    def __init__(self, parent, dict, name, key, btn: IconButton) -> None:

        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
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

        layout = QGridLayout(self)
        for i, name in enumerate(js):
            layout.addWidget(
                getIconButton(
                    functools.partial(self.selectcallback, "fa." + name),
                    icon="fa." + name,
                ),
                i // 30,
                i % 30,
            )
        self.show()

    def selectcallback(self, _):
        print(_)
        self.dict[self.key] = _
        self.close()
        gobject.baseobject.translation_ui.refreshtoolicon()

        color = (
            globalconfig["buttoncolor_1"]
            if "icon" == self.key
            and globalconfig["toolbutton"]["buttons"][self.name].get("icon2")
            else globalconfig["buttoncolor"]
        )
        self.btn.setIcon(qtawesome.icon(_, color=color))


def doadjust(_):
    gobject.baseobject.translation_ui.adjustbuttons()
    gobject.baseobject.translation_ui.enterfunction()


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
    doadjust(None)


savebtns = {}


def refreshtoolicon():
    for (name, key), btn in savebtns.items():

        color = (
            globalconfig["buttoncolor_1"]
            if "icon" == key
            and globalconfig["toolbutton"]["buttons"][name].get("icon2")
            else globalconfig["buttoncolor"]
        )
        icon = globalconfig["toolbutton"]["buttons"][name][key]
        btn.setIcon(qtawesome.icon(icon, color=color))
        btn.setStyleSheet(
            """IconButton{{border:transparent;padding: 0px;}} 
            IconButton:hover{{ background-color: {color1}; }}""".format(
                color1=globalconfig["button_color_normal"] if name != "quit" else "red",
            )
        )


def createbtn(self, name, key):
    btn = getIconButton(
        icon=globalconfig["toolbutton"]["buttons"][name][key],
    )
    savebtns[(name, key)] = btn
    btn.clicked.connect(
        functools.partial(
            dialog_selecticon,
            self,
            globalconfig["toolbutton"]["buttons"][name],
            name,
            key,
            btn,
        )
    )
    return btn


def createbuttonwidget(self, lay: QLayout):
    grids = [
        [
            getsmalllabel("大小"),
            D_getspinbox(
                5,
                100,
                globalconfig,
                "buttonsize",
                callback=lambda _: toolcolorchange(),
            ),
            getsmalllabel(""),
            getsmalllabel("颜色"),
            D_getcolorbutton(
                self,
                globalconfig,
                "buttoncolor",
                callback=lambda: (toolcolorchange(), refreshtoolicon()),
            ),
            D_getcolorbutton(
                self,
                globalconfig,
                "buttoncolor_1",
                callback=lambda: (toolcolorchange(), refreshtoolicon()),
            ),
            D_getcolorbutton(
                self,
                globalconfig,
                "button_color_normal",
                callback=lambda: (toolcolorchange(), refreshtoolicon()),
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
    grids = [["显示", "", "", "对齐", "", ("图标", 2), "", "说明"]]
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
            functools.partial(createbtn, self, k, "icon"),
        ]
        if "icon2" in globalconfig["toolbutton"]["buttons"][k]:
            l.append(functools.partial(createbtn, self, k, "icon2"))
        else:
            l.append("")
        l.append(getsmalllabel())
        t = globalconfig["toolbutton"]["buttons"][k]["tip"]
        if "belong" in globalconfig["toolbutton"]["buttons"][k]:
            t += "_(仅_{})".format(
                " ".join(globalconfig["toolbutton"]["buttons"][k]["belong"])
            )
        l.append(t)
        grids.append(l)
    makescrollgrid(grids, lay, savelist, savelay)
    savescroll.append(lay.itemAt(lay.count() - 1).widget())
    refreshtoolicon()
