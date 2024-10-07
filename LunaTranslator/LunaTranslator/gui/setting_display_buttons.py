from qtsymbols import *
import functools, json
import qtawesome, gobject
from myutils.config import globalconfig
from myutils.wrapper import Singleton
from gui.usefulwidget import (
    D_getsimplecombobox,
    D_getIconButton,
    getIconButton,
    makescrollgrid,
    D_getsimpleswitch,
)
from gui.dynalang import LDialog


@Singleton
class dialog_selecticon(LDialog):
    def __init__(self, parent, dict, key) -> None:

        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.dict = dict
        self.key = key
        self.setWindowTitle("选择图标")
        with open(
            "./files/fonts/fontawesome4.7-webfont-charmap.json", "r", encoding="utf8"
        ) as ff:
            js = json.load(ff)

        layout = QGridLayout()
        self.setLayout(layout)
        for i, name in enumerate(js):
            layout.addWidget(
                getIconButton(
                    functools.partial(self.selectcallback, "fa." + name),
                    qicon=qtawesome.icon(
                        "fa." + name, color=globalconfig["buttoncolor"]
                    ),
                ),
                i // 30,
                i % 30,
            )
        self.show()

    def selectcallback(self, _):
        print(_)
        self.dict[self.key] = _
        self.close()


def doadjust(_):
    gobject.baseobject.translation_ui.adjustbuttons()
    gobject.baseobject.translation_ui.enterfunction()


def changerank(item, up, sortlist, savelist, savelay):

    idx = sortlist.index(item)
    idx2 = idx + (-1 if up else 1)
    if idx2 < 0 or idx2 >= len(sortlist):
        return
    headoffset = 1
    idx2 = idx + (-1 if up else 1)
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


def createbuttonwidget(self, lay):
    # return table
    grids = [["显示", "", "", "对齐", "图标", "图标2", "说明"]]
    sortlist = globalconfig["toolbutton"]["rank2"]
    savelist = []
    savelay = []

    for i, k in enumerate(sortlist):

        button_up = D_getIconButton(
            callback=functools.partial(
                changerank, k, True, sortlist, savelist, savelay
            ),
            icon="fa.arrow-up",
        )
        button_down = D_getIconButton(
            callback=functools.partial(
                changerank, k, False, sortlist, savelist, savelay
            ),
            icon="fa.arrow-down",
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
            D_getIconButton(
                functools.partial(
                    dialog_selecticon,
                    self,
                    globalconfig["toolbutton"]["buttons"][k],
                    "icon",
                ),
                qicon=qtawesome.icon(
                    globalconfig["toolbutton"]["buttons"][k]["icon"],
                    color=globalconfig["buttoncolor"],
                ),
            ),
        ]
        if "icon2" in globalconfig["toolbutton"]["buttons"][k]:
            l.append(
                D_getIconButton(
                    functools.partial(
                        dialog_selecticon,
                        self,
                        globalconfig["toolbutton"]["buttons"][k],
                        "icon2",
                    ),
                    qicon=qtawesome.icon(
                        globalconfig["toolbutton"]["buttons"][k]["icon2"],
                        color=globalconfig["buttoncolor"],
                    ),
                ),
            )
        else:
            l.append("")
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
