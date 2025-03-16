from qtsymbols import *
import functools, os
from myutils.post import POSTSOLVE
from myutils.utils import (
    selectdebugfile,
    checkpostlangmatch,
    dynamiclink,
    loadpostsettingwindowmethod,
)
from myutils.config import globalconfig, postprocessconfig, static_data
from gui.codeacceptdialog import codeacceptdialog
from gui.usefulwidget import (
    D_getIconButton,
    getIconButton,
    D_getsimpleswitch,
    makescrollgrid,
    getboxlayout,
    makesubtab_lazy,
)
from gui.inputdialog import (
    postconfigdialog,
    autoinitdialog,
    autoinitdialog_items,
    postconfigdialog2x,
)


def delaysetcomparetext(self, s, x):
    try:
        self.__fromtext.setPlainText(s)
        self.__totext.setPlainText(x)
    except:
        self.__fromtext_cache = s
        self.__totext_cache = x


def getcomparelayout(self):

    w = QWidget()
    layout = QHBoxLayout(w)
    fromtext = QPlainTextEdit()
    totext = QPlainTextEdit()
    solvebutton = getIconButton(
        callback=lambda: totext.setPlainText(POSTSOLVE(fromtext.toPlainText())),
        icon="fa.chevron-right",
    )

    layout.addWidget(fromtext)
    layout.addWidget(solvebutton)
    layout.addWidget(totext)
    self.__fromtext = fromtext
    self.__totext = totext
    try:
        fromtext.setPlainText(self.__fromtext_cache)
        totext.setPlainText(self.__totext_cache)
    except:
        pass
    return w


def setTab7_lazy(self, basel):
    grids = [
        [
            D_getIconButton(
                lambda: os.startfile(dynamiclink("{docs_server}/textprocess.html")),
                "fa.question",
            ),
            ("预处理方法", 5),
            "",
            "",
            "",
            ("调整执行顺序", 6),
        ]
    ]
    if set(postprocessconfig.keys()) != set(globalconfig["postprocess_rank"]):
        globalconfig["postprocess_rank"] = list(postprocessconfig.keys())
    sortlist = globalconfig["postprocess_rank"]
    savelist = []
    savelay = []

    def changerank(item, up, tomax):

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

    for i, post in enumerate(sortlist):
        if post == "_11":
            config = D_getIconButton(
                callback=lambda: selectdebugfile("./userconfig/mypost.py"),
                icon="fa.edit",
            )
        else:
            if post not in postprocessconfig:
                continue
            if post == "_remove_chaos":
                config = D_getIconButton(
                    callback=lambda: codeacceptdialog(self),
                )
            elif "args" in postprocessconfig[post]:

                if post == "stringreplace":
                    callback = functools.partial(
                        postconfigdialog2x,
                        self,
                        postprocessconfig[post]["args"]["internal"],
                        postprocessconfig[post]["name"],
                        ["正则", "转义", "原文内容", "替换为"],
                    )
                elif isinstance(
                    list(postprocessconfig[post]["args"].values())[0], dict
                ):
                    callback = functools.partial(
                        postconfigdialog,
                        self,
                        postprocessconfig[post]["args"]["替换内容"],
                        postprocessconfig[post]["name"],
                        ["原文内容", "替换为"],
                    )
                else:
                    items = autoinitdialog_items(postprocessconfig[post])
                    callback = functools.partial(
                        autoinitdialog,
                        self,
                        postprocessconfig[post]["args"],
                        postprocessconfig[post]["name"],
                        600,
                        items,
                    )
                config = D_getIconButton(callback=callback)
            else:
                config = ""

        button_up = D_getIconButton(
            callback=functools.partial(changerank, post, True, False),
            icon="fa.arrow-up",
            callback2=functools.partial(changerank, post, True, True),
        )
        button_down = D_getIconButton(
            callback=functools.partial(changerank, post, False, False),
            icon="fa.arrow-down",
            callback2=functools.partial(changerank, post, False, True),
        )

        l = [
            ((postprocessconfig[post]["name"]), 6),
            D_getsimpleswitch(postprocessconfig[post], "use"),
            config,
            "",
            button_up,
            button_down,
        ]
        grids.append(l)
    grids2 = [
        [
            D_getIconButton(
                lambda: os.startfile(dynamiclink("{docs_server}/transoptimi.html")),
                "fa.question",
            )
        ]
    ]
    for item in static_data["transoptimi"]:
        name = item["name"]
        visname = item["visname"]
        if checkpostlangmatch(name):
            grids2.append(
                [((visname), 6), D_getsimpleswitch(globalconfig["transoptimi"], name)]
            )
            setting = loadpostsettingwindowmethod(name)

            def __(_f, _1):
                return _f(_1)

            if setting:
                kwarg = dict(callback=functools.partial(__, setting, self))
                if name == "myprocess":
                    kwarg.update(dict(icon="fa.edit"))
                grids2[-1].append(D_getIconButton(**kwarg))
    grids2 += [[("", 15)]]

    def ___(lay: QVBoxLayout):
        vboxw, vbox = getboxlayout(
            [], lc=QVBoxLayout, margin0=True, makewidget=True, both=True
        )
        lay.addWidget(vboxw)
        makescrollgrid(grids, vbox, True, savelist, savelay)

        lay.addWidget(getcomparelayout(self))

    tab, dotab = makesubtab_lazy(
        ["文本预处理", "翻译优化"],
        [___, functools.partial(makescrollgrid, grids2)],
        delay=True,
    )
    basel.addWidget(tab)
    dotab()
