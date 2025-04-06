from qtsymbols import *
import functools, json
import gobject
from myutils.config import globalconfig
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getIconButton,
    IconButton,
    getIconButton,
    makescrollgrid,
    D_getsimpleswitch,
    getsmalllabel,
)
from gui.dynalang import LDialog


class dialog_selecticon(LDialog):
    def __init__(self, parent, dict, key, btn: IconButton) -> None:

        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.dict = dict
        self.btn = btn
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
        self.btn.setIconStr(_)


def doadjust(_):
    gobject.baseobject.translation_ui.adjustbuttons()
    gobject.baseobject.translation_ui.enterfunction()


def changerank(item, up, tomax, sortlist, savelist, savelay):

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

        w1 = savelay[0].indexOf(ww)
        w2 = savelay[0].indexOf(savelist[idx2 + headoffset][i])
        p1 = savelay[0].getItemPosition(w1)
        p2 = savelay[0].getItemPosition(w2)
        savelay[0].removeWidget(ww)
        savelay[0].removeWidget(savelist[idx2 + headoffset][i])

        savelay[0].addWidget(savelist[idx2 + headoffset][i], *p1)
        savelay[0].addWidget(ww, *p2)
    savelist[idx + headoffset], savelist[idx2 + headoffset] = (
        savelist[idx2 + headoffset],
        savelist[idx + headoffset],
    )
    doadjust(None)


def createbtn(self, k, key):
    btn = getIconButton(
        icon=globalconfig["toolbutton"]["buttons"][k][key],
    )
    btn.clicked.connect(
        functools.partial(
            dialog_selecticon,
            self,
            globalconfig["toolbutton"]["buttons"][k],
            key,
            btn,
        )
    )
    return btn


def createbuttonwidget(self, lay):
    # return table
    grids = [["显示", "", "", "对齐", "", "图标", "", "图标_2", "", "说明"]]
    sortlist = globalconfig["toolbutton"]["rank2"]
    savelist = []
    savelay = []

    for i, k in enumerate(sortlist):

        button_up = D_getIconButton(
            callback=functools.partial(
                changerank, k, True, False, sortlist, savelist, savelay
            ),
            icon="fa.arrow-up",
            callback2=functools.partial(
                changerank, k, True, True, sortlist, savelist, savelay
            ),
        )
        button_down = D_getIconButton(
            callback=functools.partial(
                changerank, k, False, False, sortlist, savelist, savelay
            ),
            icon="fa.arrow-down",
            callback2=functools.partial(
                changerank, k, False, True, sortlist, savelist, savelay
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
            getsmalllabel(),
        ]
        if "icon2" in globalconfig["toolbutton"]["buttons"][k]:
            l.append(functools.partial(createbtn, self, k, "icon2"))
        else:
            l.append("")
        l.append(getsmalllabel())
        if "belong" in globalconfig["toolbutton"]["buttons"][k]:
            belong = (
                "_"
                + "仅"
                + "_"
                + " ".join(globalconfig["toolbutton"]["buttons"][k]["belong"])
            )
        else:
            belong = ""
        l.append(globalconfig["toolbutton"]["buttons"][k]["tip"] + belong)
        grids.append(l)
    makescrollgrid(grids, lay, True, savelist, savelay)
